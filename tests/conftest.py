import os
os.environ["STUDENT_DB_PATH"] = ":memory:"

import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app, get_db


@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def client(db_conn):
    def override_get_db():
        try:
            yield db_conn
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
