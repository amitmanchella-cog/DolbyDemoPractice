"""Seed the fake demo admin user. DEMO ONLY — these are not real credentials.

Run with ``python -m app.seed`` (or ``make seed``). Safe to run repeatedly.
"""

from app.auth import create_user, get_user

# DEMO ONLY: fake sample login for local demos. Never use real credentials here.
DEMO_USERNAME = "demo.admin"
DEMO_PASSWORD = "DemoPass!2026"


def seed_demo_user() -> bool:
    """Create the demo user if missing. Returns True if it was created."""
    existed = get_user(DEMO_USERNAME) is not None
    create_user(DEMO_USERNAME, DEMO_PASSWORD)
    return not existed


def main() -> None:
    created = seed_demo_user()
    status = "created" if created else "already exists"
    print(f"Demo user '{DEMO_USERNAME}' {status} (demo only, not a real account).")


if __name__ == "__main__":
    main()
