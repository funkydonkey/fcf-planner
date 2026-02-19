"""
Industry default driver values.

Provides reasonable starting points for each industry
based on typical benchmarks.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from drivers.models import (
    CapExDrivers,
    FinancingDrivers,
    ForecastDrivers,
    Industry,
    RevenueDrivers,
    WorkingCapitalDrivers,
)

_BENCHMARKS_PATH = Path(__file__).resolve().parent.parent / "data" / "industry_benchmarks.json"
_benchmarks_cache: Optional[Dict] = None


def _load_benchmarks() -> Dict:
    """Load benchmarks from JSON file with caching."""
    global _benchmarks_cache
    if _benchmarks_cache is None:
        with open(_BENCHMARKS_PATH, encoding="utf-8") as f:
            _benchmarks_cache = json.load(f)
    return _benchmarks_cache


_CAPEX_DEFAULTS: Dict[str, CapExDrivers] = {
    "retail": CapExDrivers(capex_pct_of_revenue=3, depreciation_years=10),
    "manufacturing": CapExDrivers(capex_pct_of_revenue=8, depreciation_years=15),
    "services": CapExDrivers(capex_pct_of_revenue=2, depreciation_years=5),
    "technology": CapExDrivers(capex_pct_of_revenue=10, depreciation_years=5),
    "healthcare": CapExDrivers(capex_pct_of_revenue=6, depreciation_years=12),
}

_FINANCING_DEFAULTS: Dict[str, FinancingDrivers] = {
    "retail": FinancingDrivers(interest_rate_pct=6, debt_to_equity=1.5, tax_rate_pct=25),
    "manufacturing": FinancingDrivers(interest_rate_pct=5, debt_to_equity=1.2, tax_rate_pct=25),
    "services": FinancingDrivers(interest_rate_pct=5, debt_to_equity=0.8, tax_rate_pct=25),
    "technology": FinancingDrivers(interest_rate_pct=4, debt_to_equity=0.5, tax_rate_pct=20),
    "healthcare": FinancingDrivers(interest_rate_pct=5, debt_to_equity=1.0, tax_rate_pct=25),
}


def get_industry_defaults(industry: Industry) -> ForecastDrivers:
    """Return typical drivers for the given industry."""
    benchmarks = _load_benchmarks()
    key = industry.value

    if key not in benchmarks:
        raise ValueError(f"No benchmarks for industry: {key}")

    b = benchmarks[key]

    return ForecastDrivers(
        working_capital=WorkingCapitalDrivers(
            dso_days=b["dso"],
            dpo_days=b["dpo"],
            dio_days=b["dio"],
        ),
        revenue=RevenueDrivers(
            revenue_growth_pct=b["revenue_growth"],
            gross_margin_pct=b["gross_margin"],
        ),
        capex=_CAPEX_DEFAULTS.get(key),
        financing=_FINANCING_DEFAULTS.get(key),
        industry=industry,
    )
