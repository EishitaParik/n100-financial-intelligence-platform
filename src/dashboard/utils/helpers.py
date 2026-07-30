import pandas as pd


def safe_value(value, default="N/A", decimals=2):
    """
    Safely format numeric/text values for display.
    """

    if value is None:
        return default

    if pd.isna(value):
        return default

    try:
        return round(float(value), decimals)
    except Exception:
        return value


def safe_metric(value, suffix="", decimals=2):
    """
    Returns a formatted metric value for Streamlit KPI cards.
    """

    value = safe_value(value, default="N/A", decimals=decimals)

    if value == "N/A":
        return value

    return f"{value}{suffix}"

