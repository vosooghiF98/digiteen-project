import subprocess, time, uuid
from common import register, login, request, CONSUMER

email = f"events-{uuid.uuid4().hex}@example.com"
register(email)
token = login(email)

print("Stopping consumer for at least 30 seconds...")
subprocess.run(["docker", "compose", "stop", "wallet-event-consumer"], check=True)
transaction_ids = []
started = time.time()
for i in range(3):
    status, data = request("POST", "/api/v1/wallet/deposit", {"requestId": str(uuid.uuid4()), "amount": 100 + i}, token)
    assert status == 200, (status, data)
    transaction_ids.append(data["transactionId"])
    if i < 2:
        time.sleep(10)
remaining = 30 - (time.time() - started)
if remaining > 0:
    time.sleep(remaining)

subprocess.run(["docker", "compose", "start", "wallet-event-consumer"], check=True)
print("Consumer restarted; waiting for all events...")

def processed_count(txid):
    status, data = request("GET", f"/api/v1/processed-events/transaction/{txid}/count", base=CONSUMER)
    return data if status == 200 else 0

deadline = time.time() + 45
while time.time() < deadline:
    try:
        counts = [processed_count(txid) for txid in transaction_ids]
        if counts == [1, 1, 1]:
            print("PASS: all events recovered and each has exactly one observable effect")
            break
    except Exception:
        pass
    time.sleep(2)
else:
    raise AssertionError(f"events were not processed exactly once: {[processed_count(t) for t in transaction_ids]}")
