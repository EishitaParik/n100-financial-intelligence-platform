import sqlite3
import time

from fastapi import APIRouter

router = APIRouter()

DB_PATH = "nifty100.db"
START_TIME = time.time()


@router.get("/health")
def health():

    conn = sqlite3.connect(DB_PATH)

    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """).fetchall()

    row_counts = {}

    for table in tables:
        table_name = table[0]

        row_counts[table_name] = conn.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

    conn.close()

    return {
        "status": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
    }
