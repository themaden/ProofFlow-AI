# ProofFlow AI

A small, auditable proof-of-concept of a purchase-order/invoice verification workflow. Built for software engineering interviews: deterministic amount checks, traceable evidence, human approval and idempotent mock ERP submission.

**Status:** local MVP, not a production financial system. **No actual payments**. No generative LLM in this release; adding one without compromising verifiable calculations is documented as a future step.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
pytest -q
uvicorn proofflow.api:app --reload
```

Open `http://127.0.0.1:8000/docs` and POST the example in `examples/request.json` to `/cases`. Use the returned case ID to inspect `/cases/{id}`, and approve only if review is required via `/cases/{id}/decision`.

## Scope
- Input: structured invoice and purchase order, **not** scanned PDF/OCR.
- Rule-based verification is intentional; no misleading assertion that an LLM determined monetary accuracy.
- Case repository is in-memory for the demo; restart clears state. Not multi-worker safe.
- Approval endpoint has a demo actor field, **not authentication**. Do not expose publicly.
- This code makes no claim of bank-specific compliance or credit underwriting.

See [architecture](docs/architecture.md), [security](docs/security.md), [licensing](THIRD_PARTY_LICENSES.md) and [roadmap](docs/roadmap.md).

## Jupyter research

Four executable ML notebooks (EDA, training, evaluation, error analysis) are in [`notebooks/`](notebooks/README.md). Install with `pip install -e ".[notebooks,dev]"`. Uses synthetic data and a reproducible scikit-learn pipeline; evaluation is **not** valid evidence for actual financial decisions.
