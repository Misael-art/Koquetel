// PT-06 disposable harness (NON-PRODUCTION): lease recovery + fencing after holder
// death. OFD locks, serialized epoch counter, transactional counter, and the journal
// epoch classifier. Synthetic inputs; no secrets. Outside the product build graph.
use rusqlite::Connection;
use std::os::unix::io::RawFd;
use std::time::{SystemTime, UNIX_EPOCH};
fn now_ns() -> u128 { SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() }
fn open_lease(path: &str) -> RawFd {
    let c = std::ffi::CString::new(path).unwrap();
    unsafe { libc::open(c.as_ptr(), libc::O_RDWR | libc::O_CREAT, 0o600) }
}
fn ofd_lock(fd: RawFd, wait: bool) -> bool {
    let fl = libc::flock { l_type: libc::F_WRLCK as i16, l_whence: libc::SEEK_SET as i16,
        l_start: 0, l_len: 0, l_pid: 0 };
    let cmd = if wait { libc::F_OFD_SETLKW } else { libc::F_OFD_SETLK };
    unsafe { libc::fcntl(fd, cmd, &fl) == 0 }
}
fn set_cloexec(fd: RawFd) { unsafe { let f = libc::fcntl(fd, libc::F_GETFD); libc::fcntl(fd, libc::F_SETFD, f | libc::FD_CLOEXEC); } }
fn db(path: &str) -> Connection {
    let c = Connection::open(path).unwrap();
    c.pragma_update(None, "journal_mode", &"WAL").unwrap();
    c.pragma_update(None, "synchronous", &"FULL").unwrap();
    c.pragma_update(None, "busy_timeout", 5000).unwrap();
    c.execute_batch(
        "CREATE TABLE IF NOT EXISTS counter(id INTEGER PRIMARY KEY, n INTEGER);
         INSERT OR IGNORE INTO counter(id,n) VALUES(1,0);
         CREATE TABLE IF NOT EXISTS epoch(id INTEGER PRIMARY KEY, e INTEGER);
         INSERT OR IGNORE INTO epoch(id,e) VALUES(1,0);").unwrap();
    c
}
#[derive(Debug, PartialEq)]
enum Class { Valid, Preserve, Quarantine, Escalate }
struct Entry { lease_epoch: u64, seq: u64, committed: bool }
fn classify(e: &Entry, current_epoch: u64, rev: &std::collections::HashMap<u64,u64>) -> Class {
    if e.lease_epoch == current_epoch { return Class::Valid; }
    match rev.get(&e.lease_epoch) {
        Some(&r) if e.seq > r => Class::Quarantine,
        Some(&r) if e.seq < r && e.committed => Class::Preserve,
        _ => Class::Escalate,
    }
}
fn fence_test() {
    let mut rev = std::collections::HashMap::new(); rev.insert(1u64, 10u64);
    let cur = 2u64;
    let cases = [
        ("legit_prior_history", Entry{lease_epoch:1,seq:5,committed:true}, Class::Preserve),
        ("provably_stale", Entry{lease_epoch:1,seq:15,committed:true}, Class::Quarantine),
        ("ambiguous", Entry{lease_epoch:1,seq:10,committed:true}, Class::Escalate),
        ("current_epoch", Entry{lease_epoch:2,seq:20,committed:true}, Class::Valid),
    ];
    let mut ok = true;
    for (name, e, want) in cases {
        let got = classify(&e, cur, &rev); let pass = got == want; ok &= pass;
        println!("fence_case {} got={:?} want={:?} {}", name, got, want, if pass {"PASS"} else {"FAIL"});
    }
    println!("FENCE_CLASSIFY {}", if ok {"PASS"} else {"FAIL"});
    println!("naive_leaseEpoch_lt_current_would_DISCARD_legit_history seq=5 -> WRONG");
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        Some("acquire-inc") => {
            let (lease, dbp, iters) = (&a[2], &a[3], a[4].parse::<u64>().unwrap());
            let c = db(dbp);
            for _ in 0..iters {
                let fd = open_lease(lease); assert!(ofd_lock(fd, true));
                c.execute_batch("BEGIN IMMEDIATE").unwrap();
                c.execute("UPDATE epoch SET e=e+1 WHERE id=1", []).unwrap();
                c.execute("UPDATE counter SET n=n+1 WHERE id=1", []).unwrap();
                c.execute_batch("COMMIT").unwrap();
                unsafe { libc::close(fd) };
            }
        }
        Some("kill-holder") => { let fd = open_lease(&a[2]); assert!(ofd_lock(fd, true));
            println!("KILL_AT {}", now_ns()); std::io::Write::flush(&mut std::io::stdout()).ok();
            unsafe { libc::kill(libc::getpid(), libc::SIGKILL) }; }
        Some("acquire-wait") => { let fd = open_lease(&a[2]); assert!(ofd_lock(fd, true)); println!("GRANT_AT {}", now_ns()); }
        Some("try") => { let fd = open_lease(&a[2]); println!("{}", if ofd_lock(fd, false) {"ACQUIRED"} else {"BLOCKED"}); }
        Some("acquire-exec") => { let lease = &a[2]; let fd = open_lease(lease); assert!(ofd_lock(fd, true)); set_cloexec(fd);
            let exe = std::env::current_exe().unwrap();
            let e = std::ffi::CString::new(exe.to_str().unwrap()).unwrap();
            let a1 = std::ffi::CString::new("try").unwrap();
            let a2 = std::ffi::CString::new(lease.as_str()).unwrap();
            let argv = [e.as_ptr(), a1.as_ptr(), a2.as_ptr(), std::ptr::null()];
            unsafe { libc::execv(e.as_ptr(), argv.as_ptr()); } }
        Some("acquire-dup") => { let lease = &a[2]; let fd1 = open_lease(lease); assert!(ofd_lock(fd1, true));
            let fd2 = unsafe { libc::dup(fd1) }; unsafe { libc::close(fd1) };
            println!("DUP_HOLDING"); std::io::Write::flush(&mut std::io::stdout()).ok();
            std::thread::sleep(std::time::Duration::from_millis(300));
            unsafe { libc::close(fd2) }; println!("DUP_RELEASED"); }
        Some("counter") => { let c = db(&a[2]);
            let n: i64 = c.query_row("SELECT n FROM counter WHERE id=1", [], |r| r.get(0)).unwrap();
            let e: i64 = c.query_row("SELECT e FROM epoch WHERE id=1", [], |r| r.get(0)).unwrap();
            println!("counter={} epoch={}", n, e); }
        Some("fence") => fence_test(),
        _ => { eprintln!("modes: acquire-inc|kill-holder|acquire-wait|try|acquire-exec|acquire-dup|counter|fence"); std::process::exit(2); }
    }
}
