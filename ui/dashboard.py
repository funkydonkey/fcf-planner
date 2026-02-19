"""
Cash flow dashboard components for Cash Flow Planner v2.0

Renders Plotly-powered charts (waterfall, line) with a graceful
fallback to native Streamlit charts when Plotly is not installed.

Functions accept plain dicts, DataFrames, or simple attribute-bearing
objects — never Pydantic models directly — to avoid import coupling.
"""

import streamlit as st
import pandas as pd


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------

def render_cashflow_dashboard(forecast_df: pd.DataFrame) -> None:
    """
    Main dashboard with cash flow visualisation.

    Args:
        forecast_df: DataFrame with required columns:
            period, revenue, operating_cashflow, free_cashflow,
            gross_profit, depreciation, delta_ar, delta_ap,
            delta_inventory, ccc_days
    """
    st.subheader("📊 Cash Flow Forecast")

    try:
        import plotly.graph_objects as go

        # 1. Waterfall: composition of Operating Cash Flow
        fig_waterfall = go.Figure(
            go.Waterfall(
                name="Operating Cash Flow",
                orientation="v",
                x=[
                    "Gross Profit",
                    "Depreciation",
                    "Δ Receivables",
                    "Δ Payables",
                    "Δ Inventory",
                    "Operating CF",
                ],
                y=[
                    forecast_df["gross_profit"].sum(),
                    forecast_df["depreciation"].sum(),
                    -forecast_df["delta_ar"].sum(),
                    forecast_df["delta_ap"].sum(),
                    -forecast_df["delta_inventory"].sum(),
                    0,
                ],
                measure=[
                    "relative",
                    "relative",
                    "relative",
                    "relative",
                    "relative",
                    "total",
                ],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            )
        )
        fig_waterfall.update_layout(
            title="Operating Cash Flow Breakdown",
            showlegend=False,
        )
        st.plotly_chart(fig_waterfall, use_container_width=True)

        # 2. Line chart: Revenue vs Operating CF vs Free CF
        fig_lines = go.Figure()
        fig_lines.add_trace(
            go.Scatter(
                x=forecast_df["period"],
                y=forecast_df["revenue"],
                name="Revenue",
                line=dict(color="blue"),
            )
        )
        fig_lines.add_trace(
            go.Scatter(
                x=forecast_df["period"],
                y=forecast_df["operating_cashflow"],
                name="Operating CF",
                line=dict(color="green"),
            )
        )
        fig_lines.add_trace(
            go.Scatter(
                x=forecast_df["period"],
                y=forecast_df["free_cashflow"],
                name="Free CF",
                line=dict(color="orange"),
            )
        )
        fig_lines.update_layout(
            title="Cash Flow Trends",
            xaxis_title="Period",
            yaxis_title="Amount",
        )
        st.plotly_chart(fig_lines, use_container_width=True)

    except ImportError:
        # Fallback to native Streamlit charts when Plotly is unavailable
        chart_df = forecast_df[
            ["period", "revenue", "operating_cashflow", "free_cashflow"]
        ].set_index("period")
        st.line_chart(chart_df)

    # 3. Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Σ Operating CF",
            f"{forecast_df['operating_cashflow'].sum():,.0f}",
        )
    with col2:
        st.metric(
            "Σ Free CF",
            f"{forecast_df['free_cashflow'].sum():,.0f}",
        )
    with col3:
        st.metric(
            "Avg CCC",
            f"{forecast_df['ccc_days'].mean():.1f} days",
        )
    with col4:
        total_rev = forecast_df["revenue"].sum()
        if total_rev > 0:
            conversion = forecast_df["free_cashflow"].sum() / total_rev * 100
            st.metric("FCF/Revenue", f"{conversion:.1f}%")


# ---------------------------------------------------------------------------
# AI driver analysis
# ---------------------------------------------------------------------------

def render_driver_analysis_results(analysis_response) -> None:
    """
    Display AI driver analysis results.

    Args:
        analysis_response: object (or duck-typed dict-like) with attributes:
            - recommendations: list of objects with driver_name, current_value,
              recommended_value, industry_benchmark, impact_on_cashflow, reasoning
            - overall_assessment: str
            - risk_factors: list[str]
            - opportunities: list[str]
    """
    st.subheader("🤖 AI Driver Analysis")

    # Overall assessment
    st.info(analysis_response.overall_assessment)

    # Recommendations
    if analysis_response.recommendations:
        st.markdown("#### Recommendations")
        for rec in analysis_response.recommendations:
            with st.expander(
                f"📌 {rec.driver_name}: {rec.current_value} → {rec.recommended_value}"
            ):
                st.write(f"**Industry Benchmark:** {rec.industry_benchmark}")
                st.write(f"**Impact on CF:** {rec.impact_on_cashflow}")
                st.write(f"**Reasoning:** {rec.reasoning}")

    # Risks and opportunities side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚠️ Risks")
        for risk in analysis_response.risk_factors:
            st.warning(risk)

    with col2:
        st.markdown("#### 💡 Opportunities")
        for opp in analysis_response.opportunities:
            st.success(opp)


# ---------------------------------------------------------------------------
# Forecast explanation
# ---------------------------------------------------------------------------

def render_forecast_explanation(explanation) -> None:
    """
    Display AI forecast explanation.

    Args:
        explanation: object (or duck-typed dict-like) with attributes:
            - summary: str
            - key_drivers: list[str]
            - assumptions: list[str]
            - risks: list[str]
            - confidence_level: str ("high", "medium", or "low")
            - recommendation: str
    """
    st.subheader("📝 Forecast Explanation")

    # Confidence badge
    confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
    badge = confidence_colors.get(explanation.confidence_level, "⚪")
    st.markdown(
        f"**Confidence Level:** {badge} {explanation.confidence_level}"
    )

    # Summary
    st.markdown(f"**Summary:** {explanation.summary}")

    # Key drivers
    st.markdown("**Key Drivers:**")
    for driver in explanation.key_drivers:
        st.markdown(f"- {driver}")

    # Assumptions (collapsed by default)
    with st.expander("📋 Assumptions"):
        for assumption in explanation.assumptions:
            st.markdown(f"- {assumption}")

    # Risks (collapsed by default)
    with st.expander("⚠️ Risks"):
        for risk in explanation.risks:
            st.markdown(f"- {risk}")

    # Recommendation
    st.markdown(f"**💡 Recommendation:** {explanation.recommendation}")
