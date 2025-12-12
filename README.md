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
- **Auto-Refresh**: Data refreshes automatically when Excel opens
- **Always Current**: Reflects most recent successful ingestion
- **No Transformation Logic**: All normalization lives in SQL views

## Excel Integration Guide (Step-by-Step)

### Prerequisites
1. **PostgreSQL ODBC Driver**: Download and install from [PostgreSQL ODBC Driver](https://www.postgresql.org/ftp/odbc/versions/msi/) (choose the latest version matching your system)
2. **Database Connection String**: Your `POSTGRES_URL` from GitHub Secrets (format: `postgresql://user:password@host:port/database?sslmode=require`)

### Setup Excel Connection (Easiest Method)

#### Step 1: Create Data Connection
1. Open Excel
2. Go to **Data** tab → **Get Data** → **From Database** → **From PostgreSQL Database**
3. In the dialog box, enter your connection details:
   - **Server**: Extract from your `POSTGRES_URL` (e.g., `ep-icy-dew-a4rn7s84-pooler.us-east-1.aws.neon.tech`)
   - **Database**: Extract from your `POSTGRES_URL` (e.g., `neondb`)
   - **Port**: Usually `5432` (or extract from your URL)
   - Click **OK**

#### Step 2: Authenticate
1. Enter your database **username** and **password** (from your `POSTGRES_URL`)
2. Check **"Save my password"** (credentials stored securely on your machine)
3. Click **Connect**

#### Step 3: Select Data View
1. In the Navigator window, select **"fact_fx_rates_daily"** or **"fact_interest_rates_daily"**
2. Click **Load** (or **Transform Data** if you want to modify before loading)

#### Step 4: Enable Auto-Refresh
1. Right-click on the loaded table → **Table** → **External Data Properties**
2. Check **"Refresh data when opening the file"**
3. Optionally set **"Refresh every X minutes"** for live updates
4. Click **OK**

### Sharing Spreadsheets with Live Data

When you share an Excel file with this connection:

✅ **What Works Automatically:**
- Connection string is embedded in the workbook
- Each user authenticates **once** (first time they open)
- Excel stores credentials securely **per-user** (not in the file)
- Data refreshes automatically when any user opens the file
- Always pulls **live data** from the database

⚠️ **First-Time Setup for Recipients:**
1. Recipient opens the shared Excel file
2. Excel prompts for database credentials (username/password)
3. Recipient enters credentials and checks **"Save my password"**
4. Data loads and refreshes automatically on future opens

### Alternative: Using Connection String Directly

If you prefer to use the full connection string:

1. **Data** → **Get Data** → **From Other Sources** → **From ODBC**
2. Select your PostgreSQL driver
3. In the connection string field, paste your full `POSTGRES_URL`:
   ```
   Driver={PostgreSQL Unicode};Server=your-host;Port=5432;Database=your-db;Uid=your-user;Pwd=your-password;SSLMode=require;
   ```
4. Click **OK** and select your view

### Troubleshooting

- **"Driver not found"**: Install PostgreSQL ODBC driver (see Prerequisites)
- **Connection timeout**: Check firewall settings, ensure database allows your IP
- **SSL errors**: Ensure `sslmode=require` is in your connection string
- **Credentials prompt every time**: Check "Save my password" during authentication

### Best Practices

- **Use Views**: Always connect to `fact_fx_rates_daily` or `fact_interest_rates_daily`, not raw tables
- **Refresh Settings**: Enable "Refresh on open" for always-current data
- **Shared Workbooks**: Each user authenticates once; credentials are stored per-user (secure)
- **Read-Only**: Excel never writes to the database; all changes are local to the spreadsheet

