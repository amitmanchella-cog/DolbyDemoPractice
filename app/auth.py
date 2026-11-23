"""Admin user storage and password hashing.

Users live in SQLite at ``$ADMIN_PORTAL_DB`` (default ``admin_portal.db``).
Passwords are stored as salted PBKDF2-SHA256 hashes, never in plaintext.
"""

import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import closing
from dataclasses import dataclass

DEFAULT_DB_PATH = "admin_portal.db"
HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 600_000


@dataclass(frozen=True)
class User:
    username: str
    password_hash: str


def db_path() -> str:
    return os.environ.get("ADMIN_PORTAL_DB", DEFAULT_DB_PATH)


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(db_path())


def init_db() -> None:
    with closing(_connect()) as conn, conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "username TEXT PRIMARY KEY, password_hash TEXT NOT NULL)"
        )


def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), HASH_ITERATIONS)
    return f"{HASH_ALGORITHM}${HASH_ITERATIONS}${salt}${digest.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        algorithm, iterations, salt, expected = hashed.split("$")
        rounds = int(iterations)
    except ValueError:
        return False
    if algorithm != HASH_ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), rounds)
    return hmac.compare_digest(digest.hex(), expected)


def create_user(username: str, password: str) -> None:
    """Create a user; does nothing if the username already exists."""
    init_db()
    with closing(_connect()) as conn, conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password)),
        )


def get_user(username: str) -> User | None:
    init_db()
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT username, password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    return User(*row) if row else None


def authenticate(username: str, password: str) -> User | None:
    user = get_user(username)
    if user is None:
        # Hash anyway so unknown usernames take as long as wrong passwords.
        verify_password(password, _DUMMY_HASH)
        return None
    return user if verify_password(password, user.password_hash) else None


_DUMMY_HASH = hash_password(secrets.token_hex(16))
