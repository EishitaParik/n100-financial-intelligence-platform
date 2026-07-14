import sqlite3
from pathlib import Path

# Database file
DATABASE = "nifty100.db"

# Schema file
SCHEMA = Path("db/schema.sql")


def create_database():

    conn = sqlite3.connect(DATABASE)

    with open(SCHEMA, "r", encoding="utf-8") as file:
        conn.executescript(file.read())

    conn.commit()
    conn.close()

    print("✅ Database created successfully!")
    print(f"Database created: {DATABASE}")


if __name__ == "__main__":
    create_database()