from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from proofflow.service import CaseService
from proofflow.models import CaseInput
from proofflow.api import app

DATA = {"invoice":{"invoice_id":"A-001","supplier_id":"SUP-A","po_id":"PO-001","amount":"120.00","currency":"USD"},"purchase_order":{"po_id":"PO-001","supplier_id":"SUP-A","amount":"100.00","currency":"USD"}}

def test_persists_reviewer_audit(tmp_path):
    location = str(tmp_path / "workflow.db")
    a = CaseService(location)
    record = a.create(CaseInput.model_validate(DATA))
    assert record.state == "needs_review"
    b = CaseService(location)
    assert b.get(record.id).state == "needs_review"
    with pytest.raises(ValueError):
        b.submit(record.id)
    b.review(record.id,"reviewer",True)
    b.submit(record.id)
    b.submit(record.id)
    assert [e["event"] for e in b.history(record.id)] == ["created","approved","mock_erp_submitted"]
    assert b.get(record.id).version == 3

def test_requires_keys_and_roles(monkeypatch):
    monkeypatch.setenv("PROOFFLOW_OPERATOR_KEY", "test-operator-key-2026")
    monkeypatch.setenv("PROOFFLOW_REVIEWER_KEY", "test-reviewer-key-2026")
    client = TestClient(app)
    assert client.get('/cases').status_code == 401
    assert client.post('/cases', json=DATA, headers={'x-api-key':'test-reviewer-key-2026'}).status_code == 403
    assert client.post('/cases', json=DATA, headers={'x-api-key':'wrong'}).status_code == 401

def test_demo_and_audit_controls(monkeypatch):
    monkeypatch.setenv("PROOFFLOW_OPERATOR_KEY", "demo-operator-key-2026")
    monkeypatch.setenv("PROOFFLOW_REVIEWER_KEY", "demo-reviewer-key-2026")
    c=TestClient(app)
    assert c.get('/demo').status_code == 200
    assert 'ProofFlow AI' in c.get('/demo').text
    case=c.post('/cases',json={**DATA,"invoice":{**DATA["invoice"],"invoice_id":"AUDIT-TEST-901"}},headers={"x-api-key":"demo-operator-key-2026"}).json()
    cid=case['id']
    assert c.get(f'/cases/{cid}/audit').status_code == 401
    assert len(c.get(f'/cases/{cid}/audit',headers={"x-api-key":"demo-reviewer-key-2026"}).json()) == 1
    assert c.post(f'/cases/{cid}/decision',json={"actor":"admin","approve":True},headers={"x-api-key":"demo-operator-key-2026"}).status_code == 403


def test_short_and_missing_secrets_rejected(monkeypatch):
    monkeypatch.setenv("PROOFFLOW_OPERATOR_KEY", "short")
    monkeypatch.delenv("PROOFFLOW_REVIEWER_KEY", raising=False)
    c = TestClient(app)
    assert c.get("/cases", headers={"x-api-key": "short"}).status_code == 401
    assert c.get("/cases", headers={"x-api-key": "anything"}).status_code == 401
