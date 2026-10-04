# Digiteen Digital Wallet — Java / Spring Boot

Implementation of the supplied wallet assessment using Java 17, Spring Boot 3.3.5, PostgreSQL, Kafka, JWT, pessimistic locking, Transactional Outbox, idempotent consumer, structured JSON logs, Flyway, and repeatable concurrency scripts.

The ZIP contains two independently runnable service projects (`wallet-service` and `wallet-event-consumer`). For submission, put each service directory in its own Git repository and keep real incremental commit history, as required by the assessment. The root Maven `pom.xml` exists only so IntelliJ can import both modules together.

## Fastest start — one command

Requirements: Docker Desktop / Docker Compose.

```bash
docker compose up --build -d
```

Then:
- wallet API: `http://localhost:8080`
- consumer verification API: `http://localhost:8081`
- PostgreSQL: `localhost:5432`
- Kafka: `localhost:9092`

Health:
```bash
curl http://localhost:8080/actuator/health
curl http://localhost:8081/actuator/health
```

Reset everything:
```bash
docker compose down -v
```

## IntelliJ IDEA

Open the ZIP folder as a Maven project by selecting the root `pom.xml`. Java SDK must be 17. IntelliJ will show two modules:
- `wallet-service` → run `WalletServiceApplication`
- `wallet-event-consumer` → run `WalletEventConsumerApplication`

If running the apps from IntelliJ instead of Docker, start only infrastructure first:
```bash
docker compose up -d postgres kafka
```
Then run both application classes. Default local configuration already points to `localhost`.

## Core APIs

Register:
```http
POST /api/v1/auth/register
{"name":"Ali","email":"ali@example.com","phone":"09120000000","password":"Password123!"}
```

Login:
```http
POST /api/v1/auth/login
{"email":"ali@example.com","password":"Password123!"}
```

Authenticated wallet endpoints (`Authorization: Bearer <token>`):
```text
POST /api/v1/wallet/deposit
POST /api/v1/wallet/withdraw
POST /api/v1/wallet/transfer
GET  /api/v1/wallet/balance
GET  /api/v1/wallet/transactions
```

Every financial request has a UUID `requestId`; it is the idempotency key and is part of the request content.

Example withdrawal:
```json
{"requestId":"5af6bf7f-cb2d-4620-8501-a9429ba2ca39","amount":3000}
```

## Acceptance scripts
Run them from the root directory after the stack is up:

```bash
python scripts/concurrency_withdrawal_test.py
python scripts/duplicate_transfer_test.py
python scripts/event_recovery_test.py
python scripts/trace_demo.py
```

Expected concurrency output:
```text
success=33 insufficient=17 final_balance=1000.00
PASS: deterministic 50-request concurrency scenario
```

The duplicate-transfer test sends the exact same transfer five times concurrently and verifies one financial effect + four idempotent replays.

The event-recovery test stops the consumer for at least 30 seconds, creates transactions while it is down, starts it again, and verifies every transaction event was processed once.

`trace_demo.py` performs a transfer with a known correlation id and prints the log command needed to reconstruct the full path.

## Design notes
See `ARCHITECTURE.md`.
