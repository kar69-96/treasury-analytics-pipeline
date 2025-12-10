# Treasury Analytics Pipeline

Automated, cloud-deployed data pipeline that ingests treasury interest rates and foreign exchange data from public APIs, stores it in a managed Postgres database, and provides normalized views for direct consumption via Excel or other analytics tools. Automatically triggered at 2AM UTC daily.

## Objective

Refresh workflows by automating the ingestion of:
- **Interest Rates**: Treasury rates (2Y, 5Y, 10Y, 30Y) and Federal Reserve rates from FRED API
- **Foreign Exchange Rates**: Major currency pairs (EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR) from FRED API

The pipeline runs 24/7 in the cloud via GitHub Actions, ensuring Excel and other clients always have access to the latest data without any local machine dependencies or manual intervention.

- **Ingestion Script** (`ingestion/ingest.py`): Python script that fetches from FRED API and writes to Postgres
- **GitHub Actions Workflow**: Runs daily via cron, can be triggered manually
- **Postgres Database**: Managed service (Neon/Supabase/RDS) with raw tables and normalized views
- **SQL Views**: `fact_fx_rates_daily`, `fact_interest_rates_daily` provide clean, normalized data

### Prerequisites
1. **FRED API Key**: Get free key from https://fred.stlouisfed.org/docs/api/api_key.html
2. **Managed Postgres**: Provision database (Neon, Supabase, or AWS RDS)
3. **GitHub Repository**: Fork/clone this repo

### Setup Steps

1. **Add GitHub Secrets** (Settings → Secrets and variables → Actions):
   - `POSTGRES_URL`: Full connection string (`postgresql://user:password@host:port/database`)
   - `FRED_API_KEY`: Your FRED API key

2. **Enable GitHub Actions** (Settings → Actions → General):
   - Enable "Allow all actions and reusable workflows"
   - Workflow runs automatically at 2 AM UTC daily

3. **Test**: Go to Actions tab → "Treasury Data Ingestion" → "Run workflow"

4. **Connect Excel**:
   - Install PostgreSQL ODBC driver
   - Data → Get Data → From PostgreSQL Database
   - Connect to views: `fact_fx_rates_daily` or `fact_interest_rates_daily`
   - Enable "Refresh on open"



## Data Schema

### Raw Tables
- **`raw_fred_rates`**: `date`, `series_id`, `series_name`, `rate` (percentage)
- **`raw_fx_rates`**: `date`, `currency`, `rate_to_usd`

### Views (Use These in Excel)
- **`fact_fx_rates_daily`**: Clean FX rates, filtered NULLs, sorted by date
- **`fact_interest_rates_daily`**: Interest rates converted to decimal (5.5% → 0.055)

## Excel Integration

Excel connects directly to Postgres views via ODBC:
- **Read-Only**: Excel never writes to database
- **Auto-Refresh**: Data refreshes automatically when Excel opens
- **Always Current**: Reflects most recent successful ingestion
- **No Transformation Logic**: All normalization lives in SQL views

