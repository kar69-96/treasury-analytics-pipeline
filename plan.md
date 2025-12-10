BUILD PLAN — Async Treasury Analytics Pipeline
Goal: Fully cloud-deployed, 24/7 data pipeline using public APIs, async ingestion, hosted Postgres, and Excel as a live read-only client.
0. Constraints
No local execution
Async ingestion only
Runs 24/7
Deployable via GitHub (required)
Optional Vercel API for health/status
Excel connects read-only and always loads latest data
1. Create GitHub Repository
Repository name:
treasury-analytics-pipeline
Directory structure:
treasury-analytics-pipeline/
├─ ingestion/
│  ├─ ingest.py
│  ├─ requirements.txt
├─ sql/
│  └─ views.sql
├─ .github/
│  └─ workflows/
│     └─ ingest.yml
└─ README.md
2. Managed Database (External)
Provision a managed Postgres database (Neon or Supabase).
Store connection string as:
POSTGRES_URL
3. Ingestion Script (Python)
Create ingestion/ingest.py.
Responsibilities:
Fetch interest rate time series from FRED using fredapi
Fetch FX timeseries from exchangerate.host (USD base)
Write results to Postgres tables:
raw_fred_rates
raw_fx_rates
Overwrite tables on each run (if_exists="replace")
No local files
Use only environment variables
Env vars:
POSTGRES_URL
FRED_API_KEY
4. Python Dependencies
Create ingestion/requirements.txt with:
fredapi
pandas
requests
sqlalchemy
psycopg2-binary
5. SQL Views (Treasury Canonical Layer)
Create sql/views.sql.
Views:
fact_fx_rates_daily
Columns: date, currency, rate_to_usd
Normalize FX to USD base
fact_interest_rates_daily
Columns: date, series_id, series_name, rate
Convert percent → decimal
No logic should live in Excel that belongs here.
6. Async Execution (GitHub Actions)
Create .github/workflows/ingest.yml.
Requirements:
Runs on workflow_dispatch
Runs daily via cron (UTC)
Installs Python
Installs requirements
Executes ingest.py
Injects secrets:
POSTGRES_URL
FRED_API_KEY
No local runners.
7. Secrets Configuration (GitHub)
Add repository secrets:
POSTGRES_URL
FRED_API_KEY
8. Optional Vercel Status API (Separate Repo)
Repo structure:
treasury-status/
├─ api/
│  └─ health.ts
├─ package.json
└─ vercel.json
Responsibilities:
Read from Postgres
Return:
last successful ingestion timestamp
row counts
Read-only DB access
Used only for status/debugging
9. Excel Integration (Consumer Only)
Excel behavior:
Connects directly to Postgres
Reads from views only:
fact_fx_rates_daily
fact_interest_rates_daily
Load to Data Model
Refresh on open
No ingestion, no transformation logic
10. Runtime Behavior
GitHub Actions runs ingestion daily
Postgres always online
Excel always reflects most recent successful ingestion
No dependency on any local machine
System runs indefinitely
11. Non-Goals (Explicit)
No Stripe APIs
No local CSVs
No manual refresh pipelines
No Excel-based ingestion
No private data
12. README Requirements
README must include:
Purpose
Architecture diagram (text)
How async ingestion works
How Excel consumes data
Security notes
Refresh guarantees
✅ Deliverable Definition
A user must be able to:
Fork repo
Add secrets
Enable GitHub Actions
Open Excel → Refresh → see live data