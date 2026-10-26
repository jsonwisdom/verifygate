#!/usr/bin/env python3
"""JOSHUA / NORAD fictional wallet replay. Offline only. No keys, RPC, signatures or funds."""
import hashlib
import json

SIGNERS = frozenset(("IPHONE", "YUBIKEY", "WALLET"))
THRESHOLDS = {"SPEND": 2, "ADMIN": 3}

def evaluate(operation, approvals):
    kind = operation.get("kind")
    if kind not in THRESHOLDS:
        return "HOLD_UNKNOWN_OPERATION"
    if any(s not in SIGNERS for s in approvals):
        return "HOLD_UNKNOWN_SIGNER"
    if len(approvals) != len(set(approvals)):
        return "HOLD_DUPLICATE_SIGNER"
    if operation.get("chain_id") != 84532:
        return "HOLD_CHAIN"
    if operation.get("value") != 0 or operation.get("calldata") != "0x":
        return "HOLD_NONZERO_OR_CALLDATA"
    if operation.get("expires") != 4102444800 or operation.get("nonce") != 1:
        return "HOLD_OPERATION_BINDING"
    return "SIMULATED_APPROVAL" if len(approvals) >= THRESHOLDS[kind] else "DENIED_THRESHOLD"

def main():
    operation = {"kind":"SPEND", "chain_id":84532, "value":0, "calldata":"0x",
                 "nonce":1, "expires":4102444800, "to":"SIMULATED_NO_ADDRESS"}
    admin = dict(operation,kind="ADMIN")
    scenarios = [
        ("JESSUP_ORDER",operation,["YUBIKEY"],"DENIED_THRESHOLD"),
        ("JOSHUA_CHALLENGE",operation,["IPHONE","YUBIKEY"],"SIMULATED_APPROVAL"),
        ("JESSUP_ADMIN_OVERRIDE",admin,["IPHONE","YUBIKEY"],"DENIED_THRESHOLD"),
        ("THREE_KEYS",admin,["IPHONE","YUBIKEY","WALLET"],"SIMULATED_APPROVAL"),
        ("DUPLICATE_KEY",operation,["YUBIKEY","YUBIKEY"],"HOLD_DUPLICATE_SIGNER"),
        ("UNKNOWN_SENDER",operation,["JESSUP","YUBIKEY"],"HOLD_UNKNOWN_SIGNER"),
        ("WRONG_CHAIN",dict(operation,chain_id=8453),["IPHONE","YUBIKEY"],"HOLD_CHAIN"),
        ("HIDDEN_TRANSFER",dict(operation,value=1),["IPHONE","YUBIKEY"],"HOLD_NONZERO_OR_CALLDATA"),
        ("HIDDEN_CALL",dict(operation,calldata="0xdeadbeef"),["IPHONE","YUBIKEY"],"HOLD_NONZERO_OR_CALLDATA"),
        ("REPLAY_NONCE",dict(operation,nonce=0),["IPHONE","YUBIKEY"],"HOLD_OPERATION_BINDING"),
        ("EXPIRED_BINDING",dict(operation,expires=0),["IPHONE","YUBIKEY"],"HOLD_OPERATION_BINDING"),
        ("UNKNOWN_METHOD",dict(operation,kind="MODULE_UPGRADE"),["IPHONE","YUBIKEY","WALLET"],"HOLD_UNKNOWN_OPERATION"),
    ]
    rows=[]
    for name, op, approvals, expected in scenarios:
        result=evaluate(op, approvals)
        assert result==expected, f"HOLD {name}: {result}"
        rows.append({"scenario":name,"result":result,"expected":expected})
    record={"title":"JOSHUA_NORAD_WALLET_OFFLINE_REPLAY","not_on_chain":True,
            "no_wallet_signatures":True,"not_contract_verification":True,
            "policy":"SPEND_2_OF_3__ADMIN_3_OF_3","results":rows}
    data=(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n").encode()
    print("JOSHUA_REPLAY_SCENARIOS_PASS",len(rows))
    print("RECEIPT_SHA256",hashlib.sha256(data).hexdigest())
    print("ON_CHAIN HOLD; TESTNET HOLD; X402 HOLD; MAINNET HOLD")
if __name__=="__main__":
    main()
