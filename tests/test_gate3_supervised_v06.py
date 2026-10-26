#!/usr/bin/env python3
"""Synthetic only; exercises safety gates, not the unavailable 55-vector original."""
import unittest,sys,signal,tempfile,pathlib,json,hashlib,hmac,shlex
from scripts.gate3_supervised_v06 import classify,verify_bundle
def sha(b):return hashlib.sha256(b).hexdigest()
def cmd(code):return shlex.quote(sys.executable)+" -c "+shlex.quote(code)
class Controls(unittest.TestCase):
 def test_segfault(self):
  r=classify(cmd("import os,signal;os.kill(os.getpid(),signal.SIGSEGV)"),b"{}")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_abort(self):
  r=classify(cmd("import os;os.abort()"),b"{}")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_exception(self):
  r=classify(cmd("raise RuntimeError('boom')"),b"{}")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_oom(self):
  r=classify(cmd("raise MemoryError('synthetic OOM')"),b"{}")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_timeout(self):
  r=classify(cmd("import time;time.sleep(2)"),b"{}",timeout=0.03)
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN");self.assertTrue(r["timeout"])
 def test_fake_rejection(self):
  r=classify(cmd("import sys;sys.exit(20)"),b"{}")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_structured_rejection(self):
  r=classify(cmd("import sys,json;sys.stderr.write(json.dumps({'schema':'jcs-rejection-v1','code':20,'reason':'INVALID_UTF8'}));sys.exit(20)"),b"x")
  self.assertEqual(r["outcome"],"REJECT");self.assertTrue(r["stderr_schema_valid"])
 def test_signal_and_sanitizer(self):
  r=classify(cmd("import sys;sys.stderr.write('AddressSanitizer: boom');sys.exit(20)"),b"x")
  self.assertEqual(r["outcome"],"CRASH_UNKNOWN")
 def test_bundle_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);files=[p/f for f in ("manifest.json","expected.json","provenance.json","key")]
   m={"cases":[{"id":"VEC-CANON-0001" if i==0 else f"SYN-{i:02d}","hex":"7b7d"} for i in range(55)]}
   e={"results":{x["id"]:{"outcome":"accept","canonical_hex":"7b7d","canonical_sha256":sha(b"{}")} for x in m["cases"]}}
   rawm=json.dumps(m,sort_keys=True).encode();rawe=json.dumps(e,sort_keys=True).encode()
   files[0].write_bytes(rawm);files[1].write_bytes(rawe);files[3].write_bytes(b"synthetic-fixture-hmac-key-not-production")
   record={"schema":"gate3-custodian-v1","manifest_sha256":sha(rawm),"expected_sha256":sha(rawe),"generator_identity":"synthetic-test","generator_version":"1","environment_digest":"test","transcript_sha256":"test"}
   msg=json.dumps(record,sort_keys=True,separators=(",",":")).encode()
   record["custodian_hmac_sha256"]=hmac.new(files[3].read_bytes(),msg,"sha256").hexdigest()
   files[2].write_text(json.dumps(record,sort_keys=True))
   args=tuple(str(x) for x in files)
   verify_bundle(*args)
   files[1].write_bytes(rawe+b" ");self.assertRaises(AssertionError,verify_bundle,*args)
   files[1].write_bytes(rawe)
   files[0].write_bytes(rawm+b" ");self.assertRaises(AssertionError,verify_bundle,*args)
   files[0].write_bytes(rawm)
   modified=json.loads(files[2].read_text());modified["custodian_hmac_sha256"]="0"*64
   files[2].write_text(json.dumps(modified));self.assertRaises(AssertionError,verify_bundle,*args)
if __name__=="__main__":unittest.main()
