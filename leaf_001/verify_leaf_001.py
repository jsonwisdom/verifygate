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
    expected_hash = "4a918ab359f0228d1d142fde6270d9ea7f18b4f08dd9c725f17356835adf2a76"

    print(f"Arithmetic: {'PASS' if res == artifact['reported_total'] else 'FAIL'}")
    print(f"Hash Match: {'PASS' if actual_hash == expected_hash else 'FAIL'}")


if __name__ == "__main__":
    verify()
