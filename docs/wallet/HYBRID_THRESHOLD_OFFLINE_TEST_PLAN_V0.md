# Hybrid Threshold Wallet — Offline Security Test Plan (Not Executed)

**Contract under test:** NONE selected. **Gate:** TEST_DESIGN_ONLY / HOLD.

## A. Precondition and traceability
- Define one immutable policy table: SPEND=2 distinct of 3; ADMIN=3 distinct of 3; unknown class=deny.
- Record source commit, compiler, dependencies/SBOM, chain configuration, validator/account code hashes, simulation engine version, fixture and test receipt hashes.
- Establish **three distinct public credentials** and prove enrollment uniqueness without putting private keys on GitHub. No real user secrets.
- Confirm the account has no alternate 1-of-N entrypoint, bypass-capable module, unrestricted owner path, upgrade entry or fallback.

## B. Offline deterministic test matrix

| ID | Case | Expected |
|---|---|---|
| AUTH-01..03 | Each signer alone, SPEND | REJECT |
| AUTH-04..06 | A+B, A+C, B+C on same SPEND digest | ACCEPT |
| AUTH-07 | A+B+C, SPEND | ACCEPT (policy does not forbid extra valid approvals) |
| AUTH-08..10 | Each 2-of-3 pair, ADMIN | REJECT |
| AUTH-11 | A+B+C, ADMIN | ACCEPT |
| AUTH-12 | Same credential counted twice | REJECT |
| AUTH-13 | Single key enrolled under two names | REJECT |
| AUTH-14 | Unsupported signer / revoked credential | REJECT |
| BIND-01..09 | Mutate recipient, asset, amount, chain, account, nonce, deadline, calldata, operation class separately | REJECT |
| BIND-10 | Reorder batch after signatures | REJECT |
| REPLAY-01 | Replay successful operation with consumed nonce | REJECT |
| REPLAY-02 | Replay on another chain/account | REJECT |
| WEBAUTHN-01..06 | Bad challenge, RP hash, origin, type, UV requirement, P-256 signature | REJECT |
| ECDSA-01..03 | Wrong domain, malleable signature, wrong recovered owner | REJECT |
| ESC-01..06 | Owner update, validator/module install, upgrade, recovery, admin-through-spend wrapper, fallback route with less than 3 approvals | REJECT |
| FAILURE-01..04 | Signer offline, timeout, corrupted payload, malformed ABI | HOLD/REJECT |
| AMOUNT-01 | Zero-value call with privileged calldata | ADMIN or REJECT, never auto-SPEND |
| AMOUNT-02 | Token approval with zero native value | SPEND requiring 2-of-3; stricter policy possible |
| TESTNET-01 | Fresh isolated Base Sepolia account zero-value test | DEFERRED: requires separate approval |

## C. Test methods
1. Pure offline deterministic unit tests for quorum counting, operation classification, and signature/digest verification.
2. Property-based fuzzing of signature order/duplicates, calldata, Unicode/encoding, nonces, expiration and batch order.
3. Differential signature-verifier tests against independent reference implementation(s); compare exact acceptance decisions and bytes.
4. Stateful simulation/invariant testing against representative account abstraction execution paths (validation, execution, fallback, upgrade, module paths).
5. Failure injection for bundler, paymaster, RPC, browser, authenticator and network; no failure may turn HOLD into ACCEPT.
6. Independent security review and audit of the selected contract/validator before any testnet deployment.

## D. Evidence acceptance gates
- Each test has fixed ID, human-reviewed expected result, actual output, run environment, code/fixture digests, failed IDs and mutation evidence.
- All required tests pass, no unknown outcomes or unbounded bypass paths.
- A separate negative-control suite must fail if the threshold is weakened to 1-of-3 or ADMIN to 2-of-3; prevents ornamental tests.
- Signed approval from human release authority is distinct from automated test success.
- For testnet: fresh explicit approval, zero-value only, independent read-back receipt, no preexisting wallet linkage by default.
- Mainnet, x402 settlement and any custody integration require their own release reviews; passing this plan does not authorize them.

## E. Current disposition

**NOT RUN — no smart contract or signer enrollments exist under this PR.**  
**No deployment · no transactions · no funds · no live signing · no merge authorization.**
