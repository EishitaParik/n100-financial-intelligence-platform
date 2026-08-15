import sqlite3

import pandas as pd

conn = sqlite3.connect("nifty100.db")

companies = ["TCS", "INFY", "HDFCBANK", "RELIANCE", "ITC"]

for company in companies:

    print("=" * 70)
    print(company)

    query = f"""
    SELECT
        company_id,
        year,
        net_profit_margin_pct,
        return_on_equity_pct,
        debt_to_equity,
        interest_coverage,
        asset_turnover
    FROM financial_ratios
    WHERE company_id='{company}'
    ORDER BY year DESC
    LIMIT 3;
    """

    df = pd.read_sql(query, conn)

    print(df)

conn.close()
