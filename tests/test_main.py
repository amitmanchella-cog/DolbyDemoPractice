from app.main import APP_TITLE


def test_landing_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert f"<h1>{APP_TITLE}</h1>" in response.text


def test_landing_page_has_sign_in_link_to_login(client):
    response = client.get("/")
    assert 'href="/login"' in response.text
    assert "Sign in</a>" in response.text


def test_static_stylesheet_served(client):
    response = client.get("/static/styles.css")
    assert response.status_code == 200


def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}
