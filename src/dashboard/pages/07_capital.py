import plotly.express as px
import streamlit as st
from utils.db import get_dashboard_data

st.set_page_config(layout="wide")

st.title("💰 Market Capitalization & Valuation")

year = st.sidebar.selectbox(
    "Financial Year", [2019, 2020, 2021, 2022, 2023, 2024], index=5
)

df = get_dashboard_data(year)

if df.empty:
    st.warning("No valuation data available.")
    st.stop()

    st.subheader("Market Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Companies", len(df))

c2.metric("Total Market Cap", f"{df['market_cap_crore'].sum():,.0f} Cr")

c3.metric("Average P/E", f"{df['pe_ratio'].mean():.2f}")

c4.metric("Average P/B", f"{df['pb_ratio'].mean():.2f}")

st.divider()

st.subheader("Market Cap Categories")

if "market_cap_category" in df.columns:

    category = df.groupby("market_cap_category").size().reset_index(name="Companies")

    fig = px.pie(
        category,
        names="market_cap_category",
        values="Companies",
        hole=0.45,
        title="Large / Mid / Small Cap Distribution",
    )

    st.plotly_chart(fig, use_container_width=True)

else:

    st.info("Market cap category data not available.")

st.divider()

st.subheader("Top 10 Companies by Market Cap")

top = df.sort_values("market_cap_crore", ascending=False).head(10)

fig = px.bar(
    top,
    x="company_name",
    y="market_cap_crore",
    color="broad_sector",
    text_auto=True,
    title="Largest Companies",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("P/E vs P/B Analysis")

fig = px.scatter(
    df,
    x="pe_ratio",
    y="pb_ratio",
    size="market_cap_crore",
    color="broad_sector",
    hover_name="company_name",
    title="Valuation Comparison",
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Dividend Yield Distribution")

fig = px.histogram(df, x="dividend_yield_pct", nbins=25, title="Dividend Yield")

st.plotly_chart(fig, use_container_width=True)

st.divider()


st.subheader("Valuation Table")

columns = [
    "company_name",
    "market_cap_crore",
    "pe_ratio",
    "pb_ratio",
    "ev_ebitda",
    "dividend_yield_pct",
]

available = [c for c in columns if c in df.columns]

st.dataframe(
    df[available].sort_values("market_cap_crore", ascending=False),
    use_container_width=True,
    hide_index=True,
)
