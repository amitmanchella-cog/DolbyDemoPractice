# Admin Portal demo

Small web app with a landing page, admin login, and a demo sign-in.
Tracked in Jira epic MBA-3912 (stories MBA-3913, MBA-3914, MBA-3915).

Built with [FastAPI](https://fastapi.tiangolo.com/) and Jinja2 templates.

## Run locally

Requires Python 3.12+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000. (`make install` and `make run` do the same.)

## Routes

| Route      | Description                                                  |
|------------|--------------------------------------------------------------|
| `/`        | Landing page with app title, description and **Sign in**     |
| `/login`   | Placeholder sign-in page (real login form in MBA-3914)       |
| `/admin`   | Placeholder protected admin page (auth wired up in MBA-3914/MBA-3915) |
| `/healthz` | Health check                                                 |

## Lint and test

```bash
ruff check . && ruff format --check .
pytest
```

CI runs the same checks on every pull request (`.github/workflows/ci.yml`).

## Project layout

```
app/
  main.py          # FastAPI app and routes
  templates/       # Jinja2 templates (base.html + one per page)
  static/          # CSS
tests/             # pytest tests
```

## Run locally

```bash
make install
make run   # http://localhost:8000
```

## Admin login (MBA-3914)

- `/login` checks credentials against salted PBKDF2-SHA256 hashes (`app/auth.py`); no plaintext passwords are stored.
- On success a signed session cookie is set and the user is redirected to `/admin`; `/admin` redirects to `/login` without a session. **Log out** clears the session.
- Users are stored in SQLite; the `users` table is created on app startup. No users are seeded here (see MBA-3915). Create one with:
  `python -c "from app.auth import create_user; create_user('admin', 'change-me')"`

| Env var | Default | Purpose |
| --- | --- | --- |
| `ADMIN_PORTAL_DB` | `admin_portal.db` | SQLite database path |
| `ADMIN_PORTAL_SECRET_KEY` | random per process | Session cookie signing key (set it so sessions survive restarts) |
| `ADMIN_PORTAL_HTTPS_ONLY` | unset | Set to `1` to mark the session cookie `Secure` |
