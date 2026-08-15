"""
Cash Flow KPI Functions
Sprint 2 - Day 11
"""


def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow

    Formula:
    CFO + Investing Activity
    """

    return operating_activity + investing_activity


def cfo_quality_score(cfo, pat):
    """
    CFO Quality Score
    """

    if pat == 0:
        return None

    ratio = cfo / pat

    if ratio > 1:
        return "High Quality"

    if ratio >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity
    """

    if sales == 0:
        return None

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        return "Asset Light"

    if intensity <= 8:
        return "Moderate"

    return "Capital Intensive"


def fcf_conversion(fcf, operating_profit):
    """
    FCF Conversion
    """

    if operating_profit == 0:
        return None

    return (fcf / operating_profit) * 100


def capital_allocation_pattern(cfo, cfi, cff):
    """
    Classify capital allocation pattern
    """

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-",
    )

    patterns = {
        ("+", "-", "-"): "Reinvestor",
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    return patterns.get(signs, "Unknown")
