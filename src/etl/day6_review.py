import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

print("=" * 60)
print("TOTAL COMPANIES")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM companies")
print(cursor.fetchone()[0])

print("\n" + "=" * 60)
print("FIVE RANDOM COMPANIES")
print("=" * 60)

cursor.execute("""
SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5
""")

companies = cursor.fetchall()

for company in companies:
    print(company)

print("\n" + "=" * 60)
print("YEAR COVERAGE")
print("=" * 60)

for company_id, company_name in companies:

    cursor.execute(
        """
        SELECT COUNT(DISTINCT year)
        FROM profitandloss
        WHERE company_id = ?
    """,
        (company_id,),
    )

    years = cursor.fetchone()[0]

    print(f"{company_id:15} {company_name:35} Years = {years}")

print("\n" + "=" * 60)
print("COMPANIES WITH LESS THAN 5 YEARS")
print("=" * 60)

cursor.execute("""
SELECT company_id, COUNT(DISTINCT year)
FROM profitandloss
GROUP BY company_id
HAVING COUNT(DISTINCT year) < 5
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(row)
else:
    print("None")

conn.close()
