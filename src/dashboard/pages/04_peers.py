import streamlit as st
import plotly.express as px

from utils.db import (
    get_peer_groups,
    get_peers,
)

st.set_page_config(layout="wide")

st.title("🤝 Peer Comparison")

groups = get_peer_groups()

if groups.empty:
    st.error("No peer groups found.")
    st.stop()

peer_group = st.selectbox(
    "Select Peer Group",
    groups["peer_group_name"]
)

df = get_peers(peer_group)

if df.empty:
    st.warning("No companies available.")
    st.stop()

st.subheader("Peer Group Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    df["company_name"].nunique()
)

c2.metric(
    "Average ROE",
    f"{df['return_on_equity_pct'].mean():.2f}%"
)

c3.metric(
    "Average PE",
    f"{df['pe_ratio'].mean():.2f}"
)

c4.metric(
    "Average Market Cap",
    f"{df['market_cap_crore'].mean():,.0f} Cr"
)

st.divider()

st.subheader("Peer Comparison Table")

latest = (
    df.sort_values("year", ascending=False)
      .drop_duplicates("company_name")
)

columns = [
    "company_name",
    "is_benchmark",
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "pe_ratio",
    "pb_ratio",
    "market_cap_crore",
]

available = [c for c in columns if c in latest.columns]

st.dataframe(
    latest[available],
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.subheader("ROE Comparison")

fig = px.bar(
    latest,
    x="company_name",
    y="return_on_equity_pct",
    color="is_benchmark",
    title="Return on Equity"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

st.subheader("P/E Ratio Comparison")

fig = px.bar(
    latest,
    x="company_name",
    y="pe_ratio",
    color="company_name",
    title="P/E Ratio"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()


st.subheader("Market Capitalization")

fig = px.scatter(
    latest,
    x="market_cap_crore",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="company_name",
    hover_name="company_name",
    title="Market Cap vs ROE"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

st.subheader("Profit Growth")

fig = px.bar(
    latest,
    x="company_name",
    y="compounded_profit_growth",
    color="company_name",
    title="Compounded Profit Growth"
)

st.plotly_chart(
    fig,
    use_container_width=True
)




