# VerifyGate // Genesis Node

**Sovereign Verifier v0.1**  
**Node:** jaywisdom.base  
**Status:** T4_SETTLED  

Immutable root-of-trust for on-chain and off-chain verification. Receipts over narration.

### What is VerifyGate?
A minimal, client-side + on-chain verifier that turns any text/JSON/AI output into a SHA-256 fingerprint and offers settlement tiers up to T4 (fully settled genesis anchor).

- T1: Local client-side hash  
- T2: $5 attested receipt (via PayPal)  
- T3/T4: Future multi-auditor & on-chain settlement  

### Quick Start
1. Paste any content into the box  
2. Generate SHA-256 fingerprint  
3. Commit hash to ledger for higher-tier attestation  

Live site: https://jsonwisdom.github.io/verifygate

### Genesis Receipt (Root of Trust)
```json
{
  "sha256": "6a64241528b87f9f6eb571764eda724a5b5d68f63461a3b9563915d12748b22e",
  "auditor_id": "jaywisdom.base",
  "status": "T4_SETTLED",
  "settled_at": "2026-03-28T00:30:00Z",
  "message": "Immutable root for all chained verifications."
}
