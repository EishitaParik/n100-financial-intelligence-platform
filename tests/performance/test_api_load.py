import time
from concurrent.futures import ThreadPoolExecutor

import requests

URL = "http://127.0.0.1:8000/api/v1/screener?min_roe=15"


def make_request():
    start = time.perf_counter()

    response = requests.get(URL, timeout=10)

    elapsed = time.perf_counter() - start

    return response.status_code, elapsed


def test_10_concurrent_screener_calls():
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(
            executor.map(
                lambda _: make_request(),
                range(10),
            )
        )

    total_time = time.perf_counter() - start

    print("\n=== API LOAD TEST ===")
    print(f"Total time: {total_time:.4f} seconds")

    for i, (status, elapsed) in enumerate(results, 1):
        print(f"Request {i}: " f"status={status}, " f"time={elapsed:.4f}s")

    assert all(status == 200 for status, _ in results)
    assert total_time < 10

    print("PASS: 10 concurrent requests completed within 10 seconds.")
