import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

tables = [
    "balancesheet",
    "cashflow",
    "profitandloss",
    "analysis",
    "documents",
    "prosandcons",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices",
]

for table in tables:
    print(f"\n===== {table} =====")

    cursor.execute(f"""
        SELECT DISTINCT company_id
        FROM {table}
        WHERE company_id NOT IN (
            SELECT id FROM companies
        )
        ORDER BY company_id;
    """)

    rows = cursor.fetchall()

    if not rows:
        print("No invalid company IDs.")
    else:
        for row in rows:
            print(row[0])

conn.close()