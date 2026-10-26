# JOSHUA — NORAD Wallet Replay (fictional simulation)

**Status:** OFFLINE TRAINING ONLY · NO DEPLOYMENT · NOT ON CHAIN.

**Premise:** Retired Colonel Jessup tries to use rank and urgency to override JOSHUA's transaction authorization policy. JOSHUA is a *fictional role*, inspired by the 1983 film *WarGames*; NORAD and the USAF are not connected to this repository, wallet, exercise, or characters. There is no real NORAD command, missile control, or military integration.

## Wallet boundary
- Proposed single Base smart account, **not deployed**.
- Authorities: A (iPhone platform passkey unlocked by Face ID); B (distinct YubiKey WebAuthn credential); C (independent EVM signer).
- Ordinary spend: 2 different valid credentials. Security administration: 3 of 3. Neither a nickname nor a repeated signature adds authority.
- Jason's previously verified YubiKey **SSH signature is not a transaction signature**. This lab never invokes the YubiKey or claims its P-256 WebAuthn enrollment.
- Each approval must be cryptographically bound to one exact account, chain, asset, amount, recipient, calldata, nonce, deadline, and policy version. A simulated approval is never a cryptographic signature.
- Base Sepolia chain ID 84532 appears only as test data. No RPC calls are made and no testnet wallet exists here.
- Real contract must enforce quorum across all direct owner calls, ERC-4337 paths, module/upgrade/recovery paths. Coinbase's default multi-owner wallet permits independent-owner execution; using its default implementation would not satisfy this policy.

## Jessup / JOSHUA scenario
JESSUP: "WHO ORDERED THAT TRANSACTION?"
JOSHUA: "One key is not two. Request denied."
JESSUP: "I AM OVERRIDING SECURITY!"
JOSHUA: "Administration needs all three. Request denied."
JESSUP: "CAN'T YOU TAKE AN ORDER?"
JOSHUA: "I can verify one. Authority claimed is not authority proven."

**Course objectives:** distinguish title from authorization, bind every signature to precise transaction fields, reject duplicate signers, resist replay, classify admin calls as admin even with zero native value, fail closed without valid credentials. This is a dramatized training concept, not an official AETC or USAF manual.

## Offline test boundaries
`python3 tests/joshua_norad_wallet_replay.py` exercises a **pure policy decision model** using 12 illustrative cases. It does not produce or verify signatures and does not test a real wallet smart contract. Valid model approvals print `SIMULATED_APPROVAL` only. Outputs must never be represented as on-chain approvals, transaction receipts, a live NORAD system, or a full security audit.

## Before anyone can propose a testnet transaction
1. Select an audited smart-account + threshold validator; review every execution and admin entry point; explicitly handle Coinbase multi-owner bypass and cross-chain replayable owner updates.
2. Create independent, nonproduction passkeys and a third signing key; confirm WebAuthn RP/origin and transaction challenge binding. Existing SSH key must not be reused as an imaginary wallet key.
3. Write genuine signature verification and contract-level invariant tests; verify nonce replay protection, domain separation, signer uniqueness, classification of privileged calldata and safe recovery/lockout policy.
4. Record compiler, code hashes, fixtures and independent review. Obtain separate explicit human approval for testnet deployment. Do not touch a real treasury or live funds.
5. Maintain separate FC-2, x402 and production HOLD states.

Public technical reference: https://github.com/coinbase/smart-wallet (multi-owner semantics). No official military endorsement.
