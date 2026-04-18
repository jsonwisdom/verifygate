import json
import hashlib


def verify():
    with open('artifact.json', 'r') as f:
        artifact = json.load(f)

    # Arithmetic
    i = artifact['inputs']
    res = (i['beginning_balance'] + i['total_revenue']) - (i['total_spending'] + i['reserves'])

    # Hash check
    canonical = json.dumps(artifact, separators=(',', ':'), sort_keys=True)
    actual_hash = hashlib.sha256(canonical.encode()).hexdigest()
    expected_hash = "95b5fd99d927cb7f3468d5645ef2827b2c29bf978c194916a0888d6f9a97fe30"

    print(f"Arithmetic: {'PASS' if res == artifact['reported_total'] else 'FAIL'}")
    print(f"Hash Match: {'PASS' if actual_hash == expected_hash else 'FAIL'}")


if __name__ == "__main__":
    verify()
