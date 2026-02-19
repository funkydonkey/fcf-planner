"""
Scenario modeling engine for what-if analysis.

Creates Base/Optimistic/Pessimistic scenarios by adjusting drivers,
and runs Monte Carlo simulations for risk assessment.
"""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from drivers.models import ForecastDrivers
from .driver_based import DriverBasedForecaster


@dataclass
class Scenario:
    """A single what-if scenario."""
    name: str
    description: str
    drivers: ForecastDrivers
    probability: float = 0.33


class ScenarioEngine:
    """Engine for scenario modeling and Monte Carlo simulation."""

    def __init__(self, base_drivers: ForecastDrivers):
        self.base_drivers = base_drivers

    def create_scenarios(self) -> List[Scenario]:
        """Create Base, Optimistic, and Pessimistic scenarios."""
        scenarios = []

        # Base Case
        scenarios.append(Scenario(
            name="Base Case",
            description="Current trends continue",
            drivers=self.base_drivers,
            probability=0.50,
        ))

        # Optimistic: better collections, faster growth
        opt = self.base_drivers.model_copy(deep=True)
        opt.working_capital.dso_days *= 0.85   # DSO -15%
        opt.working_capital.dpo_days *= 1.1    # DPO +10%
        opt.revenue.revenue_growth_pct *= 1.2  # Growth +20%
        scenarios.append(Scenario(
            name="Optimistic",
            description="Better receivables collection, sales growth",
            drivers=opt,
            probability=0.25,
        ))

        # Pessimistic: slower payments, lower growth
        pes = self.base_drivers.model_copy(deep=True)
        pes.working_capital.dso_days *= 1.2    # DSO +20%
        pes.working_capital.dio_days *= 1.15   # DIO +15%
        pes.revenue.revenue_growth_pct *= 0.5  # Growth -50%
        scenarios.append(Scenario(
            name="Pessimistic",
            description="Payment delays, growth slowdown",
            drivers=pes,
            probability=0.25,
        ))

        return scenarios

    def run_scenarios(
        self, historical_data, periods: int = 12
    ) -> Dict[str, Dict]:
        """Run all scenarios and return results.

        Returns dict mapping scenario name to result dict with:
        total_fcf, total_ocf, avg_ccc, forecast_df.
        """
        results = {}
        for scenario in self.create_scenarios():
            forecaster = DriverBasedForecaster(scenario.drivers)
            forecast = forecaster.generate_forecast(historical_data, periods)
            results[scenario.name] = {
                "total_fcf": forecast["free_cashflow"].sum(),
                "total_ocf": forecast["operating_cashflow"].sum(),
                "avg_ccc": forecast["ccc_days"].mean(),
                "forecast_df": forecast,
                "probability": scenario.probability,
                "description": scenario.description,
            }
        return results

    def run_monte_carlo(
        self,
        historical_data,
        n_simulations: int = 1000,
        periods: int = 12,
    ) -> Dict:
        """Monte Carlo simulation with random driver variations.

        Each simulation randomly adjusts drivers by +-20% and computes
        total FCF. Returns percentile statistics.
        """
        results = []

        for _ in range(n_simulations):
            drivers = self.base_drivers.model_copy(deep=True)

            # Random +-20% variation on key drivers
            drivers.working_capital.dso_days *= np.random.uniform(0.8, 1.2)
            drivers.working_capital.dpo_days *= np.random.uniform(0.8, 1.2)
            drivers.working_capital.dio_days *= np.random.uniform(0.8, 1.2)
            drivers.revenue.revenue_growth_pct *= np.random.uniform(0.5, 1.5)

            forecaster = DriverBasedForecaster(drivers)
            forecast = forecaster.generate_forecast(historical_data, periods)
            results.append(forecast["free_cashflow"].sum())

        arr = np.array(results)

        return {
            "mean": float(arr.mean()),
            "std": float(arr.std()),
            "p5": float(np.percentile(arr, 5)),
            "p25": float(np.percentile(arr, 25)),
            "p50": float(np.percentile(arr, 50)),
            "p75": float(np.percentile(arr, 75)),
            "p95": float(np.percentile(arr, 95)),
            "min": float(arr.min()),
            "max": float(arr.max()),
        }
