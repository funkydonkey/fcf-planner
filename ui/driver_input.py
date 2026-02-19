"""
Financial driver input form for Cash Flow Planner v2.0

Renders a Streamlit form for entering working capital, revenue,
and CapEx drivers. Returns a plain dict to avoid coupling with
Pydantic models or other modules.
"""

import streamlit as st
from typing import Dict, Any


INDUSTRY_OPTIONS = {
    "retail": "Retail",
    "manufacturing": "Manufacturing",
    "services": "Services",
    "technology": "Technology / IT",
    "healthcare": "Healthcare",
}


def render_driver_input_form() -> Dict[str, Any]:
    """
    Renders a Streamlit form for entering financial drivers.

    Returns a dict with keys:
        - working_capital: {dso_days, dpo_days, dio_days}
        - revenue: {revenue_growth_pct, gross_margin_pct}
        - capex: {capex_pct_of_revenue, depreciation_years} or None
        - industry: str (key from INDUSTRY_OPTIONS)
        - ccc_days: float (calculated Cash Conversion Cycle)
    """
    st.subheader("📊 Financial Drivers")

    # --- Industry selector ---
    industry = st.selectbox(
        "Industry",
        options=list(INDUSTRY_OPTIONS.keys()),
        format_func=lambda x: INDUSTRY_OPTIONS[x],
        help="Select an industry for benchmark comparison",
    )

    # --- Working Capital section ---
    st.markdown("### 💰 Working Capital")
    col1, col2, col3 = st.columns(3)

    with col1:
        dso = st.number_input(
            "DSO (days)",
            min_value=0.0,
            max_value=365.0,
            value=45.0,
            help="Days Sales Outstanding — average time to collect receivables",
        )
    with col2:
        dpo = st.number_input(
            "DPO (days)",
            min_value=0.0,
            max_value=365.0,
            value=30.0,
            help="Days Payable Outstanding — average time to pay suppliers",
        )
    with col3:
        dio = st.number_input(
            "DIO (days)",
            min_value=0.0,
            max_value=365.0,
            value=60.0,
            help="Days Inventory Outstanding — average time inventory is held",
        )

    # CCC = DSO + DIO - DPO; lower is better
    ccc = dso + dio - dpo

    st.metric(
        "Cash Conversion Cycle (CCC)",
        f"{ccc:.0f} days",
        help="CCC = DSO + DIO - DPO. Lower is better.",
    )

    # --- Revenue section ---
    st.markdown("### 📈 Revenue")
    col1, col2 = st.columns(2)

    with col1:
        revenue_growth = st.number_input(
            "Revenue Growth (%)",
            min_value=-100.0,
            max_value=500.0,
            value=10.0,
        )
    with col2:
        gross_margin = st.number_input(
            "Gross Margin (%)",
            min_value=0.0,
            max_value=100.0,
            value=35.0,
        )

    # --- CapEx section (optional) ---
    capex_data = None
    with st.expander("⚙️ CapEx (optional)"):
        capex_pct = st.number_input(
            "CapEx (% of revenue)",
            min_value=0.0,
            max_value=100.0,
            value=5.0,
        )
        depr_years = st.number_input(
            "Depreciation Period (years)",
            min_value=1,
            max_value=40,
            value=10,
        )
        if capex_pct > 0:
            capex_data = {
                "capex_pct_of_revenue": capex_pct,
                "depreciation_years": depr_years,
            }

    return {
        "working_capital": {"dso_days": dso, "dpo_days": dpo, "dio_days": dio},
        "revenue": {
            "revenue_growth_pct": revenue_growth,
            "gross_margin_pct": gross_margin,
        },
        "capex": capex_data,
        "industry": industry,
        "ccc_days": ccc,
    }
