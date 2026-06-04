"""Test configuration — use in-memory SQLite so tests are isolated and fast."""

import os

os.environ.setdefault("DB_PATH", ":memory:")

import pytest

import nurse_agents.api.diagnosis as _diag_module
from nurse_agents.storage.sqlite_repository import DiagnosisRepository


@pytest.fixture(autouse=True)
def fresh_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the module-level repository with a fresh in-memory instance per test."""
    monkeypatch.setattr(_diag_module, "_repo", DiagnosisRepository(":memory:"))
