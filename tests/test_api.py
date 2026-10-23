import os
os.environ["PROOFFLOW_DB"] = ":memory:"
os.environ["PROOFFLOW_OPERATOR_KEY"] = "operator-test-secret"
os.environ["PROOFFLOW_REVIEWER_KEY"] = "reviewer-test-secret"
import json
from pathlib import Path
from fastapi.testclient import TestClient
from proofflow.api import app

client = TestClient(app)
client.headers.update({"x-api-key": "operator-test-secret"})


def payload():
    return json.loads((Path(__file__).parents[1] / "examples/request.json").read_text())


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_idempotent_submit():
    data = payload()
    data["invoice"]["invoice_id"] = "API-101"
    response = client.post("/cases", json=data)
    assert response.status_code == 200
    case = response.json()
    assert client.post("/cases", json=data).json()["id"] == case["id"]
    assert client.post(f"/cases/{case['id']}/submit").json()["state"] == "submitted"
    assert client.post(f"/cases/{case['id']}/submit").json()["erp_reference"].startswith("MOCK-")


def test_conflicting_duplicate_invoice():
    data = payload()
    data["invoice"]["invoice_id"] = "API-102"
    assert client.post("/cases", json=data).status_code == 200
    data["invoice"]["amount"] = "10.00"
    assert client.post("/cases", json=data).status_code == 409


def test_review_gate():
    data = payload()
    data["invoice"]["invoice_id"] = "API-103"
    data["invoice"]["amount"] = "999.00"
    case = client.post("/cases", json=data).json()
    case_id = case["id"]
    assert case["state"] == "needs_review"
    assert client.post(f"/cases/{case_id}/submit").status_code == 409
    assert client.post(f"/cases/{case_id}/decision", json={"actor": "reviewer", "approve": True}, headers={"x-api-key":"reviewer-test-secret"}).json()["state"] == "approved_by_human"
    assert client.post(f"/cases/{case_id}/submit").status_code == 200


def test_not_found():
    assert client.get("/cases/missing").status_code == 404
