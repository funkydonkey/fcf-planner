"""
Driver-based cash flow forecasting engine.

Calculates working capital, operating cash flow, and free cash flow
based on financial drivers (DSO, DPO, DIO, growth, margins, etc).
"""

import pandas as pd
import numpy as np
from typing import Dict

from drivers.models import ForecastDrivers


class DriverBasedForecaster:
    """Forecaster that uses financial drivers to project cash flows."""

    def __init__(self, drivers: ForecastDrivers):
        self.drivers = drivers

    def forecast_working_capital(
        self, revenue: float, cogs: float
    ) -> Dict[str, float]:
        """Calculate working capital components from revenue and COGS.

        Returns dict with: accounts_receivable, accounts_payable,
        inventory, net_working_capital, ccc_days.
        """
        wc = self.drivers.working_capital
        ar = (revenue / 365) * wc.dso_days
        ap = (cogs / 365) * wc.dpo_days
        inventory = (cogs / 365) * wc.dio_days
        nwc = ar + inventory - ap

        return {
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "inventory": inventory,
            "net_working_capital": nwc,
            "ccc_days": wc.ccc_days,
        }

    def forecast_operating_cashflow(
        self,
        revenue: float,
        previous_revenue: float,
        cogs: float,
        previous_cogs: float,
        depreciation: float = 0,
    ) -> Dict[str, float]:
        """Operating CF = Gross Profit + Depreciation - Delta WC (indirect method)."""
        current_wc = self.forecast_working_capital(revenue, cogs)
        previous_wc = self.forecast_working_capital(previous_revenue, previous_cogs)

        delta_wc = current_wc["net_working_capital"] - previous_wc["net_working_capital"]
        gross_profit = revenue * (self.drivers.revenue.gross_margin_pct / 100)
        operating_cf = gross_profit + depreciation - delta_wc

        return {
            "gross_profit": gross_profit,
            "depreciation": depreciation,
            "delta_working_capital": delta_wc,
            "delta_ar": current_wc["accounts_receivable"] - previous_wc["accounts_receivable"],
            "delta_ap": current_wc["accounts_payable"] - previous_wc["accounts_payable"],
            "delta_inventory": current_wc["inventory"] - previous_wc["inventory"],
            "operating_cashflow": operating_cf,
        }

    def forecast_free_cashflow(
        self, operating_cf: float, revenue: float
    ) -> Dict[str, float]:
        """FCF = Operating CF - CapEx."""
        capex = (
            revenue * (self.drivers.capex.capex_pct_of_revenue / 100)
            if self.drivers.capex
            else 0
        )
        return {
            "capex": capex,
            "free_cashflow": operating_cf - capex,
        }

    def generate_forecast(
        self, historical_data: pd.DataFrame, periods: int = 12
    ) -> pd.DataFrame:
        """Generate full forecast for N periods.

        Args:
            historical_data: DataFrame with 'revenue' column (and optionally 'cogs').
            periods: Number of forecast periods.

        Returns:
            DataFrame with columns: period, revenue, cogs, accounts_receivable,
            accounts_payable, inventory, net_working_capital, ccc_days,
            gross_profit, depreciation, delta_working_capital, delta_ar,
            delta_ap, delta_inventory, operating_cashflow, capex, free_cashflow.
        """
        last_revenue = historical_data["revenue"].iloc[-1]
        last_cogs = (
            historical_data["cogs"].iloc[-1]
            if "cogs" in historical_data
            else last_revenue * 0.65
        )

        forecasts = []
        for i in range(periods):
            # Monthly growth from annual rate
            growth = 1 + (self.drivers.revenue.revenue_growth_pct / 100) / 12
            revenue = last_revenue * growth
            cogs = revenue * (1 - self.drivers.revenue.gross_margin_pct / 100)

            # Apply seasonality
            if self.drivers.revenue.seasonality_factors:
                month_idx = i % 12
                revenue *= self.drivers.revenue.seasonality_factors[month_idx]

            wc = self.forecast_working_capital(revenue, cogs)
            ocf = self.forecast_operating_cashflow(
                revenue, last_revenue,
                cogs, last_cogs,
                depreciation=revenue * 0.02,
            )
            fcf = self.forecast_free_cashflow(ocf["operating_cashflow"], revenue)

            forecasts.append({
                "period": i + 1,
                "revenue": revenue,
                "cogs": cogs,
                **wc,
                **ocf,
                **fcf,
            })

            last_revenue = revenue
            last_cogs = cogs

        return pd.DataFrame(forecasts)
