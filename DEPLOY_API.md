# Quick API Deployment Guide for Excel Integration

Deploy the API endpoints to Vercel to get URLs that Excel can connect to (no drivers needed).

## Prerequisites

- Node.js installed (for Vercel CLI)
- Your Neon `POSTGRES_URL` connection string

## Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy

```bash
cd /path/to/Stripe_Treasury
vercel
```

Follow the prompts:
- Press Enter to accept defaults
- When asked about environment variables, you can add them later in the dashboard

### 4. Add Environment Variable

1. Go to [vercel.com](https://vercel.com)
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Key**: `POSTGRES_URL`
   - **Value**: Your full Neon connection string (from SETUP.md)
   - **Environment**: Production, Preview, Development (select all)
5. Click **Save**

### 5. Redeploy

Go to **Deployments** tab → Click **⋯** on latest deployment → **Redeploy**

Or trigger a new deployment:
```bash
vercel --prod
```

## Your API URLs

After deployment, you'll get URLs like:
- `https://your-app-name.vercel.app/api/fx-rates`
- `https://your-app-name.vercel.app/api/interest-rates`

## Connect Excel

1. Open Excel
2. **Data** → **Get Data** → **From Other Sources** → **From Web**
3. Enter one of your API URLs
4. Click **OK**
5. Excel will automatically parse the JSON and load the data
6. Right-click table → **Table** → **External Data Properties** → Check **"Refresh data when opening the file"**

## Notes

- The Neon API key you have is for Neon's management API, not for database access
- Use your `POSTGRES_URL` connection string (from SETUP.md) as the environment variable
- The API endpoints are read-only and safe to share
- Free Vercel tier includes 100GB bandwidth/month (plenty for Excel usage)
