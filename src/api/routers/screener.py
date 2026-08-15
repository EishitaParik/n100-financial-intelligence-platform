import re
import sqlite3

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

DB_PATH = "nifty100.db"


def get_connection():
    """Create a SQLite database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def extract_cagr(value, period):
    """Extract a CAGR percentage for the requested period."""
    if value is None:
        return None

    text = str(value)

    pattern = rf"{period}\s*Years?\s*:\s*(-?\d+(?:\.\d+)?)%"
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return None


@router.get("")
def screener(
    min_roe: str | None = Query(None),
    max_de: str | None = Query(None),
    min_fcf: str | None = Query(None),
    sector: str | None = Query(None),
    min_rev_cagr_5yr: str | None = Query(None),
    min_pat_cagr_5yr: str | None = Query(None),
    max_pe: str | None = Query(None),
):
    """Return ranked companies matching screener filters."""

    # ---------------------------------------------------------
    # Validate and convert numeric parameters
    # ---------------------------------------------------------

    try:
        min_roe = float(min_roe) if min_roe is not None else None
        max_de = float(max_de) if max_de is not None else None
        min_fcf = float(min_fcf) if min_fcf is not None else None

        min_rev_cagr_5yr = (
            float(min_rev_cagr_5yr) if min_rev_cagr_5yr is not None else None
        )

        min_pat_cagr_5yr = (
            float(min_pat_cagr_5yr) if min_pat_cagr_5yr is not None else None
        )

        max_pe = float(max_pe) if max_pe is not None else None

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid numeric parameter",
        ) from exc

    # ---------------------------------------------------------
    # Range validation
    # ---------------------------------------------------------

    if min_roe is not None and min_roe < -100:
        raise HTTPException(
            status_code=400,
            detail="Invalid min_roe",
        )

    if max_de is not None and max_de < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid max_de",
        )

    if min_rev_cagr_5yr is not None and min_rev_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="Invalid min_rev_cagr_5yr",
        )

    if min_pat_cagr_5yr is not None and min_pat_cagr_5yr < -100:
        raise HTTPException(
            status_code=400,
            detail="Invalid min_pat_cagr_5yr",
        )

    if max_pe is not None and max_pe < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid max_pe",
        )

    # ---------------------------------------------------------
    # Database connection
    # ---------------------------------------------------------

    conn = get_connection()

    # ---------------------------------------------------------
    # Base query
    # ---------------------------------------------------------

    query = """
        SELECT
            fr.company_id,
            c.company_name,
            s.broad_sector,
            s.sub_sector,
            fr.year,

            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,

            mc.pe_ratio,
            mc.pb_ratio,
            mc.ev_ebitda,
            mc.dividend_yield_pct,

            a.compounded_sales_growth,
            a.compounded_profit_growth

        FROM financial_ratios fr

        JOIN companies c
            ON c.id = fr.company_id

        LEFT JOIN sectors s
            ON s.company_id = fr.company_id

        LEFT JOIN market_cap mc
            ON mc.company_id = fr.company_id
            AND mc.year = fr.year

        LEFT JOIN analysis a
            ON a.company_id = fr.company_id

        WHERE 1 = 1
    """

    params = []

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    if min_roe is not None:
        query += """
            AND fr.return_on_equity_pct >= ?
        """
        params.append(min_roe)

    if max_de is not None:
        query += """
            AND (
                fr.debt_to_equity <= ?
                OR LOWER(s.broad_sector) = 'financials'
            )
        """
        params.append(max_de)

    if min_fcf is not None:
        query += """
            AND fr.free_cash_flow_cr >= ?
        """
        params.append(min_fcf)

    if sector:
        query += """
            AND LOWER(s.broad_sector) = LOWER(?)
        """
        params.append(sector)

    if max_pe is not None:
        query += """
            AND mc.pe_ratio <= ?
        """
        params.append(max_pe)

    # ---------------------------------------------------------
    # Execute query
    # ---------------------------------------------------------

    rows = conn.execute(query, params).fetchall()

    conn.close()

    # ---------------------------------------------------------
    # Convert rows and apply CAGR filters
    # ---------------------------------------------------------

    results = []

    for row in rows:
        item = dict(row)

        sales_cagr = extract_cagr(
            item.get("compounded_sales_growth"),
            5,
        )

        profit_cagr = extract_cagr(
            item.get("compounded_profit_growth"),
            5,
        )

        item["sales_cagr_5yr"] = sales_cagr
        item["profit_cagr_5yr"] = profit_cagr

        if min_rev_cagr_5yr is not None and (
            sales_cagr is None or sales_cagr < min_rev_cagr_5yr
        ):
            continue

        if min_pat_cagr_5yr is not None and (
            profit_cagr is None or profit_cagr < min_pat_cagr_5yr
        ):
            continue

        results.append(item)

    # ---------------------------------------------------------
    # Ranking
    # ---------------------------------------------------------

    results.sort(
        key=lambda x: (
            x["return_on_equity_pct"] is not None,
            x["return_on_equity_pct"] or 0,
            x["free_cash_flow_cr"] or 0,
        ),
        reverse=True,
    )

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return {
        "count": len(results),
        "results": results,
    }
