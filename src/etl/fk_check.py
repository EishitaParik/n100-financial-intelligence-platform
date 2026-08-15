import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_key_check")
errors = cursor.fetchall()

if len(errors) == 0:
    print("✅ Foreign Key Check Passed")
else:
    print(f"❌ {len(errors)} Foreign Key Errors Found")
    print(errors)

conn.close()
