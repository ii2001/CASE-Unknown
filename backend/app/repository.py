import sqlite3
from pathlib import Path

from .models import CanonicalCase, PlayerState


class CaseRepository:
    def __init__(self, path: str):
        self.path = path.removeprefix("sqlite:///")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS games (id TEXT PRIMARY KEY, case_json TEXT NOT NULL, player_json TEXT NOT NULL, event TEXT NOT NULL DEFAULT '')")

    def connect(self):
        return sqlite3.connect(self.path)

    def save(self, case: CanonicalCase, player: PlayerState, event: str = "") -> None:
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO games VALUES (?, ?, ?, ?)", (case.id, case.model_dump_json(), player.model_dump_json(), event))

    def load(self, case_id: str) -> tuple[CanonicalCase, PlayerState]:
        with self.connect() as db:
            row = db.execute("SELECT case_json, player_json FROM games WHERE id=?", (case_id,)).fetchone()
        if not row:
            raise KeyError(case_id)
        return CanonicalCase.model_validate_json(row[0]), PlayerState.model_validate_json(row[1])

    def latest_id(self) -> str | None:
        with self.connect() as db:
            row = db.execute("SELECT id FROM games ORDER BY rowid DESC LIMIT 1").fetchone()
        return row[0] if row else None

    def event(self, case_id: str) -> str:
        with self.connect() as db:
            row = db.execute("SELECT event FROM games WHERE id=?", (case_id,)).fetchone()
        return row[0] if row else ""
