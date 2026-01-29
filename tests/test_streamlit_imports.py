"""
Test Streamlit imports to find TensorFlow error
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import traceback

st.title("🔍 Import Diagnostics")

st.write("### Python Info")
st.write(f"Python version: {sys.version}")
st.write(f"Python executable: {sys.executable}")

st.write("### Step 1: Import core modules")
try:
    from core.data_transform import pivot_to_wide_format
    st.success("✅ core.data_transform imported")
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.code(traceback.format_exc())

st.write("### Step 2: Import forecast_agent")
try:
    from ai_agents.forecast_agent import build_cashflow_forecast
    st.success("✅ ai_agents.forecast_agent imported")
except Exception as e:
    st.error(f"❌ Error: {e}")
    st.code(traceback.format_exc())

st.write("### Step 3: Test forecast function")
try:
    import pandas as pd
    from core.data_transform import pivot_to_wide_format, get_next_month_name

    df = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01']),
        'category': ['Sales', 'Sales', 'Sales'],
        'amount': [100, 110, 120]
    })

    df_wide = pivot_to_wide_format(df)
    next_month = get_next_month_name(df, 'date')

    st.write("Test data prepared:")
    st.write(df_wide)
    st.write(f"Next month: {next_month}")

    with st.spinner("Calling AI agent..."):
        from ai_agents.forecast_agent import build_cashflow_forecast
        result = build_cashflow_forecast(df_wide, next_month)
        st.success("✅ Forecast completed!")
        st.write(result)

except Exception as e:
    st.error(f"❌ Error during forecast: {e}")
    st.code(traceback.format_exc())

st.write("### Step 4: Check loaded modules")
tensorflow_modules = [m for m in sys.modules if 'tensorflow' in m.lower()]
if tensorflow_modules:
    st.warning(f"⚠️ TensorFlow modules found: {tensorflow_modules}")
else:
    st.success("✅ No TensorFlow modules loaded")
