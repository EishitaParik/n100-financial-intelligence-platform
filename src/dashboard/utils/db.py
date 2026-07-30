import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

# -------------------------------------------------
# Database Configuration
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE = PROJECT_ROOT / "nifty100.db"


def get_connection():
    """
    Create SQLite connection
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(query, params=None):
    """
    Execute SQL query and return DataFrame
    """

    conn = get_connection()

    if params is None:
        params = ()

    df = pd.read_sql_query(
        query,
        conn,
        params=params,
    )

    conn.close()

    return df


# -------------------------------------------------
# Companies
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_companies():

    query = """
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY company_name
    """

    return run_query(query)


# -------------------------------------------------
# Dashboard
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_dashboard_data(year):

    query = """
    SELECT

        c.id,
        c.company_name,

        s.broad_sector,
        s.sub_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.net_profit_margin_pct,
        fr.free_cash_flow_cr,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.ev_ebitda,
        mc.dividend_yield_pct,

        a.compounded_sales_growth,
        a.compounded_profit_growth

    FROM companies c

    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id

    LEFT JOIN market_cap mc
        ON c.id = mc.company_id
        AND fr.year = mc.year

    LEFT JOIN sectors s
        ON c.id = s.company_id

   LEFT JOIN analysis a
        ON c.id = a.company_id
        AND fr.year = a.year

    WHERE fr.year=?

    ORDER BY
        c.company_name
    """

    return run_query(query, (year,))

# -------------------------------------------------
# Company Profile
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_company_profile(ticker):

    query = """
    SELECT

        c.id,
        c.company_name,
        c.about_company,
        c.website,
        c.company_logo,
        c.chart_link,
        c.face_value,
        c.book_value,
        c.roce_percentage,
        c.roe_percentage,

        s.broad_sector,
        s.sub_sector

    FROM companies c

    LEFT JOIN sectors s
        ON c.id = s.company_id

    WHERE c.id=?
    """

    df = run_query(query, (ticker,))

    if df.empty:
        return None

    return df.iloc[0]


# -------------------------------------------------
# Financial Ratios
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):

    query = """
    SELECT *

    FROM financial_ratios

    WHERE company_id=?
    """

    params = [ticker]

    if year is not None:

        query += " AND year=?"

        params.append(year)

    query += """
    ORDER BY year
    """

    return run_query(query, tuple(params))


# -------------------------------------------------
# Profit & Loss
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_pl(ticker):

    query = """
    SELECT *

    FROM profitandloss

    WHERE company_id=?

    ORDER BY year
    """

    return run_query(query, (ticker,))


# -------------------------------------------------
# Balance Sheet
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_bs(ticker):

    query = """
    SELECT *

    FROM balancesheet

    WHERE company_id=?

    ORDER BY year
    """

    return run_query(query, (ticker,))


# -------------------------------------------------
# Cash Flow
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_cf(ticker):

    query = """
    SELECT *

    FROM cashflow

    WHERE company_id=?

    ORDER BY year
    """

    return run_query(query, (ticker,))

# -------------------------------------------------
# Sectors
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_sectors():

    query = """
    SELECT DISTINCT

        broad_sector,
        sub_sector,
        company_id,
        market_cap_category

    FROM sectors

    ORDER BY
        broad_sector,
        sub_sector
    """

    return run_query(query)


# -------------------------------------------------
# Peer Groups
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_peer_groups():

    query = """
    SELECT DISTINCT
        peer_group_name
    FROM peer_groups
    ORDER BY peer_group_name
    """

    return run_query(query)


@st.cache_data(ttl=600)
def get_peers(group_name):

    query = """
    SELECT

        pg.peer_group_name,
        pg.is_benchmark,

        c.company_name,
        c.id,

        fr.year,
        fr.return_on_equity_pct,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.asset_turnover,
        fr.free_cash_flow_cr,

        mc.market_cap_crore,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,

        a.compounded_sales_growth,
        a.compounded_profit_growth

    FROM peer_groups pg

    LEFT JOIN companies c
        ON pg.company_id = c.id

    LEFT JOIN financial_ratios fr
        ON pg.company_id = fr.company_id

    LEFT JOIN market_cap mc
        ON fr.company_id = mc.company_id
        AND fr.year = mc.year

    LEFT JOIN analysis a
        ON fr.company_id = a.company_id

    WHERE pg.peer_group_name = ?

    ORDER BY
        c.company_name,
        fr.year DESC
    """

    return run_query(query, (group_name,))

# -------------------------------------------------
# Valuation
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_valuation(ticker):

    query = """
    SELECT

        mc.*,
        s.broad_sector

    FROM market_cap mc

    LEFT JOIN sectors s
        ON mc.company_id=s.company_id

    WHERE mc.company_id=?

    ORDER BY mc.year DESC
    """

    return run_query(query, (ticker,))

# -------------------------------------------------
# Pros & Cons
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_pros_cons(ticker):

    query = """
    SELECT
        pros,
        cons
    FROM prosandcons
    WHERE company_id=?
    """

    return run_query(query, (ticker,))

# -------------------------------------------------
# Annual Reports
# -------------------------------------------------

@st.cache_data(ttl=600)
def get_reports(ticker):

    query = """
    SELECT
        year,
        annual_report
    FROM documents
    WHERE company_id=?
    ORDER BY year DESC
    """

    return run_query(query, (ticker,))

# -------------------------------------------------
# Company Search
# -------------------------------------------------

@st.cache_data(ttl=600)
def search_company(keyword):

    query = """
    SELECT
        id,
        company_name
    FROM companies
    WHERE
        company_name LIKE ?
        OR id LIKE ?
    ORDER BY company_name
    """

    value = f"%{keyword}%"

    return run_query(query, (value, value))


