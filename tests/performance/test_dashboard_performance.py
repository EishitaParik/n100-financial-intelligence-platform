import time

import requests

TICKERS = ["TCS", "INFY", "HDFCBANK", "RELIANCE", "ITC"]

BASE_URL = "http://127.0.0.1:8000/api/v1/companies"


def test_company_profile_performance():
    print("\n=== COMPANY PROFILE PERFORMANCE ===")

    for ticker in TICKERS:
        start = time.perf_counter()

        response = requests.get(
            f"{BASE_URL}/{ticker}",
            timeout=10,
        )

        elapsed = time.perf_counter() - start

        print(f"{ticker}: " f"status={response.status_code}, " f"time={elapsed:.4f}s")

        assert response.status_code == 200
        assert elapsed < 3

    print("PASS: All 5 company profiles loaded under 3 seconds.")
