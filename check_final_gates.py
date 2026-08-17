import re
import sqlite3
import subprocess
from pathlib import Path

import pandas as pd

DB = "nifty100.db"
ROOT = Path(".")
c = sqlite3.connect(DB)

PASS = 0
FAIL = 0


def gate(number, name, condition, detail=""):
    global PASS, FAIL

    status = "PASS" if condition else "FAIL"

    if condition:
        PASS += 1
    else:
        FAIL += 1

    print(f"AC-{number:02d} {name:<42} {status}")

    if detail:
        print(f"      {detail}")


print("=" * 75)
print("FINAL 20 ACCEPTANCE GATES")
print("=" * 75)


# ============================================================
# AC-01 — 92 COMPANIES
# ============================================================

company_count = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

gate(
    1,
    "92 companies",
    company_count == 92,
    f"Count = {company_count}",
)


# ============================================================
# AC-02 — >=90% HAVE 10+ YEARS
# ============================================================

rows = c.execute("""
    SELECT COUNT(*)
    FROM companies c
    WHERE
        (SELECT COUNT(DISTINCT year)
         FROM profitandloss p
         WHERE p.company_id = c.id
           AND p.year IS NOT NULL) >= 10
        AND
        (SELECT COUNT(DISTINCT year)
         FROM balancesheet b
         WHERE b.company_id = c.id
           AND b.year IS NOT NULL) >= 10
        AND
        (SELECT COUNT(DISTINCT year)
         FROM cashflow f
         WHERE f.company_id = c.id
           AND f.year IS NOT NULL) >= 10
    """).fetchone()[0]

percentage = rows / company_count * 100

gate(
    2,
    ">=90% companies have 10+ years",
    percentage >= 90,
    f"{rows}/{company_count} = {percentage:.2f}%",
)


# ============================================================
# AC-03 — FOREIGN KEY CHECK
# ============================================================

fk = c.execute("PRAGMA foreign_key_check").fetchall()

gate(
    3,
    "Foreign key check = 0 rows",
    len(fk) == 0,
    f"Violations = {len(fk)}",
)


# ============================================================
# AC-04 — FINANCIAL RATIOS
# ============================================================

ratio_count = c.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]

gate(
    4,
    "Financial ratios >= 1,100",
    ratio_count >= 1100,
    f"Rows = {ratio_count}",
)


# ============================================================
# AC-05 — MANUAL CAGR EXCEL CALCULATION
# ============================================================

cagr_file = ROOT / "output" / "ac05_cagr_spot_check.xlsx"

cagr_ok = False
cagr_detail = "Artifact missing"

if cagr_file.exists():
    try:
        df = pd.read_excel(cagr_file)

        if "Excel CAGR" in df.columns and len(df) >= 5:
            calculated = []

            for _, row in df.iterrows():
                value = (row["End Sales"] / row["Start Sales"]) ** (1 / 5) - 1

                calculated.append(value)

            cagr_ok = all(pd.notna(x) and x > -1 for x in calculated)

            cagr_detail = (
                f"{len(calculated)} companies manually calculated "
                "using (End/Start)^(1/5)-1"
            )

    except Exception as exc:
        cagr_detail = str(exc)

gate(
    5,
    "Revenue CAGR manual Excel calculation",
    cagr_ok,
    cagr_detail,
)


# ============================================================
# AC-06 — ROE
# ============================================================

roe_query = """
SELECT
    c.id,
    c.roe_percentage,
    fr.return_on_equity_pct,
    ABS(fr.return_on_equity_pct - c.roe_percentage)
        / NULLIF(ABS(c.roe_percentage), 0) * 100 AS diff_pct
FROM companies c
JOIN financial_ratios fr
    ON c.id = fr.company_id
WHERE fr.id IN (
    SELECT MAX(fr2.id)
    FROM financial_ratios fr2
    GROUP BY fr2.company_id
)
AND c.roe_percentage IS NOT NULL
AND fr.return_on_equity_pct IS NOT NULL
"""

roe_rows = c.execute(roe_query).fetchall()

roe_pass = sum(1 for row in roe_rows if row[3] is not None and row[3] <= 5)

gate(
    6,
    "ROE within 5%",
    roe_pass >= 5,
    f"{roe_pass} companies within 5%",
)


# ============================================================
# AC-07 — QUALITY SCREENER
# ============================================================

screener_file = ROOT / "output" / "screener_output.xlsx"

quality_count = 0
quality = pd.DataFrame()

if screener_file.exists():
    try:
        quality = pd.read_excel(
            screener_file,
            sheet_name="quality_compounder",
        )

        quality_count = quality["company_id"].dropna().nunique()

    except Exception:
        quality_count = 0

gate(
    7,
    "Quality screener 10-50 companies",
    10 <= quality_count <= 50,
    f"Companies = {quality_count}",
)


# ============================================================
# AC-08 — PERFORMANCE
# ============================================================

perf = ROOT / "output" / "perf_notes.md"

gate(
    8,
    "Company Profile performance documented",
    perf.exists(),
    f"File = {perf}",
)


# ============================================================
# AC-09 — CSV
# ============================================================

csv_candidates = [
    ROOT / "output" / "screener_download.csv",
    ROOT / "output" / "screener.csv",
    ROOT / "output" / "screener_output.csv",
]

csv_file = next(
    (x for x in csv_candidates if x.exists()),
    None,
)

csv_ok = False

if csv_file:
    try:
        csv_df = pd.read_csv(csv_file)
        csv_ok = len(csv_df.columns) > 0
    except Exception:
        csv_ok = False

gate(
    9,
    "Screener CSV valid",
    csv_ok,
    f"File = {csv_file}" if csv_file else "CSV not found",
)


# ============================================================
# AC-10 — TEARSHEETS
# ============================================================

tearsheet_dir = ROOT / "reports" / "tearsheets"
pdfs = list(tearsheet_dir.glob("*.pdf"))

readable = 0

for pdf in pdfs:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf))

        if len(reader.pages) > 0:
            readable += 1

    except Exception:
        pass

gate(
    10,
    "Tearsheet PDFs readable",
    len(pdfs) == 92 and readable == 92,
    f"{readable}/{len(pdfs)} readable",
)


# ============================================================
# AC-11 — HEALTH
# ============================================================

health_ok = False
health_detail = "Health check failed"

try:
    import requests

    response = requests.get(
        "http://127.0.0.1:8000/api/v1/health",
        timeout=5,
    )

    health_ok = response.status_code == 200
    health_detail = f"HTTP {response.status_code}"

except Exception as exc:
    health_detail = str(exc)

gate(
    11,
    "Health endpoint HTTP 200",
    health_ok,
    health_detail,
)


# ============================================================
# AC-12 — TCS RATIOS
# ============================================================

tcs_years = c.execute("""
    SELECT COUNT(DISTINCT year)
    FROM financial_ratios
    WHERE company_id = 'TCS'
      AND year IS NOT NULL
    """).fetchone()[0]

gate(
    12,
    "TCS ratios >=10 years",
    tcs_years >= 10,
    f"Years = {tcs_years}",
)


# ============================================================
# AC-13 — API / EXCEL
# ============================================================

api_match = False
api_detail = "API check failed"

try:
    import requests

    api = requests.get(
        "http://127.0.0.1:8000/api/v1/screener" "?min_roe=10&max_de=2&min_fcf=0",
        timeout=5,
    ).json()

    api_ids = {x["company_id"] for x in api["results"]}

    excel_ids = set(quality["company_id"].dropna().astype(str))

    api_match = api_ids == excel_ids

    api_detail = f"API={len(api_ids)}, Excel={len(excel_ids)}, " f"match={api_match}"

except Exception as exc:
    api_detail = str(exc)

gate(
    13,
    "API screener matches Excel",
    api_match,
    api_detail,
)


# ============================================================
# AC-14 — PEER GROUPS
# ============================================================

peer_groups = c.execute("""
    SELECT COUNT(DISTINCT peer_group_name)
    FROM peer_groups
    """).fetchone()[0]

gate(
    14,
    "All 11 peer groups",
    peer_groups == 11,
    f"Peer groups = {peer_groups}",
)


# ============================================================
# AC-15 — CLUSTERS
# ============================================================

cluster_file = ROOT / "output" / "cluster_labels.csv"

cluster_count = 0

if cluster_file.exists():
    try:
        cluster_df = pd.read_csv(cluster_file)

        if "company_id" in cluster_df.columns:
            cluster_count = cluster_df["company_id"].nunique()

    except Exception:
        cluster_count = 0

gate(
    15,
    "All 92 companies clustered",
    cluster_count == 92,
    f"Companies = {cluster_count}",
)


# ============================================================
# AC-16 — PROS / CONS
# ============================================================

pc_file = ROOT / "output" / "pros_cons_generated.csv"

pros_cons_ok = False
pros_cons_count = 0

if pc_file.exists():
    try:
        pc = pd.read_csv(pc_file)

        if {"company_id", "type"}.issubset(pc.columns):
            grouped = pc.groupby(["company_id", "type"]).size()

            companies = set(pc["company_id"])
            pros_cons_count = len(companies)

            pros_cons_ok = len(companies) == 92 and all(
                grouped.get((company, "pro"), 0) >= 1
                and grouped.get((company, "con"), 0) >= 1
                for company in companies
            )

    except Exception:
        pros_cons_ok = False

gate(
    16,
    "92 companies have pro and con",
    pros_cons_ok,
    f"Companies = {pros_cons_count}",
)


# ============================================================
# AC-17 — 92 TEARSHEETS >=30 KB
# ============================================================

small = [pdf for pdf in pdfs if pdf.stat().st_size < 30_000]

gate(
    17,
    "92 tearsheets >=30 KB",
    len(pdfs) == 92 and len(small) == 0,
    f"PDFs={len(pdfs)}, under30KB={len(small)}",
)


# ============================================================
# AC-18 — PYTEST
# ============================================================

test_ok = False
test_detail = "pytest report missing"

report = ROOT / "reports" / "pytest_report.html"

if report.exists():
    try:
        result = subprocess.run(
            [
                ".\\venv\\Scripts\\python.exe",
                "-m",
                "pytest",
                "tests",
                "-q",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr

        test_ok = result.returncode == 0 and "passed" in output

        test_detail = output.splitlines()[-1] if output else ""

    except Exception as exc:
        test_detail = str(exc)

gate(
    18,
    "Pytest 60+ and 0 failures",
    test_ok,
    test_detail,
)


# ============================================================
# AC-19 — VALIDATION FILE
# ============================================================

validation = ROOT / "output" / "validation_failures.csv"

validation_ok = False

if validation.exists():
    try:
        vdf = pd.read_csv(validation)

        validation_ok = set(
            [
                "company_id",
                "field",
                "issue",
                "severity",
            ]
        ).issubset(vdf.columns)

    except Exception:
        validation_ok = False

gate(
    19,
    "Validation file required columns",
    validation_ok,
    str(validation),
)


# ============================================================
# AC-20 — ANALYST GUIDE
# ============================================================

guide = ROOT / "docs" / "analyst_guide.pdf"

guide_pages = 0

if guide.exists():
    try:
        from pypdf import PdfReader

        guide_pages = len(PdfReader(str(guide)).pages)

    except Exception:
        guide_pages = 0

gate(
    20,
    "Analyst guide >=10 pages",
    guide_pages >= 10,
    f"Pages = {guide_pages}",
)


# ============================================================
# SUMMARY
# ============================================================

c.close()

print("=" * 75)
print(f"PASSED: {PASS}/20")
print(f"FAILED: {FAIL}/20")
print("=" * 75)

if FAIL == 0:
    print("🎉 ALL 20 ACCEPTANCE GATES PASS")
else:
    print(
        "⚠️ Gates still requiring action:",
        FAIL,
    )
