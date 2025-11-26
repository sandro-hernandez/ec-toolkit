# ec_toolkit/db/schema.py

import sqlite3

def init_db(conn):
    cur = conn.cursor()

    # Runs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time REAL,
            end_time REAL,
            config_json TEXT
        );
    """)

    # Samples (raw data)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            logger TEXT,
            timestamp REAL,
            key TEXT,
            value REAL,
            FOREIGN KEY(run_id) REFERENCES runs(id)
        );
    """)

    # Summary metrics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS summary_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            logger TEXT,
            timestamp REAL,
            key TEXT,
            value REAL,
            FOREIGN KEY(run_id) REFERENCES runs(id)
        );
    """)

    conn.commit()