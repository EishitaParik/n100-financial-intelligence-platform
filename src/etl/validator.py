from pathlib import Path
import pandas as pd
import csv

from normaliser import normalize_year, normalize_ticker

# ==========================================
# Configuration
# ==========================================

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

validation_failures = []

SUPPORTING_FILES = {
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx",
}


# ==========================================
# Load Dataset
# ==========================================

def load_dataset(filename):

    file_path = DATA_DIR / filename

    if filename in SUPPORTING_FILES:
        df = pd.read_excel(file_path)

    else:
        df = pd.read_excel(file_path, header=None)
        df.columns = df.iloc[1]
        df = df.iloc[2:].reset_index(drop=True)

    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)

    if "year" in df.columns:
        df["year"] = df["year"].apply(normalize_year)

    if "Year" in df.columns:
        df["Year"] = df["Year"].apply(normalize_year)
        df.rename(columns={"Year": "year"}, inplace=True)

    return df


# ==========================================
# DQ-01 Primary Key
# ==========================================

def check_primary_key(df, table_name):

    if "id" not in df.columns:
        return

    duplicates = df[df["id"].duplicated()]

    if duplicates.empty:
        print(f"✅ {table_name}: Primary Key Passed")

    else:
        print(f"❌ {table_name}: {len(duplicates)} duplicate IDs")

        validation_failures.append({
            "table": table_name,
            "rule": "DQ-01",
            "severity": "CRITICAL",
            "message": f"{len(duplicates)} duplicate primary keys"
        })


# ==========================================
# DQ-02 Company + Year
# ==========================================

def check_company_year_key(df, table_name):

    VALID_TABLES = {
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "profitandloss.xlsx",
        "market_cap.xlsx",
    }

    if table_name not in VALID_TABLES:
        return

    if "company_id" not in df.columns:
        return

    if "year" not in df.columns:
        return

    duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]

    if duplicates.empty:
        print(f"✅ {table_name}: Company-Year Passed")

    else:

        summary = (
            duplicates
            .groupby(["company_id", "year"])
            .size()
            .reset_index(name="count")
        )

        print(f"⚠️ {table_name}: {len(summary)} duplicate company-year records")

        validation_failures.append({
            "table": table_name,
            "rule": "DQ-02",
            "severity": "WARNING",
            "message": f"{len(summary)} duplicate company-year combinations"
        })


# ==========================================
# DQ-03 Foreign Key
# ==========================================

def check_foreign_key(df, table_name, valid_companies):

    if table_name == "companies.xlsx":
        return

    if "company_id" not in df.columns:
        return

    invalid = df[~df["company_id"].isin(valid_companies)]

    if invalid.empty:
        print(f"✅ {table_name}: Foreign Key Passed")

    else:

        print(f"❌ {table_name}: {len(invalid)} invalid company IDs")

        validation_failures.append({
            "table": table_name,
            "rule": "DQ-03",
            "severity": "CRITICAL",
            "message": f"{len(invalid)} invalid company IDs"
        })



def check_balance_sheet(df, table_name):
    if table_name != "balancesheet.xlsx":
        return

    required = ["total_assets", "total_liabilities"]

    if not all(col in df.columns for col in required):
        return

    invalid = df[
        pd.to_numeric(df["total_assets"], errors="coerce") <
        pd.to_numeric(df["total_liabilities"], errors="coerce")
    ]

    if invalid.empty:
        print("✅ DQ-04 Balance Sheet Passed")
    else:
        print(f"⚠️ DQ-04: {len(invalid)} balance mismatches")

        validation_failures.append({
            "table": table_name,
            "rule": "DQ-04",
            "severity": "WARNING",
            "message": f"{len(invalid)} balance sheet mismatches"
        })



def check_positive_sales(df, table_name):
    if "sales" not in df.columns:
        return

    invalid = pd.to_numeric(df["sales"], errors="coerce") <= 0

    if invalid.sum() == 0:
        print("✅ DQ-05 Positive Sales Passed")
    else:
        print(f"⚠️ DQ-05: {invalid.sum()} invalid sales")

        validation_failures.append({
            "table": table_name,
            "rule": "DQ-05",
            "severity": "WARNING",
            "message": f"{invalid.sum()} non-positive sales"
        })


def check_positive_assets(df, table_name):
    if "total_assets" not in df.columns:
        return

    invalid = pd.to_numeric(df["total_assets"], errors="coerce") <= 0

    if invalid.sum() == 0:
        print("✅ DQ-06 Positive Assets Passed")
    else:
        print(f"⚠️ DQ-06: {invalid.sum()} invalid assets")


def check_urls(df, table_name):

    for col in ["website", "annual_report"]:

        if col in df.columns:

            invalid = ~df[col].astype(str).str.startswith("http")

            if invalid.sum() == 0:
                print(f"✅ DQ-07 {col} Passed")
            else:
                print(f"⚠️ DQ-07: {invalid.sum()} invalid URLs")


def check_tax(df, table_name):

    if "tax_percentage" not in df.columns:
        return

    tax = pd.to_numeric(df["tax_percentage"], errors="coerce")

    invalid = (tax < 0) | (tax > 100)

    if invalid.sum() == 0:
        print("✅ DQ-08 Tax Passed")
    else:
        print(f"⚠️ DQ-08: {invalid.sum()} invalid tax values")



def check_dividend(df, table_name):

    if "dividend_payout" not in df.columns:
        return

    div = pd.to_numeric(df["dividend_payout"], errors="coerce")

    invalid = div < 0

    if invalid.sum() == 0:
        print("✅ DQ-09 Dividend Passed")
    else:
        print(f"⚠️ DQ-09: {invalid.sum()} invalid dividends")



def check_eps(df, table_name):

    if "eps" not in df.columns:
        return

    if df["eps"].isnull().sum() == 0:
        print("✅ DQ-10 EPS Passed")
    else:
        print("⚠️ DQ-10 Missing EPS")


def check_missing(df, table_name):

    missing = df.isnull().sum().sum()

    if missing == 0:
        print("✅ DQ-11 Missing Values Passed")
    else:
        print(f"⚠️ DQ-11: {missing} missing values")



def check_year(df, table_name):

    if "year" not in df.columns:
        return

    invalid = (
        (pd.to_numeric(df["year"], errors="coerce") < 2000) |
        (pd.to_numeric(df["year"], errors="coerce") > 2035)
    )

    if invalid.sum() == 0:
        print("✅ DQ-12 Year Range Passed")
    else:
        print(f"⚠️ DQ-12: {invalid.sum()} invalid years")



def check_volume(df, table_name):

    if "volume" not in df.columns:
        return

    invalid = pd.to_numeric(df["volume"], errors="coerce") < 0

    if invalid.sum() == 0:
        print("✅ DQ-13 Volume Passed")
    else:
        print(f"⚠️ DQ-13: {invalid.sum()} invalid volume")



def check_duplicates(df, table_name):

    dup = df.duplicated().sum()

    if dup == 0:
        print("✅ DQ-14 Duplicate Rows Passed")
    else:
        print(f"⚠️ DQ-14: {dup} duplicate rows")



def check_company(df, table_name):

    if "company_id" not in df.columns:
        return

    invalid = df["company_id"].isnull().sum()

    if invalid == 0:
        print("✅ DQ-15 Company IDs Passed")
    else:
        print(f"⚠️ DQ-15: {invalid} missing company IDs")



def check_id(df, table_name):

    if "id" not in df.columns:
        return

    invalid = df["id"].isnull().sum()

    if invalid == 0:
        print("✅ DQ-16 ID Passed")
    else:
        print(f"⚠️ DQ-16: {invalid} missing IDs")



     
# ==========================================
# Main
# ==========================================

def main():

    files = [
        "companies.xlsx",
        "balancesheet.xlsx",
        "cashflow.xlsx",
        "profitandloss.xlsx",
        "analysis.xlsx",
        "documents.xlsx",
        "prosandcons.xlsx",
        "financial_ratios.xlsx",
        "market_cap.xlsx",
        "peer_groups.xlsx",
        "sectors.xlsx",
        "stock_prices.xlsx",
    ]

    companies_df = load_dataset("companies.xlsx")
    valid_companies = set(companies_df["id"])

    for file in files:

        print("\n" + "=" * 60)
        print(f"Checking {file}")

        df = load_dataset(file)

        check_primary_key(df, file)
        check_company_year_key(df, file)
        check_foreign_key(df, file, valid_companies)
        check_balance_sheet(df, file)
        check_positive_sales(df, file)
        check_positive_assets(df, file)
        check_urls(df, file)
        check_tax(df, file)
        check_dividend(df, file)
        check_eps(df, file)
        check_missing(df, file)
        check_year(df, file)
        check_volume(df, file)
        check_duplicates(df, file)
        check_company(df, file)
        check_id(df, file)
    # ======================================
    # Save validation report
    # ======================================

    validation_file = OUTPUT_DIR / "validation_failures.csv"

    with open(validation_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "table",
                "rule",
                "severity",
                "message"
            ]
        )

        writer.writeheader()
        writer.writerows(validation_failures)

    print("\n" + "=" * 60)
    print("Validation report generated successfully.")
    print(validation_file)


if __name__ == "__main__":
    main()