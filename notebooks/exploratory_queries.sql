-- ==========================================
-- Exploratory Queries
-- Sprint 1
-- ==========================================


-- 1. Total number of companies

SELECT COUNT(*) AS total_companies
FROM companies;


-- 2. Total rows in Profit & Loss

SELECT COUNT(*) AS total_profit_loss_records
FROM profitandloss;


-- 3. Total rows in Balance Sheet

SELECT COUNT(*) AS total_balance_sheet_records
FROM balancesheet;


-- 4. Total rows in Cash Flow

SELECT COUNT(*) AS total_cashflow_records
FROM cashflow;


-- 5. Companies with highest ROE

SELECT
    company_name,
    roe_percentage
FROM companies
ORDER BY roe_percentage DESC
LIMIT 10;


-- 6. Top 10 companies by Market Capitalization

SELECT
    company_id,
    year,
    market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;


-- 7. Average EPS

SELECT
    ROUND(AVG(eps),2) AS average_eps
FROM profitandloss;


-- 8. Companies with negative profit

SELECT
    company_id,
    year,
    net_profit
FROM profitandloss
WHERE net_profit < 0;


-- 9. Number of companies in each sector

SELECT
    broad_sector,
    COUNT(*) AS total_companies
FROM sectors
GROUP BY broad_sector
ORDER BY total_companies DESC;


-- 10. Latest stock prices

SELECT
    company_id,
    date,
    close_price
FROM stock_prices
ORDER BY date DESC
LIMIT 20;