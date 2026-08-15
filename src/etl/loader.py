import csv
import sqlite3
import traceback
from pathlib import Path

import pandas as pd
from normaliser import normalize_ticker, normalize_year

# =====================================================
# Configuration
# =====================================================

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

DATABASE = "nifty100.db"

SUPPORTING_FILES = {
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx",
}

TABLE_MAPPING = {
    "companies.xlsx": "companies",
    "profitandloss.xlsx": "profitandloss",
    "balancesheet.xlsx": "balancesheet",
    "cashflow.xlsx": "cashflow",
    "analysis.xlsx": "analysis",
    "documents.xlsx": "documents",
    "prosandcons.xlsx": "prosandcons",
    "financial_ratios.xlsx": "financial_ratios",
    "market_cap.xlsx": "market_cap",
    "peer_groups.xlsx": "peer_groups",
    "sectors.xlsx": "sectors",
    "stock_prices.xlsx": "stock_prices",
}

conn = sqlite3.connect(DATABASE)


# =====================================================
# Load Excel File
# =====================================================


def load_excel(file_path):

    try:

        # --------------------------
        # Read Excel
        # --------------------------

        if file_path.name in SUPPORTING_FILES:
            df = pd.read_excel(file_path)

        else:
            df = pd.read_excel(file_path, header=None)
            df.columns = df.iloc[1]
            df = df.iloc[2:].reset_index(drop=True)

        # --------------------------
        # Normalize Data
        # --------------------------

        if "company_id" in df.columns:
            df["company_id"] = df["company_id"].apply(normalize_ticker)

        if "year" in df.columns:
            df["year"] = df["year"].apply(normalize_year)

        if "Year" in df.columns:
            df["Year"] = df["Year"].apply(normalize_year)
            df.rename(columns={"Year": "year"}, inplace=True)

        # --------------------------
        # Load into SQLite
        # --------------------------

        table_name = TABLE_MAPPING[file_path.name]

        cursor = conn.cursor()

        cursor.execute(f"DELETE FROM {table_name}")

        conn.commit()

        df.to_sql(table_name, conn, if_exists="append", index=False)

        print("=" * 70)
        print(f"File      : {file_path.name}")
        print(f"Table     : {table_name}")
        print(f"Rows      : {len(df)}")
        print(f"Columns   : {len(df.columns)}")
        print("Status    : ✅ Loaded Successfully")

        return {
            "table": table_name,
            "file": file_path.name,
            "rows_loaded": len(df),
            "rows_rejected": 0,
            "status": "Success",
        }

    except (OSError, ValueError, KeyError) as e:

        print("=" * 70)
        print(f"❌ Error loading {file_path.name}")
        traceback.print_exc()

        return {
            "table": TABLE_MAPPING.get(file_path.name, ""),
            "file": file_path.name,
            "rows_loaded": 0,
            "rows_rejected": 0,
            "status": f"Failed: {e}",
        }


# =====================================================
# Main
# =====================================================


def main():

    excel_files = sorted(DATA_DIR.glob("*.xlsx"))

    print("=" * 70)
    print(f"Found {len(excel_files)} Excel files")
    print("=" * 70)

    audit_data = []
    total_rows = 0

    for file in excel_files:

        result = load_excel(file)

        audit_data.append(result)

        total_rows += result["rows_loaded"]

    conn.commit()
    conn.close()

    # ---------------------------------
    # Write Load Audit CSV
    # ---------------------------------

    audit_file = OUTPUT_DIR / "load_audit.csv"

    with open(audit_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f, fieldnames=["table", "file", "rows_loaded", "rows_rejected", "status"]
        )

        writer.writeheader()
        writer.writerows(audit_data)

    print("\n" + "=" * 70)
    print("🎉 ETL Completed Successfully")
    print(f"Files Loaded : {len(excel_files)}")
    print(f"Total Rows   : {total_rows}")
    print(f"Database     : {DATABASE}")
    print(f"Audit File   : {audit_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
