// PT-01 disposable evidence harness (NON-PRODUCTION).
// It exercises Linux OFD locks and emits one CSV row per granted acquisition.
use std::io::Write;
use std::os::fd::RawFd;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

fn now_ns() -> u128 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_nanos()
}

fn open_lease(path: &str) -> RawFd {
    let c = std::ffi::CString::new(path).unwrap();
    let fd = unsafe { libc::open(c.as_ptr(), libc::O_RDWR | libc::O_CREAT, 0o600) };
    assert!(fd >= 0, "open lease failed");
    fd
}

fn lock(fd: RawFd) {
    let fl = libc::flock {
        l_type: libc::F_WRLCK as i16,
        l_whence: libc::SEEK_SET as i16,
        l_start: 0,
        l_len: 0,
        l_pid: 0,
    };
    assert_eq!(unsafe { libc::fcntl(fd, libc::F_OFD_SETLKW, &fl) }, 0);
}

fn owner_record(fd: RawFd, holder: &str, seq: u64, start: u128) {
    let line = format!("holder={holder} seq={seq} start_ns={start}\n");
    unsafe {
        assert_eq!(libc::ftruncate(fd, 0), 0);
        assert_eq!(libc::lseek(fd, 0, libc::SEEK_SET), 0);
        assert_eq!(libc::write(fd, line.as_ptr().cast(), line.len()), line.len() as isize);
        assert_eq!(libc::fsync(fd), 0);
    }
}

fn append_row(out: &mut std::fs::File, variant: &str, holder: &str, seq: u64,
              start: u128, end: u128, lease: &str) {
    writeln!(out, "{variant},{holder},{seq},{start},{end},{lease}").unwrap();
    out.flush().unwrap();
}

fn wait_child(pid: libc::pid_t) {
    let mut status = 0;
    assert_eq!(unsafe { libc::waitpid(pid, &mut status, 0) }, pid);
    assert!(libc::WIFEXITED(status));
    assert_eq!(libc::WEXITSTATUS(status), 0);
}

fn contend(variant: &str, lease: &str, holder: &str, iters: u64, log: &str) {
    let mut out = std::fs::OpenOptions::new().create(true).append(true).open(log).unwrap();
    for seq in 0..iters {
        let fd = open_lease(lease);
        lock(fd);
        match variant {
            "main" => {
                let start = now_ns();
                owner_record(fd, holder, seq, start);
                std::thread::sleep(Duration::from_micros(25));
                let end = now_ns();
                append_row(&mut out, variant, holder, seq, start, end, lease);
                unsafe { libc::close(fd) };
            }
            "fork-a" => {
                let child = unsafe { libc::fork() };
                assert!(child >= 0);
                if child == 0 {
                    unsafe {
                        libc::close(fd);
                        libc::_exit(0);
                    }
                }
                wait_child(child);
                let start = now_ns();
                owner_record(fd, holder, seq, start);
                std::thread::sleep(Duration::from_micros(25));
                let end = now_ns();
                append_row(&mut out, variant, holder, seq, start, end, lease);
                unsafe { libc::close(fd) };
            }
            "fork-b" => {
                let mut ready = [0; 2];
                let mut release = [0; 2];
                assert_eq!(unsafe { libc::pipe(ready.as_mut_ptr()) }, 0);
                assert_eq!(unsafe { libc::pipe(release.as_mut_ptr()) }, 0);
                let child = unsafe { libc::fork() };
                assert!(child >= 0);
                if child == 0 {
                    unsafe {
                        libc::close(ready[0]);
                        libc::close(release[1]);
                        let byte = [1u8; 1];
                        libc::write(ready[1], byte.as_ptr().cast(), 1);
                        let mut signal = [0u8; 1];
                        libc::read(release[0], signal.as_mut_ptr().cast(), 1);
                        libc::close(fd);
                        libc::_exit(0);
                    }
                }
                unsafe {
                    libc::close(ready[1]);
                    libc::close(release[0]);
                    let mut signal = [0u8; 1];
                    assert_eq!(libc::read(ready[0], signal.as_mut_ptr().cast(), 1), 1);
                    libc::close(fd); // parent reference closes first; child still holds the OFD
                }
                let start = now_ns();
                std::thread::sleep(Duration::from_micros(25));
                let end = now_ns();
                append_row(&mut out, variant, holder, seq, start, end, lease);
                unsafe {
                    let byte = [1u8; 1];
                    assert_eq!(libc::write(release[1], byte.as_ptr().cast(), 1), 1);
                    libc::close(ready[0]);
                    libc::close(release[1]);
                }
                wait_child(child);
            }
            _ => panic!("unknown variant"),
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 7 || args[1] != "contend" {
        eprintln!("usage: pt01_r2 contend main|fork-a|fork-b LEASE HOLDER ITERS LOG");
        std::process::exit(2);
    }
    contend(&args[2], &args[3], &args[4], args[5].parse().unwrap(), &args[6]);
}
