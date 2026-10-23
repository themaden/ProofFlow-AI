# Reproducible ML research notebooks

Run from repository root:

```bash
python -m pip install -e '.[notebooks]'
jupyter lab
```

Run notebooks in order 01–04 (each notebook is also independently executable). Data is generated locally with a fixed seed; no downloads, API keys or production data. Model training utilities live in `src/proofflow/ml.py` rather than notebook-only code.

**Scope:** This is an educational *invoice review triage* classifier trained on artificial labels. It is **not** a financial credit-risk model, and metrics must not be described as real-world performance.
