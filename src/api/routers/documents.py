import sqlite3

from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_PATH = "nifty100.db"


@router.get("/companies/{ticker}/documents")
def company_documents(ticker: str):

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            company_id,
            year,
            annual_report
        FROM documents
        WHERE UPPER(company_id) = UPPER(?)
        ORDER BY year DESC
    """,
        (ticker,),
    ).fetchall()

    conn.close()

    if not rows:
        raise HTTPException(
            status_code=404, detail=f"No documents found for '{ticker}'"
        )

    return {
        "ticker": ticker.upper(),
        "documents": [
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "annual_report": row["annual_report"],
                "is_url_valid": bool(
                    row["annual_report"]
                    and str(row["annual_report"]).startswith("http")
                ),
            }
            for row in rows
        ],
    }
