from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib import colors


OUTPUT = "docs/analyst_guide.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45,
)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=24,
    spaceAfter=20,
)

heading = ParagraphStyle(
    "HeadingCustom",
    parent=styles["Heading1"],
    fontSize=18,
    spaceBefore=10,
    spaceAfter=12,
)

subheading = ParagraphStyle(
    "SubHeadingCustom",
    parent=styles["Heading2"],
    fontSize=13,
    spaceBefore=8,
    spaceAfter=8,
)

body = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontSize=10,
    leading=15,
    spaceAfter=8,
)

small = ParagraphStyle(
    "SmallCustom",
    parent=styles["BodyText"],
    fontSize=9,
    leading=13,
)


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(
        A4[0] / 2,
        25,
        f"Page {doc.page}",
    )
    canvas.restoreState()


story = []


# ---------------------------------------------------------
# PAGE 1
# ---------------------------------------------------------

story.append(Paragraph(
    "N100 Financial Intelligence Platform",
    title,
))

story.append(Paragraph(
    "Analyst User Guide",
    styles["Heading2"],
))

story.append(Spacer(1, 30))

story.append(Paragraph(
    "<b>Purpose</b>",
    heading,
))

story.append(Paragraph(
    "This guide explains how an analyst can use the N100 Financial "
    "Intelligence Platform to explore company financials, screen "
    "companies, compare peers, analyse sectors and trends, review "
    "capital structure information, and generate company reports.",
    body,
))

story.append(Paragraph(
    "<b>Platform components</b>",
    heading,
))

data = [
    ["Component", "Purpose"],
    ["Streamlit Dashboard", "Interactive analyst interface"],
    ["FastAPI", "Programmatic access to financial data"],
    ["SQLite Database", "Central financial data store"],
    ["Analytics Engine", "Ratios, clustering and financial analytics"],
    ["Reports", "Tearsheet and analytical outputs"],
]

table = Table(data, colWidths=[150, 300])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("PADDING", (0, 0), (-1, -1), 7),
]))

story.append(table)
story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 2
# ---------------------------------------------------------

story.append(Paragraph("1. Getting Started", heading))

story.append(Paragraph(
    "The platform uses a SQLite database named nifty100.db. "
    "The interactive dashboard is implemented with Streamlit and "
    "the API layer is implemented using FastAPI.",
    body,
))

story.append(Paragraph("Starting the API", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    ".\\venv\\Scripts\\python.exe -m uvicorn "
    "src.api.main:app --port 8000"
    "</font>",
    body,
))

story.append(Paragraph(
    "The API is available at http://127.0.0.1:8000.",
    body,
))

story.append(Paragraph("Starting the dashboard", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "streamlit run src\\dashboard\\app.py --server.port 8501"
    "</font>",
    body,
))

story.append(Paragraph(
    "The dashboard is available at http://localhost:8501.",
    body,
))

story.append(Paragraph("Recommended startup order", subheading))

story.append(Paragraph(
    "1. Activate the virtual environment.<br/>"
    "2. Start FastAPI on port 8000.<br/>"
    "3. Start Streamlit on port 8501.<br/>"
    "4. Open the Streamlit dashboard in a browser.<br/>"
    "5. Verify the API health endpoint if required.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 3
# ---------------------------------------------------------

story.append(Paragraph("2. Home Dashboard", heading))

story.append(Paragraph(
    "The Home screen provides the starting point for analyst "
    "navigation. It is intended to provide a high-level view "
    "before moving into detailed company or analytical screens.",
    body,
))

story.append(Paragraph("Typical workflow", subheading))

story.append(Paragraph(
    "Start with the overall market/company view, identify an "
    "interesting company or sector, and then move to the relevant "
    "detail screen.",
    body,
))

story.append(Paragraph("Analyst use cases", subheading))

story.append(Paragraph(
    "• Discover companies for further research.<br/>"
    "• Navigate to company profiles.<br/>"
    "• Identify sectors requiring deeper analysis.<br/>"
    "• Move from high-level information to detailed financial metrics.",
    body,
))

story.append(Paragraph(
    "The dashboard is designed so that an analyst can progressively "
    "move from overview information toward quantitative analysis.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 4
# ---------------------------------------------------------

story.append(Paragraph("3. Company Profile", heading))

story.append(Paragraph(
    "The Company Profile screen is used for detailed analysis of "
    "an individual company.",
    body,
))

story.append(Paragraph("Selecting a company", subheading))

story.append(Paragraph(
    "Select a company ticker such as TCS, INFY, HDFCBANK, RELIANCE "
    "or ITC. The profile screen retrieves company-specific financial "
    "information from the underlying database/API layer.",
    body,
))

story.append(Paragraph("What to examine", subheading))

story.append(Paragraph(
    "• Company identity and sector.<br/>"
    "• Historical financial ratios.<br/>"
    "• Profitability measures.<br/>"
    "• Capital structure.<br/>"
    "• Cash-flow information.<br/>"
    "• Historical trends.",
    body,
))

story.append(Paragraph(
    "The Company Profile is particularly useful when an analyst "
    "has already identified a company through the screener and "
    "wants to investigate it further.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 5
# ---------------------------------------------------------

story.append(Paragraph("4. Screener", heading))

story.append(Paragraph(
    "The Screener allows analysts to filter companies according "
    "to financial criteria.",
    body,
))

story.append(Paragraph("Available filtering concepts", subheading))

story.append(Paragraph(
    "The API supports filters including minimum ROE, maximum debt "
    "to equity, minimum free cash flow, sector, revenue CAGR, "
    "profit CAGR and maximum P/E.",
    body,
))

story.append(Paragraph("Example", subheading))

story.append(Paragraph(
    "A request such as <font name='Courier'>"
    "/api/v1/screener?min_roe=15"
    "</font> returns companies whose return on equity is at least 15.",
    body,
))

story.append(Paragraph("Analyst workflow", subheading))

story.append(Paragraph(
    "1. Set the desired financial filters.<br/>"
    "2. Review the returned companies.<br/>"
    "3. Identify candidates for further analysis.<br/>"
    "4. Open individual Company Profiles.<br/>"
    "5. Compare candidates with peer companies.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 6
# ---------------------------------------------------------

story.append(Paragraph("5. Peer Comparison", heading))

story.append(Paragraph(
    "Peer analysis allows an analyst to compare companies operating "
    "within a relevant peer group.",
    body,
))

story.append(Paragraph("Example API calls", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "GET /api/v1/peers/Private%20Banks"
    "</font>",
    body,
))

story.append(Paragraph(
    "<font name='Courier'>"
    "GET /api/v1/companies/TCS/peers/compare"
    "</font>",
    body,
))

story.append(Paragraph(
    "The first request retrieves companies belonging to a peer group. "
    "The second provides a company-level comparison against the "
    "company's peer group.",
    body,
))

story.append(Paragraph(
    "Use peer analysis to determine whether a company's profitability, "
    "capital structure or other metrics are strong or weak relative "
    "to comparable businesses.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 7
# ---------------------------------------------------------

story.append(Paragraph("6. Trends and Sector Analysis", heading))

story.append(Paragraph(
    "The Trends and Sectors screens provide broader analytical "
    "context beyond a single company.",
    body,
))

story.append(Paragraph("Sector analysis", subheading))

story.append(Paragraph(
    "The platform contains sectors including Communication Services, "
    "Consumer Discretionary, Consumer Staples, Energy, Financials, "
    "Healthcare, Industrials, Information Technology, Materials and "
    "Real Estate.",
    body,
))

story.append(Paragraph(
    "For example, Information Technology contains companies such as "
    "HCL Technologies, Infosys, LTIMindtree, TCS and Tech Mahindra.",
    body,
))

story.append(Paragraph("Analyst workflow", subheading))

story.append(Paragraph(
    "Compare sector-level profitability and then drill down to "
    "individual companies. Sector analysis is useful for identifying "
    "relative strengths and weaknesses across industries.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 8
# ---------------------------------------------------------

story.append(Paragraph("7. Capital Analysis", heading))

story.append(Paragraph(
    "The Capital screen is intended to help analysts evaluate "
    "capital structure and financial strength.",
    body,
))

story.append(Paragraph(
    "Important metrics include debt to equity, interest coverage, "
    "free cash flow, cash generated from operations and other "
    "capital-related measures.",
    body,
))

story.append(Paragraph("Interpretation", subheading))

story.append(Paragraph(
    "Lower leverage can indicate a stronger balance sheet, although "
    "appropriate leverage depends on the company's industry. "
    "Interest coverage provides an indication of the company's "
    "ability to service interest obligations.",
    body,
))

story.append(Paragraph(
    "Always interpret capital metrics alongside sector characteristics "
    "rather than using one ratio in isolation.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 9
# ---------------------------------------------------------

story.append(Paragraph("8. Reports and Tearsheet Generation", heading))

story.append(Paragraph(
    "The Reports screen provides access to generated analytical "
    "outputs and company reports.",
    body,
))

story.append(Paragraph("Tearsheets", subheading))

story.append(Paragraph(
    "Company tearsheets consolidate important financial information "
    "into a report suitable for analyst review.",
    body,
))

story.append(Paragraph("Recommended workflow", subheading))

story.append(Paragraph(
    "1. Identify the company.<br/>"
    "2. Review its Company Profile.<br/>"
    "3. Review peer comparison.<br/>"
    "4. Review financial and capital metrics.<br/>"
    "5. Generate or open the corresponding tearsheet.",
    body,
))

story.append(Paragraph(
    "Generated reports should be checked for readability, complete "
    "content and absence of text overflow before final use.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 10
# ---------------------------------------------------------

story.append(Paragraph("9. API Usage", heading))

story.append(Paragraph(
    "FastAPI exposes programmatic access to the platform's financial "
    "data and analytics.",
    body,
))

story.append(Paragraph("Health check", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "curl http://127.0.0.1:8000/api/v1/health"
    "</font>",
    body,
))

story.append(Paragraph("Sector list", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "curl http://127.0.0.1:8000/api/v1/sectors"
    "</font>",
    body,
))

story.append(Paragraph("Sector companies", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "curl http://127.0.0.1:8000/api/v1/sectors/"
    "Information%20Technology/companies"
    "</font>",
    body,
))

story.append(Paragraph("Screener", subheading))

story.append(Paragraph(
    "<font name='Courier'>"
    "curl \"http://127.0.0.1:8000/api/v1/screener?min_roe=15\""
    "</font>",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 11
# ---------------------------------------------------------

story.append(Paragraph("10. API Endpoints and Data Access", heading))

story.append(Paragraph(
    "The API includes endpoints for health checks, company data, "
    "sectors, screening, market-cap history, portfolio statistics, "
    "documents and peer analysis.",
    body,
))

endpoint_data = [
    ["Endpoint", "Purpose"],
    ["/api/v1/health", "API/database health"],
    ["/api/v1/sectors", "Sector-level information"],
    ["/api/v1/sectors/{sector}/companies", "Companies in sector"],
    ["/api/v1/companies", "Company listing"],
    ["/api/v1/companies/{ticker}", "Company profile"],
    ["/api/v1/screener", "Financial screening"],
    ["/api/v1/portfolio/stats", "Portfolio KPI statistics"],
    ["/api/v1/peers/{group}", "Peer group companies"],
    ["/api/v1/companies/{ticker}/peers/compare", "Peer comparison"],
]

table = Table(endpoint_data, colWidths=[220, 230])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("PADDING", (0, 0), (-1, -1), 5),
]))

story.append(table)
story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 12
# ---------------------------------------------------------

story.append(Paragraph("11. Troubleshooting", heading))

story.append(Paragraph("Port 8000 already in use", subheading))

story.append(Paragraph(
    "Find the process using port 8000:",
    body,
))

story.append(Paragraph(
    "<font name='Courier'>netstat -ano | findstr :8000</font>",
    body,
))

story.append(Paragraph(
    "Terminate the process using its actual PID:",
    body,
))

story.append(Paragraph(
    "<font name='Courier'>taskkill /PID &lt;PID&gt; /F</font>",
    body,
))

story.append(Paragraph("Python import errors", subheading))

story.append(Paragraph(
    "Set the project root as PYTHONPATH:",
    body,
))

story.append(Paragraph(
    "<font name='Courier'>$env:PYTHONPATH = (Get-Location).Path</font>",
    body,
))

story.append(Paragraph("Testing", subheading))

story.append(Paragraph(
    "Run the complete test suite:",
    body,
))

story.append(Paragraph(
    "<font name='Courier'>pytest tests\\ -v</font>",
    body,
))

story.append(Paragraph(
    "The project should be run from the repository root with the "
    "virtual environment activated.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 13
# ---------------------------------------------------------

story.append(Paragraph("12. Testing and Performance", heading))

story.append(Paragraph(
    "The project includes automated tests covering ETL normalization, "
    "financial KPIs, data-quality rules, API endpoints and performance.",
    body,
))

story.append(Paragraph(
    "The completed test suite contains 92 tests, all of which passed "
    "during the Day 43 verification.",
    body,
))

story.append(Paragraph("Performance results", subheading))

story.append(Paragraph(
    "The concurrent API load test completed 10 screener requests "
    "within approximately 1.28 seconds total, below the 10-second "
    "requirement.",
    body,
))

story.append(Paragraph(
    "The five sampled company profiles loaded substantially below "
    "the three-second requirement.",
    body,
))

story.append(Paragraph(
    "FastAPI and Streamlit were also verified running simultaneously "
    "on ports 8000 and 8501.",
    body,
))

story.append(PageBreak())


# ---------------------------------------------------------
# PAGE 14
# ---------------------------------------------------------

story.append(Paragraph("13. Analyst Workflow Summary", heading))

story.append(Paragraph(
    "A recommended end-to-end research workflow is:",
    body,
))

story.append(Paragraph(
    "1. Open the dashboard.<br/>"
    "2. Review the overall market/company information.<br/>"
    "3. Use the Screener to identify candidate companies.<br/>"
    "4. Open the Company Profile for detailed financial analysis.<br/>"
    "5. Review Peer Comparison.<br/>"
    "6. Examine sector and trend information.<br/>"
    "7. Review capital structure and cash-flow metrics.<br/>"
    "8. Generate or review the company tearsheet.<br/>"
    "9. Use API endpoints when programmatic access is required.<br/>"
    "10. Record conclusions and validate important figures before "
    "using them in investment or analytical decisions.",
    body,
))

story.append(Paragraph(
    "The platform should be treated as an analytical decision-support "
    "system. Financial metrics should be interpreted in context and "
    "not used as the sole basis for investment decisions.",
    body,
))

story.append(Spacer(1, 30))

story.append(Paragraph(
    "End of Analyst Guide",
    styles["Heading2"],
))

doc.build(
    story,
    onFirstPage=page_number,
    onLaterPages=page_number,
)

print(f"Created {OUTPUT}")