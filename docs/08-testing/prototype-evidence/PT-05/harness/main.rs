// PT-05 disposable harness (NON-PRODUCTION): Rust distribution — SQLite (bundled),
// Unix socket + peer-credential auth, journaled mutation, recovery after kill.
// Synthetic inputs only; no secrets. Not part of the product build/release graph.
use rusqlite::Connection;
use std::io::{BufRead, BufReader, Write};
use std::os::unix::fs::PermissionsExt;
use std::os::unix::io::AsRawFd;
use std::os::unix::net::{UnixListener, UnixStream};

fn open_db(path: &str) -> Connection {
    let c = Connection::open(path).unwrap();
    c.pragma_update(None, "journal_mode", &"WAL").unwrap();
    c.pragma_update(None, "synchronous", &"FULL").unwrap(); // governance-grade
    c.pragma_update(None, "busy_timeout", 5000).unwrap();
    c
}
fn migrate(c: &Connection) {
    c.execute_batch(
        "CREATE TABLE IF NOT EXISTS schema_meta(k TEXT PRIMARY KEY, v INTEGER);
         INSERT OR IGNORE INTO schema_meta(k, v) VALUES('version', 1);
         CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, val TEXT);
         CREATE TABLE IF NOT EXISTS journal(seq INTEGER PRIMARY KEY AUTOINCREMENT, txid TEXT, state TEXT);",
    ).unwrap();
}
fn recover(c: &Connection) -> usize {
    c.execute(
        "UPDATE journal SET state='rolled_back' WHERE state='staged'
           AND txid NOT IN (SELECT txid FROM journal WHERE state='committed')", [],
    ).unwrap()
}
fn peer_uid(s: &UnixStream) -> u32 {
    unsafe {
        let mut cred: libc::ucred = std::mem::zeroed();
        let mut len = std::mem::size_of::<libc::ucred>() as libc::socklen_t;
        let r = libc::getsockopt(s.as_raw_fd(), libc::SOL_SOCKET, libc::SO_PEERCRED,
            &mut cred as *mut _ as *mut libc::c_void, &mut len);
        if r != 0 { return u32::MAX; }
        cred.uid
    }
}
fn stage_intent(c: &Connection, txid: &str) {
    c.execute("INSERT INTO journal(txid, state) VALUES(?1, 'staged')", [txid]).unwrap();
}
fn full_mutate(c: &Connection, key: &str, val: &str) {
    stage_intent(c, key);
    c.execute_batch("BEGIN IMMEDIATE").unwrap();
    c.execute("INSERT OR REPLACE INTO kv(key, val) VALUES(?1, ?2)", [key, val]).unwrap();
    c.execute("INSERT INTO journal(txid, state) VALUES(?1, 'committed')", [key]).unwrap();
    c.execute_batch("COMMIT").unwrap();
}
fn kill_self() -> ! { unsafe { libc::kill(libc::getpid(), libc::SIGKILL) }; std::process::exit(137); }

fn serve(db: &str, sock: &str, owner_uid: u32) {
    let c = open_db(db);
    migrate(&c);
    let rec = recover(&c);
    let _ = std::fs::remove_file(sock);
    let l = UnixListener::bind(sock).unwrap();
    std::fs::set_permissions(sock, std::fs::Permissions::from_mode(0o600)).unwrap();
    println!("READY recovered={}", rec);
    std::io::stdout().flush().ok();
    for conn in l.incoming() {
        let mut s = conn.unwrap();
        let uid = peer_uid(&s);
        if uid != owner_uid { writeln!(s, "DENIED peer_uid={} owner_uid={}", uid, owner_uid).ok(); continue; }
        let mut line = String::new();
        BufReader::new(s.try_clone().unwrap()).read_line(&mut line).ok();
        let p: Vec<&str> = line.trim().split_whitespace().collect();
        match p.as_slice() {
            ["mutate", k, v] => { full_mutate(&c, k, v); writeln!(s, "OK").ok(); }
            ["killbefore", k, v] => {
                stage_intent(&c, k);
                c.execute_batch("BEGIN IMMEDIATE").unwrap();
                c.execute("INSERT OR REPLACE INTO kv(key,val) VALUES(?1,?2)", [k, v]).unwrap();
                writeln!(s, "DYING").ok(); s.flush().ok(); kill_self();
            }
            ["killafter", k, v] => { full_mutate(&c, k, v); s.flush().ok(); kill_self(); }
            ["get", k] => {
                let r: Result<String, _> = c.query_row("SELECT val FROM kv WHERE key=?1", [k], |r| r.get(0));
                writeln!(s, "{}", r.unwrap_or_else(|_| "<absent>".into())).ok();
            }
            ["jstate", k] => {
                let r: Result<String, _> = c.query_row(
                    "SELECT state FROM journal WHERE txid=?1 ORDER BY seq DESC LIMIT 1", [k], |r| r.get(0));
                writeln!(s, "{}", r.unwrap_or_else(|_| "<none>".into())).ok();
            }
            ["version"] => {
                let v: i64 = c.query_row("SELECT v FROM schema_meta WHERE k='version'", [], |r| r.get(0)).unwrap();
                writeln!(s, "{}", v).ok();
            }
            _ => { writeln!(s, "ERR").ok(); }
        }
    }
}
fn client(sock: &str, args: &[String]) {
    let mut s = UnixStream::connect(sock).unwrap();
    writeln!(s, "{}", args.join(" ")).unwrap(); s.flush().unwrap();
    let mut line = String::new();
    BufReader::new(s).read_line(&mut line).ok();
    print!("{}", line);
}
fn main() {
    let a: Vec<String> = std::env::args().collect();
    match a.get(1).map(|s| s.as_str()) {
        Some("serve") => serve(&a[2], &a[3], a[4].parse().unwrap()),
        Some("client") => client(&a[2], &a[3..]),
        _ => { eprintln!("usage: pt05_core serve <db> <sock> <owner_uid> | client <sock> <cmd..>"); std::process::exit(2); }
    }
}
