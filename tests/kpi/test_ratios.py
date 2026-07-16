from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
)


def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20.0


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(200, 0) is None


def test_operating_profit_margin():
    assert operating_profit_margin(250, 1000) == 25.0


def test_operating_profit_margin_zero_sales():
    assert operating_profit_margin(250, 0) is None


def test_return_on_equity():
    assert return_on_equity(500, 1000, 4000) == 10.0


def test_return_on_equity_negative_equity():
    assert return_on_equity(500, -1000, 500) is None


def test_return_on_capital_employed():
    assert return_on_capital_employed(600, 1000, 4000, 2000) == (600 / 7000) * 100


def test_return_on_assets():
    assert return_on_assets(300, 6000) == 5.0


def test_return_on_assets_zero_assets():
    assert return_on_assets(300, 0) is None


    # =====================================================
# Debt to Equity
# =====================================================

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    interest_coverage_label,
    interest_warning,
    net_debt,
    asset_turnover,
)


def test_debt_to_equity():
    assert debt_to_equity(2000, 1000, 3000) == 0.5


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 1000, 3000) == 0


def test_high_leverage():
    assert high_leverage_flag(6.2, "IT") is True


def test_financial_company_not_flagged():
    assert high_leverage_flag(8.5, "Financials") is False


def test_interest_coverage():
    assert interest_coverage_ratio(200, 50, 50) == 5


def test_interest_zero():
    assert interest_coverage_ratio(200, 50, 0) is None


def test_interest_label():
    assert interest_coverage_label(0) == "Debt Free"


def test_interest_warning():
    assert interest_warning(1.2) is True


def test_net_debt():
    assert net_debt(5000, 1200) == 3800


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2