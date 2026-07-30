import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

# Print all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nTABLES:")
for table in tables:
    print(table[0])

print("\n" + "=" * 60)

# Print columns of every table
for table in tables:
    table_name = table[0]
    print(f"\nTABLE: {table_name}")
    cursor.execute(f"PRAGMA table_info({table_name});")
    cols = cursor.fetchall()

    for col in cols:
        print(f"{col[1]} ({col[2]})")

conn.close()