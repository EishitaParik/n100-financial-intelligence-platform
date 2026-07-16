import sqlite3
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect("nifty100.db")
cursor = conn.cursor()

log_file = OUTPUT_DIR / "ratio_edge_cases.log"

with open(log_file, "w", encoding="utf-8") as f:

    f.write("========== Ratio Edge Cases ==========\n\n")

    # -----------------------------------
    # Financial companies
    # -----------------------------------

    f.write("Financial Sector Companies\n")

    financials = cursor.execute("""
        SELECT company_id
        FROM sectors
        WHERE broad_sector='Financials'
    """).fetchall()

    for company in financials:
        f.write(f"{company[0]} : High leverage expected - D/E warning suppressed\n")

    f.write("\n")

    # -----------------------------------
    # ROE Comparison
    # -----------------------------------

    f.write("ROE Source Comparison\n")

    rows = cursor.execute("""
        SELECT
            id,
            company_name,
            roe_percentage
        FROM companies
    """).fetchall()

    for row in rows:

        company = row[1]
        roe = row[2]

        if roe is None:
            continue

        if roe < 1:

            f.write(
                f"{company}: Source ROE = {roe} "
                "(Possible source anomaly)\n"
            )

    f.write("\nReview Category:\n")
    f.write("- Data Source Issue\n")
    f.write("- Formula Difference\n")
    f.write("- Version Difference\n")

conn.close()

print("=" * 60)
print("Edge Case Log Generated Successfully")
print(log_file)
print("=" * 60)