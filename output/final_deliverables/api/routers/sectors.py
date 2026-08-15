import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_PATH = "nifty100.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("")
def get_sectors():
    conn = get_connection()

    rows = conn.execute("""
        SELECT
            s.broad_sector AS sector,
            COUNT(DISTINCT s.company_id) AS company_count,
            ROUND(AVG(c.roe_percentage), 2) AS median_roe
        FROM sectors s
        LEFT JOIN companies c
            ON c.id = s.company_id
        GROUP BY s.broad_sector
        ORDER BY s.broad_sector
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


@router.get("/{sector}/companies")
def get_sector_companies(sector: str):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            c.roe_percentage AS roe_pct,
            c.roce_percentage AS roce_pct
        FROM companies c
        JOIN sectors s
            ON c.id = s.company_id
        WHERE LOWER(s.broad_sector) = LOWER(?)
        ORDER BY c.company_name
    """,
        (sector,),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")

    return [dict(row) for row in rows]
