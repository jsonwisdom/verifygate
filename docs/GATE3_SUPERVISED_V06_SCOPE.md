# Gate 3 v0.6 — Supervisor + expectation binding laboratory

**Stacked draft on PR #7**. Only synthetic controls are present. This is not the original Gate 3 v0.5 55-vector corpus.

## Supervised classification
- ACCEPT: exit 0, no stderr, no signal, no timeout. The separate matrix check compares stdout to expected canonical bytes.
- REJECT: exit code 20 or 21, empty stdout, exact `jcs-rejection-v1` JSON record with code and uppercase reason, and no known crash/sanitizer markers.
- CRASH_UNKNOWN: signal/negative return code, timeout, supervisor error, unexpected exit or stderr, sanitizer, traceback, OOM or abort, or malformed rejection.

This is a **prototype classifier**, not an OS-level independent supervisor. It does not currently capture core-dump metadata, kernel OOM-killer telemetry, platform-specific sanitizer streams or complete resource accounting. Accordingly any classification uncertainty and the production execution gate stay HOLD.

## Expectation separation
The verifier reads separate raw manifest, canonical expected bytes and provenance JSON, checking their hashes and a bound custodian HMAC. The test uses a synthetic local HMAC key only. This **cannot establish an independent custodian signature**: prior out-of-band authentication, trusted key custody and verified transcripts are still missing. The API allows command selection and the adapter execution remains offline and read-only. Source provenance and adapter identity must be independently verified before accepting a 55-vector comparison as meaningful.

## Controls
Synthetic tests cover SIGSEGV, SIGABRT, uncaught exception, simulated MemoryError, timeout, fake rejection, valid structured rejection, sanitizer text, tampered expected bytes, changed manifest and altered HMAC. CI PASS means only these checks passed, not full RFC 8785 conformance.

## Invariants
`PASS_SCOPED_OUTPUT_MATCH_ONLY` is the **maximum** result for 165 output comparisons. Library independence remains unverified. `GAP-003=OPEN`, Coinbase frozen execution contract unchanged, price ambiguity unresolved, trading disabled, production authority ZERO. This work does not merge PR #7 or authorize further execution.
