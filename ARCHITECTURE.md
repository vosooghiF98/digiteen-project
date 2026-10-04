# Architecture decisions

## Concurrency
All balance mutations use PostgreSQL pessimistic row locking (`PESSIMISTIC_WRITE` / `SELECT ... FOR UPDATE`). Transfers lock both wallets in deterministic UUID order to avoid deadlocks. The database also has `CHECK (balance >= 0)` as a final invariant.

## Idempotency
Every financial command carries a client-generated `requestId`. `wallet_transaction.request_id` is unique. The service rechecks the request after acquiring wallet locks, so five simultaneous copies serialize and return the same successful transaction without applying money twice. Reusing the same request id for different content returns HTTP 409.

## Atomic transfer
Debit, credit, transaction row, and outbox row are written inside the same PostgreSQL transaction. Any unexpected failure rolls all of them back.

## Reliable events
The service implements the Transactional Outbox pattern. Business state + outbox commit atomically; a scheduled publisher sends unpublished rows to Kafka. A crash after Kafka send but before `published_at` may cause redelivery, therefore the consumer is idempotent (`processed_event.id` primary key). This provides at-least-once delivery with exactly-once observable consumer effect.

## Traceability
`X-Correlation-ID` is generated/accepted at HTTP ingress, placed in MDC, stored on transaction/outbox rows, included in Kafka payloads, and restored to MDC by the consumer.
