from app import auth
from app.seed import DEMO_PASSWORD, DEMO_USERNAME, seed_demo_user


def test_seed_creates_demo_user():
    assert auth.get_user(DEMO_USERNAME) is None
    assert seed_demo_user() is True
    assert auth.authenticate(DEMO_USERNAME, DEMO_PASSWORD) is not None


def test_seed_is_idempotent():
    seed_demo_user()
    first_hash = auth.get_user(DEMO_USERNAME).password_hash
    assert seed_demo_user() is False
    assert auth.get_user(DEMO_USERNAME).password_hash == first_hash


def test_seeded_demo_user_signs_in_and_logs_out(client):
    seed_demo_user()

    response = client.post("/login", data={"username": DEMO_USERNAME, "password": DEMO_PASSWORD})
    assert response.status_code == 200
    assert response.url.path == "/admin"
    assert f"Welcome, {DEMO_USERNAME}" in response.text
    assert 'action="/logout"' in response.text

    response = client.post("/logout")
    assert response.status_code == 200
    assert response.url.path == "/login"
    assert client.get("/admin").url.path == "/login"


def test_demo_user_rejects_wrong_password(client):
    seed_demo_user()
    response = client.post("/login", data={"username": DEMO_USERNAME, "password": "wrong"})
    assert response.status_code == 401
    assert f"Welcome, {DEMO_USERNAME}" not in response.text
