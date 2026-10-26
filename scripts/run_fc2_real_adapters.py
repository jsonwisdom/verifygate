#!/usr/bin/env python3
"""FC-2 actual adapter runner: evidence-only, fail closed. Requires local adapter paths."""
import hashlib,json,os,pathlib,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
FIX=ROOT/"fixtures/fc2_hostile_bytes_v1.json"
def hold(m): raise RuntimeError("HOLD: "+m)
def main():
    fx=json.loads(FIX.read_bytes())
    cases=fx["cases"]
    adapters={"python":os.getenv("FC2_PYTHON_ADAPTER"),"js":os.getenv("FC2_JS_ADAPTER"),"go":os.getenv("FC2_GO_ADAPTER")}
    if any(not v for v in adapters.values()): hold("all three FC2_*_ADAPTER paths required; no mock fallback")
    receipt={"schema":"fc2-real-adapters-v1","status":"HOLD","fixtures_sha256":hashlib.sha256(FIX.read_bytes()).hexdigest(),"results":[],"adapter_sha256":{}}
    for name,path in adapters.items():
        p=pathlib.Path(path).resolve(strict=True)
        if not p.is_file():hold("adapter not file: "+name)
        receipt["adapter_sha256"][name]=hashlib.sha256(p.read_bytes()).hexdigest()
    for c in cases:
        raw=bytes.fromhex(c["hex"])
        outputs={}
        for name,path in adapters.items():
            # Contract: each executable reads bytes on stdin; stdout is canonical bytes on accept.
            # Reject means nonzero exit and no stdout. Do not treat signal/timeouts as successful rejects.
            try:
                p=subprocess.run([path],input=raw,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=4,check=False)
            except (OSError,subprocess.TimeoutExpired) as e:
                hold(c["id"]+" "+name+" launch/timeout "+str(e))
            accepted=(p.returncode==0)
            if accepted and c["expect"]!="accept":hold(c["id"]+" "+name+" accepted malicious input")
            if not accepted and c["expect"]!="reject":hold(c["id"]+" "+name+" rejected expected valid input")
            if not accepted and p.stdout:hold(c["id"]+" "+name+" emitted stdout on rejection")
            outputs[name]={"exit":p.returncode,"accepted":accepted,"stdout_sha256":hashlib.sha256(p.stdout).hexdigest(),"stdout_hex":p.stdout.hex() if accepted else ""}
        if c["expect"]=="accept" and len({v["stdout_hex"] for v in outputs.values()})!=1:hold(c["id"]+" cross-runtime bytes differ")
        receipt["results"].append({"id":c["id"],"expect":c["expect"],"implementations":outputs})
    receipt["status"]="PASS_FC2_ADAPTER_CORPUS_ONLY"
    out=ROOT/"fc2_real_adapters_receipt.json"
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("FC2_REAL_ADAPTER_CORPUS_PASS",len(cases),"receipt=",out)
if __name__=="__main__":
    try: main()
    except Exception as e:
        print("FC2_REAL_ADAPTER_HOLD",e,file=sys.stderr)
        sys.exit(1)
