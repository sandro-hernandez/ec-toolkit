# ec_toolkit/db/connection.py

import sqlite3
from pathlib import Path


def get_connection(db_path) -> sqlite3.Connection:
    """
    Create a SQLite connection ensuring the parent directory exists.
    """
    db_path = Path(db_path)
    if db_path.parent:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    return conn
