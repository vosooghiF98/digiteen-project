from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
from common import register, login, request

sender_email = f"sender-{uuid.uuid4().hex}@example.com"
receiver_email = f"receiver-{uuid.uuid4().hex}@example.com"
sender = register(sender_email)
receiver = register(receiver_email)
sender_token = login(sender_email)
receiver_token = login(receiver_email)

status, _ = request("POST", "/api/v1/wallet/deposit", {"requestId": str(uuid.uuid4()), "amount": 100000}, sender_token)
assert status == 200

body = {"requestId": str(uuid.uuid4()), "destinationWalletId": receiver["walletId"], "amount": 3000}

def transfer(_):
    return request("POST", "/api/v1/wallet/transfer", body, sender_token)

with ThreadPoolExecutor(max_workers=5) as pool:
    results = [f.result() for f in as_completed([pool.submit(transfer, i) for i in range(5)])]

assert all(status == 200 for status, _ in results), results
non_duplicates = sum(1 for _, data in results if data["duplicate"] is False)
duplicates = sum(1 for _, data in results if data["duplicate"] is True)
_, sb = request("GET", "/api/v1/wallet/balance", token=sender_token)
_, rb = request("GET", "/api/v1/wallet/balance", token=receiver_token)
print(f"first_effects={non_duplicates} duplicate_replays={duplicates} sender={sb['balance']} receiver={rb['balance']}")
assert non_duplicates == 1
assert duplicates == 4
assert float(sb["balance"]) == 97000.0
assert float(rb["balance"]) == 3000.0
print("PASS: five concurrent identical transfers have one financial effect")
