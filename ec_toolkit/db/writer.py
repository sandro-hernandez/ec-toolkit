# ec_toolkit/db/writer.py

import json
import time
from pathlib import Path
from typing import List, Tuple

from .connection import get_connection
from .schema import init_db


class DBWriter:
    """
    Small helper around SQLite for EC Toolkit.
    """

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = get_connection(self.db_path)
        init_db(self.conn)

    # --- Run lifecycle -----------------------------------------------------

    def create_run(self, config: dict) -> int:
        """
        Insert a new run row and return its ID.
        """
        cur = self.conn.cursor() # type: ignore
        start_time = time.time()
        cur.execute(
            "INSERT INTO runs (start_time, config_json) VALUES (?, ?)",
            (start_time, json.dumps(config)),
        )
        self.conn.commit() # type: ignore
        return cur.lastrowid # type: ignore

    def finalize_run(self, run_id: int) -> None:
        """
        Set end_time for the run and keep connection open (caller can close later).
        """
        cur = self.conn.cursor() # type: ignore
        end_time = time.time()
        cur.execute(
            "UPDATE runs SET end_time = ? WHERE id = ?",
            (end_time, run_id),
        )
        self.conn.commit() # type: ignore

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None

    def insert_samples(self, run_id, logger, samples):
        if not samples:
            return

        rows = []

        for (ts, val) in samples:
            # Per-core list
            if isinstance(val, list):
                for i, v in enumerate(val):
                    rows.append((run_id, logger, ts, str(i), float(v)))

            # Dict metrics (cpu_total)
            elif isinstance(val, dict):
                for k, v in val.items():
                    rows.append((run_id, logger, ts, str(k), float(v)))

            # Scalar metrics
            else:
                rows.append((run_id, logger, ts, None, float(val)))

        cur = self.conn.cursor() # type: ignore
        cur.executemany(
            """
            INSERT INTO samples (run_id, logger, timestamp, key, value)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit() # type: ignore


    def insert_summary_metrics(self, run_id, logger, summary):
        if not summary:
            return

        rows = []

        for (ts, val) in summary:
            # Per-core list
            if isinstance(val, list):
                for i, v in enumerate(val):
                    rows.append((run_id, logger, ts, str(i), float(v)))

            # Dict metrics (cpu_total)
            elif isinstance(val, dict):
                for k, v in val.items():
                    rows.append((run_id, logger, ts, str(k), float(v)))

            # Scalar metrics
            else:
                rows.append((run_id, logger, ts, None, float(val)))

        cur = self.conn.cursor() # type: ignore
        cur.executemany(
            """
            INSERT INTO summary_metrics (run_id, logger, timestamp, key, value)
            VALUES (?, ?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit() # type: ignore
