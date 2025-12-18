# Treasury Analytics Pipeline

Automated, cloud-deployed data pipeline that ingests treasury interest rates and foreign exchange data from public APIs, stores it in a managed Postgres database, and provides normalized views for direct consumption via Excel dashboard. Automatically triggered at 2AM UTC daily.

## Objective

Refresh workflows by automating the ingestion of:
- **Interest Rates**: Treasury rates (2Y, 5Y, 10Y, 30Y) and Federal Reserve rates from **FRED API** (Federal Reserve Economic Data)
- **Foreign Exchange Rates**: Major currency pairs (EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR) from **FRED API**

The pipeline runs 24/7 in the cloud via GitHub Actions, ensuring Excel and other clients always have access to the latest data without any local machine dependencies or manual intervention.

### Data Source & Update Schedule

**Data Source**: All data is pulled from the [FRED API](https://fred.stlouisfed.org/) (Federal Reserve Economic Data), a public database maintained by the Federal Reserve Bank of St. Louis.

**Update Frequency**: 
- The ingestion workflow runs **daily at 2 AM UTC** to fetch the latest available data from FRED
- Data can also be manually triggered via GitHub Actions

   **Important Note on Data Delay**: 
   - FRED typically publishes data with a **1-2 day delay** from the actual observation date
   - For example, data for a Monday may not be available in FRED until Tuesday or Wednesday
   - The pipeline fetches the most recent data available from FRED at the time of ingestion
   - If you see data only up to a specific date (e.g., December 5th), this reflects the latest data point published by FRED, not a pipeline issue


## Setup

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

4. **Connect Excel** (Choose one method):
   - **Easiest (No Downloads)**: Use Web API method - see "Excel Integration Guide" below
   - **Direct Connection**: Install PostgreSQL ODBC driver → Data → Get Data → From PostgreSQL Database → Connect to views: `fact_fx_rates_daily` or `fact_interest_rates_daily`



## Data Schema

### Raw Tables
- **`raw_fred_rates`**: `date`, `series_id`, `series_name`, `rate` (percentage)
- **`raw_fx_rates`**: `date`, `currency`, `rate_to_usd`

### Views (Use These in Excel)
- **`fact_fx_rates_daily`**: Clean FX rates, filtered NULLs, sorted by date
- **`fact_interest_rates_daily`**: Interest rates converted to decimal (5.5% → 0.055)


## Excel Integration

Excel connects directly to Postgres views via ODBC:
- **Auto-Refresh**: Data refreshes automatically when Excel opens
- **Always Current**: Reflects most recent successful ingestion
- **No Transformation Logic**: All normalization lives in SQL views

## Excel Integration Guide (Step-by-Step)

### Method 1: Web API Connection

This method works on **any platform** (Windows, Mac, Excel Online) and requires **no driver downloads**. It works perfectly with shared spreadsheets.

**Quick Start for Neon Users**: Use this stable, shareable URL in Excel:
- **Combined Data**: `https://treasury-api-tawny.vercel.app/api/data`
  - Returns both FX rates and interest rates in one call
- **Individual Endpoints** (also available):
  - FX Rates: `https://treasury-api-tawny.vercel.app/api/fx-rates`
  - Interest Rates: `https://treasury-api-tawny.vercel.app/api/interest-rates`

**Use this URL in Excel's "From Web" connector if using Windows.**

**Auto-Refresh**: After connecting, enable "Refresh data when opening the file" in connection properties so data updates automatically every time the file is opened. 
