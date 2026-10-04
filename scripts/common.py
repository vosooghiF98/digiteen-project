import json
import urllib.request
import urllib.error

BASE = "http://localhost:8080"
CONSUMER = "http://localhost:8081"

def request(method, path, body=None, token=None, trace_id=None, base=BASE):
    data = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if trace_id:
        headers["X-Correlation-ID"] = trace_id
    req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: payload = json.loads(raw)
        except Exception: payload = raw
        return e.code, payload

def register(email, password="Password123!"):
    status, data = request("POST", "/api/v1/auth/register", {
        "name": "Concurrency Test", "email": email, "phone": None, "password": password
    })
    assert status == 201, (status, data)
    return data

def login(email, password="Password123!"):
    status, data = request("POST", "/api/v1/auth/login", {"email": email, "password": password})
    assert status == 200, (status, data)
    return data["accessToken"]
