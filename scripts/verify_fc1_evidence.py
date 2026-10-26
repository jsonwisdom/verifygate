#!/usr/bin/env python3
"""Fail-closed verification of the pinned FC-1 evidence. No network, keys, or deployment."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "fc1-20261026"
PINNED = {
    "differential_receipt_patched.json": "7639db51de2fa70b7c9c83a02aa0a2ae0f4c2533bbb22ffc451e235bb980c95d",
    "canon_js_fixed.js": "f44c0bccd7d77454fc47066ec7e6938330dbf7ace7caba510ebebe2d364d2f0d",
}
FIXTURE_HASH = "51907e95c967f847de38921727b484e144333fc9647bd925160f91b7c8ac07ae"

def check(value, description):
    if not value:
        raise ValueError("HOLD: " + description)

def main():
    for filename, expected in PINNED.items():
        path = EVIDENCE / filename
        check(path.is_file(), f"missing {filename}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        check(actual == expected, f"SHA-256 mismatch: {filename}")
        print(f"PINNED SHA-256 OK: {filename}")
    receipt = json.loads((EVIDENCE / "differential_receipt_patched.json").read_text(encoding="utf-8"))
    check(receipt.get("gate") == "PASS_FC1_SCOPE_ONLY", "gate field")
    check(receipt.get("passed") == 60, "passed count")
    check(receipt.get("fixtures_sha256") == FIXTURE_HASH, "fixtures digest")
    check(receipt.get("failed_ids") == [], "failed_ids not empty")
    results = receipt.get("results")
    check(isinstance(results, list) and len(results) == 60, "expected exactly 60 result records")
    check(len({r.get("id") for r in results}) == 60, "duplicate or missing IDs")
    canonical = rejected = 0
    for r in results:
        check(r.get("pass") is True, f"failed result: {r.get('id')}")
        expected = r.get("expect")
        check(expected in ("canonical", "reject"), f"unknown expectation: {r.get('id')}")
        impl = r.get("implementations")
        check(isinstance(impl, dict) and set(impl) == {"reference", "js", "go"}, f"implementations: {r.get('id')}")
        if expected == "canonical":
            canonical += 1
            output = r.get("expected_hex")
            check(isinstance(output, str) and bool(output), f"expected_hex: {r.get('id')}")
            for name, data in impl.items():
                check(data.get("accepted") is True and data.get("exit") == 0 and data.get("output_hex") == output,
                      f"canonical mismatch {r.get('id')} / {name}")
        else:
            rejected += 1
            check(r.get("expected_hex") is None, f"reject expected_hex: {r.get('id')}")
            for name, data in impl.items():
                check(data.get("accepted") is False and data.get("exit") != 0 and data.get("output_hex") == "",
                      f"rejection mismatch {r.get('id')} / {name}")
    check((canonical, rejected) == (50, 10), f"class counts {canonical}/{rejected}")
    print("FC1_EVIDENCE_CI_PASS 60/60 (50 canonical + 10 reject)")
    print("SCOPE: archived receipt consistency only; not a test rerun, FC-2 approval, or deployment")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FC1_EVIDENCE_CI_HOLD: {exc}", file=sys.stderr)
        sys.exit(1)
