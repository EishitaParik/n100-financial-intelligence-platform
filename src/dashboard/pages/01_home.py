import streamlit as st
import plotly.express as px
import pandas as pd

from utils.db import get_dashboard_data

st.set_page_config(layout="wide")

st.title("🏠 N100 Financial Intelligence Dashboard")

# ---------------------------------------
# Sidebar
# ---------------------------------------

st.sidebar.header("Dashboard Filters")

year = st.sidebar.selectbox(
    "Financial Year",
    [2019, 2020, 2021, 2022, 2023, 2024],
    index=5
)

df = get_dashboard_data(year)

if df.empty:
    st.warning("No records found.")
    st.stop()

# ---------------------------------------
# Data Cleaning
# ---------------------------------------

numeric_cols = [
    "return_on_equity_pct",
    "debt_to_equity",
    "pe_ratio",
    "pb_ratio",
    "market_cap_crore",
    "compounded_sales_growth",
    "compounded_profit_growth",
    "free_cash_flow_cr",
]

for col in numeric_cols:

    if col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace(",", "", regex=False)
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# ---------------------------------------
# Quality Score
# ---------------------------------------

df["quality_score"] = (

    df["return_on_equity_pct"].fillna(0)

    + df["compounded_sales_growth"].fillna(0)

    + df["compounded_profit_growth"].fillna(0)

    - df["debt_to_equity"].fillna(0)

)

# ---------------------------------------
# KPI Calculations
# ---------------------------------------

avg_roe = df["return_on_equity_pct"].mean()

median_pe = df["pe_ratio"].median()

median_de = df["debt_to_equity"].median()

total_companies = len(df)

median_sales_growth = df["compounded_sales_growth"].median()

debt_free = (
    df["debt_to_equity"] <= 0
).sum()

# ---------------------------------------
# KPI Cards
# ---------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric(
    "Average ROE",
    f"{avg_roe:.2f}%"
)

c2.metric(
    "Median P/E",
    f"{median_pe:.2f}"
)

c3.metric(
    "Median D/E",
    f"{median_de:.2f}"
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "Companies",
    total_companies
)

c5.metric(
    "Median Revenue CAGR",
    f"{median_sales_growth:.2f}%"
)

c6.metric(
    "Debt Free Companies",
    debt_free
)

st.divider()

# ---------------------------------------
# Sector Distribution
# ---------------------------------------

st.subheader("Sector Distribution")

sector_df = (
    df.groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
    .sort_values("Companies", ascending=False)
)

fig_sector = px.pie(
    sector_df,
    names="broad_sector",
    values="Companies",
    hole=0.55,
    title="Companies by Sector"
)

st.plotly_chart(
    fig_sector,
    use_container_width=True
)

st.divider()

# ---------------------------------------
# Top Quality Companies
# ---------------------------------------

st.subheader("Top 5 Companies by Quality Score")

top_quality = (
    df.sort_values(
        "quality_score",
        ascending=False
    )
    .head(5)
)

st.dataframe(
    top_quality[
        [
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "debt_to_equity",
            "quality_score",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.divider()

# ---------------------------------------
# Largest Companies
# ---------------------------------------

st.subheader("Top 10 Companies by Market Cap")

top_mc = (
    df.sort_values(
        "market_cap_crore",
        ascending=False
    )
    .head(10)
)

fig_market = px.bar(
    top_mc,
    x="company_name",
    y="market_cap_crore",
    color="broad_sector",
    title="Largest Companies",
)

fig_market.update_layout(
    xaxis_title="Company",
    yaxis_title="Market Cap (Cr)"
)

st.plotly_chart(
    fig_market,
    use_container_width=True,
)

st.divider()

# ---------------------------------------
# ROE Distribution
# ---------------------------------------

st.subheader("ROE Distribution")

fig_roe = px.histogram(
    df,
    x="return_on_equity_pct",
    nbins=25,
    title="Distribution of Return on Equity",
)

fig_roe.update_layout(
    xaxis_title="ROE (%)",
    yaxis_title="Number of Companies",
)

st.plotly_chart(
    fig_roe,
    use_container_width=True,
)

st.divider()

# ---------------------------------------
# Raw Data
# ---------------------------------------

with st.expander("View Complete Dataset"):

    st.dataframe(
        df.sort_values("company_name"),
        use_container_width=True,
        hide_index=True,
    )