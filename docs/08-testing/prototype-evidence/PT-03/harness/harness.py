#!/usr/bin/env python3
# PT-03 disposable harness (NON-PRODUCTION): the arms ai-memory's own tests do not
# cover, using ai-memory's exact observed pragmas (EA-01 lib.rs:91-93): WAL +
# synchronous=NORMAL + busy_timeout=5000. Cross-process contention, byte-corruption
# fail-closed, export/import round-trip digest. Synthetic inputs; no secrets.
import hashlib, os, sqlite3, sys

def connect(db):
    c = sqlite3.connect(db, timeout=5.0, isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=NORMAL"); c.execute("PRAGMA busy_timeout=5000")
    return c

def setup(db):
    c = connect(db); c.execute("CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, scope TEXT, digest TEXT)"); c.close()

def writer(db, prefix, n):
    c = connect(db); retries = 0
    for i in range(int(n)):
        rid = f"{prefix}-{i}"; dig = hashlib.sha256(rid.encode()).hexdigest(); budget = 5
        while True:
            try:
                c.execute("BEGIN IMMEDIATE")
                c.execute("INSERT OR IGNORE INTO records(id,scope,digest) VALUES(?,?,?)", (rid, "project", dig))
                c.execute("COMMIT"); break
            except sqlite3.OperationalError as e:
                try: c.execute("ROLLBACK")
                except Exception: pass
                budget -= 1; retries += 1
                if budget == 0: print(f"UNHANDLED_LOCK {rid} {e}", file=sys.stderr); sys.exit(3)
    c.close(); print(f"writer {prefix} done retries={retries}")

def count(db):
    c = connect(db); rows = c.execute("SELECT id,digest FROM records").fetchall(); c.close()
    bad = sum(1 for rid, dig in rows if dig != hashlib.sha256(rid.encode()).hexdigest())
    print(f"count={len(rows)} torn_or_wrong_digest_rows={bad}")

def corrupt(db):
    c = connect(db); c.execute("CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, scope TEXT, digest TEXT)")
    for i in range(500): c.execute("INSERT OR IGNORE INTO records VALUES(?,?,?)", (f"x-{i}", "p", "d"))
    c.execute("PRAGMA wal_checkpoint(TRUNCATE)"); c.close()
    size = os.path.getsize(db)
    with open(db, "r+b") as f: f.seek(size // 2); f.write(b"\xff" * 8)
    detected = False
    try:
        c = connect(db); ic = c.execute("PRAGMA integrity_check").fetchone()[0]
        if ic != "ok": detected = True; print(f"integrity_check={ic[:70]!r}")
        try: c.execute("SELECT count(*) FROM records").fetchone()
        except sqlite3.DatabaseError as e: detected = True; print(f"read_raised={e}")
        c.close()
    except sqlite3.DatabaseError as e: detected = True; print(f"open_raised={e}")
    print("CORRUPTION_DETECTED" if detected else "CORRUPTION_SILENT_FAIL")

def dump_digest(db):
    c = connect(db); rows = c.execute("SELECT id,scope,digest FROM records ORDER BY id").fetchall(); c.close()
    return hashlib.sha256("\n".join(f"{r[0]}|{r[1]}|{r[2]}" for r in rows).encode()).hexdigest(), len(rows)

def export_import(src, dst):
    c = connect(src); rows = c.execute("SELECT id,scope,digest FROM records WHERE scope='project' ORDER BY id").fetchall(); c.close()
    if os.path.exists(dst): os.remove(dst)
    d = connect(dst); d.execute("CREATE TABLE records(id TEXT PRIMARY KEY, scope TEXT, digest TEXT)")
    for r in rows: d.execute("INSERT INTO records VALUES(?,?,?)", r)
    d.close()
    s1, n1 = dump_digest(src); s2, n2 = dump_digest(dst)
    print(f"src_rows={n1} src_digest={s1} dst_rows={n2} dst_digest={s2}")
    print("EXPORT_ROUNDTRIP_MATCH" if s1 == s2 else "EXPORT_ROUNDTRIP_MISMATCH")

def purge(db):
    c = connect(db)
    before = c.execute("SELECT count(*) FROM records WHERE scope='project'").fetchone()[0]
    c.execute("BEGIN IMMEDIATE"); c.execute("DELETE FROM records WHERE scope='project'"); c.execute("COMMIT")
    after = c.execute("SELECT count(*) FROM records WHERE scope='project'").fetchone()[0]
    c.close(); print(f"purge_before={before} purge_after_queryable={after}")

if __name__ == "__main__":
    m = sys.argv[1]
    {"setup": lambda: setup(sys.argv[2]), "writer": lambda: writer(sys.argv[2], sys.argv[3], sys.argv[4]),
     "count": lambda: count(sys.argv[2]), "corrupt": lambda: corrupt(sys.argv[2]),
     "export": lambda: export_import(sys.argv[2], sys.argv[3]), "purge": lambda: purge(sys.argv[2])}[m]()
