#!/usr/bin/env python3
# PT-02 disposable harness (NON-PRODUCTION): journal recovery with a truncated
# final write, full truncation-offset sweep, mid-file corruption, and second-run
# idempotency. Synthetic inputs; no secrets. Outside the product build graph.
import hashlib, json, sys

def digest(rec):
    m = f"{rec['seq']}|{rec['txid']}|{rec['entryType']}|{rec['payloadDigest']}|{rec.get('prevEntryDigest','')}"
    return hashlib.sha256(m.encode()).hexdigest()

def build_journal(n):
    lines, prev = [], ""
    for seq in range(n):
        rec = {"schemaVersion": 1, "seq": seq, "txid": f"tx{seq:05d}", "entryType": "intent",
               "payloadDigest": hashlib.sha256(f"p{seq}".encode()).hexdigest(), "prevEntryDigest": prev}
        rec["entryDigest"] = digest(rec)
        prev = rec["entryDigest"]
        lines.append(json.dumps(rec))
    return lines

# Recovery: read complete digest-valid records; a torn/undecodable FINAL line is
# isolated; a digest break on a NON-final line stops with evidence (fail-closed).
def recover(blob):
    lines = blob.split("\n")
    recovered, isolated_tail, halted, halt_reason = 0, 0, False, None
    n = len(lines)
    for i, ln in enumerate(lines):
        if ln == "":
            continue
        is_last_nonempty = all(x == "" for x in lines[i + 1:])
        try:
            rec = json.loads(ln)
        except json.JSONDecodeError:
            if is_last_nonempty:
                isolated_tail += 1; break
            halted = True; halt_reason = f"undecodable mid-file line {i}"; break
        if rec.get("entryDigest") != digest(rec):
            if is_last_nonempty:
                isolated_tail += 1; break
            halted = True; halt_reason = f"digest mismatch mid-file line {i}"; break
        recovered += 1
    state = "halted-for-operator" if halted else "converged"
    return {"recovered": recovered, "isolated_tail": isolated_tail, "halted": halted,
            "halt_reason": halt_reason, "terminal_state": state}

def main():
    n = 1000
    lines = build_journal(n)
    complete = "\n".join(lines[:-1]) + "\n"       # first n-1 lines intact
    last = lines[-1]
    results = {"n": n, "sweep": [], "mid_file": None, "idempotent": None}
    # full truncation sweep over the final line
    for off in range(0, len(last)):   # 0 bytes .. full-record-minus-one (all truncated)
        blob = complete + last[:off]
        r = recover(blob)
        r2 = recover(blob)                         # second run (idempotency)
        # Core invariant: earlier records always readable (recovered==n-1), converges,
        # idempotent. isolated_tail is 1 when the interrupted append left partial bytes
        # and 0 at offset 0 (it left nothing to isolate) — both are correct recoveries.
        ok = (r["recovered"] == n - 1 and r["terminal_state"] == "converged" and r == r2
              and r["isolated_tail"] in (0, 1))
        results["sweep"].append({"offset": off, **r, "idempotent": r == r2, "ok": ok})
    # mid-file corruption: flip a char in line 500's entryDigest
    corrupt = list(lines)
    rec = json.loads(corrupt[500]); ed = list(rec["entryDigest"])
    ed[0] = "0" if ed[0] != "0" else "1"; rec["entryDigest"] = "".join(ed)
    corrupt[500] = json.dumps(rec)
    mid = recover("\n".join(corrupt) + "\n")
    results["mid_file"] = mid
    # summary
    sweep_ok = all(s["ok"] for s in results["sweep"])
    offsets = len(results["sweep"])
    idem_ok = all(s["idempotent"] for s in results["sweep"])
    midfile_ok = mid["halted"] and mid["recovered"] == 500 and "digest mismatch" in (mid["halt_reason"] or "")
    if len(sys.argv) > 1:   # optional: dump full per-offset matrix to CSV
        with open(sys.argv[1], "w") as f:
            f.write("offset,recovered,isolated_tail,terminal_state,idempotent,ok\n")
            for s in results["sweep"]:
                f.write(f"{s['offset']},{s['recovered']},{s['isolated_tail']},{s['terminal_state']},{s['idempotent']},{s['ok']}\n")
    min_rec = min(s["recovered"] for s in results["sweep"])
    max_rec = max(s["recovered"] for s in results["sweep"])
    tails = sorted({s["isolated_tail"] for s in results["sweep"]})
    print(json.dumps({
        "offsets_tested": offsets,
        "sweep_all_ok": sweep_ok,
        "recovered_min": min_rec, "recovered_max": max_rec, "expected_recovered": n - 1,
        "isolated_tail_values": tails,
        "idempotent_all": idem_ok,
        "mid_file_detected_failclosed": midfile_ok,
        "mid_file": mid,
        "overall_pass": sweep_ok and idem_ok and midfile_ok,
    }, indent=2))

if __name__ == "__main__":
    main()
