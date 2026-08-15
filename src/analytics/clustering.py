import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE = PROJECT_ROOT / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


# ============================================================
# CLUSTERING FEATURES
# ============================================================

FEATURES = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct",
]


# ============================================================
# LOAD DATA
# ============================================================


def load_data():
    """Load historical financial data required for clustering."""

    conn = sqlite3.connect(DATABASE)

    query = """
        SELECT
            fr.company_id,
            fr.year,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.operating_profit_margin_pct,
            fr.free_cash_flow_cr,
            pl.sales,
            s.broad_sector
        FROM financial_ratios fr
        LEFT JOIN profitandloss pl
            ON fr.company_id = pl.company_id
            AND fr.year = pl.year
        LEFT JOIN sectors s
            ON fr.company_id = s.company_id
        ORDER BY fr.company_id, fr.year
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ============================================================
# CLEAN DATA
# ============================================================


def clean_data(df):
    """Convert financial columns to numeric values."""

    numeric_columns = [
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "free_cash_flow_cr",
        "sales",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


# ============================================================
# CAGR CALCULATION
# ============================================================


def calculate_cagr(start_value, end_value, years=5):
    """Calculate CAGR for positive start and end values."""

    if pd.isna(start_value) or pd.isna(end_value):
        return np.nan

    if start_value <= 0 or end_value <= 0:
        return np.nan

    return ((end_value / start_value) ** (1 / years) - 1) * 100


# ============================================================
# BUILD COMPANY-LEVEL DATASET
# ============================================================


def build_company_features(df):
    """Create one latest-year clustering record for each company."""

    records = []

    for company_id, group in df.groupby("company_id"):

        group = group.sort_values("year")

        # Latest available year
        latest = group.iloc[-1]

        latest_year = latest["year"]

        # Look for approximately 5 years earlier
        five_years_ago = group[group["year"] <= latest_year - 5]

        if five_years_ago.empty:
            start_row = None
        else:
            start_row = five_years_ago.iloc[-1]

        # ----------------------------------------------------
        # Revenue CAGR
        # ----------------------------------------------------

        revenue_cagr = np.nan

        if start_row is not None:
            revenue_cagr = calculate_cagr(start_row["sales"], latest["sales"], 5)

        # ----------------------------------------------------
        # FCF CAGR
        # ----------------------------------------------------

        fcf_cagr = np.nan

        if start_row is not None:
            fcf_cagr = calculate_cagr(
                start_row["free_cash_flow_cr"], latest["free_cash_flow_cr"], 5
            )

        records.append(
            {
                "company_id": company_id,
                "broad_sector": latest["broad_sector"],
                "year": latest_year,
                "return_on_equity_pct": latest["return_on_equity_pct"],
                "debt_to_equity": latest["debt_to_equity"],
                "revenue_cagr_5yr": revenue_cagr,
                "fcf_cagr_5yr": fcf_cagr,
                "operating_profit_margin_pct": latest["operating_profit_margin_pct"],
            }
        )

    return pd.DataFrame(records)


# ============================================================
# SECTOR MEDIAN IMPUTATION
# ============================================================


def impute_missing_values(df):
    """
    Impute missing clustering features using sector medians.
    """

    result = df.copy()

    for feature in FEATURES:

        result[feature] = result.groupby("broad_sector")[feature].transform(
            lambda x: x.fillna(x.median())
        )

        # Global median fallback if sector median is unavailable
        result[feature] = result[feature].fillna(result[feature].median())

    return result


# ============================================================
# ELBOW METHOD
# ============================================================


def generate_elbow_plot(X_scaled):
    """Generate KMeans elbow plot for k=2 through k=10."""

    inertias = []

    for k in range(2, 11):

        model = KMeans(n_clusters=k, random_state=42, n_init=10)

        model.fit(X_scaled)

        inertias.append(model.inertia_)

    plt.figure(figsize=(8, 5))

    plt.plot(range(2, 11), inertias, marker="o")

    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("KMeans Elbow Plot")

    plt.xticks(range(2, 11))

    plt.tight_layout()

    output_path = REPORTS_DIR / "elbow_plot.png"

    plt.savefig(output_path, dpi=150)

    plt.close()

    print(f"Elbow plot saved: {output_path}")


# ============================================================
# RUN KMEANS
# ============================================================


def run_kmeans(df):
    """Scale features and run reproducible 5-cluster KMeans."""

    scaler = StandardScaler()

    X = df[FEATURES]

    X_scaled = scaler.fit_transform(X)

    # Elbow plot
    generate_elbow_plot(X_scaled)

    # Required Sprint configuration
    model = KMeans(n_clusters=5, random_state=42, n_init=10)

    cluster_ids = model.fit_predict(X_scaled)

    result = df.copy()

    result["cluster_id"] = cluster_ids

    # Distance to assigned centroid
    distances = model.transform(X_scaled)

    result["distance_from_centroid"] = [
        distances[i, cluster_ids[i]] for i in range(len(result))
    ]

    return result


# ============================================================
# SAVE RESULTS
# ============================================================


def save_results(df):
    """Save required Sprint 6 cluster output."""

    # Temporary names.
    # We will assign meaningful names during Day 37.
    cluster_names = {
        0: "Cluster 0",
        1: "Cluster 1",
        2: "Cluster 2",
        3: "Cluster 3",
        4: "Cluster 4",
    }

    df["cluster_name"] = df["cluster_id"].map(cluster_names)

    output_columns = [
        "company_id",
        "cluster_id",
        "cluster_name",
        "distance_from_centroid",
    ]

    output_path = OUTPUT_DIR / "cluster_labels.csv"

    df[output_columns].to_csv(output_path, index=False)

    return output_path


# ============================================================
# MAIN
# ============================================================


def main():
    """Run the complete Day 36 clustering pipeline."""

    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE PLATFORM")
    print("DAY 36 - KMEANS CLUSTERING")
    print("=" * 70)

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    print("\n[1/6] Loading database...")

    df = load_data()

    print(f"Historical rows loaded: {len(df):,}")
    print(f"Companies found: " f"{df['company_id'].nunique()}")

    # --------------------------------------------------------
    # Clean
    # --------------------------------------------------------

    print("\n[2/6] Cleaning numeric data...")

    df = clean_data(df)

    # --------------------------------------------------------
    # Build features
    # --------------------------------------------------------

    print("\n[3/6] Building clustering features...")

    company_features = build_company_features(df)

    print(f"Company-level records: " f"{len(company_features)}")

    print("\nFeatures:")
    print(company_features[["company_id"] + FEATURES].head())

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    print("\n[4/6] Applying sector median imputation...")

    print("\nMissing values BEFORE imputation:")

    print(company_features[FEATURES].isna().sum())

    company_features = impute_missing_values(company_features)

    print("\nMissing values AFTER imputation:")

    print(company_features[FEATURES].isna().sum())

    # --------------------------------------------------------
    # KMeans
    # --------------------------------------------------------

    print("\n[5/6] Running KMeans...")

    clustered = run_kmeans(company_features)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    print("\n[6/6] Saving results...")

    output_path = save_results(clustered)

    print("\n" + "=" * 70)
    print("CLUSTERING RESULTS")
    print("=" * 70)

    print(f"\nTotal companies: " f"{clustered['company_id'].nunique()}")

    print("\nCluster distribution:")

    print(clustered["cluster_id"].value_counts().sort_index())

    print(f"\nCluster labels:" f"\n{output_path}")

    print(f"\nElbow plot:" f"\n{REPORTS_DIR / 'elbow_plot.png'}")

    print("\nDAY 36 COMPLETE")


if __name__ == "__main__":
    main()
