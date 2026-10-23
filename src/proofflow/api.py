from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from importlib.resources import files
from .auth import identity, operator, reviewer
from .models import Case, CaseInput, Decision
from .service import CaseService
from .workflow import InvalidTransition

app = FastAPI(title="ProofFlow AI", version="1.0.0", description="Auditable demo; no real payment integration")
service = CaseService()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/cases", response_model=list[Case])
def list_cases(role: str = Depends(identity)):
    return service.list()

@app.post("/cases", response_model=Case)
def create_case(data: CaseInput, role: str = Depends(operator)):
    try:
        return service.create(data,role)
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc

@app.get("/cases/{case_id}", response_model=Case)
def read_case(case_id: str, role: str = Depends(identity)):
    try:
        return service.get(case_id)
    except KeyError as exc:
        raise HTTPException(404,"Case not found") from exc

@app.get("/cases/{case_id}/audit")
def audit_case(case_id: str, role: str = Depends(identity)):
    try:
        return service.history(case_id)
    except KeyError as exc:
        raise HTTPException(404,"Case not found") from exc

@app.post("/cases/{case_id}/decision", response_model=Case)
def review_case(case_id: str, decision: Decision, role: str = Depends(reviewer)):
    try:
        return service.review(case_id,role,decision.approve)
    except KeyError as exc:
        raise HTTPException(404,"Case not found") from exc
    except InvalidTransition as exc:
        raise HTTPException(409,str(exc)) from exc

@app.post("/cases/{case_id}/submit", response_model=Case)
def submit_case(case_id: str, role: str = Depends(operator)):
    try:
        return service.submit(case_id,role)
    except KeyError as exc:
        raise HTTPException(404,"Case not found") from exc
    except InvalidTransition as exc:
        raise HTTPException(409,str(exc)) from exc


@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo():
    return (files("proofflow") / "static" / "index.html").read_text(encoding="utf-8")
