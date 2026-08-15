import pandas as pd
import streamlit as st
from utils.db import get_dashboard_data

st.set_page_config(layout="wide")

st.title("🔍 Stock Screener")

year = st.sidebar.selectbox(
    "Financial Year", [2019, 2020, 2021, 2022, 2023, 2024], index=5
)

df = get_dashboard_data(year)

if df.empty:
    st.warning("No data available.")
    st.stop()

    # Convert numeric columns
numeric_cols = [
    "return_on_equity_pct",
    "pe_ratio",
    "debt_to_equity",
    "compounded_sales_growth",
    "dividend_yield_pct",
    "market_cap_crore",
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

st.sidebar.header("Preset Screeners")

preset = st.sidebar.selectbox(
    "Choose Preset",
    [
        "Custom",
        "Quality Compounder",
        "Value Pick",
        "Growth Accelerator",
        "Dividend Champion",
        "Debt Free Bluechip",
    ],
)

roe = 0
pe = 999
de = 999
growth = 0
dividend = 0

if preset == "Quality Compounder":
    roe = 15
    de = 1
    growth = 10

elif preset == "Value Pick":
    pe = 20
    de = 2

elif preset == "Growth Accelerator":
    growth = 20
    de = 2

elif preset == "Dividend Champion":
    dividend = 2

elif preset == "Debt Free Bluechip":
    roe = 12
    de = 0

st.sidebar.header("Custom Filters")

min_roe = st.sidebar.slider(
    "Minimum ROE (%)",
    0,
    50,
    roe,
)

max_pe = st.sidebar.slider(
    "Maximum PE",
    0,
    100,
    min(100, pe),
)

max_de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    5.0,
    float(de),
)

min_growth = st.sidebar.slider(
    "Minimum Sales Growth (%)",
    0,
    50,
    growth,
)

min_dividend = st.sidebar.slider(
    "Minimum Dividend Yield",
    0.0,
    10.0,
    float(dividend),
)

numeric_columns = [
    "return_on_equity_pct",
    "pe_ratio",
    "debt_to_equity",
    "compounded_sales_growth",
    "dividend_yield_pct",
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")


st.write("Rows before filtering:", len(df))

st.write(df[numeric_columns].describe())

filtered = df.copy()

filtered = filtered[
    (filtered["return_on_equity_pct"] >= min_roe)
    & (filtered["pe_ratio"] <= max_pe)
    & (filtered["debt_to_equity"] <= max_de)
    # &
    # (filtered["compounded_sales_growth"] >= min_growth)
    & (filtered["dividend_yield_pct"] >= min_dividend)
]


st.subheader("Screening Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Companies Found", len(filtered))

c2.metric(
    "Average ROE",
    f"{filtered['return_on_equity_pct'].mean():.2f}%" if len(filtered) else "0",
)

c3.metric("Average PE", f"{filtered['pe_ratio'].mean():.2f}" if len(filtered) else "0")

st.subheader("Matching Companies")

columns = [
    "company_name",
    "broad_sector",
    "return_on_equity_pct",
    "pe_ratio",
    "debt_to_equity",
    "compounded_sales_growth",
    "dividend_yield_pct",
    "market_cap_crore",
]

available = [c for c in columns if c in filtered.columns]

st.dataframe(
    filtered[available],
    use_container_width=True,
    hide_index=True,
)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Results",
    csv,
    "screener_output.csv",
    "text/csv",
)
