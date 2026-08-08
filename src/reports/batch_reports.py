import sqlite3
from pathlib import Path

import pandas as pd

from tearsheet import build_tearsheet


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "nifty100.db"

OUTPUT_DIR = BASE_DIR / "reports" / "tearsheets"
SECTOR_DIR = BASE_DIR / "reports" / "sectors"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SECTOR_DIR.mkdir(parents=True, exist_ok=True)

SKIPPED_FILE = (
    BASE_DIR
    / "output"
    / "skipped_tearsheets.csv"
)


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


# ==========================================================
# COMPANY LIST
# ==========================================================

companies = companies.drop_duplicates(
    subset=["company_id"]
)

print("Companies :", len(companies))


# ==========================================================
# BATCH TEARSHEETS
# ==========================================================

skipped = []

successful = 0

for company_id in companies["company_id"]:

    try:

        result = build_tearsheet(company_id)

        if result:

            successful += 1

        else:

            skipped.append({
                "company_id": company_id,
                "reason": "No data available",
            })

    except Exception as exc:

        skipped.append({
            "company_id": company_id,
            "reason": str(exc),
        })


# ==========================================================
# SAVE SKIPPED
# ==========================================================

skipped_df = pd.DataFrame(skipped)

skipped_df.to_csv(
    SKIPPED_FILE,
    index=False,
)


# ==========================================================
# SECTOR REPORTS
# ==========================================================

sector_map = sectors.drop_duplicates(
    subset=["company_id"]
)

company_sector = companies.merge(
    sector_map,
    on="company_id",
    how="left",
)

sector_counts = (
    company_sector["broad_sector"]
    .value_counts(dropna=False)
)

print()
print("Sector Distribution:")
print(sector_counts)


# ==========================================================
# GENERATE SECTOR SUMMARY PDFs
# ==========================================================

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm


styles = getSampleStyleSheet()


for sector, group in company_sector.groupby(
    "broad_sector",
    dropna=False
):

    sector_name = (
        "Unknown"
        if pd.isna(sector)
        else str(sector)
    )

    safe_name = (
        sector_name
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    output_file = (
        SECTOR_DIR
        / f"{safe_name}_sector_report.pdf"
    )

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []

    story.append(
        Paragraph(
            f"{sector_name} — Sector Report",
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            f"Companies: {len(group)}",
            styles["Normal"],
        )
    )

    story.append(
        Spacer(1, 10)
    )

    table_data = [
        [
            "Company ID",
            "Company Name",
        ]
    ]

    for _, row in group.iterrows():

        table_data.append(
            [
                str(row["company_id"]),
                str(row["company_name"]),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            45 * mm,
            115 * mm,
        ],
    )

    table.setStyle(
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
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ]
        )
    )

    story.append(table)

    doc.build(story)

    print(
        f"Sector report created: {output_file}"
    )


# ==========================================================
# FINAL SUMMARY
# ==========================================================

print()
print("=" * 60)
print("DAY 34 COMPLETED")
print("=" * 60)

print()

print(
    "Successful company PDFs :",
    successful,
)

print(
    "Skipped company PDFs :",
    len(skipped_df),
)

print(
    "Sector reports :",
    company_sector["broad_sector"]
    .nunique(),
)

print()

print(
    "Skipped file :",
    SKIPPED_FILE,
)

conn.close()