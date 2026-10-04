import uuid, subprocess
from common import register, login, request

sender_email = f"trace-a-{uuid.uuid4().hex}@example.com"
receiver_email = f"trace-b-{uuid.uuid4().hex}@example.com"
register(sender_email)
receiver = register(receiver_email)
token = login(sender_email)
request("POST", "/api/v1/wallet/deposit", {"requestId": str(uuid.uuid4()), "amount": 5000}, token)
trace_id = f"trace-demo-{uuid.uuid4()}"
status, data = request("POST", "/api/v1/wallet/transfer", {
    "requestId": str(uuid.uuid4()), "destinationWalletId": receiver["walletId"], "amount": 1000
}, token, trace_id=trace_id)
assert status == 200, (status, data)
print("Trace ID:", trace_id)
print("Transaction ID:", data["transactionId"])
print("Run this to reconstruct the chain:")
print(f'docker compose logs wallet-service wallet-event-consumer | grep "{trace_id}"')
