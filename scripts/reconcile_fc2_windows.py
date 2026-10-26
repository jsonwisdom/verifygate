#!/usr/bin/env python3
"""Reconcile frozen Windows Go+JS receipt with Python FC-2 policy seed. No production gate."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_RECEIPT = "54f751b6fd48b585387e777e0e5f23a4912b807e66250946e1d22212ae59a6bc"
EXPECTED_FIXTURE = "c0775a2bc387d93bc31064b6b1ccf131a11943158c935354bae503dc3bdb7375"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def require(condition, why):
    if not condition:
        raise ValueError("HOLD: " + why)

def run():
    receipt_file = ROOT / "fc2_windows_adapters_receipt.json"
    fixtures_file = ROOT / "fixtures/fc2_hostile_bytes_v1.json"
    require(receipt_file.is_file(), "missing local two-adapter receipt")
    original_bytes = receipt_file.read_bytes()
    require(digest(original_bytes) == EXPECTED_RECEIPT, "original Windows receipt SHA-256 changed")
    fixture_bytes = fixtures_file.read_bytes()
    require(digest(fixture_bytes) == EXPECTED_FIXTURE, "fixture SHA-256 changed")
    receipt = json.loads(original_bytes)
    fixtures = json.loads(fixture_bytes)
    cases = fixtures["cases"]
    rows = receipt["results"]
    require(len(cases) == len(rows) == 16, "fixture/receipt count")
    require(len({case["id"] for case in cases}) == 16, "duplicate fixture IDs")
    require(receipt.get("fixture_sha256") == EXPECTED_FIXTURE, "receipt fixture hash")
    require(receipt.get("gate") == "PASS_TWO_ADAPTERS_ONLY", "original gate")
    require(receipt.get("failures") == [], "reported failures not empty")
    require(set(receipt.get("adapter_sha256", {})) == {"go", "js"}, "adapter hashes unavailable")
    for name, value in receipt["adapter_sha256"].items():
        require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value), name + " adapter digest malformed")

    sys.path.insert(0, str(ROOT / "tests"))
    from test_fc2_python_seed import strict_parse

    combined = []
    for case, row in zip(cases, rows):
        cid = case["id"]
        require(row.get("id") == cid and row.get("expect") == case["expect"], cid + " order/expect")
        impls = row.get("results")
        require(isinstance(impls, dict) and set(impls) == {"go", "js"}, cid + " implementations")
        accepted_outputs = []
        for name in ("go", "js"):
            impl = impls[name]
            require(impl.get("pass") is True, cid + " " + name + " failed")
            require(type(impl.get("exit")) is int, cid + " " + name + " invalid exit")
            expect_accept = case["expect"] == "accept"
            require((impl["exit"] == 0) == expect_accept, cid + " " + name + " exit mismatch")
            require(impl.get("actual") == ("accept" if expect_accept else "reject"), cid + " " + name + " outcome")
            out_hex = impl.get("output_hex")
            require(isinstance(out_hex, str), cid + " " + name + " output absent")
            output = bytes.fromhex(out_hex)
            if expect_accept:
                require(bool(output), cid + " " + name + " empty canonical bytes")
                accepted_outputs.append(output)
            else:
                require(not output, cid + " " + name + " stdout on rejection")
        if accepted_outputs:
            require(accepted_outputs[0] == accepted_outputs[1], cid + " Go/JS output mismatch")
        raw = bytes.fromhex(case["hex"])
        try:
            strict_parse(raw)
            py_result = "accept"
        except (ValueError, UnicodeError, RecursionError):
            py_result = "reject"
        require(py_result == case["expect"], cid + " Python policy mismatch")
        combined.append({"id": cid, "expect": case["expect"], "python_policy": py_result, "go_js_canonical_agree": bool(accepted_outputs) or case["expect"] == "reject"})
    report = {"scope": "FC2_16_CASE_PYTHON_POLICY_PLUS_GO_JS_RECONCILED_ONLY", "full_fc2_gate": "HOLD", "production": "HOLD", "x402_live": "HOLD", "source_receipt_sha256": EXPECTED_RECEIPT, "fixtures_sha256": EXPECTED_FIXTURE, "adapter_sha256": receipt["adapter_sha256"], "count": len(combined), "results": combined}
    out = ROOT / "fc2_combined_scoped_receipt.json"
    out.write_bytes((json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))
    print("FC2_THREE_POLICY_CHECKS_RECONCILED", len(combined), "/", len(cases))
    print("FULL_FC2_GATE HOLD")
    print("COMBINED_SHA256", digest(out.read_bytes()))
    print("COMBINED_RECEIPT", out)

if __name__ == "__main__":
    try:
        run()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print("FC2_RECONCILIATION_HOLD", exc, file=sys.stderr)
        sys.exit(1)
