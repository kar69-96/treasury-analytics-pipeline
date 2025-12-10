#!/bin/bash
# Local test script for Treasury Analytics Pipeline
# This script tests the ingestion locally before pushing to GitHub

set -e

echo "=========================================="
echo "Testing Treasury Analytics Pipeline Locally"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "ingestion/ingest.py" ]; then
    echo "Error: Please run this script from the repository root"
    exit 1
fi

# Set environment variables
export POSTGRES_URL="postgresql://neondb_owner:npg_pSjZO1dUo7EW@ep-icy-dew-a4rn7s84-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
export FRED_API_KEY="b2b4c4bec27e9960af2d959812c3862d"

echo ""
echo "Installing dependencies..."
cd ingestion
python3 -m pip install -q -r requirements.txt

echo ""
echo "Running ingestion script..."
python3 ingest.py

echo ""
echo "=========================================="
echo "✓ Local test completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Push this repository to GitHub"
echo "2. Add POSTGRES_URL and FRED_API_KEY as GitHub Secrets"
echo "3. Trigger the GitHub Actions workflow"
echo ""

