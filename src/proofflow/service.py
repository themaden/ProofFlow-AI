from threading import RLock
from .models import Case, CaseInput, State
from .workflow import evaluate_case, decide, InvalidTransition


class CaseService:
    """Thread-synchronized local demo store. Replace with transactional DB in production."""
    def __init__(self):
        self._cases: dict[str, Case] = {}
        self._invoice_ids: dict[str, str] = {}
        self._lock = RLock()

    def create(self, data: CaseInput) -> Case:
        with self._lock:
            invoice_id = data.invoice.invoice_id
            if invoice_id in self._invoice_ids:
                existing = self._cases[self._invoice_ids[invoice_id]]
                if existing.input != data:
                    raise ValueError("Invoice ID already exists with different content")
                return existing
            case = evaluate_case(data)
            self._cases[case.id] = case
            self._invoice_ids[invoice_id] = case.id
            return case

    def get(self, case_id: str) -> Case:
        with self._lock:
            if case_id not in self._cases:
                raise KeyError(case_id)
            return self._cases[case_id]

    def review(self, case_id: str, actor: str, approve: bool) -> Case:
        with self._lock:
            updated = decide(self.get(case_id), actor, approve)
            self._cases[case_id] = updated
            return updated

    def submit(self, case_id: str) -> Case:
        with self._lock:
            case = self.get(case_id)
            if case.state == State.submitted:
                return case
            if case.state not in (State.approved_by_rules, State.approved_by_human):
                raise InvalidTransition("Only approved cases can be submitted")
            updated = case.model_copy(update={"state": State.submitted, "erp_reference": f"MOCK-{case.id[:8]}", "version": case.version + 1})
            self._cases[case_id] = updated
            return updated
