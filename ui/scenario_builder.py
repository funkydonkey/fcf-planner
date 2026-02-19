"""
Scenario comparison and Monte Carlo results display
for Cash Flow Planner v2.0

All functions accept plain dicts / DataFrames to avoid coupling
with Pydantic models or other modules.
"""

import streamlit as st
import pandas as pd
from typing import Dict


def render_scenario_comparison(scenarios_results: Dict[str, Dict]) -> None:
    """
    Display a side-by-side scenario comparison with a bar chart and detail table.

    Args:
        scenarios_results: mapping of scenario name to result dict.
            Each result dict must contain:
                - total_fcf  (float): total free cash flow
                - total_ocf  (float): total operating cash flow
                - avg_ccc    (float): average cash conversion cycle in days
    """
    st.subheader("🎯 Scenario Modeling")

    if not scenarios_results:
        st.info("No scenarios to compare.")
        return

    # Build comparison DataFrame
    comparison_data = []
    for name, result in scenarios_results.items():
        comparison_data.append(
            {
                "Scenario": name,
                "Free Cash Flow": result.get("total_fcf", 0),
                "Operating CF": result.get("total_ocf", 0),
                "Avg CCC (days)": result.get("avg_ccc", 0),
            }
        )
    df_comparison = pd.DataFrame(comparison_data)

    # Bar chart comparing FCF and Operating CF across scenarios
    st.bar_chart(
        df_comparison.set_index("Scenario")[["Free Cash Flow", "Operating CF"]]
    )

    # Detail table
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)


def render_monte_carlo_results(mc_results: Dict) -> None:
    """
    Display Monte Carlo simulation summary statistics.

    Args:
        mc_results: dict with keys:
            mean, std, p5, p25, p50, p75, p95, min, max
    """
    st.subheader("🎲 Monte Carlo Simulation")

    with st.expander("What is Monte Carlo Simulation?", expanded=False):
        st.markdown(
            """
**Monte Carlo Simulation** is a statistical method that estimates the range of
possible outcomes by running thousands of randomized trials.

**How it works in this app:**

1. We take your current financial drivers (DSO, DPO, DIO, revenue growth, etc.)
2. For each of **1,000 iterations**, every driver is randomly varied within
   ±20 % of its base value
3. A full cash flow forecast is calculated for each random combination
4. The resulting 1,000 Free Cash Flow values are aggregated into percentile
   statistics

**How to read the results:**

| Metric | Meaning |
|--------|---------|
| **Mean FCF** | Average outcome across all simulations |
| **Std. Deviation** | How spread out the results are — higher means more uncertainty |
| **5th Percentile** | Worst-case boundary (only 5 % of outcomes are worse) |
| **95th Percentile** | Best-case boundary (only 5 % of outcomes are better) |
| **90 % Confidence Range** | The interval between P5 and P95 — your most likely landing zone |

> A narrow range signals a robust forecast; a wide range suggests high
> sensitivity to driver assumptions and warrants deeper scenario analysis.
"""
        )

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Mean FCF", f"{mc_results['mean']:,.0f}")
        st.metric("Std. Deviation", f"{mc_results['std']:,.0f}")

    with col2:
        st.metric("5th Percentile (worst)", f"{mc_results['p5']:,.0f}")
        st.metric("95th Percentile (best)", f"{mc_results['p95']:,.0f}")

    st.info(
        f"📊 With 90% confidence, FCF will be in the range: "
        f"**{mc_results['p5']:,.0f}** — **{mc_results['p95']:,.0f}**"
    )
