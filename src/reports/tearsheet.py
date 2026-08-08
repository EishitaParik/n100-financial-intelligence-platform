import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "tearsheets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEMP_DIR = BASE_DIR / "reports" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================================
# DATABASE
# ==========================================================

conn = sqlite3.connect(DB_PATH)

company_query = """
SELECT
    c.id AS company_id,
    c.company_name,
    c.roce_percentage,
    c.roe_percentage
FROM companies c
"""

companies = pd.read_sql(company_query, conn)

# ==========================================================
# STYLES
# ==========================================================

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    fontSize=20,
    leading=24,
    alignment=TA_CENTER,
    spaceAfter=10,
)

heading_style = ParagraphStyle(
    "HeadingCustom",
    parent=styles["Heading2"],
    fontSize=12,
    leading=15,
    spaceBefore=8,
    spaceAfter=6,
)

body_style = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11,
)

small_style = ParagraphStyle(
    "SmallCustom",
    parent=styles["BodyText"],
    fontSize=7,
    leading=9,
)

# ==========================================================
# DATA HELPERS
# ==========================================================

def get_company_data(company_id):

    ratio_query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year
    """

    ratios = pd.read_sql(
        ratio_query,
        conn,
        params=[company_id],
    )

    analysis_query = """
    SELECT *
    FROM analysis
    WHERE company_id = ?
    """

    analysis = pd.read_sql(
        analysis_query,
        conn,
        params=[company_id],
    )

    market_query = """
    SELECT *
    FROM market_cap
    WHERE company_id = ?
    ORDER BY year
    """

    market = pd.read_sql(
        market_query,
        conn,
        params=[company_id],
    )

    cashflow_query = """
    SELECT *
    FROM cashflow
    WHERE company_id = ?
    ORDER BY year
    """

    cashflow = pd.read_sql(
        cashflow_query,
        conn,
        params=[company_id],
    )

    return ratios, analysis, market, cashflow


def get_pros_cons(company_id):

    file = BASE_DIR / "output" / "pros_cons_generated.csv"

    if not file.exists():
        return pd.DataFrame(), pd.DataFrame()

    data = pd.read_csv(file)

    company_data = data[
        data["company_id"] == company_id
    ]

    pros = company_data[
        company_data["type"].str.lower() == "pro"
    ]

    cons = company_data[
        company_data["type"].str.lower() == "con"
    ]

    return pros, cons


def get_capital_allocation(company_id):

    file = (
        BASE_DIR
        / "output"
        / "cashflow_intelligence.xlsx"
    )

    if not file.exists():
        return None

    data = pd.read_excel(file)

    company_data = data[
        data["company_id"] == company_id
    ]

    if company_data.empty:
        return None

    return company_data.iloc[-1].get(
        "capital_allocation"
    )


# ==========================================================
# CHARTS
# ==========================================================

def create_growth_chart(company_id, ratios):

    if ratios.empty:
        return None

    required = [
        "year",
        "earnings_per_share",
    ]

    if not all(
        column in ratios.columns
        for column in required
    ):
        return None

    data = ratios.dropna(
        subset=["year", "earnings_per_share"]
    ).copy()

    if data.empty:
        return None

    path = TEMP_DIR / f"{company_id}_growth.png"

    plt.figure(figsize=(6, 2.5))

    plt.plot(
        data["year"],
        data["earnings_per_share"],
        marker="o",
    )

    plt.title("EPS Trend")

    plt.xlabel("Year")
    plt.ylabel("EPS")

    plt.tight_layout()

    plt.savefig(path, dpi=150)

    plt.close()

    return path


def create_cashflow_chart(company_id, cashflow):

    if cashflow.empty:
        return None

    required = [
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
    ]

    if not all(
        column in cashflow.columns
        for column in required
    ):
        return None

    data = cashflow.dropna(
        subset=required
    ).tail(8)

    if data.empty:
        return None

    path = TEMP_DIR / f"{company_id}_cashflow.png"

    plt.figure(figsize=(6, 2.5))

    plt.plot(
        data["year"],
        data["operating_activity"],
        marker="o",
        label="Operating",
    )

    plt.plot(
        data["year"],
        data["investing_activity"],
        marker="o",
        label="Investing",
    )

    plt.plot(
        data["year"],
        data["financing_activity"],
        marker="o",
        label="Financing",
    )

    plt.title("Cash Flow Trend")

    plt.legend(
        fontsize=7
    )

    plt.tight_layout()

    plt.savefig(path, dpi=150)

    plt.close()

    return path


# ==========================================================
# TEARSHEET
# ==========================================================

def build_tearsheet(company_id):

    company_match = companies[
        companies["company_id"] == company_id
    ]

    if company_match.empty:
        print(
            f"Skipping {company_id}: company not found"
        )
        return False

    company = company_match.iloc[0]

    ratios, analysis, market, cashflow = (
        get_company_data(company_id)
    )

    if ratios.empty:
        print(
            f"Skipping {company_id}: no ratio data"
        )
        return False

    pros, cons = get_pros_cons(company_id)

    allocation = get_capital_allocation(
        company_id
    )

    company_name = company["company_name"]

    output_file = (
        OUTPUT_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    story = []

    # ------------------------------------------------------
    # TITLE
    # ------------------------------------------------------

    story.append(
        Paragraph(
            f"{company_name}",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"Company ID: {company_id}",
            body_style,
        )
    )

    story.append(Spacer(1, 5))

    # ------------------------------------------------------
    # KPI TILES
    # ------------------------------------------------------

    latest = ratios.iloc[-1]

    def safe_number(value, suffix=""):
        if pd.isna(value):
            return "N/A"

        try:
            return f"{float(value):.2f}{suffix}"
        except (TypeError, ValueError):
            return "N/A"


    kpis = [
        [
            "ROE",
            safe_number(
                latest.get("return_on_equity_pct"),
                "%"
            ),
        ],
        [
            "D/E",
            safe_number(
                latest.get("debt_to_equity")
            ),
        ],
        [
            "OPM",
            safe_number(
                latest.get("operating_profit_margin_pct"),
                "%"
            ),
        ],
        [
            "FCF",
            safe_number(
                latest.get("free_cash_flow_cr")
            ),
        ],
    ]

    table = Table(
        kpis,
        colWidths=[
            42 * mm,
            42 * mm,
        ] * 2,
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 10))

    # ------------------------------------------------------
    # GROWTH
    # ------------------------------------------------------

    story.append(
        Paragraph(
            "Financial Performance",
            heading_style,
        )
    )

    growth_chart = create_growth_chart(
        company_id,
        ratios,
    )

    if growth_chart:

        story.append(
            Image(
                str(growth_chart),
                width=170 * mm,
                height=65 * mm,
            )
        )

    # ------------------------------------------------------
    # CAPITAL ALLOCATION
    # ------------------------------------------------------

    story.append(
        Paragraph(
            "Capital Allocation",
            heading_style,
        )
    )

    allocation_text = (
        allocation
        if allocation is not None
        else "Not Available"
    )

    story.append(
        Paragraph(
            f"<b>Latest Pattern:</b> {allocation_text}",
            body_style,
        )
    )

    story.append(Spacer(1, 5))

    # ------------------------------------------------------
    # CASH FLOW
    # ------------------------------------------------------

    cashflow_chart = create_cashflow_chart(
        company_id,
        cashflow,
    )

    if cashflow_chart:

        story.append(
            Image(
                str(cashflow_chart),
                width=170 * mm,
                height=65 * mm,
            )
        )

    # ------------------------------------------------------
    # PAGE 2
    # ------------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Investment Snapshot",
            title_style,
        )
    )

    # ------------------------------------------------------
    # ANALYSIS
    # ------------------------------------------------------

    if not analysis.empty:

        analysis_row = analysis.iloc[0]

        analysis_data = [
            [
                "Sales CAGR",
                str(
                    analysis_row.get(
                        "compounded_sales_growth",
                        "N/A",
                    )
                ),
            ],
            [
                "Profit CAGR",
                str(
                    analysis_row.get(
                        "compounded_profit_growth",
                        "N/A",
                    )
                ),
            ],
            [
                "Stock CAGR",
                str(
                    analysis_row.get(
                        "stock_price_cagr",
                        "N/A",
                    )
                ),
            ],
            [
                "ROE",
                str(
                    analysis_row.get(
                        "roe",
                        "N/A",
                    )
                ),
            ],
        ]

        analysis_table = Table(
            analysis_data,
            colWidths=[
                55 * mm,
                110 * mm,
            ],
        )

        analysis_table.setStyle(
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
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(analysis_table)

    # ------------------------------------------------------
    # PROS
    # ------------------------------------------------------

    story.append(
        Paragraph(
            "Pros",
            heading_style,
        )
    )

    if pros.empty:

        story.append(
            Paragraph(
                "No generated pros available.",
                body_style,
            )
        )

    else:

        for _, item in pros.head(6).iterrows():

            story.append(
                Paragraph(
                    f"• {item['text']} "
                    f"({item['confidence_pct']}%)",
                    body_style,
                )
            )

    # ------------------------------------------------------
    # CONS
    # ------------------------------------------------------

    story.append(
        Paragraph(
            "Cons",
            heading_style,
        )
    )

    if cons.empty:

        story.append(
            Paragraph(
                "No generated cons available.",
                body_style,
            )
        )

    else:

        for _, item in cons.head(6).iterrows():

            story.append(
                Paragraph(
                    f"• {item['text']} "
                    f"({item['confidence_pct']}%)",
                    body_style,
                )
            )

    # ------------------------------------------------------
    # BUILD PDF
    # ------------------------------------------------------

    doc.build(story)

    print(
        f"Created: {output_file}"
    )

    return True


