import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(".")
c = sqlite3.connect("nifty100.db")

# ============================================================
# AC-17 — FIND MISSING TEARSHEETS
# ============================================================

print("\n=== AC-17 MISSING TEARSHEETS ===")

companies = {
    x[0]
    for x in c.execute("SELECT id FROM companies").fetchall()
}

tearsheet_dir = ROOT / "reports" / "tearsheets"
pdfs = list(tearsheet_dir.glob("*.pdf"))

# Remove "_tearsheet" suffix from filenames
existing = {
    p.stem.replace("_tearsheet", "").upper()
    for p in pdfs
}

# Companies intentionally skipped because required data is unavailable
skipped = {"ATGL", "BAJAJ-AUTO", "SBIN"}

missing = sorted(companies - existing - skipped)

print("Expected companies:", len(companies))
print("Existing PDFs:", len(pdfs))
print("Documented skips:", sorted(skipped))
print("Missing:", missing)

if not missing:
    print("AC-17: PASS")
else:
    print("AC-17: FAIL")


# ============================================================
# AC-16 — HEROMOTOCO
# ============================================================

print("\n=== AC-16 HEROMOTOCO ===")

pc = ROOT / "output" / "pros_cons_generated.csv"
df = pd.read_csv(pc)

hero = df[df["company_id"] == "HEROMOTOCO"]

print(hero.to_string(index=False))

types = set(hero["type"].str.lower())

if {"pro", "con"}.issubset(types):
    print("AC-16: PASS")
else:
    print("AC-16: FAIL")


# ============================================================
# AC-19 — VALIDATION FILE
# ============================================================

print("\n=== AC-19 VALIDATION FILE ===")

vf = ROOT / "output" / "validation_failures.csv"

if vf.exists():
    validation = pd.read_csv(vf)

    print("Columns:", list(validation.columns))
    print("Rows:", len(validation))

    print("\nFirst rows:")
    print(validation.head(10).to_string(index=False))

    expected_columns = {
        "company_id",
        "field",
        "issue",
        "severity",
    }

    if (
        set(validation.columns) == expected_columns
        and validation.empty
    ):
        print("AC-19: PASS")
    else:
        print("AC-19: REVIEW")

else:
    print("validation_failures.csv NOT FOUND")
    print("AC-19: FAIL")


# ============================================================
# AC-13 — SCREENER EXCEL
# ============================================================

print("\n=== AC-13 SCREENER EXCEL ===")

xlsx = ROOT / "output" / "screener_output.xlsx"

if xlsx.exists():
    excel = pd.read_excel(
        xlsx,
        sheet_name="quality_compounder",
    )

    print("Excel rows:", len(excel))

    if "company_id" in excel.columns:
        excel_companies = sorted(
            excel["company_id"].dropna().unique().tolist()
        )

        print("Excel companies:", excel_companies)

        expected_quality = {
            "HDFCBANK",
            "INFY",
            "SBILIFE",
            "TCS",
        }

        if set(excel_companies) == expected_quality:
            print("AC-13: PASS")
        else:
            print("AC-13: REVIEW")

else:
    print("screener_output.xlsx NOT FOUND")
    print("AC-13: FAIL")


c.close()