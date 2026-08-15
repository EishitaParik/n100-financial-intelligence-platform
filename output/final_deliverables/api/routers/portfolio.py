import sqlite3

import pandas as pd
from fastapi import APIRouter

router = APIRouter()

DB_PATH = "nifty100.db"


@router.get("/stats")
def portfolio_stats():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT
            return_on_equity_pct,
            debt_to_equity,
            operating_profit_margin_pct,
            free_cash_flow_cr,
            interest_coverage,
            asset_turnover,
            net_profit_margin_pct,
            earnings_per_share,
            dividend_payout_ratio_pct,
            cash_from_operations_cr
        FROM financial_ratios
    """,
        conn,
    )

    conn.close()

    metrics = list(df.columns)

    result = []

    for metric in metrics:
        s = pd.to_numeric(df[metric], errors="coerce").dropna()

        result.append(
            {
                "metric": metric,
                "p10": round(s.quantile(0.10), 2),
                "p25": round(s.quantile(0.25), 2),
                "p50": round(s.quantile(0.50), 2),
                "p75": round(s.quantile(0.75), 2),
                "p90": round(s.quantile(0.90), 2),
                "mean": round(s.mean(), 2),
                "std": round(s.std(), 2),
            }
        )

    return result
