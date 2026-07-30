import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_valuation,
)

st.set_page_config(layout="wide")

st.title("📈 Financial Trends")

companies = get_companies()

company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

ticker = companies.loc[
    companies["company_name"] == company,
    "id"
].iloc[0]

ratios = get_ratios(ticker)
pl = get_pl(ticker)
valuation = get_valuation(ticker)

if ratios.empty:
    st.warning("No trend data available.")
    st.stop()

st.sidebar.header("Trend Analysis")

trend = st.sidebar.selectbox(
    "Select Metric",
    [
        "Return on Equity",
        "Debt to Equity",
        "Net Profit Margin",
        "Operating Profit Margin",
        "Revenue",
        "Net Profit",
        "PE Ratio",
        "PB Ratio",
        "Market Cap",
    ]
)

ratio_map = {
    "Return on Equity": "return_on_equity_pct",
    "Debt to Equity": "debt_to_equity",
    "Net Profit Margin": "net_profit_margin_pct",
    "Operating Profit Margin": "operating_profit_margin_pct",
}


if trend in ratio_map:

    col = ratio_map[trend]

    if col in ratios.columns:

        fig = px.line(
            ratios,
            x="year",
            y=col,
            markers=True,
            title=trend,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

elif trend in ["Revenue", "Net Profit"]:

    metric_map = {
        "Revenue": "sales",
        "Net Profit": "net_profit",
    }

    metric = metric_map[trend]

    if metric in pl.columns:

        fig = px.bar(
            pl,
            x="year",
            y=metric,
            text_auto=True,
            title=trend,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(f"{trend} column not available in Profit & Loss data.")

else:

    valuation_map = {
        "PE Ratio": "pe_ratio",
        "PB Ratio": "pb_ratio",
        "Market Cap": "market_cap_crore",
    }

    metric = valuation_map[trend]

    if metric in valuation.columns:

        fig = px.line(
            valuation,
            x="year",
            y=metric,
            markers=True,
            title=trend,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(f"{trend} data not available.")


st.divider()

st.subheader("Underlying Data")

tab1, tab2, tab3 = st.tabs([
    "Financial Ratios",
    "Profit & Loss",
    "Valuation"
])

with tab1:
    st.dataframe(
        ratios,
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.dataframe(
        pl,
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.dataframe(
        valuation,
        use_container_width=True,
        hide_index=True,
    )

