#!/usr/bin/env python3
"""Synthetic-only harness unit tests. Never represent these as the missing Gate 3 corpus."""
import hashlib, json, pathlib, subprocess, tempfile, unittest
from argparse import Namespace
from unittest.mock import patch
from scripts.run_gate3_v05 import check

class HarnessControls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.cases=[{"id":"VEC-CANON-0001" if i==0 else f"SYNTHETIC-{i:02d}",
                     "hex":"7b7d","expect":"accept","canonical_hex":"7b7d"} for i in range(55)]
        self.args=Namespace(corpus=str(self.root/"synthetic.json"),corpus_sha256="",
          python="fake-python",javascript="fake-js",go="fake-go",timeout=0.05,
          receipt=str(self.root/"receipt.json"))
    def prepare(self):
        raw=json.dumps({"cases":self.cases},sort_keys=True).encode()
        pathlib.Path(self.args.corpus).write_bytes(raw)
        self.args.corpus_sha256=hashlib.sha256(raw).hexdigest()
    @staticmethod
    def ok(*args,**kwargs):
        return subprocess.CompletedProcess(args[0],0,b"{}",b"")
    def test_valid_synthetic_scoped_only(self):
        self.prepare()
        with patch("scripts.run_gate3_v05.subprocess.run",side_effect=self.ok):
            self.assertEqual(check(self.args),0)
        receipt=json.loads(pathlib.Path(self.args.receipt).read_text())
        self.assertEqual(receipt["gate"],"PASS_SCOPED_OUTPUT_MATCH_ONLY")
        self.assertEqual(receipt["three_library_certification"],"HOLD")
    def test_wrong_digest(self):
        self.prepare();self.args.corpus_sha256="0"*64
        with self.assertRaisesRegex(ValueError,"digest mismatch"):check(self.args)
    def test_duplicate_ids(self):
        self.cases[-1]["id"]=self.cases[1]["id"];self.prepare()
        with self.assertRaisesRegex(ValueError,"incomplete/duplicate"):check(self.args)
    def test_invalid_hex(self):
        self.cases[2]["hex"]="XYZ";self.prepare()
        with patch("scripts.run_gate3_v05.subprocess.run",side_effect=self.ok):
            with self.assertRaises(ValueError):check(self.args)
    def test_adapter_disagreement(self):
        self.prepare()
        def wrong(command,**kwargs):
            return subprocess.CompletedProcess(command,0,b"WRONG",b"")
        with patch("scripts.run_gate3_v05.subprocess.run",side_effect=wrong):
            self.assertEqual(check(self.args),2)
        self.assertEqual(json.loads(pathlib.Path(self.args.receipt).read_text())["matrix"]["go"]["FAIL"],55)
    def test_adapter_timeout(self):
        self.prepare()
        def timeout(command,**kwargs):
            raise subprocess.TimeoutExpired(command,0.05)
        with patch("scripts.run_gate3_v05.subprocess.run",side_effect=timeout):
            self.assertEqual(check(self.args),2)
        self.assertEqual(json.loads(pathlib.Path(self.args.receipt).read_text())["matrix"]["javascript"]["INCONCLUSIVE"],55)
    def test_bad_expected_outcome(self):
        self.cases[2]["expect"]="unknown";self.prepare()
        with self.assertRaisesRegex(ValueError,"unknown expectation"):check(self.args)

if __name__=="__main__":unittest.main()
