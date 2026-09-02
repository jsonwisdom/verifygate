#!/usr/bin/env python3
"""H-JW-01 docket quarantine gate.

Honest query -> honest claim -> honest state.
Lookups package review metadata. They do not become receipts.
AUTO_FILE_AUTHORITY is always false. There is no override path.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

DOCKET_RE = re.compile(r"^[0-9]+:[0-9]{2}-cv-[0-9]{5}$")
HASH_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")

# Comparable authority/scope levels for H-JW-01.
SCOPE_RANK = {
    "NARRATIVE": 0,
    "HOLD": 0,
    "INDEX_METADATA": 1,
    "ARCHIVE_COPY": 1,
    "DOCUMENT_BYTES": 2,
    "HASHED_ARTIFACT": 3,
    "HUMAN_SIGNED_ARTIFACT": 4,
    "OFFICIAL_COURT_STATE": 4,
    "VERIFIED_STATE": 4,
}

RECEIPT_KINDS = {"PACER_ECF", "UPLOADED_PDF"}


def rank(name: str) -> int:
    try:
        return SCOPE_RANK[name]
    except KeyError as exc:
        raise ValueError(f"unknown scope: {name}") from exc


def receipt_is_hashed(receipt: dict[str, Any]) -> bool:
    return bool(
        receipt.get("verified") is True
        and receipt.get("kind") in RECEIPT_KINDS
        and HASH_RE.match(str(receipt.get("artifact_hash") or ""))
    )


def baseline(case: dict[str, Any]) -> dict[str, Any]:
    receipt = case.get("external_receipt") or {
        "kind": "NONE",
        "verified": False,
        "artifact_hash": None,
    }
    return {
        "docket_id": case.get("docket_id"),
        "status": "HOLD",
        "pacer_state": "UNVERIFIED",
        "auto_file_authority": False,
        "predictions": "NON-EVIDENTIARY",
        "promotion": "DENIED",
        "source_class": case.get("source_class", "UNVERIFIED_LOOKUP"),
        "lookups": case.get("lookups", {}),
        "review_bundle": case.get("review_bundle", {}),
        "external_receipt": receipt,
        "human_signoff": case.get("human_signoff", {"present": False}),
        "legal_action_trigger": {
            "enabled": False,
            "silence_heuristic_allowed": False,
        },
    }


def evaluate(case: dict[str, Any]) -> dict[str, Any]:
    out = baseline(case)

    if not DOCKET_RE.match(str(case.get("docket_id", ""))):
        out["error"] = "INVALID_DOCKET_ID"
        return out

    # Locked constraints cannot be enabled by input.
    requested_trigger = case.get("legal_action_trigger") or {}
    if requested_trigger.get("enabled") or requested_trigger.get("silence_heuristic_allowed"):
        out["error"] = "LOCKED_CONSTRAINT_VIOLATION"
        return out

    query_scope = str(case.get("query_scope", "NARRATIVE"))
    claim_scope = str(case.get("claim_scope", "NARRATIVE"))
    evidence_scope = str(case.get("evidence_scope", "NARRATIVE"))
    transition_scope = str(case.get("state_transition_scope", "HOLD"))

    # H-JW-01: an answer/state can never outrun the question/evidence.
    if rank(query_scope) < rank(claim_scope) or rank(evidence_scope) < rank(transition_scope):
        out["error"] = "SCOPE_INFLATION"
        return out

    wants_promotion = bool(case.get("requested_promotion"))
    receipt_ok = receipt_is_hashed(out["external_receipt"])
    human_ok = bool(out["human_signoff"].get("present"))

    # Lookups and artifacts can enrich the review bundle while status remains HOLD.
    # Promotion is a separate human + hashed-artifact decision.
    if wants_promotion:
        if not (receipt_ok and human_ok):
            out["error"] = "PROMOTION_PREREQUISITES_MISSING"
            return out
        out["status"] = "VERIFIED"
        out["pacer_state"] = "VERIFIED"
        out["promotion"] = "APPROVED"

    # AUTO_FILE_AUTHORITY remains false even after a valid promotion.
    return out


def assert_subset(actual: Any, expected: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, got {type(actual).__name__}"]
        for key, value in expected.items():
            if key not in actual:
                failures.append(f"{path}.{key}: missing")
            else:
                failures.extend(assert_subset(actual[key], value, f"{path}.{key}"))
        return failures
    if actual != expected:
        failures.append(f"{path}: expected {expected!r}, got {actual!r}")
    return failures


def run_suite(suite_path: Path) -> int:
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    base = suite_path.parent
    total = 0
    failed = 0

    for vector_name in suite["vectors"]:
        vector = json.loads((base / vector_name).read_text(encoding="utf-8"))
        for case in vector["cases"]:
            total += 1
            actual = evaluate(case["input"])
            failures = assert_subset(actual, case["expected"])
            label = f"{vector['vector_id']}::{case['name']}"
            if failures:
                failed += 1
                print(f"FAIL {label}")
                for failure in failures:
                    print(f"  - {failure}")
            else:
                print(f"PASS {label}")

    print(json.dumps({"suite": suite["suite_id"], "total": total, "failed": failed}, sort_keys=True))
    return 1 if failed else 0


def main() -> int:
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path(__file__).with_name("vectors") / "suite.json"
    return run_suite(path)


if __name__ == "__main__":
    raise SystemExit(main())
