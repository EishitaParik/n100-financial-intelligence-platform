# Sprint 5 Retrospective — N100 Financial Intelligence Platform

## Sprint Goal

Build the financial intelligence and reporting layer for the N100 Financial Intelligence Platform, including automated pros/cons generation, cash-flow intelligence, capital-allocation analysis, company tearsheets, sector reports, and a portfolio summary.

## Completed

### Day 29 — NLP Parser

* Parsed financial narrative/content into structured analysis data.
* Generated `analysis_parsed.csv`.
* Added parse-failure tracking for unsuccessful records.

### Day 30 — Pros & Cons Generator

* Implemented automated rule-based financial pros and cons.
* Final output covers 92 companies.
* Implemented 12 Pro rules and 12 Con rules.
* Generated `pros_cons_generated.csv`.
* Added confidence scores and fallback handling.

### Day 31 — Cash-Flow Intelligence

* Implemented CFO quality analysis.
* Implemented CapEx intensity classification.
* Implemented FCF CAGR and FCF conversion.
* Added distress detection.
* Added deleveraging detection.
* Added capital-allocation classification.
* Generated `cashflow_intelligence.xlsx`.
* Generated `distress_alerts.csv`.

### Day 32 — Capital Allocation

* Classified capital-allocation patterns.
* Generated pattern-change analysis.
* Updated cash-flow intelligence output with capital-allocation labels.
* Generated `pattern_changes.csv`.

### Day 33 — Company Tearsheet

* Generated automated company-level PDF tearsheets.
* Added KPI and financial trend information.
* Created reusable PDF generation logic.

### Day 34 — Batch & Sector Reports

* Added automated batch company-report generation.
* Generated 89 company tearsheets from companies with available financial-ratio data.
* Generated sector-level PDF reports.
* Documented skipped companies in `skipped_tearsheets.csv`.

### Day 35 — Portfolio Summary

* Generated the consolidated portfolio summary PDF.
* Portfolio report contains the available company-level financial summaries.
* Final output created at:
  `reports/portfolio/portfolio_summary.pdf`

## Key Results

* 92-company financial universe validated for the intelligence outputs.
* 24 rule-based NLP rules implemented.
* 12 Pro rules.
* 12 Con rules.
* 92 cash-flow intelligence records generated.
* 13 distress signals identified by the implemented distress condition.
* 89 company tearsheets generated.
* 3 companies had no financial-ratio records and were documented as skipped:

  * ATGL
  * BAJAJ-AUTO
  * SBIN
* Portfolio summary PDF generated successfully.

## What Went Well

* Existing database tables could be reused across multiple intelligence modules.
* The rule-based architecture made the NLP-style outputs deterministic and reproducible.
* The reporting pipeline successfully converted structured financial data into company and sector reports.
* Output validation during the sprint helped catch issues such as incorrect company-universe joins, database-column mismatches, and PDF generation failures.

## Challenges

* Several source tables used different schemas and column naming conventions.
* Some datasets contained companies outside the official 92-company financial-ratio universe.
* PDF generation initially encountered database lifecycle issues.
* Missing financial-ratio data required explicit handling rather than fabricated reports.
* Rule implementation initially contained indentation/output-order issues, which were identified through rule-count validation.

## Improvements Made

* Restricted intelligence outputs to the official 92-company financial universe.
* Added explicit output-schema validation.
* Added rule-count validation for the NLP generator.
* Added safe handling for missing numerical values in reports.
* Added skipped-company reporting.
* Added automated PDF batch generation.

## Final Takeaway

Sprint 5 established the financial-intelligence and reporting layer of the N100 platform. The pipeline now converts structured financial data into interpretable financial signals, company-level insights, sector reports, and portfolio-level reporting outputs.

The main lesson from the sprint was the importance of validating not only whether code executes successfully, but also whether the resulting outputs satisfy the required schema, company universe, rule coverage, and reporting requirements.
