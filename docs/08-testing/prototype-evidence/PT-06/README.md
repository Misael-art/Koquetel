# PT-06 evidence bundle (verification rerun after RF-03)

Verdict: **PASS**. Generated 2026-07-23T00:31:56Z. Follows PROTOTYPE-EVIDENCE-POLICY.md.
Honest note: the first counter-equality rerun exposed a harness startup race
(8750/10000); the harness was pre-init-hardened and the corrected rerun reached
10000/10000 — see manifest.json limitations. Binary not committed (sha in
metrics.json). Synthetic inputs; no secrets. Harness NON-PRODUCTION/DISPOSABLE.
