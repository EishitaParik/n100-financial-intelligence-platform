import streamlit as st
import pandas as pd

from utils.db import (
    get_companies,
    get_reports,
    get_dashboard_data,
)

st.set_page_config(layout="wide")

st.title("📄 Reports & Downloads")

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

company = st.selectbox(
    "Select Company",
    companies["company_name"]
)

ticker = companies.loc[
    companies["company_name"] == company,
    "id"
].iloc[0]

reports = get_reports(ticker)

year = st.sidebar.selectbox(
    "Financial Year",
    [2019, 2020, 2021, 2022, 2023, 2024],
    index=5
)

dashboard = get_dashboard_data(year)

st.subheader("📄 Annual Reports")

if reports.empty:

    st.info("No annual reports available.")

else:

    st.dataframe(
        reports,
        use_container_width=True,
        hide_index=True,
    )

    if "annual_report" in reports.columns:

        for _, row in reports.iterrows():

            st.markdown(
                f"**{row['year']} Report:** {row['annual_report']}"
            )

st.divider()

st.subheader("📊 Dashboard Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(dashboard)
)

c2.metric(
    "Average ROE",
    f"{dashboard['return_on_equity_pct'].mean():.2f}%"
)

c3.metric(
    "Average PE",
    f"{dashboard['pe_ratio'].mean():.2f}"
)

c4.metric(
    "Total Market Cap",
    f"{dashboard['market_cap_crore'].sum():,.0f} Cr"
)

st.divider()

st.subheader("📥 Export Dashboard Data")

csv = dashboard.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Dashboard CSV",
    data=csv,
    file_name=f"dashboard_{year}.csv",
    mime="text/csv",
)

st.subheader("📊 Export Excel")

excel_buffer = pd.ExcelWriter(
    "dashboard_report.xlsx",
    engine="openpyxl"
)

dashboard.to_excel(
    excel_buffer,
    index=False,
    sheet_name="Dashboard"
)

excel_buffer.close()

with open("dashboard_report.xlsx", "rb") as f:

    st.download_button(
        label="⬇ Download Excel Report",
        data=f,
        file_name="dashboard_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.divider()

st.subheader("📋 Dataset Preview")

st.dataframe(
    dashboard,
    use_container_width=True,
    hide_index=True,
)

