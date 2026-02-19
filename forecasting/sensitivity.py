"""
Sensitivity analysis for driver-based forecasting.

Analyzes how changing individual drivers affects Free Cash Flow,
useful for understanding which levers matter most.
"""

from typing import Dict, List, Optional
import numpy as np

from drivers.models import ForecastDrivers
from .driver_based import DriverBasedForecaster


class SensitivityAnalyzer:
    """Analyzes sensitivity of FCF to individual driver changes."""

    def __init__(self, base_drivers: ForecastDrivers):
        self.base_drivers = base_drivers

    def analyze_driver_sensitivity(
        self,
        historical_data,
        driver_name: str,
        variations: Optional[List[float]] = None,
        periods: int = 12,
    ) -> Dict[float, float]:
        """Analyze how changing one driver affects total FCF.

        Args:
            historical_data: DataFrame with 'revenue' column.
            driver_name: One of 'dso_days', 'dpo_days', 'dio_days',
                'revenue_growth_pct', 'gross_margin_pct'.
            variations: Percentage changes to test (default: [-20, -10, 0, +10, +20]).
            periods: Forecast periods.

        Returns:
            Dict mapping variation percentage to total FCF.
        """
        if variations is None:
            variations = [-20, -10, 0, 10, 20]

        results = {}
        for pct in variations:
            drivers = self.base_drivers.model_copy(deep=True)
            multiplier = 1 + pct / 100

            # Apply variation to the specified driver
            if driver_name == "dso_days":
                drivers.working_capital.dso_days *= multiplier
            elif driver_name == "dpo_days":
                drivers.working_capital.dpo_days *= multiplier
            elif driver_name == "dio_days":
                drivers.working_capital.dio_days *= multiplier
            elif driver_name == "revenue_growth_pct":
                drivers.revenue.revenue_growth_pct *= multiplier
            elif driver_name == "gross_margin_pct":
                drivers.revenue.gross_margin_pct = min(
                    100, drivers.revenue.gross_margin_pct * multiplier
                )
            else:
                raise ValueError(f"Unknown driver: {driver_name}")

            forecaster = DriverBasedForecaster(drivers)
            forecast = forecaster.generate_forecast(historical_data, periods)
            results[pct] = float(forecast["free_cashflow"].sum())

        return results

    def tornado_chart_data(
        self,
        historical_data,
        periods: int = 12,
    ) -> List[Dict]:
        """Generate data for tornado chart: +-10% impact per driver.

        Returns list of dicts with: driver_name, low_value, base_value, high_value.
        """
        drivers_to_test = [
            "dso_days", "dpo_days", "dio_days",
            "revenue_growth_pct", "gross_margin_pct",
        ]

        # Base case FCF
        base_forecaster = DriverBasedForecaster(self.base_drivers)
        base_forecast = base_forecaster.generate_forecast(historical_data, periods)
        base_fcf = float(base_forecast["free_cashflow"].sum())

        tornado_data = []
        for driver in drivers_to_test:
            sensitivity = self.analyze_driver_sensitivity(
                historical_data, driver, variations=[-10, 10], periods=periods
            )
            tornado_data.append({
                "driver_name": driver,
                "low_value": sensitivity[-10],
                "base_value": base_fcf,
                "high_value": sensitivity[10],
            })

        # Sort by impact range (largest impact first)
        tornado_data.sort(
            key=lambda x: abs(x["high_value"] - x["low_value"]),
            reverse=True,
        )
        return tornado_data
