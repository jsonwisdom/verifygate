# Gate 3 v0.5 — 55-fixture differential runner
Status: PRELIMINARY / THREE_LIBRARY_VERIFICATION=INCOMPLETE / HOLD.

This branch contains a **harness**, not the user's claimed v0.5 corpus. The exact 55-fixture file was not found in the connected Drive searches or current verification repository. No expected outputs, provenance, archive digest or pinned independent implementations may be invented.

The runner requires a local JSON object with `cases` (exactly 55 unique cases), each: `id`, `hex` (exact raw input bytes), `expect` ('accept' or 'reject'), and `canonical_hex` for accepted cases. It requires `VEC-CANON-0001` and a separately supplied SHA-256 matching the exact corpus bytes. Do not silently reinterpret a ZIP's digest as a contained manifest digest.

It accepts **three separate executable adapter commands**, one each for Python, JavaScript and Go. Each must accept raw bytes on stdin and emit canonical bytes on stdout with status 0, or reject nonzero with empty stdout. Output for accepted cases is compared byte-for-byte with supplied expected canonical_hex. The runner records every exit, output and stderr hash (or timeout/inconclusive), writes a deterministic matrix receipt, and returns nonzero unless each implementation matches all 55 expectations.

**This is not third-party library identity verification.** Adapter library names/versions, package digests, transitive dependency provenance, independent JCS conformance and genuine source-derived expected outputs must be checked separately. A 55/55 output match does not certify full RFC 8785.

Example (run only when authentic corpus and pinned adapter commands exist):

```bash
python scripts/run_gate3_v05.py \
  --corpus local/gate3_v05_manifest.json \
  --corpus-sha256 YOUR_VERIFIED_64_HEX_SHA256 \
  --python 'python pinned_python_adapter.py' \
  --javascript 'node pinned_js_adapter.js' \
  --go './pinned_go_adapter' \
  --receipt local/gate3_v05_receipt.json
```

No live provider, Coinbase order endpoint, YubiKey, wallet, RPC, transaction or signing path is touched.

GAP-003 envelope enforcement remains SPECIFIED_NOT_DEPLOYED, frozen Drive execution contract unchanged, price-parameter ambiguity unresolved, REAL_TRADING=DISABLED, PRODUCTION_AUTHORITY=ZERO.
