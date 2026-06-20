"""Tests for db_query — SQL injection and read-only guarantees."""

import os
import sqlite3
import tempfile
import pytest
from tools.db_query import query


@pytest.fixture
def test_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob')")
    conn.commit()
    conn.close()
    yield path
    try:
        os.unlink(path)
    except (OSError, PermissionError):
        pass


class TestDbQuery:
    def test_select_works(self, test_db):
        result = query(test_db, "SELECT * FROM users")
        assert result["ok"] is True
        assert result["count"] == 2

    def test_select_with_params(self, test_db):
        result = query(test_db, "SELECT * FROM users WHERE id = ?", [1])
        assert result["ok"] is True
        assert result["count"] == 1
        assert result["rows"][0]["name"] == "Alice"

    def test_blocks_drop_table(self, test_db):
        result = query(test_db, "DROP TABLE users")
        assert result["ok"] is False
        assert "SELECT" in result["error"] or "PRAGMA" in result["error"]

    def test_blocks_delete(self, test_db):
        result = query(test_db, "DELETE FROM users")
        assert result["ok"] is False

    def test_blocks_insert(self, test_db):
        result = query(test_db, "INSERT INTO users VALUES (3, 'Eve')")
        assert result["ok"] is False

    def test_parametrized_prevents_injection(self, test_db):
        result = query(test_db, "SELECT * FROM users WHERE name = ?", ["' OR 1=1--"])
        assert result["ok"] is True
        assert result["count"] == 0
