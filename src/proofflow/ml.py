"""Synthetic invoice mismatch classification experiments (not a banking risk model)."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split

FEATURES = ["invoice_amount", "po_amount", "days_since_po", "vendor_tenure_months", "line_count", "amount_ratio", "amount_gap", "currency"]
NUMERIC = ["invoice_amount", "po_amount", "days_since_po", "vendor_tenure_months", "line_count", "amount_ratio", "amount_gap"]


def synthetic_invoices(n: int = 1500, seed: int = 42) -> pd.DataFrame:
    if n < 20:
        raise ValueError("n must be >=20")
    rng = np.random.default_rng(seed)
    po = rng.uniform(100, 20000, n).round(2)
    mismatch = rng.random(n) < 0.22
    invoice = (po * np.where(mismatch, rng.choice([0.75, 0.85, 1.15, 1.35], n), 1.0)).round(2)
    days = rng.integers(0, 120, n)
    tenure = rng.integers(0, 90, n)
    lines = rng.integers(1, 40, n)
    currency = rng.choice(["TRY", "EUR", "USD"], n)
    # Ground truth comes from the synthetic generator. Not a customer default label.
    review = (mismatch | ((days > 95) & (tenure < 10))).astype(int)
    return pd.DataFrame({"invoice_amount": invoice,"po_amount":po,"days_since_po":days,
                         "vendor_tenure_months":tenure,"line_count":lines,"amount_ratio":invoice/po,"amount_gap":abs(invoice/po-1),"currency":currency,
                         "needs_review":review})


def split_data(df: pd.DataFrame):
    return train_test_split(df[FEATURES], df["needs_review"], test_size=0.25,
                            stratify=df["needs_review"], random_state=42)


def build_pipeline() -> Pipeline:
    numeric = Pipeline([("impute", SimpleImputer(strategy="median")),("scale", StandardScaler())])
    categories = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                           ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    preprocess = ColumnTransformer([("num", numeric, NUMERIC), ("cat", categories, ["currency"])])
    return Pipeline([("preprocess",preprocess), ("classifier",LogisticRegression(max_iter=1000, class_weight="balanced",random_state=42))])
