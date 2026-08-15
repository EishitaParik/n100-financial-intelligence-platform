import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "portfolio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "portfolio_summary.pdf"


# ==========================================================
# DATABASE
# ==========================================================

conn = sqlite3.connect(DB_PATH)


companies = pd.read_sql(
    """
    SELECT
        id AS company_id,
        company_name
    FROM companies
    """,
    conn,
)


sectors = pd.read_sql(
    """
    SELECT
        company_id,
        broad_sector
    FROM sectors
    """,
    conn,
)


ratios = pd.read_sql(
    """
    SELECT *
    FROM financial_ratios
    ORDER BY company_id, year
    """,
    conn,
)


# ==========================================================
# CLEAN DATA
# ==========================================================

companies = companies.drop_duplicates(subset=["company_id"])

sectors = sectors.drop_duplicates(subset=["company_id"])


df = ratios.merge(
    companies,
    on="company_id",
    how="left",
)

df = df.merge(
    sectors,
    on="company_id",
    how="left",
)


df = df.sort_values(["company_id", "year"])


# ==========================================================
# HELPERS
# ==========================================================


def clean_value(value):

    if pd.isna(value):
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


def format_value(value, suffix=""):

    value = clean_value(value)

    if value is None:
        return "N/A"

    return f"{value:,.2f}{suffix}"


def trend_arrow(previous, latest):

    previous = clean_value(previous)
    latest = clean_value(latest)

    if previous is None or latest is None:
        return "→"

    if previous == 0:
        if latest > 0:
            return "↑"
        if latest < 0:
            return "↓"
        return "→"

    change = abs((latest - previous) / abs(previous))

    if change <= 0.02:
        return "→"

    if latest > previous:
        return "↑"

    return "↓"


def latest_two_years(company_data, column):

    data = company_data[["year", column]].dropna()

    if len(data) < 2:
        return None, None

    data = data.sort_values("year")

    return (
        data.iloc[-2][column],
        data.iloc[-1][column],
    )


# ==========================================================
# PDF STYLES
# ==========================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "PortfolioTitle",
    parent=styles["Title"],
    fontSize=19,
    leading=23,
    alignment=TA_CENTER,
    spaceAfter=8,
)

subtitle_style = ParagraphStyle(
    "PortfolioSubtitle",
    parent=styles["Normal"],
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    spaceAfter=12,
)

heading_style = ParagraphStyle(
    "PortfolioHeading",
    parent=styles["Heading2"],
    fontSize=12,
    leading=15,
    spaceAfter=7,
)

body_style = ParagraphStyle(
    "PortfolioBody",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11,
)


# ==========================================================
# PDF
# ==========================================================

doc = SimpleDocTemplate(
    str(OUTPUT_FILE),
    pagesize=A4,
    rightMargin=15 * mm,
    leftMargin=15 * mm,
    topMargin=15 * mm,
    bottomMargin=15 * mm,
)


story = []


# ==========================================================
# COMPANY PAGES
# ==========================================================

company_ids = sorted(companies["company_id"].tolist())


generated = 0


for company_id in company_ids:

    company_data = df[df["company_id"] == company_id].sort_values("year")

    if company_data.empty:
        continue

    latest = company_data.iloc[-1]

    company_name = latest.get(
        "company_name",
        company_id,
    )

    sector = latest.get(
        "broad_sector",
        "Unknown",
    )

    if pd.isna(sector):
        sector = "Unknown"

    # ------------------------------------------------------
    # TITLE
    # ------------------------------------------------------

    story.append(
        Paragraph(
            str(company_name),
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Ticker:</b> {company_id} &nbsp;&nbsp; " f"<b>Sector:</b> {sector}",
            subtitle_style,
        )
    )

    # ------------------------------------------------------
    # TOP 6 KPIs
    # ------------------------------------------------------

    kpi_definitions = [
        (
            "ROE",
            "return_on_equity_pct",
            "%",
        ),
        (
            "Net Profit Margin",
            "net_profit_margin_pct",
            "%",
        ),
        (
            "Operating Margin",
            "operating_profit_margin_pct",
            "%",
        ),
        (
            "Debt / Equity",
            "debt_to_equity",
            "",
        ),
        (
            "Interest Coverage",
            "interest_coverage",
            "x",
        ),
        (
            "Free Cash Flow",
            "free_cash_flow_cr",
            "",
        ),
    ]

    kpi_rows = []

    for label, column, suffix in kpi_definitions:

        previous, current = latest_two_years(
            company_data,
            column,
        )

        arrow = trend_arrow(
            previous,
            current,
        )

        value_text = format_value(
            current,
            suffix,
        )

        kpi_rows.append(
            [
                label,
                value_text,
                arrow,
            ]
        )

    kpi_table = Table(
        kpi_rows,
        colWidths=[
            72 * mm,
            60 * mm,
            20 * mm,
        ],
    )

    kpi_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.whitesmoke,
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(kpi_table)

    story.append(Spacer(1, 12))

    # ------------------------------------------------------
    # TREND SUMMARY
    # ------------------------------------------------------

    story.append(
        Paragraph(
            "Latest-Year Trend Summary",
            heading_style,
        )
    )

    trend_rows = [
        [
            "Metric",
            "Previous",
            "Latest",
            "Trend",
        ]
    ]

    for label, column, suffix in kpi_definitions:

        previous, current = latest_two_years(
            company_data,
            column,
        )

        trend_rows.append(
            [
                label,
                format_value(previous, suffix),
                format_value(current, suffix),
                trend_arrow(previous, current),
            ]
        )

    trend_table = Table(
        trend_rows,
        colWidths=[
            60 * mm,
            40 * mm,
            40 * mm,
            20 * mm,
        ],
    )

    trend_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(trend_table)

    story.append(Spacer(1, 15))

    # ------------------------------------------------------
    # DATA COVERAGE
    # ------------------------------------------------------

    years = company_data["year"].dropna()

    if not years.empty:

        story.append(
            Paragraph(
                f"<b>Data coverage:</b> "
                f"{int(years.min())} – {int(years.max())} "
                f"({len(years)} financial observations)",
                body_style,
            )
        )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "Trend arrows: ↑ improved, ↓ declined, " "→ flat within 2%.",
            body_style,
        )
    )

    generated += 1

    # ------------------------------------------------------
    # NEXT COMPANY
    # ------------------------------------------------------

    story.append(PageBreak())


# ==========================================================
# BUILD
# ==========================================================

doc.build(story)


print()
print("=" * 60)
print("DAY 35 PORTFOLIO REPORT GENERATED")
print("=" * 60)
print()
print("Companies :", generated)
print("Output :", OUTPUT_FILE)


conn.close()
