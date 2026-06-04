"""SQLite-backed persistence for diagnosis results."""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional

from nurse_agents.core.models import DiagnosisResponse

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS diagnoses (
    project_id    TEXT PRIMARY KEY,
    project_name  TEXT NOT NULL,
    data          TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
)
"""


class DiagnosisRepository:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        # For :memory: keep one shared connection so the table persists across calls
        if db_path == ":memory:":
            self._shared_conn: Optional[sqlite3.Connection] = sqlite3.connect(
                ":memory:", check_same_thread=False
            )
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute(_CREATE_TABLE)
            self._shared_conn.commit()
        else:
            self._shared_conn = None
            self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(_CREATE_TABLE)

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        if self._shared_conn is not None:
            yield self._shared_conn
            self._shared_conn.commit()
            return
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def save(self, project_id: str, project_name: str, result: DiagnosisResponse) -> None:
        data = result.model_dump_json()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO diagnoses (project_id, project_name, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    project_name,
                    data,
                    result.created_at.isoformat(),
                    result.updated_at.isoformat(),
                ),
            )

    def get(self, project_id: str) -> Optional[tuple[str, DiagnosisResponse]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT project_name, data FROM diagnoses WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return row["project_name"], DiagnosisResponse.model_validate_json(row["data"])

    def list_all(
        self, limit: int = 20, offset: int = 0
    ) -> tuple[list[tuple[str, str, DiagnosisResponse]], int]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM diagnoses").fetchone()[0]
            rows = conn.execute(
                "SELECT project_id, project_name, data FROM diagnoses ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        items = [
            (row["project_id"], row["project_name"], DiagnosisResponse.model_validate_json(row["data"]))
            for row in rows
        ]
        return items, total

    def delete(self, project_id: str) -> bool:
        with self._conn() as conn:
            cursor = conn.execute(
                "DELETE FROM diagnoses WHERE project_id = ?", (project_id,)
            )
        return cursor.rowcount > 0

    def update(self, project_id: str, result: DiagnosisResponse) -> bool:
        data = result.model_dump_json()
        with self._conn() as conn:
            cursor = conn.execute(
                "UPDATE diagnoses SET data = ?, updated_at = ? WHERE project_id = ?",
                (data, result.updated_at.isoformat(), project_id),
            )
        return cursor.rowcount > 0
