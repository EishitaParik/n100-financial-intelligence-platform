import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

DB_PATH = "nifty100.db"


def get_connection():
    """Return a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dict(rows):
    """Convert SQLite rows to dictionaries."""
    return [dict(row) for row in rows]


@router.get("/")
def get_companies(
    sector: str | None = None,
    market_cap_category: str | None = None,
    search: str | None = None,
):
    """Return all companies with optional filters."""

    conn = get_connection()

    query = """
        SELECT
            c.id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            c.roe_percentage AS roe_pct,
            c.roce_percentage AS roce_pct
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE 1 = 1
    """

    params = []

    if sector:
        query += """
            AND LOWER(s.broad_sector) = LOWER(?)
        """
        params.append(sector)

    if market_cap_category:
        query += """
            AND LOWER(s.market_cap_category) = LOWER(?)
        """
        params.append(market_cap_category)

    if search:
        query += """
            AND (
                LOWER(c.id) LIKE LOWER(?)
                OR LOWER(c.company_name) LIKE LOWER(?)
            )
        """
        search_value = f"%{search}%"
        params.extend([search_value, search_value])

    query += " ORDER BY c.id"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return rows_to_dict(rows)


@router.get("/{ticker}")
def get_company(ticker: str):
    """Return complete company profile."""

    conn = get_connection()

    company = conn.execute(
        """
        SELECT *
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    if company is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    sector = conn.execute(
        """
        SELECT *
        FROM sectors
        WHERE company_id = ?
        """,
        (company["id"],),
    ).fetchall()

    latest_kpis = conn.execute(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 1
        """,
        (company["id"],),
    ).fetchone()

    conn.close()

    return {
        **dict(company),
        "sector": rows_to_dict(sector),
        "latest_kpis": dict(latest_kpis) if latest_kpis else None,
    }


@router.get("/{ticker}/pl")
def get_profit_loss(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return profit and loss history."""

    conn = get_connection()

    exists = conn.execute(
        """
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    query = """
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
    """

    params = [exists["id"]]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "ticker": exists["id"],
        "history": rows_to_dict(rows),
    }


@router.get("/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return balance sheet history."""

    conn = get_connection()

    exists = conn.execute(
        """
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    query = """
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
    """

    params = [exists["id"]]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "ticker": exists["id"],
        "history": rows_to_dict(rows),
    }


@router.get("/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: str | None = None,
    to_year: str | None = None,
):
    """Return cash flow history."""

    conn = get_connection()

    exists = conn.execute(
        """
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    query = """
        SELECT *
        FROM cashflow
        WHERE company_id = ?
    """

    params = [exists["id"]]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year)

    if to_year:
        query += " AND year <= ?"
        params.append(to_year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "ticker": exists["id"],
        "history": rows_to_dict(rows),
    }


@router.get("/{ticker}/ratios")
def get_ratios(
    ticker: str,
    year: int | None = None,
):
    """Return calculated financial ratios."""

    conn = get_connection()

    exists = conn.execute(
        """
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    if exists is None:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    query = """
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
    """

    params = [exists["id"]]

    if year is not None:
        query += " AND year = ?"
        params.append(year)

    query += " ORDER BY year"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return {
        "ticker": exists["id"],
        "ratios": rows_to_dict(rows),
    }


@router.get("/{ticker}/tearsheet")
def get_tearsheet(ticker: str):
    """Return the company's tearsheet PDF."""

    conn = get_connection()

    company = conn.execute(
        """
        SELECT id
        FROM companies
        WHERE UPPER(id) = UPPER(?)
        """,
        (ticker,),
    ).fetchone()

    conn.close()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found",
        )

    pdf_path = Path(f"reports/tearsheets/{company['id']}_tearsheet.pdf")

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Tearsheet not found for '{company['id']}'",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )
