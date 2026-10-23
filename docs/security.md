# Security model and threat boundaries

- Two role-specific API keys are supplied by environment variables and validated with constant-time comparison. Never commit real credentials.
- All business mutations require appropriate role; read operations require either role.
- The review decision's supplied `actor` property is ignored for authorisation/audit; the server records the authenticated role.
- UUID case IDs are not authorization tokens. This is a **single-tenant local demo**; there is no per-organization isolation.
- Audit entries are append-only at the application level, not cryptographically immutable or tamper-evident against a database administrator.
- SQL statements use parameter binding. Typed Pydantic models validate amounts and currencies.
- The browser UI is for local demonstration, with secrets held only in page inputs (not local storage). Do not expose `/demo` on the public internet.
- No real payments, third-party API requests or actual confidential customer data.

**Before production:** OIDC, scoped service identities, encrypted connections and storage, database migrations, Postgres transactions with concurrency strategy, rate limits, CSRF/cookie policy if switching to sessions, secrets rotation, tenant separation, observability, durable integration outbox and independent security review.
