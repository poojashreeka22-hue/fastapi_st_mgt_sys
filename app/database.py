import os
import sqlite3
from typing import Optional

DEFAULT_DB_PATH = os.environ.get("STUDENT_DB_PATH", "students.db")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path if db_path is not None else DEFAULT_DB_PATH
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL
        )
        """
    )
    conn.commit()
