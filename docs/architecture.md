# Architecture and design decisions

```
POST /cases -> Pydantic validation -> deterministic 4-rule verifier
                                      -> approved_by_rules OR needs_review
POST /cases/{id}/decision -> restricted state transition (DEMO ONLY: unauthenticated)
POST /cases/{id}/submit -> idempotent MOCK-ERP reference
GET  /cases/{id} -> evidence and current state
```

Why rules instead of an LLM? Amount, currency, purchase order and supplier ID matching are deterministic operations. An LLM might assist with noncritical text explanations later, but must not bypass the validation rules.

Why lock + in-memory store? Makes a fully runnable teaching/demo artifact without external services. It is **not durable**, cross-process safe, access-controlled or suitable for concurrent banking workloads. Use transactional PostgreSQL plus uniqueness constraints, optimistic concurrency and outbox pattern before real integration.

A case is not a credit score, a bank approval or a payment authorization.
