import sqlite3

from app import auth


def test_hash_password_is_salted_and_not_plaintext():
    first = auth.hash_password("s3cret!")
    second = auth.hash_password("s3cret!")
    assert "s3cret!" not in first
    assert first != second


def test_verify_password():
    hashed = auth.hash_password("s3cret!")
    assert auth.verify_password("s3cret!", hashed)
    assert not auth.verify_password("wrong", hashed)


def test_verify_password_rejects_malformed_hash():
    assert not auth.verify_password("s3cret!", "s3cret!")
    assert not auth.verify_password("s3cret!", "md5$1$salt$abc")


def test_create_and_get_user(isolated_db):
    auth.create_user("alice", "s3cret!")
    user = auth.get_user("alice")
    assert user is not None
    assert user.username == "alice"
    assert auth.verify_password("s3cret!", user.password_hash)

    stored = sqlite3.connect(isolated_db).execute("SELECT password_hash FROM users").fetchone()[0]
    assert "s3cret!" not in stored


def test_create_user_is_idempotent():
    auth.create_user("alice", "first")
    auth.create_user("alice", "second")
    user = auth.get_user("alice")
    assert auth.verify_password("first", user.password_hash)
    assert not auth.verify_password("second", user.password_hash)


def test_get_unknown_user_returns_none():
    assert auth.get_user("nobody") is None


def test_users_table_created_on_startup(client, isolated_db):
    columns = sqlite3.connect(isolated_db).execute("PRAGMA table_info(users)").fetchall()
    assert [(c[1], c[2], c[3], c[5]) for c in columns] == [
        ("username", "TEXT", 0, 1),
        ("password_hash", "TEXT", 1, 0),
    ]


def test_authenticate():
    auth.create_user("alice", "s3cret!")
    assert auth.authenticate("alice", "s3cret!").username == "alice"
    assert auth.authenticate("alice", "wrong") is None
    assert auth.authenticate("nobody", "s3cret!") is None
