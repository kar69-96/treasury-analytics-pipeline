# Quick Setup Guide

## GitHub Secrets Configuration

After pushing this repository to GitHub, add the following secrets:

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

### Secret 1: POSTGRES_URL
```
postgresql://neondb_owner:npg_pSjZO1dUo7EW@ep-icy-dew-a4rn7s84-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Secret 2: FRED_API_KEY
```
b2b4c4bec27e9960af2d959812c3862d
```

## Test Locally (Optional)

Before pushing to GitHub, you can test the ingestion script locally:

```bash
cd ingestion
pip install -r requirements.txt
export POSTGRES_URL="postgresql://neondb_owner:npg_pSjZO1dUo7EW@ep-icy-dew-a4rn7s84-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
export FRED_API_KEY="b2b4c4bec27e9960af2d959812c3862d"
python ingest.py
```

## Next Steps

1. Push this repository to GitHub
2. Add the secrets above
3. Go to **Actions** tab and manually trigger "Treasury Data Ingestion" workflow
4. Verify the workflow completes successfully
5. Connect Excel to your Postgres database using the connection details

