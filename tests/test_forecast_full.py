"""
Test script to reproduce the TensorFlow error
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime
import traceback

print("=" * 60)
print("TESTING FULL FORECAST WORKFLOW")
print("=" * 60)

# Step 1: Create test data
print("\n1. Creating test historical data...")
df_history = pd.DataFrame({
    'date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01',
                            '2024-01-01', '2024-02-01', '2024-03-01']),
    'category': ['Sales', 'Sales', 'Sales', 'Costs', 'Costs', 'Costs'],
    'amount': [100, 110, 120, 50, 55, 60]
})
print(f"   ✅ Created {len(df_history)} records")
print(df_history)

# Step 2: Transform to wide format
print("\n2. Transforming to wide format...")
try:
    from core.data_transform import pivot_to_wide_format, get_next_month_name
    df_wide = pivot_to_wide_format(df_history)
    print("   ✅ Wide format created")
    print(df_wide)
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    exit(1)

# Step 3: Get next month
print("\n3. Getting next month...")
try:
    next_month = get_next_month_name(df_history, 'date')
    print(f"   ✅ Next month: {next_month}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    traceback.print_exc()
    exit(1)

# Step 4: Build forecast
print("\n4. Building AI forecast...")
try:
    from ai_agents.forecast_agent import build_cashflow_forecast
    print("   ✅ Function imported")

    print(f"   Calling build_cashflow_forecast with {len(df_wide)} categories...")
    print(f"   Last period: {next_month}")

    forecast_df = build_cashflow_forecast(df_wide, next_month)

    print("   ✅ Forecast generated successfully!")
    print(forecast_df)

except Exception as e:
    print(f"   ❌ ERROR: {e}")
    print("\n" + "=" * 60)
    print("FULL TRACEBACK:")
    print("=" * 60)
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
