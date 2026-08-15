import plotly.express as px
import streamlit as st
from utils.db import (
    get_bs,
    get_cf,
    get_companies,
    get_company_profile,
    get_pl,
    get_pros_cons,
    get_ratios,
)

st.set_page_config(layout="wide")

st.title("🏢 Company Profile")

companies = get_companies()

if companies.empty:
    st.error("No companies available.")
    st.stop()

company = st.selectbox("Select Company", companies["company_name"])

ticker = companies.loc[companies["company_name"] == company, "id"].iloc[0]

profile = get_company_profile(ticker)

if profile is None:
    st.error("Company not found.")
    st.stop()

    # ---------------------------------------
# Company Information
# ---------------------------------------

st.header(profile["company_name"])

col1, col2 = st.columns([3, 1])

with col1:

    st.write(profile.get("about_company", "No description available."))

    st.markdown(f"**Website:** {profile.get('website', '-')}")

    st.markdown(f"**Sector:** {profile.get('broad_sector', '-')}")

    st.markdown(f"**Sub Sector:** {profile.get('sub_sector', '-')}")

with col2:

    if profile.get("company_logo"):

        st.image(profile["company_logo"], width=140)

        # ---------------------------------------
# KPI Cards
# ---------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric("ROE", f"{profile.get('roe_percentage',0):.2f}%")

c2.metric("ROCE", f"{profile.get('roce_percentage',0):.2f}%")

c3.metric("Face Value", profile.get("face_value", "-"))

c4, c5 = st.columns(2)

c4.metric("Book Value", profile.get("book_value", "-"))

c5.metric("Ticker", ticker)

st.divider()

# ---------------------------------------
# Load Financial Data
# ---------------------------------------

ratios = get_ratios(ticker)
pl = get_pl(ticker)
bs = get_bs(ticker)
cf = get_cf(ticker)

# ---------------------------------------
# Financial Ratio Trends
# ---------------------------------------

st.subheader("📈 Financial Ratio Trends")

if not ratios.empty:

    ratio_cols = [
        "return_on_equity_pct",
        "debt_to_equity",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
    ]

    available = [col for col in ratio_cols if col in ratios.columns]

    if available:

        metric = st.selectbox("Select Ratio", available)

        fig = px.line(
            ratios,
            x="year",
            y=metric,
            markers=True,
            title=metric.replace("_", " ").title(),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

else:

    st.info("Financial ratios not available.")

st.divider()

# ---------------------------------------
# Profit & Loss
# ---------------------------------------

st.subheader("💰 Profit & Loss")

if not pl.empty:

    st.dataframe(
        pl,
        use_container_width=True,
        hide_index=True,
    )

    numeric_cols = [col for col in pl.columns if col != "company_id" and col != "year"]

    if numeric_cols:

        metric = st.selectbox("P&L Metric", numeric_cols, key="pl_metric")

        fig = px.line(
            pl,
            x="year",
            y=metric,
            markers=True,
            title=metric.replace("_", " ").title(),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

else:

    st.info("Profit & Loss data unavailable.")

st.divider()

# ---------------------------------------
# Balance Sheet
# ---------------------------------------

st.subheader("📊 Balance Sheet")

if not bs.empty:

    st.dataframe(
        bs,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("Balance Sheet unavailable.")

st.divider()
# ---------------------------------------
# Cash Flow
# ---------------------------------------

st.subheader("💵 Cash Flow")

if not cf.empty:

    st.dataframe(
        cf,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("Cash Flow unavailable.")

st.divider()


# ---------------------------------------
# Pros & Cons
# ---------------------------------------

st.subheader("✅ Pros & Cons")

pros_cons = get_pros_cons(ticker)

if not pros_cons.empty:

    left, right = st.columns(2)

    with left:

        st.success("Pros")

        for item in pros_cons["pros"].dropna():

            st.write("•", item)

    with right:

        st.error("Cons")

        for item in pros_cons["cons"].dropna():

            st.write("•", item)

else:

    st.info("No Pros & Cons available.")
