"""
Async Treasury Analytics Pipeline - Ingestion Script

Fetches interest rate time series from FRED API and FX rates from exchangerate.host,
then writes to Postgres tables.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from sqlalchemy import create_engine, text
from fredapi import Fred


def get_postgres_engine():
    """Create SQLAlchemy engine from POSTGRES_URL environment variable."""
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL environment variable is required")
    return create_engine(postgres_url)


def fetch_fred_rates(fred_api_key: str) -> pd.DataFrame:
    """
    Fetch interest rate time series from FRED API.
    
    Returns DataFrame with columns: date, series_id, series_name, rate
    """
    fred = Fred(api_key=fred_api_key)
    
    # Common Treasury and interest rate series
    series_config = {
        "DGS10": "10-Year Treasury Constant Maturity Rate",
        "DGS5": "5-Year Treasury Constant Maturity Rate",
        "DGS2": "2-Year Treasury Constant Maturity Rate",
        "DGS30": "30-Year Treasury Constant Maturity Rate",
        "DFF": "Federal Funds Effective Rate",
        "DEXUSEU": "U.S. / Euro Foreign Exchange Rate",
    }
    
    all_data = []
    
    for series_id, series_name in series_config.items():
        try:
            data = fred.get_series(series_id, observation_start="2000-01-01")
            if data is not None and len(data) > 0:
                df = pd.DataFrame({
                    "date": data.index,
                    "series_id": series_id,
                    "series_name": series_name,
                    "rate": data.values
                })
                all_data.append(df)
                print(f"✓ Fetched {series_id}: {len(df)} records")
            else:
                print(f"⚠ No data for {series_id}")
        except Exception as e:
            print(f"✗ Error fetching {series_id}: {e}")
    
    if not all_data:
        raise ValueError("No FRED data was successfully fetched")
    
    result = pd.concat(all_data, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"]).dt.date
    return result


def fetch_fx_rates(fred_api_key: str) -> pd.DataFrame:
    """
    Fetch FX time series from FRED API (USD base).
    
    Returns DataFrame with columns: date, currency, rate_to_usd
    """
    fred = Fred(api_key=fred_api_key)
    
    # FRED FX rate series - format: DEX[currency]US (USD per unit of currency)
    # For some currencies, it's inverted (e.g., DEXJPUS is JPY per USD)
    fx_series_config = {
        "DEXUSEU": ("EUR", "USD per EUR"),  # USD/EUR - need to invert
        "DEXUSUK": ("GBP", "USD per GBP"),  # USD/GBP - need to invert
        "DEXJPUS": ("JPY", "JPY per USD"),  # JPY/USD - already correct
        "DEXCAUS": ("CAD", "CAD per USD"),  # CAD/USD - need to invert
        "DEXUSAL": ("AUD", "USD per AUD"),  # USD/AUD - need to invert
        "DEXSZUS": ("CHF", "CHF per USD"),  # CHF/USD - need to invert
        "DEXCHUS": ("CNY", "Chinese Yuan per USD"),  # CNY/USD - need to invert
        "DEXINUS": ("INR", "Indian Rupees per USD"),  # INR/USD - need to invert
    }
    
    all_data = []
    
    for series_id, (currency, description) in fx_series_config.items():
        try:
            data = fred.get_series(series_id, observation_start="2000-01-01")
            if data is not None and len(data) > 0:
                # Convert to rate_to_usd format
                # For series like DEXUSEU (USD/EUR), we need 1/rate to get EUR/USD
                # For series like DEXJPUS (JPY/USD), we need 1/rate to get USD/JPY
                # Actually, we want: 1 unit of currency = X USD
                # DEXUSEU gives USD/EUR, so 1 EUR = DEXUSEU USD (no inversion needed!)
                # DEXJPUS gives JPY/USD, so 1 JPY = 1/DEXJPUS USD (inversion needed!)
                
                # Check if series is already in USD/base format or base/USD format
                # Most FRED series are USD/base, so rate_to_usd = rate
                # But DEXJPUS, DEXCAUS, etc. are base/USD, so rate_to_usd = 1/rate
                
                if series_id in ["DEXJPUS", "DEXCAUS", "DEXSZUS", "DEXCHUS", "DEXINUS"]:
                    # These are base/USD, so invert to get USD/base
                    rate_to_usd = 1.0 / data.values
                else:
                    # These are USD/base, so use directly
                    rate_to_usd = data.values
                
                df = pd.DataFrame({
                    "date": data.index,
                    "currency": currency,
                    "rate_to_usd": rate_to_usd
                })
                # Remove any invalid values
                df = df[df["rate_to_usd"].notna() & (df["rate_to_usd"] > 0)]
                
                if len(df) > 0:
                    all_data.append(df)
                    print(f"✓ Fetched {currency} ({series_id}): {len(df)} records")
                else:
                    print(f"⚠ No valid data for {currency} ({series_id})")
            else:
                print(f"⚠ No data for {currency} ({series_id})")
        except Exception as e:
            print(f"✗ Error fetching {currency} ({series_id}): {e}")
    
    if not all_data:
        raise ValueError("No FX data was successfully fetched")
    
    result = pd.concat(all_data, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"]).dt.date
    return result


def create_tables_if_not_exists(engine):
    """Create raw tables if they don't exist."""
    with engine.connect() as conn:
        # Create raw_fred_rates table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_fred_rates (
                date DATE NOT NULL,
                series_id VARCHAR(20) NOT NULL,
                series_name VARCHAR(200),
                rate NUMERIC(10, 4),
                PRIMARY KEY (date, series_id)
            )
        """))
        
        # Create raw_fx_rates table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS raw_fx_rates (
                date DATE NOT NULL,
                currency VARCHAR(10) NOT NULL,
                rate_to_usd NUMERIC(15, 6),
                PRIMARY KEY (date, currency)
            )
        """))
        
        conn.commit()
        print("✓ Tables created/verified")


def write_to_postgres(df: pd.DataFrame, table_name: str, engine):
    """Write DataFrame to Postgres table, replacing existing data."""
    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
        method="multi"
    )
    print(f"✓ Wrote {len(df)} rows to {table_name}")


def apply_sql_views(engine):
    """Apply SQL views from views.sql file."""
    views_sql_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sql",
        "views.sql"
    )
    
    if not os.path.exists(views_sql_path):
        print(f"⚠ Warning: views.sql not found at {views_sql_path}, skipping view creation")
        return
    
    with open(views_sql_path, "r") as f:
        views_sql = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in views_sql.split(";") if s.strip() and not s.strip().startswith("--")]
    
    with engine.connect() as conn:
        for statement in statements:
            if statement:
                try:
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"⚠ Warning: Error applying view statement: {e}")
    
    print("✓ SQL views applied successfully")


def main():
    """Main ingestion function."""
    print("=" * 60)
    print("Treasury Analytics Pipeline - Ingestion")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Get environment variables
    postgres_url = os.getenv("POSTGRES_URL")
    fred_api_key = os.getenv("FRED_API_KEY")
    
    if not postgres_url:
        print("✗ ERROR: POSTGRES_URL environment variable is required")
        sys.exit(1)
    
    if not fred_api_key:
        print("✗ ERROR: FRED_API_KEY environment variable is required")
        sys.exit(1)
    
    try:
        # Create database engine
        engine = get_postgres_engine()
        
        # Create tables if needed
        create_tables_if_not_exists(engine)
        
        # Fetch FRED rates
        print("\n--- Fetching FRED Interest Rates ---")
        fred_df = fetch_fred_rates(fred_api_key)
        
        # Fetch FX rates
        print("\n--- Fetching FX Rates ---")
        fx_df = fetch_fx_rates(fred_api_key)
        
        # Write to Postgres
        print("\n--- Writing to Postgres ---")
        write_to_postgres(fred_df, "raw_fred_rates", engine)
        write_to_postgres(fx_df, "raw_fx_rates", engine)
        
        # Apply SQL views
        print("\n--- Applying SQL Views ---")
        apply_sql_views(engine)
        
        print("\n" + "=" * 60)
        print("✓ Ingestion completed successfully")
        print(f"Finished at: {datetime.now().isoformat()}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

