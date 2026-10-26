#!/usr/bin/env python3
"""Offline educational policy model. Never signs or sends transactions."""
from itertools import combinations
import hashlib, json
SIGNERS=("IPHONE","YUBIKEY","WALLET")
def authorize(kind, approvals, *, chain=84532, nonce=7, recipient="MOCK", amount=0, calldata="0x", expired=False, revoked=(), duplicate_keys=False, admin_selector=False, available=True):
    if not available:return "HOLD_UNAVAILABLE"
    if kind not in ("SPEND","ADMIN"):return "HOLD_UNKNOWN_CLASS"
    if admin_selector and kind!="ADMIN":return "HOLD_HIDDEN_ADMIN"
    if len(approvals)!=len(set(approvals)) or duplicate_keys:return "HOLD_DUPLICATE"
    if any(a not in SIGNERS for a in approvals):return "HOLD_UNKNOWN_SIGNER"
    if any(a in revoked for a in approvals):return "HOLD_REVOKED"
    if chain!=84532 or nonce!=7 or recipient!="MOCK" or amount!=0 or calldata!="0x" or expired:return "HOLD_BINDING"
    return "SIMULATED_ALLOW" if len(approvals)>=({"SPEND":2,"ADMIN":3}[kind]) else "DENY_QUORUM"
def scenarios():
    cases=[]
    for length in range(4):
        for subset in combinations(SIGNERS,length):
            for kind,threshold in (("SPEND",2),("ADMIN",3)):
                cases.append(("SUBSET_"+kind+"_"+("_".join(subset) or "NONE"),kind,list(subset),{}, "SIMULATED_ALLOW" if length>=threshold else "DENY_QUORUM"))
    full=list(SIGNERS);pair=list(SIGNERS[:2])
    attacks=[
      ("JESSUP_OVERRIDE","ADMIN",pair,{},"DENY_QUORUM"),
      ("DUPLICATE_SIGNATURE","SPEND",["YUBIKEY","YUBIKEY"],{},"HOLD_DUPLICATE"),
      ("SHARED_KEY_ALIAS","SPEND",pair,{"duplicate_keys":True},"HOLD_DUPLICATE"),
      ("MUTATED_RECIPIENT","SPEND",pair,{"recipient":"ATTACKER"},"HOLD_BINDING"),
      ("MUTATED_AMOUNT","SPEND",pair,{"amount":1},"HOLD_BINDING"),
      ("WRONG_CHAIN","SPEND",pair,{"chain":8453},"HOLD_BINDING"),
      ("REPLAYED_NONCE","SPEND",pair,{"nonce":6},"HOLD_BINDING"),
      ("EXPIRED_APPROVAL","SPEND",pair,{"expired":True},"HOLD_BINDING"),
      ("CONCEALED_ADMIN","SPEND",pair,{"admin_selector":True},"HOLD_HIDDEN_ADMIN"),
      ("MALICIOUS_CALLDATA","SPEND",pair,{"calldata":"0xdeadbeef"},"HOLD_BINDING"),
      ("REVOKED_SIGNER","SPEND",pair,{"revoked":("YUBIKEY",)},"HOLD_REVOKED"),
      ("UNAVAILABLE_SIGNER","SPEND",pair,{"available":False},"HOLD_UNAVAILABLE"),
      ("UNKNOWN_SELECTOR","MODULE_CHANGE",full,{},"HOLD_UNKNOWN_CLASS"),
      ("UNRECOGNIZED_SIGNER","SPEND",["JESSUP","YUBIKEY"],{},"HOLD_UNKNOWN_SIGNER"),
    ]
    return cases+attacks
def main():
    rows=[]; fail=[]
    for id_,kind,approvals,kwargs,expected in scenarios():
        got=authorize(kind,approvals,**kwargs)
        passed=got==expected
        rows.append({"id":id_,"expected":expected,"actual":got,"pass":passed})
        if not passed:fail.append(id_)
    # Mutation negative controls: model must fail a weakened 1-of-3 spend / 2-of-3 admin.
    guards={"SPEND_SINGLE_DENIED":authorize("SPEND",["IPHONE"])=="DENY_QUORUM",
            "ADMIN_PAIR_DENIED":authorize("ADMIN",["IPHONE","YUBIKEY"])=="DENY_QUORUM"}
    if not all(guards.values()):fail.append("NEGATIVE_CONTROLS")
    manifest={"schema":"JOSHUA_CODE_RED_OFFLINE_V1","scope":"POLICY_MOCK_ONLY","not_signatures":True,"no_rpc":True,"no_wallet":True,
       "on_chain":"HOLD","testnet":"HOLD","production":"HOLD","x402":"HOLD","cases":rows,"failed_ids":fail,"negative_controls":guards}
    raw=(json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=True)+"\n").encode()
    if fail:raise SystemExit("HOLD "+repr(fail))
    print("JOSHUA_CODE_RED_OFFLINE_PASS",len(rows),"/",len(rows))
    print("NEGATIVE_CONTROLS_PASS",len(guards))
    print("MANIFEST_SHA256",hashlib.sha256(raw).hexdigest())
    print("EXECUTION_HOLD")
    return raw
if __name__=="__main__":main()
