#!/usr/bin/env python3
"""Validate pinned hostile-byte cases against the Python FC-2 seed. NOT cross-runtime certification."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_fc2_python_seed import strict_parse

fixture = json.loads((ROOT / "fixtures" / "fc2_hostile_bytes_v1.json").read_bytes())
assert fixture["schema"] == "fc2-hostile-bytes-seed-v1"
cases = fixture["cases"]
assert len(cases) == 16, f"HOLD: count={len(cases)}"
ids = [c["id"] for c in cases]
assert len(ids) == len(set(ids)), "HOLD: duplicate fixture ids"
accepts = rejects = 0
for case in cases:
    raw = bytes.fromhex(case["hex"])
    expected = case["expect"]
    assert expected in ("accept", "reject"), "HOLD: unexpected outcome"
    try:
        strict_parse(raw)
        actual = "accept"
    except (ValueError, UnicodeError, RecursionError):
        actual = "reject"
    assert actual == expected, f"HOLD: {case['id']} expected {expected} got {actual}"
    if expected == "accept": accepts += 1
    else: rejects += 1
assert (accepts, rejects) == (3, 13), "HOLD: counts"
print("FC2_FIXED_CORPUS_PYTHON_SEED_PASS: 16/16 (3 accept, 13 reject)")
print("FC2_CROSS_RUNTIME_HOLD: production Python, JS and Go adapters not tested")
