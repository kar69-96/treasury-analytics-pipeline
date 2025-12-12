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

### Method 1: Web API Connection (No Downloads Required) ⭐ RECOMMENDED

This method works on **any platform** (Windows, Mac, Excel Online) and requires **no driver downloads**. It works perfectly with shared spreadsheets.

**Quick Start for Neon Users**: ✅ **Already Deployed!** Use this stable, shareable URL in Excel:
- **Combined Data (Recommended)**: `https://treasury-api-tawny.vercel.app/api/data`
  - Returns both FX rates and interest rates in one call
  - **This is a stable production URL** - won't change with deployments
- **Individual Endpoints** (also available):
  - FX Rates: `https://treasury-api-tawny.vercel.app/api/fx-rates`
  - Interest Rates: `https://treasury-api-tawny.vercel.app/api/interest-rates`

Use this URL in Excel's "From Web" connector - no drivers needed! 

**Auto-Refresh**: After connecting, enable "Refresh data when opening the file" in connection properties so data updates automatically every time the file is opened. See **Option C** below for step-by-step instructions.

#### Option A: Using Supabase REST API (If using Supabase)

Supabase automatically generates REST APIs for your tables. Connect Excel directly:

1. **Get your Supabase API URL**:
   - Go to your Supabase project → Settings → API
   - Copy your **Project URL** (e.g., `https://xxxxx.supabase.co`)

2. **Get your API Key**:
   - In the same API settings, copy your **anon/public key**

3. **Connect in Excel**:
   - **Data** → **Get Data** → **From Other Sources** → **From Web**
   - Enter URL (replace `YOUR_PROJECT_URL` and `YOUR_API_KEY`):
     ```
     https://YOUR_PROJECT_URL.supabase.co/rest/v1/fact_fx_rates_daily?select=*&apikey=YOUR_API_KEY
     ```
   - For interest rates:
     ```
     https://YOUR_PROJECT_URL.supabase.co/rest/v1/fact_interest_rates_daily?select=*&apikey=YOUR_API_KEY
     ```
   - Click **OK**

4. **Enable Auto-Refresh** (Important!):
   - Go to **Data** → **Queries & Connections**
   - Right-click your connection → **Properties**
   - Check **"Refresh data when opening the file"**
   - Optionally: Set **"Refresh every X minutes"** for periodic updates
   - Click **OK** and **Save** your file
   - ✅ Now data will automatically refresh every time the file is opened!

**✅ Benefits**: Works everywhere, no downloads, credentials in URL (can be shared), always live data

#### Option B: Using Database Provider's REST API

Many managed Postgres providers offer REST APIs:
- **Neon**: Check if your plan includes REST API access
- **Supabase**: Use Option A above
- **AWS RDS**: Can use API Gateway + Lambda (requires setup)

#### Option C: Deploy API Endpoint for Neon (Recommended for Neon Users) ⭐

**✅ Already Deployed!** Your API is live at (stable production URL):
- **Combined Endpoint**: `https://treasury-api-tawny.vercel.app/api/data` (returns both FX rates and interest rates)

**⚠️ IMPORTANT - Before Using in Excel**: 
If you get "Cannot locate the Internet server" error in Excel, **disable password protection**:
1. Go to [vercel.com](https://vercel.com) → Project **treasury-api** → **Settings** → **Deployment Protection**
2. Disable **"Password Protection"** or set to **"No Protection"**
3. Save and try again in Excel

**Note**: If you need to redeploy or set up a new deployment, follow these steps:

**Step 1: Install Vercel CLI** (one-time setup):
```bash
npm install -g vercel
```

**Step 2: Deploy to Vercel**:
```bash
cd /path/to/Stripe_Treasury
vercel
```
- Follow prompts (press Enter for defaults)
- When asked for environment variables, add: `POSTGRES_URL` = your Neon connection string
- Copy the deployment URL (e.g., `https://your-app.vercel.app`)

**Step 3: Add Environment Variable in Vercel Dashboard**:
1. Go to [vercel.com](https://vercel.com) → Your project → Settings → Environment Variables
2. Add: `POSTGRES_URL` = your full Neon connection string
3. Redeploy (or it will auto-deploy)

**Step 4: Connect Excel**:
- **Data** → **Get Data** → **From Other Sources** → **From Web**
- Enter the combined data URL (stable production URL):
  ```
  https://treasury-api-tawny.vercel.app/api/data
  ```
- Click **OK** → Excel will load the JSON data automatically
- The response contains both `fx_rates` and `interest_rates` in one call

**Step 5: Enable Refresh on Open** (Important!):
1. After data loads, go to **Data** → **Queries & Connections**
2. Right-click your connection → **Properties**
3. Check **"Refresh data when opening the file"**
4. Optionally: Set **"Refresh every X minutes"** for periodic updates while Excel is open
5. Click **OK** and **Save** your Excel file

✅ **Result**: Every time you (or anyone) opens the Excel file, it will automatically fetch the latest data from the database. Since the database updates daily at 2 AM UTC, you'll always see the most recent treasury rates when opening the file.

**✅ Your Excel URLs** (stable production URLs - ready to share):
- **Combined Data (Recommended)**: `https://treasury-api-tawny.vercel.app/api/data`
  - Returns both FX rates and interest rates in one response
  - **This URL is stable and won't change** - perfect for sharing spreadsheets
- **Individual Endpoints** (also available):
  - FX Rates: `https://treasury-api-tawny.vercel.app/api/fx-rates`
  - Interest Rates: `https://treasury-api-tawny.vercel.app/api/interest-rates`

**Benefits**: 
- ✅ Works on Mac, Windows, Excel Online
- ✅ No driver downloads needed
- ✅ Share spreadsheets - URLs work for everyone
- ✅ Always pulls live data from database

### Method 2: Direct Database Connection (Requires Driver)

If you prefer direct database connection, you'll need to install drivers (see troubleshooting below).

### Prerequisites (For Method 2 Only)
1. **PostgreSQL ODBC Driver**: Install the appropriate driver for your operating system:
   - **Windows**: Download psqlODBC from [PostgreSQL Windows Installers](https://www.postgresql.org/download/windows/) (look for "Command Line Tools" or search for "psqlODBC")
   - **macOS**: Use one of these options:
     - [Actual Technologies ODBC Driver](https://www.actualtech.com/product.php) (free trial, paid license)
     - [Devart ODBC Driver](https://www.devart.com/odbc/postgresql/) (30-day free trial)
     - [CData ODBC Driver](https://www.cdata.com/drivers/postgresql/) (30-day free trial)
2. **Database Connection String**: Your `POSTGRES_URL` from GitHub Secrets (format: `postgresql://user:password@host:port/database?sslmode=require`)

### Setup Excel Connection - Direct Database (Method 2)

If you prefer direct database connection or your provider doesn't support REST API:

#### Step 1: Create Data Connection
1. Open Excel (Excel 365 recommended - has built-in PostgreSQL connector)
2. Go to **Data** tab → **Get Data** → **From Database** → **From PostgreSQL Database**
   - **Note**: Excel 365 may connect without requiring ODBC drivers. If you see an error, install the ODBC driver from Prerequisites above.
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

#### Using Web API Method (Method 1) - Best for Sharing ✅

When you share an Excel file using the Web API method:

✅ **Works Perfectly:**
- **No authentication needed** - API key is in the URL (or can use public endpoints)
- **Works immediately** - Recipients just open the file, data loads automatically
- **No driver installation** - Works on Windows, Mac, Excel Online
- **Always live data** - Refreshes automatically when file opens
- **Zero setup for recipients** - They don't need database credentials or drivers

**Perfect for sharing downloaded spreadsheets** - recipients get live data without any setup!

#### Using Direct Database Method (Method 2)

When you share an Excel file with direct database connection:

✅ **What Works:**
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
5. **Note**: Recipients may need to install ODBC drivers if Excel 365 doesn't have built-in support

### Alternative: Using Power Query with Connection String (No ODBC Required)

If the PostgreSQL Database option doesn't work, you can use Power Query directly:

1. **Data** → **Get Data** → **From Other Sources** → **Blank Query**
2. Click **Advanced Editor** and paste this (replace with your connection details):
   ```m
   let
       Source = Postgres.Database("your-host", "your-database", [Port=5432, Username="your-username", Password="your-password"]),
       fact_fx_rates = Source{[Schema="public",Item="fact_fx_rates_daily"]}[Data]
   in
       fact_fx_rates
   ```
3. Replace placeholders with values from your `POSTGRES_URL`
4. Click **Done** → **Close & Load**

**Note**: This method works in Excel 365 without requiring ODBC drivers.

### Troubleshooting

#### Web API Method (Method 1)
- **"Unable to open" / "Cannot locate the Internet server or proxy server"** (Excel Error):
  - **Most Common Cause**: Vercel password protection is enabled
  - **Fix**: Go to [vercel.com](https://vercel.com) → Your project (treasury-api) → **Settings** → **Deployment Protection** → Disable **"Password Protection"**
  - **Alternative**: Check if the URL works in your browser first - if you see a password prompt, that's the issue
  - **Also check**: Firewall/proxy settings, ensure Excel has internet access
- **"401 Unauthorized"**: Check your API key is correct (for Supabase, use the anon/public key)
- **"404 Not Found"**: Ensure the table/view name matches exactly (case-sensitive)
- **"500 Internal Server Error"**: Database tables may not exist yet - run the ingestion workflow first
- **Data not refreshing**: Right-click table → Refresh, or check "Refresh on open" in External Data Properties
- **URL not working**: Use the stable production URL: `https://treasury-api-tawny.vercel.app/api/data` (this URL doesn't change with deployments)

#### Direct Database Method (Method 2)
- **"Driver not found"**: Install PostgreSQL ODBC driver (see Prerequisites in Method 2 section)
- **Connection timeout**: Check firewall settings, ensure database allows your IP
- **SSL errors**: Ensure `sslmode=require` is in your connection string
- **Credentials prompt every time**: Check "Save my password" during authentication

### Best Practices

- **Use Views**: Always connect to `fact_fx_rates_daily` or `fact_interest_rates_daily`, not raw tables
- **Refresh Settings**: Enable "Refresh on open" for always-current data
- **Shared Workbooks**: Each user authenticates once; credentials are stored per-user (secure)
- **Read-Only**: Excel never writes to the database; all changes are local to the spreadsheet

