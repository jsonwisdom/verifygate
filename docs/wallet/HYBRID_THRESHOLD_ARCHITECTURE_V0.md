# JSONWisdom — Base Hybrid Threshold Treasury Architecture (Design Only)

**Status:** DESIGN_PROPOSAL / NOT IMPLEMENTED / HOLD  
**Policy selected by owner:** 2-of-3 spending; 3-of-3 security administration.  
**Scope:** A single prospective Base smart-contract treasury with three **independent cryptographic authorities**. No live address, contract, custodian, credential, or deployment is established by this document.

## 1. Authorities and independence

| Credential | Role | Independence requirement |
|---|---|---|
| A: iPhone platform passkey | WebAuthn signer, locally unlocked with Face ID or device user verification | Unique P-256 credential, RP ID and public key checked; do not count Face ID as a second signature |
| B: YubiKey WebAuthn credential | Roaming hardware-authenticator signer | Distinct credential and authenticator; **existing YubiKey SSH key is NOT evidence of WebAuthn signing support** |
| C: independent Ethereum account | secp256k1/ECDSA signer | Independently controlled hardware-backed or isolated key, not a duplicate key/seed of A or B |

One ENS label or multiple labels are *names*, not distinct signers. Owner count alone is insufficient: a Coinbase Smart Wallet with multiple independent owners can allow any single owner to execute. Only a validator that enforces unique-signer quorums for every execution path satisfies this proposal.

## 2. Authorization classes

**SPEND (2-of-3):** native/token transfers, approved swaps, interactions that change asset balances or approvals. Require two distinct authorities on the exact same immutable operation digest. At least two actual signatures, **never** one signature plus a UI tap.

**ADMIN (3-of-3):** signer add/remove/rotation, threshold changes, module/validator install/remove/upgrade, implementation upgrade, guardian/recovery changes, privileged allowances, permission grants, emergency policy overrides, and any method that alters authorization semantics. All three distinct valid signatures. An admin operation must not be encoded as a nominal spend.

**DENY by default:** any unknown selector, arbitrary delegatecall, unchecked batch, unclassified module, fallback path, privileged bundler/facilitator shortcut, or cross-chain bridge without explicit classification and approval. Recovery must not bypass 3-of-3; note this creates permanent lockout risk on one lost signer. Before using real funds, separately design an owner-approved time-delayed recovery mechanism or consciously accept that risk. This document does not silently add a recovery bypass.

## 3. One transaction, one digest

The threshold module must compute or verify a domain-separated operation commitment including: chain ID (Base mainnet 8453 or chosen test chain), verifying contract/account, operation type and policy version, account nonce, deadline, target recipient(s), native value, token address and integer units, calldata or hash thereof, function selector, intended sender/account, batch order and complete batch root, allowed gas or execution bounds if policy requires them, and paymaster/facilitator dependencies if used.

Use an audited account-standard-specific typed signing scheme (e.g. correctly constructed EIP-712 or ERC-4337 user operation commitment, as applicable). Account/contract must **enforce** signatures against the same digest; a website receipt is not enforcement. Nonce must be consumed atomically on successful execution. Expired or altered payloads fail. Different chain, account, method, amount, recipient, token or nonce fails.

## 4. WebAuthn and EVM verification

On-chain verifier must validate WebAuthn authenticatorData, SHA-256 challenge binding to the operation digest, clientDataJSON challenge and type, intended RP ID hash, UP/UV policy, P-256 signature, origin policy, and acceptable encoding. Do not assume all Base account implementations support native P-256 verification or that a browser Face ID action alone proves required origin/challenge enforcement. Confirm feasibility, gas budget and audit coverage first.

For Ethereum signer C, validate recoverable ECDSA signature with canonical low-s constraints and an account-specific digest. Reject duplicate credentials, duplicate signers, double-counted key material, signatures for another domain, revoked credentials, and signature malleability.

## 5. Execution isolation

Initial target: **offline simulation only**, followed—after review—by a fresh Base Sepolia isolated smart account with zero economic exposure. No Coinbase custodial account mutation, no mainnet signing, no connecting pre-existing treasury assets, no x402 settlement, no seed phrase handling in the UI or repository.

Signer enrollment should be separate from execution and governed by ADMIN quorum; bootstrap deployment must be defined explicitly and audited, including initialization replay and atomic owner-set constraints. A wallet with 1-of-N fallback owner cannot be accepted.

## 6. Threats and invariants

- A-only/B-only/C-only SPEND: reject; any two distinct valid: allow, subject to payload checks.
- A+B, A+C, B+C ADMIN: reject; A+B+C ADMIN: allow.
- Two signatures from same signer: reject; forged passkey/user verification: reject.
- Same signed transaction repeated: reject; changed recipient/amount/chain/contract/method/nonce/deadline: reject.
- Reordering batched operations: reject; spend-wrapper attempt to call admin: reject.
- Install new module, upgrades, fallback, recovery or contract-owner shortcut without 3-of-3: reject.
- Offline/unavailable signer, bad challenge/origin, failed simulation, or uncertain implementation: HOLD.
- No production deployment gate is implied by passing unit tests.

## 7. Explicit unresolved decisions

1. Wallet framework and audited validator implementation; default Coinbase owner-list semantics are **not acceptable** as a threshold.
2. WebAuthn support and RP/origin constraints across iPhone/YubiKey/browser; credential independence proof.
3. Recovery/lockout strategy under 3-of-3 administration.
4. Exact operation digest, nonce key-space, ERC-4337 module interaction and gas ceilings.
5. Deployment chain/address, signer fingerprints, public address linkage and privacy implications—**all unverified**.
6. x402 integration must independently bind a successful payment to the same treasury policy and has its own separate gate.

## 8. Release controls

**DESIGN ONLY.** No contract source, deploy script, transaction call, private key, address migration, policy switch, or funds movement may be introduced by this PR.  
**FC-2 full gate HOLD · x402 live HOLD · wallet deployment HOLD · production HOLD.**

References for implementation review: ERC-4337, EIP-712, WebAuthn Level 3, EIP-1271 (where applicable), Base/Coinbase smart wallet implementation and any selected threshold validator's audit reports. These are review targets, not audited dependencies selected here.
