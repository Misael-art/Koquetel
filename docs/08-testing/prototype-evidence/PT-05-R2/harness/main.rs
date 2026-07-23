// PT-05 disposable harness (NON-PRODUCTION): bundled SQLite, Unix socket
// SO_PEERCRED authorization, migration idempotency, and kill recovery.
use rusqlite::Connection;
use std::io::{BufRead, BufReader, Write};
use std::os::unix::fs::PermissionsExt;
use std::os::unix::io::AsRawFd;
use std::os::unix::net::{UnixListener, UnixStream};

fn open_db(path: &str) -> Connection {
    let connection = Connection::open(path).unwrap();
    connection.pragma_update(None, "journal_mode", "WAL").unwrap();
    connection.pragma_update(None, "synchronous", "FULL").unwrap();
    connection.pragma_update(None, "busy_timeout", 5000).unwrap();
    connection
}

fn migrate(connection: &Connection) {
    connection.execute_batch(
        "CREATE TABLE IF NOT EXISTS schema_meta(k TEXT PRIMARY KEY, v INTEGER);
         INSERT OR IGNORE INTO schema_meta(k,v) VALUES('version',1);
         CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, val TEXT);
         CREATE TABLE IF NOT EXISTS journal(
           seq INTEGER PRIMARY KEY AUTOINCREMENT, txid TEXT, state TEXT
         );",
    ).unwrap();
}

fn recover(connection: &Connection) -> usize {
    connection.execute(
        "UPDATE journal SET state='rolled_back' WHERE state='staged'
         AND txid NOT IN (SELECT txid FROM journal WHERE state='committed')", [],
    ).unwrap()
}

fn peer_uid(stream: &UnixStream) -> u32 {
    unsafe {
        let mut credential: libc::ucred = std::mem::zeroed();
        let mut length = std::mem::size_of::<libc::ucred>() as libc::socklen_t;
        let result = libc::getsockopt(
            stream.as_raw_fd(), libc::SOL_SOCKET, libc::SO_PEERCRED,
            &mut credential as *mut _ as *mut libc::c_void, &mut length,
        );
        if result == 0 { credential.uid } else { u32::MAX }
    }
}

fn stage(connection: &Connection, txid: &str) {
    connection.execute("INSERT INTO journal(txid,state) VALUES(?1,'staged')", [txid]).unwrap();
}

fn commit(connection: &Connection, key: &str, value: &str) {
    stage(connection, key);
    connection.execute_batch("BEGIN IMMEDIATE").unwrap();
    connection.execute("INSERT OR REPLACE INTO kv(key,val) VALUES(?1,?2)", [key, value]).unwrap();
    connection.execute("INSERT INTO journal(txid,state) VALUES(?1,'committed')", [key]).unwrap();
    connection.execute_batch("COMMIT").unwrap();
}

fn kill_self() -> ! {
    unsafe { libc::kill(libc::getpid(), libc::SIGKILL) };
    std::process::exit(137)
}

fn serve(db: &str, socket: &str, owner_uid: u32, mode: u32) {
    let connection = open_db(db);
    migrate(&connection);
    let recovered = recover(&connection);
    let _ = std::fs::remove_file(socket);
    let listener = UnixListener::bind(socket).unwrap();
    std::fs::set_permissions(socket, std::fs::Permissions::from_mode(mode)).unwrap();
    println!("READY pid={} owner_uid={} recovered={} mode={:o}",
             std::process::id(), owner_uid, recovered, mode);
    std::io::stdout().flush().unwrap();
    for incoming in listener.incoming() {
        let mut stream = incoming.unwrap();
        let uid = peer_uid(&stream);
        if uid != owner_uid {
            writeln!(stream, "DENIED peer_uid={} owner_uid={}", uid, owner_uid).ok();
            continue;
        }
        let mut line = String::new();
        BufReader::new(stream.try_clone().unwrap()).read_line(&mut line).ok();
        let parts: Vec<&str> = line.split_whitespace().collect();
        match parts.as_slice() {
            ["mutate", key, value] => {
                commit(&connection, key, value);
                writeln!(stream, "OK peer_uid={}", uid).ok();
            }
            ["killbefore", key, value] => {
                stage(&connection, key);
                connection.execute_batch("BEGIN IMMEDIATE").unwrap();
                connection.execute("INSERT OR REPLACE INTO kv(key,val) VALUES(?1,?2)",
                                   [key, value]).unwrap();
                writeln!(stream, "DYING peer_uid={}", uid).ok();
                stream.flush().ok();
                kill_self();
            }
            ["killafter", key, value] => {
                commit(&connection, key, value);
                writeln!(stream, "DYING peer_uid={}", uid).ok();
                stream.flush().ok();
                kill_self();
            }
            ["get", key] => {
                let value: Result<String, _> = connection.query_row(
                    "SELECT val FROM kv WHERE key=?1", [key], |row| row.get(0));
                writeln!(stream, "{}", value.unwrap_or_else(|_| "<absent>".into())).ok();
            }
            ["jstate", key] => {
                let state: Result<String, _> = connection.query_row(
                    "SELECT state FROM journal WHERE txid=?1 ORDER BY seq DESC LIMIT 1",
                    [key], |row| row.get(0));
                writeln!(stream, "{}", state.unwrap_or_else(|_| "<none>".into())).ok();
            }
            ["version"] => {
                let version: i64 = connection.query_row(
                    "SELECT v FROM schema_meta WHERE k='version'", [], |row| row.get(0)).unwrap();
                writeln!(stream, "{}", version).ok();
            }
            _ => { writeln!(stream, "ERR").ok(); }
        }
    }
}

fn client(socket: &str, command: &[String]) {
    let mut stream = UnixStream::connect(socket).unwrap();
    writeln!(stream, "{}", command.join(" ")).unwrap();
    stream.flush().unwrap();
    let mut line = String::new();
    BufReader::new(stream).read_line(&mut line).ok();
    print!("{}", line);
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("serve") => serve(
            &args[2], &args[3], args[4].parse().unwrap(),
            u32::from_str_radix(&args[5], 8).unwrap(),
        ),
        Some("client") => client(&args[2], &args[3..]),
        _ => {
            eprintln!("usage: pt05_core_r2 serve DB SOCKET OWNER_UID MODE | client SOCKET COMMAND...");
            std::process::exit(2);
        }
    }
}
