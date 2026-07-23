// PT-01 disposable harness (NON-PRODUCTION): exclusive cross-process mutual
// exclusion via OFD locks, with a fork/OFD lifecycle arm. Records acquire time
// AFTER the lock is granted (grant time, not request time). Synthetic; no secrets.
use std::io::Write;
use std::os::unix::io::RawFd;
use std::time::{SystemTime, UNIX_EPOCH};
fn now_ns() -> u128 { SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos() }
fn open_lease(path: &str) -> RawFd {
    let c = std::ffi::CString::new(path).unwrap();
    unsafe { libc::open(c.as_ptr(), libc::O_RDWR | libc::O_CREAT, 0o600) }
}
fn ofd_lock(fd: RawFd, wait: bool) -> bool {
    let fl = libc::flock { l_type: libc::F_WRLCK as i16, l_whence: libc::SEEK_SET as i16, l_start: 0, l_len: 0, l_pid: 0 };
    let cmd = if wait { libc::F_OFD_SETLKW } else { libc::F_OFD_SETLK };
    unsafe { libc::fcntl(fd, cmd, &fl) == 0 }
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        // acquire lease, timed critical section, log (holder, acquire_ns, release_ns) per acquisition
        Some("contend") => {
            let (lease, holder, iters, logf) = (&a[2], &a[3], a[4].parse::<u64>().unwrap(), &a[5]);
            let mut out = std::fs::OpenOptions::new().create(true).append(true).open(logf).unwrap();
            for _ in 0..iters {
                let fd = open_lease(lease);
                assert!(ofd_lock(fd, true), "blocking OFD lock must be granted");
                let acq = now_ns();                 // grant time (after lock)
                let mut x = 0u64; for i in 0..2000 { x = x.wrapping_add(i); } // nonzero critical section
                std::hint::black_box(x);
                let rel = now_ns();
                writeln!(out, "{} {} {}", holder, acq, rel).unwrap();
                unsafe { libc::close(fd) };          // release OFD
            }
        }
        // fork lifecycle: parent holds, child inherits+closes its ref, a contender must be BLOCKED
        Some("fork-arm") => {
            let (lease, iters) = (&a[2], a[3].parse::<u64>().unwrap());
            let mut ok = 0u64; let mut viol = 0u64;
            for _ in 0..iters {
                let fd = open_lease(lease);
                assert!(ofd_lock(fd, true));
                let child = unsafe { libc::fork() };
                if child == 0 { unsafe { libc::close(fd); libc::_exit(0); } }
                unsafe { let mut st = 0; libc::waitpid(child, &mut st, 0); }
                // parent still holds (its reference kept the OFD alive despite child close)
                let c2 = unsafe { libc::fork() };
                if c2 == 0 {
                    let f2 = open_lease(lease);
                    let got = ofd_lock(f2, false);   // non-blocking try
                    unsafe { libc::_exit(if got { 2 } else { 0 }); } // 2 = VIOLATION (acquired while held)
                }
                let mut st = 0; unsafe { libc::waitpid(c2, &mut st, 0); }
                let code = (st >> 8) & 0xff;
                if code == 0 { ok += 1; } else { viol += 1; }
                unsafe { libc::close(fd) };
            }
            println!("fork_arm iters={} ok={} violations={}", iters, ok, viol);
        }
        Some("try") => { let fd = open_lease(&a[2]); println!("{}", if ofd_lock(fd, false) {"ACQUIRED"} else {"BLOCKED"}); }
        _ => { eprintln!("modes: contend|fork-arm|try"); std::process::exit(2); }
    }
}
