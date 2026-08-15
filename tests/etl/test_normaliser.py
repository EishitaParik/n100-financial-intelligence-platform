import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src" / "etl"))

from normaliser import normalize_ticker, normalize_year

# ===========================
# normalize_year()
# ===========================


@pytest.mark.parametrize(
    "input_year, expected",
    [
        ("Dec 2012", 2012),
        ("Mar 2014", 2014),
        ("FY2022", 2022),
        ("2024", 2024),
        (2025, 2025),
        ("2026", 2026),
        ("Jan 2018", 2018),
        ("Feb 2019", 2019),
        ("Apr 2020", 2020),
        ("May 2021", 2021),
        ("Jun 2022", 2022),
        ("Jul 2023", 2023),
        ("Aug 2024", 2024),
        ("Sep 2025", 2025),
        ("Oct 2026", 2026),
        ("Nov 2017", 2017),
        ("FY2016", 2016),
        ("FY2015", 2015),
        (None, None),
        ("Invalid", None),
    ],
)
def test_normalize_year(input_year, expected):
    assert normalize_year(input_year) == expected


# ===========================
# normalize_ticker()
# ===========================


@pytest.mark.parametrize(
    "input_ticker, expected",
    [
        ("ABB", "ABB"),
        (" abb ", "ABB"),
        ("ABB.NS", "ABB"),
        ("abb.ns", "ABB"),
        ("abb", "ABB"),
        ("TCS", "TCS"),
        ("tcs", "TCS"),
        ("INFY", "INFY"),
        ("infy", "INFY"),
        ("HDFCBANK.NS", "HDFCBANK"),
        ("RELIANCE", "RELIANCE"),
        (" reliance ", "RELIANCE"),
        ("SBIN", "SBIN"),
        ("sbin.ns", "SBIN"),
        (None, None),
    ],
)
def test_normalize_ticker(input_ticker, expected):
    assert normalize_ticker(input_ticker) == expected
