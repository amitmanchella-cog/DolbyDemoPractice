import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app import auth

BASE_DIR = Path(__file__).resolve().parent

APP_TITLE = "Admin Portal"
APP_DESCRIPTION = "Manage the demo environment. Admins sign in to access the dashboard."
INVALID_CREDENTIALS = "Invalid username or password"
SESSION_COOKIE = "admin_portal_session"
SESSION_USER_KEY = "username"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    auth.init_db()
    yield


app = FastAPI(title=APP_TITLE, lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("ADMIN_PORTAL_SECRET_KEY") or secrets.token_urlsafe(32),
    session_cookie=SESSION_COOKIE,
    same_site="lax",
    https_only=os.environ.get("ADMIN_PORTAL_HTTPS_ONLY") == "1",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def render(request: Request, template: str, status_code: int = 200, **context) -> HTMLResponse:
    return templates.TemplateResponse(
        request, template, {"app_title": APP_TITLE, **context}, status_code=status_code
    )


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


def current_user(request: Request) -> auth.User | None:
    username = request.session.get(SESSION_USER_KEY)
    return auth.get_user(username) if username else None


@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    return render(request, "index.html", description=APP_DESCRIPTION)


@app.get("/login", response_class=HTMLResponse, response_model=None)
def login_form(request: Request) -> HTMLResponse | RedirectResponse:
    if current_user(request):
        return redirect("/admin")
    return render(request, "login.html")


@app.post("/login", response_class=HTMLResponse, response_model=None)
def login(
    request: Request,
    username: Annotated[str, Form()] = "",
    password: Annotated[str, Form()] = "",
) -> HTMLResponse | RedirectResponse:
    user = auth.authenticate(username.strip(), password)
    if user is None:
        return render(
            request,
            "login.html",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error=INVALID_CREDENTIALS,
            username=username,
        )
    request.session.clear()
    request.session[SESSION_USER_KEY] = user.username
    return redirect("/admin")


@app.post("/logout")
def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    return redirect("/login")


@app.get("/admin", response_class=HTMLResponse, response_model=None)
def admin(request: Request) -> HTMLResponse | RedirectResponse:
    user = current_user(request)
    if user is None:
        request.session.clear()
        return redirect("/login")
    response = render(request, "admin.html", username=user.username)
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
