from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class State(str, Enum):
    approved_by_rules = "approved_by_rules"
    needs_review = "needs_review"
    rejected = "rejected"
    approved_by_human = "approved_by_human"
    submitted = "submitted"


class Invoice(BaseModel):
    invoice_id: str = Field(min_length=1, max_length=80)
    supplier_id: str = Field(min_length=1, max_length=80)
    po_id: str = Field(min_length=1, max_length=80)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class PurchaseOrder(BaseModel):
    po_id: str = Field(min_length=1, max_length=80)
    supplier_id: str = Field(min_length=1, max_length=80)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class CaseInput(BaseModel):
    invoice: Invoice
    purchase_order: PurchaseOrder


class Evidence(BaseModel):
    rule: str
    passed: bool
    observed: str
    expected: str


class Case(BaseModel):
    id: str
    state: State
    input: CaseInput
    evidence: list[Evidence]
    version: int = 1
    erp_reference: str | None = None
    approval_actor: str | None = None


class Decision(BaseModel):
    actor: str = Field(min_length=2, max_length=100)
    approve: bool
