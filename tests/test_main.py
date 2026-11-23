from fastapi.testclient import TestClient

from app.main import APP_TITLE, app

client = TestClient(app)


def test_landing_page_renders():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert f"<h1>{APP_TITLE}</h1>" in response.text


def test_landing_page_has_sign_in_link_to_login():
    response = client.get("/")
    assert 'href="/login"' in response.text
    assert "Sign in</a>" in response.text


def test_login_placeholder_renders():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in" in response.text


def test_admin_placeholder_renders():
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Admin dashboard" in response.text


def test_static_stylesheet_served():
    response = client.get("/static/styles.css")
    assert response.status_code == 200


def test_healthz():
    assert client.get("/healthz").json() == {"status": "ok"}
