"""SQLite-backed case store for a single-process demo. No external payments."""
import json
import os
import sqlite3
from threading import RLock
from .models import Case, CaseInput, State
from .workflow import evaluate_case, decide, InvalidTransition

class CaseService:
    def __init__(self, path: str | None = None):
        self.path = path if path is not None else os.getenv("PROOFFLOW_DB", "proofflow.db")
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = RLock()
        with self._db:
            self._db.execute("PRAGMA foreign_keys=ON")
            self._db.execute("CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY, invoice_id TEXT NOT NULL UNIQUE, payload TEXT NOT NULL)")
            self._db.execute("CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL, event TEXT NOT NULL, actor TEXT NOT NULL, version INTEGER NOT NULL, at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")

    def _get(self, id):
        row = self._db.execute("SELECT payload FROM cases WHERE id=?", (id,)).fetchone()
        if row is None:
            raise KeyError(id)
        return Case.model_validate_json(row["payload"])

    def _audit(self, case, event, actor):
        self._db.execute("INSERT INTO audit (case_id,event,actor,version) VALUES (?,?,?,?)", (case.id,event,actor,case.version))

    def _save(self, case):
        self._db.execute("UPDATE cases SET payload=? WHERE id=?", (case.model_dump_json(),case.id))

    def create(self, data: CaseInput, actor="operator") -> Case:
        with self._lock, self._db:
            row = self._db.execute("SELECT payload FROM cases WHERE invoice_id=?", (data.invoice.invoice_id,)).fetchone()
            if row:
                current = Case.model_validate_json(row["payload"])
                if current.input != data:
                    raise ValueError("Invoice ID already exists with different content")
                return current
            case = evaluate_case(data)
            self._db.execute("INSERT INTO cases (id,invoice_id,payload) VALUES (?,?,?)", (case.id,data.invoice.invoice_id,case.model_dump_json()))
            self._audit(case,"created",actor)
            return case

    def get(self, case_id: str) -> Case:
        with self._lock:
            return self._get(case_id)

    def list(self, limit=50):
        with self._lock:
            rows = self._db.execute("SELECT payload FROM cases ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
            return [Case.model_validate_json(r["payload"]) for r in rows]

    def history(self, case_id: str):
        with self._lock:
            self._get(case_id)
            rows = self._db.execute("SELECT seq,event,actor,version,at FROM audit WHERE case_id=? ORDER BY seq", (case_id,)).fetchall()
            return [dict(x) for x in rows]

    def review(self, case_id: str, actor: str, approve: bool) -> Case:
        with self._lock, self._db:
            updated = decide(self._get(case_id),actor,approve)
            self._save(updated)
            self._audit(updated,"approved" if approve else "rejected",actor)
            return updated

    def submit(self, case_id: str, actor="operator") -> Case:
        with self._lock, self._db:
            case = self._get(case_id)
            if case.state == State.submitted:
                return case
            if case.state not in (State.approved_by_rules, State.approved_by_human):
                raise InvalidTransition("Only approved cases can be submitted")
            updated = case.model_copy(update={"state":State.submitted,"erp_reference":f"MOCK-{case.id[:8]}","version":case.version+1})
            self._save(updated)
            self._audit(updated,"mock_erp_submitted",actor)
            return updated
