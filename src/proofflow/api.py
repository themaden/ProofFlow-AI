from fastapi import FastAPI, HTTPException
from .models import Case, CaseInput, Decision
from .service import CaseService
from .workflow import InvalidTransition

app = FastAPI(title="ProofFlow AI", version="0.1.0", description="Auditable demo. No production payment integration.")
service = CaseService()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/cases", response_model=Case)
def create_case(data: CaseInput):
    try:
        return service.create(data)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc


@app.get("/cases/{case_id}", response_model=Case)
def read_case(case_id: str):
    try:
        return service.get(case_id)
    except KeyError as exc:
        raise HTTPException(404, "Case not found") from exc


@app.post("/cases/{case_id}/decision", response_model=Case)
def review_case(case_id: str, decision: Decision):
    try:
        return service.review(case_id, decision.actor, decision.approve)
    except KeyError as exc:
        raise HTTPException(404, "Case not found") from exc
    except InvalidTransition as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/cases/{case_id}/submit", response_model=Case)
def submit_case(case_id: str):
    try:
        return service.submit(case_id)
    except KeyError as exc:
        raise HTTPException(404, "Case not found") from exc
    except InvalidTransition as exc:
        raise HTTPException(409, str(exc)) from exc
