# Sprint 1 Retrospective

## What I completed

During Sprint 1, I built the ETL pipeline for the N100 Financial Intelligence Platform. I created the Excel loader, normalized company IDs and year values, validated the datasets using multiple data quality rules, created the SQLite database schema, and loaded all 12 Excel files into the database successfully.

## What went well

- Successfully loaded all datasets into SQLite.
- Built reusable loader and validator modules.
- Added normalization for company IDs and year values.
- Implemented unit tests for the normalizer.
- Generated load audit and validation reports.

## Challenges

The biggest challenge was handling different Excel formats because some datasets had headers on different rows. I also faced issues with foreign key validation because some company IDs in the source datasets were missing from the master companies table. These issues were identified through the validation process.

## Learnings

This sprint helped me understand how ETL pipelines work in practice. I also learned more about SQLite, data validation, and how important consistent data is before loading it into a database.

## Improvements for Next Sprint

- Improve data quality checks further.
- Optimize the ETL pipeline.
- Add more automated validation tests.
- Improve logging and reporting.