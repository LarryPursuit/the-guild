"""End-to-end API tests: auth, guild and quest CRUD, XP/ranks, rewards and error handling."""


# ---------- Auth ----------
def test_register_and_login(client):
    res = client.post("/api/auth/register", json={
        "username": "ada", "email": "ada@example.com", "password": "password123",
    })
    assert res.status_code == 201
    assert res.json()["user"]["rank"] == "Copper"

    res = client.post("/api/auth/login", json={"username": "ada", "password": "password123"})
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_duplicate_username_rejected(client):
    body = {"username": "ada", "email": "ada@example.com", "password": "password123"}
    client.post("/api/auth/register", json=body)
    res = client.post("/api/auth/register", json={**body, "email": "other@example.com"})
    assert res.status_code == 409


def test_bad_login_and_short_password(client):
    assert client.post("/api/auth/login", json={"username": "nobody", "password": "x"}).status_code == 401
    res = client.post("/api/auth/register", json={"username": "ada", "email": "a@b.co", "password": "short"})
    assert res.status_code == 422
    assert "Password" in res.json()["detail"]


def test_overlong_password_rejected_not_500(client):
    # bcrypt rejects passwords over 72 bytes; this must be a 422, not a crash.
    res = client.post("/api/auth/register", json={"username": "ada", "email": "a@b.co", "password": "é" * 40})
    assert res.status_code == 422
    assert "too long" in res.json()["detail"]


def test_routes_require_login(client):
    assert client.get("/api/guilds").status_code == 401
    client.headers["Authorization"] = "Bearer not-a-real-token"
    assert client.get("/api/guilds").status_code == 401


# ---------- Guilds ----------
def test_guild_crud(auth_client):
    res = auth_client.post("/api/guilds", json={"name": "Job Hunt Guild", "description": "Apps and interviews"})
    assert res.status_code == 201
    guild_id = res.json()["id"]

    assert len(auth_client.get("/api/guilds").json()) == 1
    res = auth_client.patch(f"/api/guilds/{guild_id}", json={"name": "Job Quest Guild"})
    assert res.json()["name"] == "Job Quest Guild"

    assert auth_client.delete(f"/api/guilds/{guild_id}").status_code == 204
    assert auth_client.get(f"/api/guilds/{guild_id}").status_code == 404


def test_cannot_see_other_users_guilds(auth_client, client):
    guild_id = auth_client.post("/api/guilds", json={"name": "Mine"}).json()["id"]
    res = client.post("/api/auth/register", json={
        "username": "mallory", "email": "m@example.com", "password": "password123",
    })
    other_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
    assert client.get(f"/api/guilds/{guild_id}", headers=other_headers).status_code == 404
    assert client.delete(f"/api/guilds/{guild_id}", headers=other_headers).status_code == 404


# ---------- Quests ----------
def make_quest(client, **overrides):
    guild_id = client.post("/api/guilds", json={"name": "Coursework"}).json()["id"]
    body = {"title": "Finish lab 3", "difficulty": "hard", "due_date": "2026-12-01", **overrides}
    res = client.post(f"/api/guilds/{guild_id}/quests", json=body)
    assert res.status_code == 201, res.text
    return guild_id, res.json()


def test_quest_crud(auth_client):
    guild_id, quest = make_quest(auth_client)
    res = auth_client.patch(f"/api/quests/{quest['id']}", json={"title": "Finish lab 4", "difficulty": "medium"})
    assert res.json()["title"] == "Finish lab 4"
    assert len(auth_client.get(f"/api/guilds/{guild_id}/quests").json()) == 1
    assert auth_client.delete(f"/api/quests/{quest['id']}").status_code == 204
    assert auth_client.get(f"/api/quests/{quest['id']}").status_code == 404


def test_invalid_difficulty_rejected(auth_client):
    guild_id = auth_client.post("/api/guilds", json={"name": "G"}).json()["id"]
    res = auth_client.post(f"/api/guilds/{guild_id}/quests", json={"title": "x", "difficulty": "legendary"})
    assert res.status_code == 422


def test_complete_quest_awards_xp_and_saves_reward(auth_client, fake_dnd):
    _, quest = make_quest(auth_client)
    res = auth_client.post(f"/api/quests/{quest['id']}/complete")
    assert res.status_code == 200
    data = res.json()
    assert data["xp_gained"] == 50
    assert data["user"]["xp"] == 50
    assert data["reward"]["item_name"] == "Longsword"
    assert data["reward_error"] is None

    inventory = auth_client.get("/api/rewards").json()
    assert inventory[0]["item_category"] == "Weapon"
    # Completing twice is an error, not double XP.
    assert auth_client.post(f"/api/quests/{quest['id']}/complete").status_code == 400


def test_rank_up(auth_client, fake_dnd):
    guild_id = auth_client.post("/api/guilds", json={"name": "Grind"}).json()["id"]
    ranked_up = False
    for i in range(2):
        q = auth_client.post(f"/api/guilds/{guild_id}/quests", json={"title": f"Q{i}", "difficulty": "hard"}).json()
        ranked_up = auth_client.post(f"/api/quests/{q['id']}/complete").json()["ranked_up"]
    assert ranked_up  # 100 XP reaches Silver
    assert auth_client.get("/api/users/me").json()["rank"] == "Silver"


def test_api_down_still_completes_quest_then_retry(auth_client, broken_dnd, monkeypatch):
    _, quest = make_quest(auth_client)
    res = auth_client.post(f"/api/quests/{quest['id']}/complete")
    assert res.status_code == 200
    data = res.json()
    assert data["quest"]["status"] == "completed"
    assert data["reward"] is None
    assert "took too long" in data["reward_error"]

    # Retry while still down -> 503 with a clear message.
    assert auth_client.post(f"/api/quests/{quest['id']}/reward").status_code == 503

    # API comes back -> retry succeeds once.
    from app import dnd_api
    from tests.conftest import FAKE_RESPONSES
    monkeypatch.setattr(dnd_api, "_get", lambda path: FAKE_RESPONSES[path])
    assert auth_client.post(f"/api/quests/{quest['id']}/reward").status_code == 201
    assert auth_client.post(f"/api/quests/{quest['id']}/reward").status_code == 409


def test_deleting_quest_keeps_reward(auth_client, fake_dnd):
    guild_id, quest = make_quest(auth_client)
    auth_client.post(f"/api/quests/{quest['id']}/complete")
    auth_client.delete(f"/api/guilds/{guild_id}")
    inventory = auth_client.get("/api/rewards").json()
    assert len(inventory) == 1
    assert inventory[0]["quest_id"] is None


# ---------- Classes ----------
def test_set_character_class(auth_client, fake_dnd):
    assert [c["index"] for c in auth_client.get("/api/classes").json()] == ["wizard", "rogue"]
    res = auth_client.patch("/api/users/me", json={"character_class": "wizard"})
    assert res.json()["character_class"] == "Wizard"
    assert auth_client.patch("/api/users/me", json={"character_class": "pirate"}).status_code == 400


def test_classes_api_down_returns_503(auth_client, broken_dnd):
    res = auth_client.get("/api/classes")
    assert res.status_code == 503
    assert "Try again" in res.json()["detail"]
