#!/usr/bin/env python3
"""Gate 3 v0.5 scoped differential runner; no wallet, RPC, signing, or trades."""
import argparse, hashlib, json, pathlib, shlex, subprocess, sys

def sha(b): return hashlib.sha256(b).hexdigest()
def check(a):
    p=pathlib.Path(a.corpus)
    if not p.is_file(): raise ValueError("HOLD: exact v0.5 corpus absent")
    raw=p.read_bytes()
    if sha(raw)!=a.corpus_sha256:raise ValueError("HOLD: corpus digest mismatch")
    cases=json.loads(raw)["cases"]
    if len(cases)!=55 or len({x["id"] for x in cases})!=55 or "VEC-CANON-0001" not in {x["id"] for x in cases}:raise ValueError("HOLD: incomplete/duplicate 55-case corpus")
    adapters={"python":shlex.split(a.python),"javascript":shlex.split(a.javascript),"go":shlex.split(a.go)}
    rows=[]
    for case in cases:
        b=bytes.fromhex(case["hex"]);expect=case["expect"]
        if expect not in ("accept","reject"):raise ValueError("HOLD: unknown expectation")
        expected=bytes.fromhex(case["canonical_hex"]) if expect=="accept" else b""
        results={}
        for name,command in adapters.items():
            try:
                r=subprocess.run(command,input=b,capture_output=True,timeout=a.timeout)
                actual="accept" if r.returncode==0 else "reject"
                good=actual==expect and (r.stdout==expected if expect=="accept" else not r.stdout)
                results[name]={"verdict":"PASS" if good else "FAIL","actual":actual,"exit":r.returncode,"stdout_hex":r.stdout.hex(),"stderr_sha256":sha(r.stderr)}
            except (OSError,subprocess.TimeoutExpired) as e:
                results[name]={"verdict":"INCONCLUSIVE","reason":type(e).__name__}
        rows.append({"id":case["id"],"expected":expect,"implementations":results})
    matrix={name:{label:sum(row["implementations"][name]["verdict"]==label for row in rows) for label in ("PASS","FAIL","INCONCLUSIVE")} for name in adapters}
    gate="PASS_SCOPED_OUTPUT_MATCH_ONLY" if all(v["PASS"]==55 for v in matrix.values()) else "HOLD"
    receipt={"schema":"gate3-v0.5-differential-v1","corpus_sha256":sha(raw),"rows":rows,"matrix":matrix,"adapter_commands":adapters,"adapter_library_identity":"UNVERIFIED","three_library_certification":"HOLD","gate":gate,"gap003":"OPEN","price_parameters":"UNRESOLVED","real_trading":"DISABLED","production_authority":"ZERO"}
    target=pathlib.Path(a.receipt);target.write_bytes((json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode())
    print("GATE3",gate,"MATRIX",json.dumps(matrix,sort_keys=True),"RECEIPT_SHA256",sha(target.read_bytes()))
    return 0 if gate.startswith("PASS_") else 2
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("corpus","corpus-sha256","python","javascript","go"):p.add_argument("--"+x,required=True)
    p.add_argument("--receipt",default="gate3_v05_receipt.json");p.add_argument("--timeout",type=float,default=10)
    try: sys.exit(check(p.parse_args()))
    except (OSError,ValueError,KeyError,TypeError,json.JSONDecodeError) as e:
        print("GATE3 HOLD",str(e),file=sys.stderr);sys.exit(2)
