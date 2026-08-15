import pandas as pd

from src.etl.validator import (
    check_company,
    check_dividend,
    check_duplicates,
    check_eps,
    check_foreign_key,
    check_id,
    check_missing,
    check_positive_assets,
    check_positive_sales,
    check_primary_key,
    check_tax,
    check_urls,
    check_volume,
    check_year,
)


def test_dq01_primary_key():
    df = pd.DataFrame({"id": [1, 2, 3]})
    check_primary_key(df, "test")


def test_dq03_foreign_key():
    df = pd.DataFrame({"company_id": ["TCS", "INVALID"]})
    check_foreign_key(df, "test", {"TCS"})


def test_dq05_positive_sales():
    df = pd.DataFrame({"sales": [1000, -10]})
    check_positive_sales(df, "test")


def test_dq06_positive_assets():
    df = pd.DataFrame({"total_assets": [1000, -10]})
    check_positive_assets(df, "test")


def test_dq07_urls():
    df = pd.DataFrame({"website": ["https://example.com"]})
    check_urls(df, "test")


def test_dq08_tax():
    df = pd.DataFrame({"tax_percentage": [20, 150]})
    check_tax(df, "test")


def test_dq09_dividend():
    df = pd.DataFrame({"dividend_payout": [20, -5]})
    check_dividend(df, "test")


def test_dq10_eps():
    df = pd.DataFrame({"eps": [10, None]})
    check_eps(df, "test")


def test_dq11_missing():
    df = pd.DataFrame({"a": [1, None]})
    check_missing(df, "test")


def test_dq12_year():
    df = pd.DataFrame({"year": [2024, 1990]})
    check_year(df, "test")


def test_dq13_volume():
    df = pd.DataFrame({"volume": [1000, -1]})
    check_volume(df, "test")


def test_dq14_duplicates():
    df = pd.DataFrame({"company_id": ["TCS", "TCS"]})
    check_duplicates(df, "test")


def test_dq15_company_id():
    df = pd.DataFrame({"company_id": ["TCS", None]})
    check_company(df, "test")


def test_dq16_id():
    df = pd.DataFrame({"id": [1, None]})
    check_id(df, "test")
