"""
Cash Flow Planner v2.0 - Streamlit Application
Driver-based forecasting with AI agents and scenario modeling
"""
import streamlit as st
import pandas as pd
from io import BytesIO

from core.io_historical import load_history_from_file, get_data_summary
from core.db import init_db, save_scenario, get_scenarios_list, get_scenario_lines
from core.data_transform import pivot_to_wide_format, add_forecast_columns, get_next_month_name

# Database initialization at startup
init_db()

# Page configuration
st.set_page_config(
    page_title="Cash Flow Planner v2.0",
    page_icon="💰",
    layout="wide"
)

# Header
st.title("💰 Cash Flow Planner v2.0")
st.markdown("Driver-based forecasting with AI")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Forecast",
    "📈 Drivers & Analysis",
    "🎯 Scenarios",
    "📜 History"
])

# === TAB 1: FORECAST (original functionality preserved) ===
with tab1:
    st.header("Data Loading and Forecasting")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload file with historical data (Excel or CSV)",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file is not None:
        try:
            # Load data
            with st.spinner("Loading data..."):
                df_history = load_history_from_file(uploaded_file)

            # Show statistics
            st.success(f"Loaded {len(df_history)} records")

            summary = get_data_summary(df_history)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records", summary['total_records'])
            with col2:
                st.metric("Categories", len(summary['categories']))
            with col3:
                st.metric("Months", summary['months_count'])
            with col4:
                st.metric("Total", f"{summary['total_amount']:,.0f}")

            # Convert to wide format for display
            df_wide = pivot_to_wide_format(df_history)

            # Determine next month
            next_month = get_next_month_name(df_history)

            # Check if there's already edited data in session_state
            if 'edited_df' in st.session_state and 'last_uploaded_file' in st.session_state:
                if st.session_state['last_uploaded_file'] == uploaded_file.name:
                    df_display = st.session_state['edited_df']
                else:
                    df_display = add_forecast_columns(df_wide, next_month)
                    st.session_state['last_uploaded_file'] = uploaded_file.name
            else:
                df_display = add_forecast_columns(df_wide, next_month)
                st.session_state['last_uploaded_file'] = uploaded_file.name

            # Save in session_state
            st.session_state['df_history'] = df_history
            st.session_state['df_wide'] = df_display
            st.session_state['next_month'] = next_month

            # Show data table
            st.subheader("Historical Data and Forecast")

            column_config = {
                "category": st.column_config.TextColumn("Category", width="medium")
            }

            for col in df_display.columns:
                if col != 'category':
                    is_editable = any(x in col for x in ['Forecast', 'Adjustments'])
                    column_config[col] = st.column_config.NumberColumn(
                        col, format="%.0f", disabled=(not is_editable)
                    )

            edited_df = st.data_editor(
                df_display, column_config=column_config,
                hide_index=True, use_container_width=True,
                key="cashflow_table"
            )

            # Recalculate totals
            total_col = f"{next_month}_Total"
            forecast_col = f"{next_month}_Forecast"
            comment_col = f"{next_month}_Comments"
            adjustment_col = f"{next_month}_Adjustments"

            edited_df[total_col] = edited_df[forecast_col] + edited_df[adjustment_col]
            st.session_state['edited_df'] = edited_df

            # Show totals
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"Forecast", f"{edited_df[forecast_col].sum():,.0f}")
            with col2:
                st.metric(f"Adjustments", f"{edited_df[adjustment_col].sum():,.0f}")
            with col3:
                st.metric(f"Total", f"{edited_df[total_col].sum():,.0f}")

            st.divider()

            # AI Forecast button
            if st.button("Calculate AI Forecast", type="primary", use_container_width=True):
                try:
                    with st.spinner("AI agent is analyzing data..."):
                        from ai_agents.forecast_agent import build_cashflow_forecast

                        df_wide_for_forecast = pivot_to_wide_format(df_history)
                        last_month = get_next_month_name(df_history, 'date')
                        forecast_df = build_cashflow_forecast(df_wide_for_forecast, last_month)

                        updated_df = edited_df.copy()
                        for idx, category in enumerate(forecast_df['category']):
                            category_idx = updated_df[updated_df['category'] == category].index
                            if len(category_idx) > 0:
                                updated_df.loc[category_idx[0], forecast_col] = forecast_df.loc[idx, 'ai_forecast']
                                updated_df.loc[category_idx[0], comment_col] = forecast_df.loc[idx, 'ai_comments']

                        updated_df[total_col] = updated_df[forecast_col] + updated_df[adjustment_col]
                        st.session_state['edited_df'] = updated_df

                        st.success(f"Forecast complete! Updated {len(forecast_df)} categories")
                        st.rerun()

                except Exception as e:
                    import traceback
                    st.error(f"Error building forecast: {str(e)}")
                    with st.expander("Error details"):
                        st.code(traceback.format_exc())

            # Save form
            with st.form("save_scenario_form"):
                st.subheader("Save Scenario")
                description = st.text_area("Scenario description (optional)")
                submitted = st.form_submit_button("Save to DB", type="primary")

                if submitted:
                    try:
                        rows = []
                        for _, row in edited_df.iterrows():
                            rows.append({
                                'category': row['category'],
                                'period_date': next_month,
                                'forecast_amount': row[forecast_col],
                                'adjustment_amount': row[adjustment_col],
                                'final_amount': row[total_col]
                            })

                        # Include drivers if set
                        drivers_data = None
                        if 'current_drivers' in st.session_state:
                            d = st.session_state['current_drivers']
                            drivers_data = {
                                'dso_days': d['working_capital']['dso_days'],
                                'dpo_days': d['working_capital']['dpo_days'],
                                'dio_days': d['working_capital']['dio_days'],
                                'ccc_days': d['ccc_days'],
                                'revenue_growth_pct': d['revenue']['revenue_growth_pct'],
                                'gross_margin_pct': d['revenue']['gross_margin_pct'],
                                'capex_pct': d['capex']['capex_pct_of_revenue'] if d.get('capex') else None,
                                'industry': d.get('industry'),
                            }

                        scenario_id = save_scenario(
                            forecast_period=next_month,
                            rows=rows,
                            description=description if description else None,
                            drivers_data=drivers_data,
                        )
                        st.success(f"Scenario saved! ID: {scenario_id}")

                    except Exception as e:
                        st.error(f"Error saving: {str(e)}")

        except Exception as e:
            st.error(f"File loading error: {str(e)}")

    else:
        st.info("Upload a file to get started")


# === TAB 2: DRIVERS & ANALYSIS ===
with tab2:
    st.header("Financial Drivers & AI Analysis")

    from ui.driver_input import render_driver_input_form

    # Render driver input form
    drivers_dict = render_driver_input_form()

    # Save drivers to session state
    st.session_state['current_drivers'] = drivers_dict

    st.divider()

    # Driver-based forecast
    if st.button("Calculate Driver-Based Forecast", type="primary", use_container_width=True):
        if 'df_history' not in st.session_state:
            st.warning("Upload historical data first (Forecast tab)")
        else:
            try:
                with st.spinner("Calculating driver-based forecast..."):
                    from drivers.models import (
                        ForecastDrivers, WorkingCapitalDrivers,
                        RevenueDrivers, CapExDrivers, Industry
                    )
                    from forecasting.driver_based import DriverBasedForecaster
                    import config

                    # Build ForecastDrivers from form data
                    wc = WorkingCapitalDrivers(
                        dso_days=drivers_dict['working_capital']['dso_days'],
                        dpo_days=drivers_dict['working_capital']['dpo_days'],
                        dio_days=drivers_dict['working_capital']['dio_days'],
                    )
                    rev = RevenueDrivers(
                        revenue_growth_pct=drivers_dict['revenue']['revenue_growth_pct'],
                        gross_margin_pct=drivers_dict['revenue']['gross_margin_pct'],
                    )
                    capex = None
                    if drivers_dict.get('capex'):
                        capex = CapExDrivers(
                            capex_pct_of_revenue=drivers_dict['capex']['capex_pct_of_revenue'],
                            depreciation_years=drivers_dict['capex']['depreciation_years'],
                        )

                    forecast_drivers = ForecastDrivers(
                        working_capital=wc,
                        revenue=rev,
                        capex=capex,
                        industry=Industry(drivers_dict['industry']) if drivers_dict.get('industry') else None,
                    )

                    # Prepare historical data for forecaster
                    df_hist = st.session_state['df_history']
                    # Aggregate monthly revenue from categories
                    monthly = df_hist.groupby(df_hist['date'].dt.to_period('M'))['amount'].sum().reset_index()
                    monthly.columns = ['period', 'revenue']
                    monthly['revenue'] = monthly['revenue'].astype(float)

                    forecaster = DriverBasedForecaster(forecast_drivers)
                    forecast_df = forecaster.generate_forecast(
                        monthly, periods=config.DEFAULT_FORECAST_PERIODS
                    )

                    st.session_state['driver_forecast_df'] = forecast_df
                    st.session_state['forecast_drivers'] = forecast_drivers

                st.success("Driver-based forecast calculated!")

            except Exception as e:
                import traceback
                st.error(f"Error: {str(e)}")
                with st.expander("Details"):
                    st.code(traceback.format_exc())

    # Display forecast dashboard if available
    if 'driver_forecast_df' in st.session_state:
        from ui.dashboard import render_cashflow_dashboard
        render_cashflow_dashboard(st.session_state['driver_forecast_df'])

    st.divider()

    # AI Driver Analysis
    if st.button("AI Driver Analysis", use_container_width=True):
        try:
            with st.spinner("AI is analyzing drivers..."):
                from ai_agents.driver_agent import analyze_drivers_sync

                analysis = analyze_drivers_sync(
                    drivers={
                        'dso_days': drivers_dict['working_capital']['dso_days'],
                        'dpo_days': drivers_dict['working_capital']['dpo_days'],
                        'dio_days': drivers_dict['working_capital']['dio_days'],
                    },
                    industry=drivers_dict.get('industry', 'services'),
                )
                st.session_state['driver_analysis'] = analysis

        except Exception as e:
            import traceback
            st.error(f"Error: {str(e)}")
            with st.expander("Details"):
                st.code(traceback.format_exc())

    if 'driver_analysis' in st.session_state:
        from ui.dashboard import render_driver_analysis_results
        render_driver_analysis_results(st.session_state['driver_analysis'])


# === TAB 3: SCENARIOS ===
with tab3:
    st.header("Scenario Modeling")

    if 'forecast_drivers' not in st.session_state:
        st.info("Set up drivers and run forecast first (Drivers & Analysis tab)")
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Run Scenario Comparison", type="primary", use_container_width=True):
                if 'df_history' not in st.session_state:
                    st.warning("Upload historical data first")
                else:
                    try:
                        with st.spinner("Running scenarios..."):
                            from forecasting.scenarios import ScenarioEngine

                            df_hist = st.session_state['df_history']
                            monthly = df_hist.groupby(
                                df_hist['date'].dt.to_period('M')
                            )['amount'].sum().reset_index()
                            monthly.columns = ['period', 'revenue']
                            monthly['revenue'] = monthly['revenue'].astype(float)

                            engine = ScenarioEngine(st.session_state['forecast_drivers'])
                            results = engine.run_scenarios(monthly)
                            st.session_state['scenario_results'] = results

                        st.success("Scenarios calculated!")

                    except Exception as e:
                        import traceback
                        st.error(f"Error: {str(e)}")
                        with st.expander("Details"):
                            st.code(traceback.format_exc())

        with col2:
            if st.button("Run Monte Carlo Simulation", use_container_width=True):
                if 'df_history' not in st.session_state:
                    st.warning("Upload historical data first")
                else:
                    try:
                        with st.spinner("Running Monte Carlo simulation (1000 iterations)..."):
                            from forecasting.scenarios import ScenarioEngine
                            import config

                            df_hist = st.session_state['df_history']
                            monthly = df_hist.groupby(
                                df_hist['date'].dt.to_period('M')
                            )['amount'].sum().reset_index()
                            monthly.columns = ['period', 'revenue']
                            monthly['revenue'] = monthly['revenue'].astype(float)

                            engine = ScenarioEngine(st.session_state['forecast_drivers'])
                            mc_results = engine.run_monte_carlo(
                                monthly,
                                n_simulations=config.MONTE_CARLO_SIMULATIONS,
                            )
                            st.session_state['mc_results'] = mc_results

                        st.success("Monte Carlo simulation complete!")

                    except Exception as e:
                        import traceback
                        st.error(f"Error: {str(e)}")
                        with st.expander("Details"):
                            st.code(traceback.format_exc())

        # Display scenario results
        if 'scenario_results' in st.session_state:
            from ui.scenario_builder import render_scenario_comparison
            render_scenario_comparison(st.session_state['scenario_results'])

        # Display Monte Carlo results
        if 'mc_results' in st.session_state:
            from ui.scenario_builder import render_monte_carlo_results
            render_monte_carlo_results(st.session_state['mc_results'])

        st.divider()

        # AI Scenario suggestions
        if st.button("AI Scenario Suggestions", use_container_width=True):
            try:
                with st.spinner("AI is generating scenario suggestions..."):
                    from ai_agents.scenario_agent import suggest_scenarios_sync

                    d = st.session_state['current_drivers']
                    suggestions = suggest_scenarios_sync(
                        current_drivers={
                            'dso_days': d['working_capital']['dso_days'],
                            'dpo_days': d['working_capital']['dpo_days'],
                            'dio_days': d['working_capital']['dio_days'],
                        },
                        industry=d.get('industry', 'services'),
                        historical_summary={
                            'months_analyzed': st.session_state.get('df_history', pd.DataFrame()).shape[0],
                        },
                    )
                    st.session_state['ai_scenarios'] = suggestions

            except Exception as e:
                import traceback
                st.error(f"Error: {str(e)}")
                with st.expander("Details"):
                    st.code(traceback.format_exc())

        if 'ai_scenarios' in st.session_state:
            suggestions = st.session_state['ai_scenarios']
            st.subheader("AI Scenario Suggestions")
            st.markdown(f"**Recommendation:** {suggestions.recommendation}")

            for s in suggestions.scenarios:
                with st.expander(f"{s.scenario_name} (p={s.probability:.0%})"):
                    st.write(s.description)
                    st.write(f"**Adjustments:** {s.driver_adjustments}")
                    st.write(f"**Reasoning:** {s.reasoning}")

            if suggestions.key_uncertainties:
                st.markdown("**Key Uncertainties:**")
                for u in suggestions.key_uncertainties:
                    st.markdown(f"- {u}")


# === TAB 4: HISTORY ===
with tab4:
    st.header("Scenario History")

    try:
        scenarios = get_scenarios_list()

        if scenarios:
            scenarios_df = pd.DataFrame(scenarios)
            scenarios_df['created_at'] = pd.to_datetime(scenarios_df['created_at'])

            st.dataframe(
                scenarios_df[[
                    'id', 'created_at', 'forecast_period',
                    'description', 'total_final_amount'
                ]],
                column_config={
                    "id": "ID",
                    "created_at": st.column_config.DatetimeColumn("Created", format="DD.MM.YYYY HH:mm"),
                    "forecast_period": "Period",
                    "description": "Description",
                    "total_final_amount": st.column_config.NumberColumn("Total", format="%.2f")
                },
                hide_index=True,
                use_container_width=True
            )

            st.divider()

            scenario_id = st.selectbox(
                "Select scenario to view details",
                options=[s['id'] for s in scenarios],
                format_func=lambda x: f"Scenario #{x} - {next(s['forecast_period'] for s in scenarios if s['id'] == x)}"
            )

            if scenario_id:
                lines = get_scenario_lines(scenario_id)
                if lines:
                    st.subheader(f"Scenario Details #{scenario_id}")
                    lines_df = pd.DataFrame(lines)
                    st.dataframe(lines_df, use_container_width=True, hide_index=True)

                # Show drivers if saved
                from core.db import get_scenario_drivers
                saved_drivers = get_scenario_drivers(scenario_id)
                if saved_drivers:
                    st.subheader("Saved Drivers")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("DSO", f"{saved_drivers['dso_days']:.0f} days")
                    with col2:
                        st.metric("DPO", f"{saved_drivers['dpo_days']:.0f} days")
                    with col3:
                        st.metric("DIO", f"{saved_drivers['dio_days']:.0f} days")
                    with col4:
                        st.metric("CCC", f"{saved_drivers['ccc_days']:.0f} days")

        else:
            st.info("No saved scenarios yet")

    except Exception as e:
        st.error(f"Error loading history: {str(e)}")
