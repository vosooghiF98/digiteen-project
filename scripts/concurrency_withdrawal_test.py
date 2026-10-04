from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
from common import register, login, request

email = f"concurrency-{uuid.uuid4().hex}@example.com"
register(email)
token = login(email)
status, _ = request("POST", "/api/v1/wallet/deposit", {"requestId": str(uuid.uuid4()), "amount": 100000}, token)
assert status == 200

def withdraw(_):
    return request("POST", "/api/v1/wallet/withdraw", {"requestId": str(uuid.uuid4()), "amount": 3000}, token)[0]

with ThreadPoolExecutor(max_workers=50) as pool:
    statuses = [f.result() for f in as_completed([pool.submit(withdraw, i) for i in range(50)])]

success = statuses.count(200)
insufficient = statuses.count(409)
status, balance = request("GET", "/api/v1/wallet/balance", token=token)
final_balance = float(balance["balance"])
print(f"success={success} insufficient={insufficient} final_balance={final_balance:.2f}")
assert success == 33, statuses
assert insufficient == 17, statuses
assert final_balance == 1000.0, balance
print("PASS: deterministic 50-request concurrency scenario")
