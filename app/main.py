from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent

APP_TITLE = "Admin Portal"
APP_DESCRIPTION = "Manage the demo environment. Admins sign in to access the dashboard."

app = FastAPI(title=APP_TITLE)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def render(request: Request, template: str, **context) -> HTMLResponse:
    return templates.TemplateResponse(request, template, {"app_title": APP_TITLE, **context})


@app.get("/", response_class=HTMLResponse)
def landing(request: Request) -> HTMLResponse:
    return render(request, "index.html", description=APP_DESCRIPTION)


@app.get("/login", response_class=HTMLResponse)
def login(request: Request) -> HTMLResponse:
    # Placeholder; the real login form is implemented in MBA-3914.
    return render(request, "login.html")


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request) -> HTMLResponse:
    # Placeholder protected route; authentication is wired up in MBA-3914/MBA-3915.
    return render(request, "admin.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
