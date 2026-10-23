from uuid import uuid4
from .models import Case, CaseInput, State
from .verification import verify


class InvalidTransition(ValueError):
    pass


def evaluate_case(data: CaseInput) -> Case:
    evidence = verify(data)
    state = State.approved_by_rules if all(e.passed for e in evidence) else State.needs_review
    return Case(id=str(uuid4()), state=state, input=data, evidence=evidence)


def decide(case: Case, actor: str, approve: bool) -> Case:
    if case.state != State.needs_review:
        raise InvalidTransition("Human decision only allowed for needs_review cases")
    return case.model_copy(update={
        "state": State.approved_by_human if approve else State.rejected,
        "approval_actor": actor,
        "version": case.version + 1,
    })
