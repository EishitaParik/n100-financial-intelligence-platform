import sqlite3
from pathlib import Path

import pandas as pd


# -------------------------------------------------
# Paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE = PROJECT_ROOT / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# -------------------------------------------------
# Database Connection
# -------------------------------------------------

def get_connection():
    return sqlite3.connect(DATABASE)


# -------------------------------------------------
# Load Valuation Dataset
# -------------------------------------------------

def load_data():

    conn = get_connection()

    query = """
    SELECT

        c.id AS company_id,
        c.company_name,

        s.broad_sector,

        mc.year,
        mc.market_cap_crore,
        mc.enterprise_value_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.ev_ebitda,
        mc.dividend_yield_pct,

        cf.net_cash_flow

    FROM companies c

    LEFT JOIN market_cap mc
        ON c.id = mc.company_id

    LEFT JOIN cashflow cf
        ON
            mc.company_id = cf.company_id
            AND
            mc.year = cf.year

    LEFT JOIN sectors s
        ON c.id = s.company_id

    WHERE mc.market_cap_crore IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

# -------------------------------------------------
# Cleaning
# -------------------------------------------------

def clean_data(df):

    numeric_cols = [

        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "dividend_yield_pct",
        "net_cash_flow",

    ]

    for col in numeric_cols:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df

# -------------------------------------------------
# FCF Yield
# -------------------------------------------------

def calculate_fcf_yield(df):

    df["fcf_yield_pct"] = (
        df["net_cash_flow"]
        /
        df["market_cap_crore"]
    ) * 100

    return df


# -------------------------------------------------
# Latest Financial Year
# -------------------------------------------------

def latest_year_data(df):

    latest_year = df["year"].max()

    latest = (
        df[df["year"] == latest_year]
        .copy()
        .reset_index(drop=True)
    )

    return latest

# -------------------------------------------------
# Sector Median PE
# -------------------------------------------------

def calculate_sector_pe(df):

    sector_pe = (
        df.groupby("broad_sector")["pe_ratio"]
        .median()
        .reset_index()
        .rename(
            columns={
                "pe_ratio": "sector_median_pe"
            }
        )
    )

    df = df.merge(
        sector_pe,
        on="broad_sector",
        how="left"
    )

    return df

# -------------------------------------------------
# PE vs Sector Median
# -------------------------------------------------

def calculate_relative_pe(df):

    df["pe_vs_sector_median_pct"] = (
        (
            df["pe_ratio"] -
            df["sector_median_pe"]
        )
        /
        df["sector_median_pe"]
    ) * 100

    return df

# -------------------------------------------------
# Valuation Flags
# -------------------------------------------------

def assign_flags(df):

    def classify(row):

        pe = row["pe_ratio"]
        median = row["sector_median_pe"]

        if pd.isna(pe) or pd.isna(median):
            return "Unknown"

        if pe > median * 1.5:
            return "Caution"

        elif pe < median * 0.7:
            return "Discount"

        else:
            return "Fair"

    df["flag"] = df.apply(
        classify,
        axis=1
    )

    return df

# -------------------------------------------------
# Export Files
# -------------------------------------------------

def export_outputs(df):

    summary_cols = [

        "company_id",
        "company_name",
        "broad_sector",
        "year",
        "market_cap_crore",
        "enterprise_value_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "dividend_yield_pct",
        "fcf_yield_pct",
        "sector_median_pe",
        "pe_vs_sector_median_pct",
        "flag",

    ]

    summary = df[summary_cols].copy()

    summary.to_excel(
        OUTPUT_DIR / "valuation_summary.xlsx",
        index=False
    )

    flags = summary[
        summary["flag"].isin(
            ["Caution", "Discount"]
        )
    ]

    flags.to_csv(
        OUTPUT_DIR / "valuation_flags.csv",
        index=False
    )

    return summary, flags

# -------------------------------------------------
# Main
# -------------------------------------------------

def main():

    print("=" * 60)
    print("VALUATION MODULE")
    print("=" * 60)

    df = load_data()

    print(f"Loaded Rows : {len(df)}")

    df = clean_data(df)

    df = calculate_fcf_yield(df)

    df = latest_year_data(df)

    df = calculate_sector_pe(df)

    df = calculate_relative_pe(df)

    df = assign_flags(df)

    summary, flags = export_outputs(df)

    print()
    print("Summary File Created")
    print(OUTPUT_DIR / "valuation_summary.xlsx")

    print()
    print("Flags File Created")
    print(OUTPUT_DIR / "valuation_flags.csv")

    print()
    print(f"Companies Processed : {len(summary)}")
    print(f"Caution/Discount : {len(flags)}")

    print()
    print("Completed Successfully")


if __name__ == "__main__":
    main()

    
