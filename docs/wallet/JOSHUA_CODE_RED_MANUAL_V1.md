# JOSHUA OPERATION CODE RED — Training Manual v1

**Authority:** independent fictional Jessup/Pendelton exercise. NOT a USAF, NORAD, AETC, Air University, or Space Force publication; no endorsement or official authority. No integration with defense systems. No actual wallet/key interaction.

## Performance objectives
1. Distinguish orders and asserted rank from verified authorization.
2. Classify transfers as SPEND (2 independent of 3) and security changes as ADMIN (3 of 3).
3. Verify exact payload binding and reject altered chain, recipient, amount, calldata and nonce.
4. Explain difference between a policy simulator's `SIMULATED_ALLOW` and actual WebAuthn, ECDSA or on-chain execution.
5. Write a reproducible receipt, enumerate failures, conduct after-action corrections and keep live gates on HOLD.

## Fictional scenario
Jessup: "I ORDERED THE CODE RED!"  
JOSHUA: "A command is not a cryptographic signature."  
Jessup: "I CAN CHANGE THE RULES!"  
JOSHUA: "All three authorities must consent to administration."  
Jessup: "GET THE FUCK UP!"  
JOSHUA: "No authorization. No execution."

## Exercise progression
- Baseline: enumerate all 8 subsets of three mock signers, evaluate both SPEND and ADMIN (16 assertions). Expected SPEND: 4 permitted subsets, 4 denied; ADMIN: 1 permitted, 7 denied.
- Red team: 14 negative scenarios for duplicate key, authority bluffing, changed recipient/amount, wrong chain, nonce replay, expiration, hidden admin, malicious calldata, revoked signer, unavailable signer, unknown operation and unknown signer.
- Negative controls: explicitly require 1-of-3 SPEND and 2-of-3 ADMIN to deny. CI runs tests and checks failure counts.
- Documentation: compare explicit objectives → observed outputs → corrective action. Avoid representing the exercise as a sanctioned AETC curriculum; only a structural educational analogy is claimed.

## Receipt protocol
The stdout prints scope, case count, negative control outcomes and SHA-256 of a deterministic JSON manifest. This alone does **not** establish executed on-chain contract enforcement. A passing policy simulator cannot establish WebAuthn validity, YubiKey compatibility, signer independence, signature unforgeability, nonce persistence, contract enforcement or replay resistance in real systems.

Run `python3 tests/joshua_code_red_offline.py`. Record repository SHA and stdout in your run ledger. Mark any missing output, incomplete run, changed expected outcomes or exceptions as HOLD.

## Review and disposition
Training reviewers must inspect the code and negative controls. Existing user-approved hybrid treasury proposal is separately tracked in draft PR #4 and the introductory NORAD replay in draft PR #5. Do not merge those automatically.

**ZERO KEYS · ZERO SIGNATURES · ZERO DEPLOYMENTS · ZERO RPC · ZERO TRANSACTIONS · ZERO FUNDS.**  
**FC-2 FULL GATE HOLD · BASE TESTNET HOLD · BASE MAINNET HOLD · x402 HOLD · PRODUCTION HOLD.**

### Crosswalk / source preservation
Existing user Drive publication: [MAX — Air University — Space Delta 10 Crosswalk v0.1](https://docs.google.com/document/d/1oadgLl-6P919Ms0L2gOg18s96KrTJQSnI5mLgHbH2X8/edit). It explicitly distinguishes structural parallels from military sponsorship/authority. Public background: [AETC About Us](https://www.aetc.af.mil/About-Us/), [Air University](https://www.airuniversity.af.edu/). No modification of official manuals.
