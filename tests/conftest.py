import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    db = tmp_path / "admin_portal.db"
    monkeypatch.setenv("ADMIN_PORTAL_DB", str(db))
    return db


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
