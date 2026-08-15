import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from clustering import (
    FEATURES,
    build_company_features,
    clean_data,
    impute_missing_values,
    load_data,
)

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
# LOAD CLUSTERS
# ============================================================


def load_clusters():
    """Load the cluster assignments generated on Day 36."""

    path = OUTPUT_DIR / "cluster_labels.csv"

    return pd.read_csv(path)


# ============================================================
# BUILD CLUSTER FEATURE DATA
# ============================================================


def build_profile_data():
    """Recreate the five clustering features for each company."""

    df = load_data()

    df = clean_data(df)

    company_features = build_company_features(df)

    company_features = impute_missing_values(company_features)

    clusters = load_clusters()

    profile = company_features.merge(
        clusters[
            [
                "company_id",
                "cluster_id",
                "cluster_name",
                "distance_from_centroid",
            ]
        ],
        on="company_id",
        how="inner",
    )

    return profile


# ============================================================
# CLUSTER STATISTICS
# ============================================================


def generate_cluster_statistics(profile):
    """Calculate mean and median for the five clustering features."""

    mean_stats = profile.groupby("cluster_id")[FEATURES].mean().round(2)

    median_stats = profile.groupby("cluster_id")[FEATURES].median().round(2)

    counts = profile.groupby("cluster_id").size().rename("company_count")

    print("\n" + "=" * 70)
    print("CLUSTER COUNTS")
    print("=" * 70)

    print(counts)

    print("\n" + "=" * 70)
    print("CLUSTER MEANS")
    print("=" * 70)

    print(mean_stats)

    print("\n" + "=" * 70)
    print("CLUSTER MEDIANS")
    print("=" * 70)

    print(median_stats)

    mean_stats.to_csv(OUTPUT_DIR / "cluster_mean_stats.csv")

    median_stats.to_csv(OUTPUT_DIR / "cluster_median_stats.csv")

    return mean_stats, median_stats


# ============================================================
# ACTUAL COMPANIES IN EACH CLUSTER
# ============================================================


def print_cluster_companies(profile):
    """Print the companies belonging to each cluster."""

    print("\n" + "=" * 70)
    print("COMPANIES BY CLUSTER")
    print("=" * 70)

    for cluster_id in sorted(profile["cluster_id"].unique()):

        companies = profile[profile["cluster_id"] == cluster_id]["company_id"].tolist()

        print(f"\nCluster {cluster_id} " f"({len(companies)} companies):")

        print(", ".join(companies))


# ============================================================
# CORRELATION DATA
# ============================================================


def load_latest_kpis():
    """Load the latest-year KPI values for correlation analysis."""

    conn = sqlite3.connect(DATABASE)

    # First determine which optional KPI columns exist.
    analysis_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(analysis)").fetchall()
    }

    available_analysis = []

    for column in [
        "compounded_sales_growth",
        "compounded_profit_growth",
    ]:
        if column in analysis_columns:
            available_analysis.append(column)

    # Build the query dynamically.
    optional_select = ""

    if "compounded_sales_growth" in available_analysis:
        optional_select += ", a.compounded_sales_growth"

    if "compounded_profit_growth" in available_analysis:
        optional_select += ", a.compounded_profit_growth"

    query = f"""
        SELECT
            fr.company_id,
            fr.year,
            fr.net_profit_margin_pct,
            fr.operating_profit_margin_pct,
            fr.return_on_equity_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            c.roce_percentage
            {optional_select}
        FROM financial_ratios fr
        LEFT JOIN companies c
            ON fr.company_id = c.id
        LEFT JOIN analysis a
            ON fr.company_id = a.company_id
        WHERE fr.year = (
            SELECT MAX(fr2.year)
            FROM financial_ratios fr2
            WHERE fr2.company_id = fr.company_id
        )
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ============================================================
# CORRELATION HEATMAP
# ============================================================


def generate_correlation_heatmap():
    """Generate Pearson correlation heatmap for ten core KPIs."""

    df = load_latest_kpis()

    kpis = [
        "return_on_equity_pct",
        "roce_percentage",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "compounded_sales_growth",
        "compounded_profit_growth",
    ]

    available = [column for column in kpis if column in df.columns]

    # Convert to numeric.
    for column in available:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    correlation = df[available].corr(method="pearson")

    print("\n" + "=" * 70)
    print("CORRELATION MATRIX")
    print("=" * 70)

    print(correlation.round(2))

    plt.figure(figsize=(11, 8))

    sns.heatmap(
        correlation,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
    )

    plt.title("Pearson Correlation Matrix - Core KPIs")

    plt.tight_layout()

    output_path = REPORTS_DIR / "correlation_heatmap.png"

    plt.savefig(output_path, dpi=150)

    plt.close()

    print(f"\nCorrelation heatmap saved:" f"\n{output_path}")


# ============================================================
# MAIN
# ============================================================


def main():
    """Run Day 37 cluster profiling and correlation analysis."""

    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE PLATFORM")
    print("DAY 37 - CLUSTER PROFILING")
    print("=" * 70)

    print("\n[1/3] Building cluster profile...")

    profile = build_profile_data()

    print(f"Companies profiled: " f"{profile['company_id'].nunique()}")

    print("\n[2/3] Calculating statistics...")

    generate_cluster_statistics(profile)

    print_cluster_companies(profile)

    print("\n[3/3] Generating correlation heatmap...")

    generate_correlation_heatmap()

    print("\n" + "=" * 70)
    print("CLUSTER PROFILING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
