# Your Excel API URLs

## ✅ Deployment Complete!

Your API has been successfully deployed to Vercel. Here are your Excel connection URLs:

### Combined Data API (Recommended) ⭐
Returns both FX rates and interest rates in one call:
```
https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/data
```

### Individual Endpoints
**FX Rates API:**
```
https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/fx-rates
```

**Interest Rates API:**
```
https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/interest-rates
```

## ⚠️ Important: Disable Password Protection

Your Vercel project currently has password protection enabled. To use these URLs in Excel, you need to disable it:

1. Go to [vercel.com](https://vercel.com)
2. Navigate to your project: **treasury-api**
3. Go to **Settings** → **Deployment Protection**
4. Disable **"Password Protection"** or set it to **"No Protection"**
5. Save changes

## Connect Excel (Mac)

Once password protection is disabled:

1. Open Excel
2. **Data** → **Get Data** → **From Other Sources** → **From Web**
3. Paste the combined data URL (recommended):
   - `https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/data`
   - This returns both FX rates and interest rates in one response
4. Click **OK**
5. Excel will automatically parse the JSON and load the data
6. Right-click the table → **Table** → **External Data Properties**
7. Check **"Refresh data when opening the file"**

## Project Details

- **Vercel Project**: treasury-api
- **Project URL**: https://vercel.com/kar69-96s-projects/treasury-api
- **Environment Variable**: POSTGRES_URL (configured ✅)

## Testing

After disabling password protection, test the URLs in your browser:
- **Combined**: https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/data (returns both datasets)
- **FX Rates**: https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/fx-rates
- **Interest Rates**: https://treasury-fb993u8jc-kar69-96s-projects.vercel.app/api/interest-rates

You should see JSON data with your treasury rates.
