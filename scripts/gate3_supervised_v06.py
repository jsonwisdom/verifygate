#!/usr/bin/env python3
"""Gate3 v0.6 supervised offline classifier, synthetic test only. NEVER production authority."""
import argparse, hashlib, json, pathlib, subprocess, shlex, sys, re
CLASSIFIER="G3_PROCESS_SUPERVISOR_V1"
REJECT_CODES={20,21}
REJECTION_SCHEMA={"schema":"jcs-rejection-v1","code":None,"reason":None}
def digest(b):return hashlib.sha256(b).hexdigest()
def classify(command, payload, timeout=2):
    try:
        r=subprocess.run(shlex.split(command),input=payload,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    except subprocess.TimeoutExpired:
        return dict(outcome="CRASH_UNKNOWN",wait_status=None,signal=None,timeout=True,stderr_schema_valid=False,reason="TIMEOUT")
    except (OSError,ValueError):
        return dict(outcome="CRASH_UNKNOWN",wait_status=None,signal=None,timeout=False,stderr_schema_valid=False,reason="SUPERVISOR_ERROR")
    code=r.returncode
    signal=-code if code<0 else None
    stderr=r.stderr.decode("utf-8","replace")
    failure_markers=("AddressSanitizer","UndefinedBehaviorSanitizer","runtime error:","core dumped","MemoryError","Traceback (most recent call last)","uncaughtException","FATAL ERROR","out of memory")
    bad=any(s.lower() in stderr.lower() for s in failure_markers)
    valid=False
    if code in REJECT_CODES and not r.stdout and not bad:
        try:
            record=json.loads(stderr)
            valid=(isinstance(record,dict) and set(record)==set(REJECTION_SCHEMA) and
                   record["schema"]=="jcs-rejection-v1" and record["code"]==code and
                   isinstance(record["reason"],str) and bool(re.fullmatch("[A-Z0-9_]{3,40}",record["reason"])))
        except (ValueError,TypeError):pass
    if signal or bad or (code!=0 and not valid) or (code==0 and bool(r.stderr)):
        outcome="CRASH_UNKNOWN"
    elif code==0:
        outcome="ACCEPT"
    else:outcome="REJECT"
    return dict(outcome=outcome,wait_status=code,signal=signal,timeout=False,stderr_schema_valid=valid,
                stdout_hex=r.stdout.hex(),stderr_sha256=digest(r.stderr),reason="SUPERVISED")
def verify_bundle(manifest_path,expected_path,provenance_path,custodian_key_path):
    manifest=pathlib.Path(manifest_path).read_bytes()
    expect=pathlib.Path(expected_path).read_bytes()
    provenance=pathlib.Path(provenance_path).read_bytes()
    key=pathlib.Path(custodian_key_path).read_bytes()
    m=json.loads(manifest);e=json.loads(expect);p=json.loads(provenance)
    assert len(m["cases"])==55 and len({x["id"] for x in m["cases"]})==55 and any(x["id"]=="VEC-CANON-0001" for x in m["cases"])
    assert set(x["id"] for x in m["cases"])==set(e["results"])
    assert p["schema"]=="gate3-custodian-v1" and p["manifest_sha256"]==digest(manifest) and p["expected_sha256"]==digest(expect)
    assert p["generator_identity"] and p["generator_version"] and p["environment_digest"] and p["transcript_sha256"]
    # This is only a pre-shared-key offline fixture binding, NOT an independent public-key signature.
    # Custodian authenticity is not established unless key is independently authenticated.
    import hmac
    unsigned={k:v for k,v in p.items() if k!="custodian_hmac_sha256"}
    message=json.dumps(unsigned,sort_keys=True,separators=(",",":")).encode()
    assert hmac.compare_digest(p["custodian_hmac_sha256"],hmac.new(key,message,"sha256").hexdigest())
    for id_,value in e["results"].items():
        assert value["outcome"] in ("accept","reject")
        if value["outcome"]=="accept":
            assert digest(bytes.fromhex(value["canonical_hex"]))==value["canonical_sha256"]
        else:
            assert value["reason_code"] and not value.get("canonical_hex")
    return m,e,p,dict(manifest_sha256=digest(manifest),expected_sha256=digest(expect),provenance_sha256=digest(provenance))
def main():
    parser=argparse.ArgumentParser()
    for v in ("manifest","expected","provenance","custodian-key","python","javascript","go"):parser.add_argument("--"+v,required=True)
    parser.add_argument("--receipt",default="gate3_supervised_receipt.json")
    a=parser.parse_args()
    try:
        m,e,p,hashes=verify_bundle(a.manifest,a.expected,a.provenance,a.custodian_key)
        results=[]
        for case in m["cases"]:
            input_bytes=bytes.fromhex(case["hex"])
            oracle=e["results"][case["id"]]
            item={"id":case["id"],"adapters":{}}
            for label,command in (("python",a.python),("javascript",a.javascript),("go",a.go)):
                r=classify(command,input_bytes)
                ok=r["outcome"]==oracle["outcome"].upper() and (r["stdout_hex"]==oracle["canonical_hex"] if oracle["outcome"]=="accept" else r["stderr_schema_valid"] and r["wait_status"]==oracle["reason_code"])
                item["adapters"][label]={"verdict":"PASS" if ok else "HOLD",**r}
            results.append(item)
        matched=sum(x["verdict"]=="PASS" for row in results for x in row["adapters"].values())
        scope="PASS_SCOPED_OUTPUT_MATCH_ONLY" if matched==165 else "HOLD"
        receipt={"schema":"gate3-supervised-receipt-v1","classifier_version":CLASSIFIER,"gate":scope,
        "three_library_certification":"HOLD","adapter_independence":"UNVERIFIED","adapter_identity_digests":"UNVERIFIED",
        "crash_checks":"SEPARATE_CI_NEGATIVE_CONTROLS","limitations":"165 matching outputs do not prove independent implementations or RFC8785 conformance",
        "gap003":"OPEN","production_authority":"ZERO","real_trading":"DISABLED",**hashes,"rows":results}
        pathlib.Path(a.receipt).write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        print(scope,matched,"/165",CLASSIFIER)
        return 0 if matched==165 else 2
    except (AssertionError,ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as ex:
        print("GATE3 HOLD - PROVENANCE/INPUT NOT ACCEPTED",type(ex).__name__,file=sys.stderr)
        return 2
if __name__=="__main__":sys.exit(main())
