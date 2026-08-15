"""
Profitability Ratio Functions
Sprint 2 - Day 08
"""


def net_profit_margin(net_profit, sales):
    """
    Net Profit Margin (%)

    Formula:
    (Net Profit / Sales) * 100
    """

    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    """
    Operating Profit Margin (%)
    """

    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def return_on_equity(net_profit, equity_capital, reserves):
    """
    Return on Equity (%)
    """

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    """
    Return on Capital Employed (%)
    """

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def return_on_assets(net_profit, total_assets):
    """
    Return on Assets (%)
    """

    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


# =====================================================
# Leverage & Efficiency Ratios
# =====================================================


def debt_to_equity(borrowings, equity_capital, reserves):
    """
    Debt to Equity Ratio

    Formula:
    Borrowings / (Equity + Reserves)

    If borrowings = 0 -> return 0
    If equity <= 0 -> return None
    """

    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(debt_equity, broad_sector):
    """
    High leverage flag.

    Financial companies are excluded.
    """

    if broad_sector == "Financials":
        return False

    return debt_equity is not None and debt_equity > 5


def interest_coverage_ratio(operating_profit, other_income, interest):
    """
    Interest Coverage Ratio

    Formula:
    (Operating Profit + Other Income) / Interest
    """

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def interest_coverage_label(interest):

    if interest == 0:
        return "Debt Free"

    return None


def interest_warning(icr):

    if icr is None:
        return False

    return icr < 1.5


def net_debt(borrowings, investments):
    """
    Net Debt

    Borrowings - Investments
    """

    return borrowings - investments


def asset_turnover(sales, total_assets):
    """
    Asset Turnover

    Sales / Total Assets
    """

    if total_assets == 0:
        return None

    return sales / total_assets
