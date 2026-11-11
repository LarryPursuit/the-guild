"""Test setup: a fresh SQLite database per test and a fake D&D 5e API (no network)."""
import os
import sys
from pathlib import Path

import pytest

TEST_DB = Path(__file__).parent / "test_guild.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

from app import dnd_api  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

FAKE_RESPONSES = {
    "/classes": {"count": 2, "results": [
        {"index": "wizard", "name": "Wizard", "url": "/api/2014/classes/wizard"},
        {"index": "rogue", "name": "Rogue", "url": "/api/2014/classes/rogue"},
    ]},
    "/equipment": {"count": 1, "results": [
        {"index": "longsword", "name": "Longsword", "url": "/api/2014/equipment/longsword"},
    ]},
    "/equipment/longsword": {
        "index": "longsword",
        "name": "Longsword",
        "equipment_category": {"index": "weapon", "name": "Weapon"},
        "cost": {"quantity": 15, "unit": "gp"},
    },
}


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    dnd_api.clear_cache()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def fake_dnd(monkeypatch):
    """Replace real HTTP calls with canned responses."""
    monkeypatch.setattr(dnd_api, "_get", lambda path: FAKE_RESPONSES[path])


@pytest.fixture
def broken_dnd(monkeypatch):
    """Simulate the D&D 5e API being down."""
    def fail(path):
        raise dnd_api.DndApiError("The D&D 5e API took too long to respond.")
    monkeypatch.setattr(dnd_api, "_get", fail)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    """A client logged in as a new user."""
    res = client.post("/api/auth/register", json={
        "username": "larry", "email": "larry@example.com", "password": "password123",
    })
    assert res.status_code == 201, res.text
    client.headers["Authorization"] = f"Bearer {res.json()['access_token']}"
    return client


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)
