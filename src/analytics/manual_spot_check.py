import sqlite3

import pandas as pd

conn = sqlite3.connect("nifty100.db")

companies = ["TCS", "INFY", "HDFCBANK"]

for company in companies:

    print("=" * 60)
    print(company)

    df = pd.read_sql(
        f"""
        SELECT
            company_id,
            year,
            net_profit_margin_pct,
            return_on_equity_pct,
            debt_to_equity
        FROM financial_ratios
        WHERE company_id='{company}'
        ORDER BY year DESC
        LIMIT 5
        """,
        conn,
    )

    print(df)

conn.close()
