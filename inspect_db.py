import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql(
    "SELECT DISTINCT interest_coverage FROM financial_ratios",
    conn
)

print(df)

conn.close()