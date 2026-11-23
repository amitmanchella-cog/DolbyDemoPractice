import sqlite3

import pytest

from app import auth
from app.main import INVALID_CREDENTIALS, SESSION_COOKIE

USERNAME = "admin"
PASSWORD = "correct-horse"


@pytest.fixture
def user():
    auth.create_user(USERNAME, PASSWORD)


def sign_in(client, username=USERNAME, password=PASSWORD):
    return client.post(
        "/login", data={"username": username, "password": password}, follow_redirects=False
    )


def test_login_page_has_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert 'name="username"' in response.text
    assert 'name="password"' in response.text
    assert 'type="password"' in response.text
    assert ">Sign in</button>" in response.text
    assert INVALID_CREDENTIALS not in response.text


def test_login_success_sets_session_and_redirects_to_admin(client, user):
    response = sign_in(client)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    assert SESSION_COOKIE in response.cookies

    admin = client.get("/admin")
    assert admin.status_code == 200
    assert f"Welcome, {USERNAME}" in admin.text
    assert ">Log out</button>" in admin.text
    assert admin.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    ("username", "password"),
    [(USERNAME, "wrong"), ("nobody", PASSWORD), ("", ""), (USERNAME, "")],
)
def test_login_failure_shows_error_and_stays_on_login(client, user, username, password):
    response = sign_in(client, username, password)
    assert response.status_code == 401
    assert "location" not in response.headers
    assert INVALID_CREDENTIALS in response.text
    assert 'action="/login"' in response.text
    assert SESSION_COOKIE not in response.cookies
    assert client.get("/admin", follow_redirects=False).headers["location"] == "/login"


def test_login_failure_keeps_username_but_not_password(client, user):
    response = sign_in(client, USERNAME, "wrong-password")
    assert f'value="{USERNAME}"' in response.text
    assert "wrong-password" not in response.text


def test_admin_redirects_to_login_without_session(client):
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_admin_redirect_lands_on_login_page(client):
    response = client.get("/admin")
    assert response.url.path == "/login"
    assert ">Sign in</button>" in response.text


def test_admin_rejects_forged_session_cookie(client, user):
    client.cookies.set(SESSION_COOKIE, "forged-value")
    response = client.get("/admin", follow_redirects=False)
    assert response.headers["location"] == "/login"


def test_admin_redirects_when_session_user_no_longer_exists(client, isolated_db, user):
    sign_in(client)
    with sqlite3.connect(isolated_db) as conn:
        conn.execute("DELETE FROM users")
    response = client.get("/admin", follow_redirects=False)
    assert response.headers["location"] == "/login"


def test_login_page_redirects_signed_in_user_to_admin(client, user):
    sign_in(client)
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"


def test_logout_clears_session_and_returns_to_login(client, user):
    sign_in(client)
    assert client.get("/admin", follow_redirects=False).status_code == 200

    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    assert client.get("/admin", follow_redirects=False).headers["location"] == "/login"
