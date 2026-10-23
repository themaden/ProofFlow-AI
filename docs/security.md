# Security posture (MVP limitations)

- **No authentication or authorization.** The demo review actor is an unverified string. All endpoints must run on localhost or a trusted isolated network only.
- **No real ERP API, no transfers, no bank customer data.** Fixtures are synthetic.
- Errors avoid returning tracebacks to callers. Request schema has bounded string fields and strict three-letter currency validation.
- Audit evidence exists as case output but is not immutable, signed, durable or protected from administrator changes.
- No uploaded files or LLM prompts, reducing injection surface at this stage.

## Production requirements
OAuth2/OIDC with RBAC; encrypted PostgreSQL; immutable audit log; secret rotation; rate limiting; tracing without PII; idempotency database constraints; human review signed with authenticated identity; authorization checks on every case; threat modeling; evaluated OCR/LLM input defenses.
