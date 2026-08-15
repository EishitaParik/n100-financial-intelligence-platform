from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"

    tables = data["db_row_counts"]

    required_tables = [
        "companies",
        "balancesheet",
        "cashflow",
        "profitandloss",
        "analysis",
        "documents",
        "prosandcons",
        "financial_ratios",
        "market_cap",
        "peer_groups",
    ]

    for table in required_tables:
        assert table in tables
