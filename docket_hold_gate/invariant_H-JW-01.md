# H-JW-01 — Honest Query / Honest JSONWisdom

## Normative invariant

JSONWisdom MUST NOT let an answer, claim, or state transition become stronger than the question asked or the evidence actually held.

```text
QUERY_SCOPE >= CLAIM_SCOPE
EVIDENCE_SCOPE >= STATE_TRANSITION_SCOPE
ELSE -> STATUS=HOLD, PROMOTION=DENIED, ERROR=SCOPE_INFLATION
```

## Locked constraints

- `AUTO_FILE_AUTHORITY = false` with no override path.
- `Predictions = NON-EVIDENTIARY`.
- Silence, elapsed time, `INDEX_HIT`, `INDEX_MISS`, `ARCHIVE_HIT`, `ARCHIVE_MISS`, and lookup errors never trigger a legal action.
- PCL, CourtListener/RECAP, MCP wrappers, and scrapers may enrich a review bundle but do not set `pacer_state=VERIFIED`.
- `pacer_state` may become `VERIFIED` only when both are present:
  1. a verifiable `PACER_ECF` or `UPLOADED_PDF` artifact with a SHA-256 hash; and
  2. `human_signoff.present=true`.
- Even after verification, `AUTO_FILE_AUTHORITY` remains `false`.

## Source authority boundaries

| Source | Allowed claim | Must not set |
|---|---|---|
| PACER Auth API | Token issued | `pacer_state=VERIFIED` |
| PCL REST | Index row exists for the queried docket/court/party | Filing granted, ECF receipt, order text |
| CourtListener / RECAP | Archive copy exists as of its archive metadata | Official current ECF state |
| recap-fetch / uploaded PDF | Document bytes and hash | Automatic promotion |
| MCP / scraper | Same authority as the backend it wraps | Extra authority |

## Canonical source classes

```text
UNVERIFIED_NARRATIVE
PCL_INDEX
CL_ARCHIVE
SCRAPE_UNOFFICIAL
DOCUMENT_SOURCE_BOUND
```

`PCL_INDEX`, `CL_ARCHIVE`, and `SCRAPE_UNOFFICIAL` are review metadata, not receipts.

## Canonical examples

### Honest index query

```json
{
  "query": "Does this docket appear in PCL?",
  "source": "PCL",
  "result": "INDEX_HIT",
  "claim_allowed": "Index row exists",
  "claim_forbidden": "Official PACER state verified",
  "status": "HOLD"
}
```

### Hashed artifact without human sign-off

```json
{
  "query": "Do we possess hashed court-document bytes?",
  "source": "UPLOADED_PDF",
  "result": "ARTIFACT_PRESENT",
  "artifact_hash": "sha256:<64-hex>",
  "human_signoff": false,
  "pacer_state": "UNVERIFIED",
  "promotion": "DENIED"
}
```

The artifact proves possession of those bytes. It does not by itself prove current PACER state, a judicial ruling, or filing authority.
