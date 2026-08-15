# Performance Test Results

## API Load Test

Tested 10 concurrent requests against the screener API.

- Endpoint: `/api/v1/screener?min_roe=15`
- Concurrent requests: 10
- Total execution time: 1.1600 seconds
- HTTP status: 200 for all requests
- Performance threshold: < 10 seconds
- Result: PASS

## Company Profile Performance

Tested company profile API response times for 5 companies.

| Company | Response Time |
|---------|---------------|
| TCS | 0.0182s |
| INFY | 0.0130s |
| HDFCBANK | 0.0125s |
| RELIANCE | 0.0133s |
| ITC | 0.0094s |

- Performance threshold: < 3 seconds per request
- Result: PASS

## Overall Performance

The API successfully handled concurrent screener requests and
individual company profile requests within the defined performance
thresholds.

# Performance Notes

## Day 43 — Performance & Integration Testing

### API Load Test

Test: 10 concurrent screener API calls

Target: All 10 requests complete within 10 seconds.

Result: PASS

Total execution time: 1.2823 seconds

Individual request times:

- Request 1: 1.0137s
- Request 2: 1.2790s
- Request 3: 1.2653s
- Request 4: 1.2630s
- Request 5: 1.2550s
- Request 6: 1.2639s
- Request 7: 0.5654s
- Request 8: 0.6622s
- Request 9: 0.9107s
- Request 10: 0.7269s

All requests returned HTTP 200.

### Dashboard Performance

Test: Company Profile screen/API performance for five representative tickers.

Target: Each company profile loads within 3 seconds.

Result: PASS

- TCS: 0.0131s
- INFY: 0.0141s
- HDFCBANK: 0.0113s
- RELIANCE: 0.0112s
- ITC: 0.0127s

All five requests returned HTTP 200.

### SQLite Query Optimisation

SQLite indexes were added to frequently queried columns:

- `financial_ratios(company_id, year)`
- `market_cap(company_id, year)`
- `sectors(company_id)`
- `analysis(company_id)`

These indexes support company-level lookups, year-based queries and API/dashboard joins.

### Performance Bottlenecks

No critical performance bottlenecks were identified during testing.

The API load test completed significantly below the 10-second target, and all five company profile requests completed well below the 3-second target.

### Summary

Day 43 performance targets were successfully met.