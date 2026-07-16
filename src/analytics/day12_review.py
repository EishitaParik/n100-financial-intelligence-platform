import sqlite3
import pandas as pd

DATABASE = "nifty100.db"

conn = sqlite3.connect(DATABASE)

print("=" * 60)
print("FINANCIAL RATIOS TABLE REVIEW")
print("=" * 60)

# -----------------------------------
# Row Count
# -----------------------------------

count = pd.read_sql(
    "SELECT COUNT(*) AS total_rows FROM financial_ratios",
    conn,
)

print("\nTotal Rows")
print(count)

# -----------------------------------
# Sample Records
# -----------------------------------

sample = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        net_profit_margin_pct,
        operating_profit_margin_pct,
        return_on_equity_pct,
        debt_to_equity,
        interest_coverage
    FROM financial_ratios
    LIMIT 10
    """,
    conn,
)

print("\nSample Financial Ratios")
print(sample)

# -----------------------------------
# Null Count
# -----------------------------------

nulls = pd.read_sql(
    """
    SELECT
        SUM(net_profit_margin_pct IS NULL) AS npm_null,
        SUM(operating_profit_margin_pct IS NULL) AS opm_null,
        SUM(return_on_equity_pct IS NULL) AS roe_null,
        SUM(debt_to_equity IS NULL) AS de_null,
        SUM(interest_coverage IS NULL) AS icr_null,
        SUM(asset_turnover IS NULL) AS at_null
    FROM financial_ratios
    """,
    conn,
)

print("\nNull Summary")
print(nulls)

conn.close()

print("\nDay 12 Review Completed Successfully")