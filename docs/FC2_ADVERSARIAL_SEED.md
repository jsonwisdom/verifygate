# FC-2 adversarial byte-parser gate — SEED / HOLD

Status: **NOT VERIFIED**. This branch introduces a **Python-only policy prototype** and tests; it does not demonstrate Python/JavaScript/Go equivalence, does not rerun FC-1, and does not authorize release.

## Scope
- Decode raw UTF-8 bytes strictly; fail on invalid, overlong, truncated, or surrogate-encoded sequences.
- Reject duplicate JSON keys, NaN/Infinity, malformed/truncated JSON, trailing JSON documents and lone surrogate escapes.
- Bound request size and nesting depth before approval.
- Verify a valid surrogate pair and normal Unicode input remain accepted.
- Next: drive the **same fixed bytes** through the actual production Python, JavaScript and Go adapters; record exact exit/accept/output behavior, independent reference expectations and SHA-256 fixtures. No acceptance on parser disagreement.
- Next: add boundary/mutation cases and cross-runtime timeout/resource controls. Keep adversarial classes that exceed RFC 8785 / I-JSON scope separately labeled.
- Next: bind each receipt to source revision, runner versions, environment and reviewable evidence; sign only after human approval.

## Non-goals / release locks
- The test is **only an independent Python prototype self-test**. Green CI must show `FC2_SEED_ONLY_PASS` rather than `FC2_PASS`.
- No YubiKey private key, wallet signing, x402 settlement, mainnet, deployment or production access.
- PR #2 remains a separate FC-1 evidence review. Never merge this draft branch into it.
- **FC-2 HOLD · x402 LIVE HOLD · PRODUCTION HOLD** until subsequent, independently verified gates.
