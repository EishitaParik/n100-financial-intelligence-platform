import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_PATH = "nifty100.db"


@router.get("/{group_name}")
def get_peers(group_name: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            pg.company_id,
            pg.peer_group_name,
            pg.is_benchmark,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            fr.earnings_per_share
        FROM peer_groups pg
        LEFT JOIN sectors s
            ON pg.company_id = s.company_id
        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
        WHERE pg.peer_group_name = ?
        AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios
            WHERE company_id = pg.company_id
        )
        """,
        (group_name,),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Peer group '{group_name}' not found",
        )

    return {
        "peer_group": group_name,
        "count": len(rows),
        "companies": [dict(row) for row in rows],
    }
