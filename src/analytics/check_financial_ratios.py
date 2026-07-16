import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios LIMIT 5",
    conn
)

print(df)

print("\nColumns:\n")

print(df.columns.tolist())

conn.close()