-- Treasury Analytics Pipeline - Canonical Data Views
-- These views provide normalized, clean data for consumption by Excel and other clients

-- FX Rates Daily View
-- Normalizes FX rates to USD base (1 unit of currency = X USD)
CREATE OR REPLACE VIEW fact_fx_rates_daily AS
SELECT 
    date,
    currency,
    rate_to_usd
FROM raw_fx_rates
WHERE rate_to_usd IS NOT NULL
ORDER BY date DESC, currency;

-- Interest Rates Daily View
-- Converts percent rates to decimal format (e.g., 5.5% -> 0.055)
CREATE OR REPLACE VIEW fact_interest_rates_daily AS
SELECT 
    date,
    series_id,
    series_name,
    CASE 
        WHEN rate IS NOT NULL THEN rate / 100.0
        ELSE NULL
    END AS rate
FROM raw_fred_rates
WHERE rate IS NOT NULL
ORDER BY date DESC, series_id;

-- Optional: Summary view for status checks
CREATE OR REPLACE VIEW ingestion_status AS
SELECT 
    'raw_fred_rates' AS table_name,
    COUNT(*) AS row_count,
    MAX(date) AS latest_date,
    MIN(date) AS earliest_date
FROM raw_fred_rates
UNION ALL
SELECT 
    'raw_fx_rates' AS table_name,
    COUNT(*) AS row_count,
    MAX(date) AS latest_date,
    MIN(date) AS earliest_date
FROM raw_fx_rates;

