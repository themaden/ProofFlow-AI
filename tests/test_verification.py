from proofflow.models import CaseInput, State
from proofflow.workflow import decide, evaluate_case, InvalidTransition
import json
from pathlib import Path
import pytest


def example():
    return CaseInput.model_validate(json.loads((Path(__file__).parents[1] / "examples/request.json").read_text()))


def test_exact_match_passes():
    case = evaluate_case(example())
    assert case.state == State.approved_by_rules
    assert len(case.evidence) == 4
    assert all(x.passed for x in case.evidence)


def test_amount_mismatch_requires_review():
    case_input = example()
    case_input.invoice.amount += 100
    case = evaluate_case(case_input)
    assert case.state == State.needs_review
    assert {x.rule for x in case.evidence if not x.passed} == {"amount_match"}
    assert decide(case, "operator", True).state == State.approved_by_human


def test_cannot_override_automatically_approved_case():
    with pytest.raises(InvalidTransition):
        decide(evaluate_case(example()), "operator", True)


def test_invalid_invoice_amount_is_rejected():
    raw = example().model_dump()
    raw["invoice"]["amount"] = "-1"
    with pytest.raises(ValueError):
        CaseInput.model_validate(raw)
