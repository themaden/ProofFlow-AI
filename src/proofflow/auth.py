"""Small demo API-key gate; replace with real IdP/OIDC for production."""
import os
from hmac import compare_digest
from fastapi import Depends, Header, HTTPException

def identity(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(401, "API key required")
    keys = {"operator": os.getenv("PROOFFLOW_OPERATOR_KEY"), "reviewer": os.getenv("PROOFFLOW_REVIEWER_KEY")}
    for role, key in keys.items():
        if key and len(key) >= 16 and compare_digest(x_api_key,key):
            return role
    raise HTTPException(401, "Invalid API key")

def operator(role: str = Depends(identity)) -> str:
    if role != "operator":
        raise HTTPException(403, "Operator permission required")
    return role

def reviewer(role: str = Depends(identity)) -> str:
    if role != "reviewer":
        raise HTTPException(403, "Reviewer permission required")
    return role
