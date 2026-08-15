import re


def normalize_year(year):
    """
    Normalize different year formats.

    Examples:
    Dec 2012 -> 2012
    Mar 2014 -> 2014
    FY2022 -> 2022
    2024 -> 2024
    """

    if year is None:
        return None

    year = str(year).strip()

    match = re.search(r"\d{4}", year)

    if match:
        return int(match.group())

    return None


def normalize_ticker(ticker):
    """
    Normalize company ticker.

    Examples:
    abb
    ABB.NS
    abb-ns

    ->
    ABB
    """

    if ticker is None:
        return None

    ticker = str(ticker).strip().upper()

    ticker = ticker.replace(".NS", "")
    ticker = ticker.replace("-", "")
    ticker = ticker.replace(" ", "")

    return ticker
