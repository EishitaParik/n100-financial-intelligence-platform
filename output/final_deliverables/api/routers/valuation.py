import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_PATH = "nifty100.db"


@router.get("/market-cap/{ticker}")
def market_cap_history(ticker: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            company_id,
            year,
            market_cap_crore,
            enterprise_value_crore,
            pe_ratio,
            pb_ratio,
            ev_ebitda,
            dividend_yield_pct
        FROM market_cap
        WHERE company_id = ?
        AND year BETWEEN 2019 AND 2024
        ORDER BY year
        """,
        (ticker.upper(),),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Market-cap data for '{ticker}' not found",
        )

    return {
        "ticker": ticker.upper(),
        "history": [dict(row) for row in rows],
    }


@router.get("/companies/{ticker}/peers/compare")
def compare_peers(ticker: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    company = conn.execute(
        """
        SELECT
            pg.peer_group_name,
            pg.company_id,
            pg.is_benchmark,
            fr.return_on_equity_pct,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            mc.pe_ratio,
            mc.pb_ratio
        FROM peer_groups pg
        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
        LEFT JOIN market_cap mc
            ON pg.company_id = mc.company_id
            AND mc.year = 2024
        WHERE pg.company_id = ?
        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
            WHERE company_id = ?
        )
        """,
        (ticker.upper(), ticker.upper()),
    ).fetchone()

    if not company:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Company '{ticker}' not found in peer groups",
        )

    peer_group = company["peer_group_name"]

    rows = conn.execute(
        """
        SELECT
            fr.return_on_equity_pct,
            fr.net_profit_margin_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            mc.pe_ratio,
            mc.pb_ratio
        FROM peer_groups pg
        JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
        LEFT JOIN market_cap mc
            ON pg.company_id = mc.company_id
            AND mc.year = 2024
        WHERE pg.peer_group_name = ?
        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
            WHERE company_id = pg.company_id
        )
        """,
        (peer_group,),
    ).fetchall()

    conn.close()

    metrics = [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "pe_ratio",
        "pb_ratio",
    ]

    averages = {}

    for metric in metrics:
        values = [row[metric] for row in rows if row[metric] is not None]

        averages[metric] = sum(values) / len(values) if values else None

    return {
        "ticker": ticker.upper(),
        "peer_group": peer_group,
        "company": dict(company),
        "peer_average": averages,
    }
