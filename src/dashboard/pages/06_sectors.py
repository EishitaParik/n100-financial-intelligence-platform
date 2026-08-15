import plotly.express as px
import streamlit as st
from utils.db import get_dashboard_data

st.set_page_config(layout="wide")

st.title("🏭 Sector Analysis")

year = st.sidebar.selectbox(
    "Financial Year",
    [2019, 2020, 2021, 2022, 2023, 2024],
    index=5,
)

df = get_dashboard_data(year)

if df.empty:
    st.warning("No sector data available.")
    st.stop()

    st.sidebar.header("Filters")

sectors = sorted(df["broad_sector"].dropna().unique())

selected_sector = st.sidebar.selectbox("Select Sector", ["All"] + sectors)

if selected_sector != "All":
    filtered = df[df["broad_sector"] == selected_sector]
else:
    filtered = df.copy()

    st.subheader("Sector Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Companies", len(filtered))

c2.metric("Average ROE", f"{filtered['return_on_equity_pct'].mean():.2f}%")

c3.metric("Average PE", f"{filtered['pe_ratio'].mean():.2f}")

c4.metric("Market Cap", f"{filtered['market_cap_crore'].sum():,.0f} Cr")

st.divider()

st.subheader("Companies by Sector")

sector_count = (
    df.groupby("broad_sector")
    .size()
    .reset_index(name="Companies")
    .sort_values("Companies", ascending=False)
)

fig = px.bar(
    sector_count,
    x="broad_sector",
    y="Companies",
    text="Companies",
    title="Sector Distribution",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Market Capitalization by Sector")

sector_cap = (
    df.groupby("broad_sector")["market_cap_crore"]
    .sum()
    .reset_index()
    .sort_values("market_cap_crore", ascending=False)
)

fig = px.bar(
    sector_cap,
    x="broad_sector",
    y="market_cap_crore",
    text_auto=True,
    title="Sector-wise Market Cap",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Average ROE by Sector")

sector_roe = (
    df.groupby("broad_sector")["return_on_equity_pct"]
    .mean()
    .reset_index()
    .sort_values("return_on_equity_pct", ascending=False)
)

fig = px.bar(
    sector_roe,
    x="broad_sector",
    y="return_on_equity_pct",
    color="return_on_equity_pct",
    title="Average ROE",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top Companies")

top = filtered.sort_values("market_cap_crore", ascending=False)

cols = [
    "company_name",
    "broad_sector",
    "return_on_equity_pct",
    "pe_ratio",
    "debt_to_equity",
    "market_cap_crore",
]

available = [c for c in cols if c in top.columns]

st.dataframe(
    top[available],
    use_container_width=True,
    hide_index=True,
)

st.subheader("ROE vs Market Cap")

fig = px.scatter(
    filtered,
    x="market_cap_crore",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="broad_sector",
    hover_name="company_name",
    title="Sector Performance",
)

st.plotly_chart(fig, use_container_width=True)
