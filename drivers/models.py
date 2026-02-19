"""
Pydantic models for financial drivers.

Drivers describe key financial parameters:
working capital, revenue, capex, and financing.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Industry(str, Enum):
    """Industries with predefined benchmarks."""
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"


class WorkingCapitalDrivers(BaseModel):
    """Working capital drivers: DSO, DPO, DIO."""

    dso_days: float = Field(
        ge=0, le=365,
        description="Days Sales Outstanding",
    )
    dpo_days: float = Field(
        ge=0, le=365,
        description="Days Payable Outstanding",
    )
    dio_days: float = Field(
        ge=0, le=365,
        description="Days Inventory Outstanding",
    )

    @property
    def ccc_days(self) -> float:
        """Cash Conversion Cycle = DSO + DIO - DPO."""
        return self.dso_days + self.dio_days - self.dpo_days


class RevenueDrivers(BaseModel):
    """Revenue drivers: growth, margin, seasonality."""

    revenue_growth_pct: float = Field(
        ge=-100, le=500,
        description="Revenue growth YoY (%)",
    )
    gross_margin_pct: float = Field(
        ge=0, le=100,
        description="Gross margin (%)",
    )
    seasonality_factors: Optional[List[float]] = Field(
        default=None,
        description="12 monthly seasonality coefficients (sum ~12.0)",
    )

    @model_validator(mode="after")
    def validate_seasonality_length(self) -> "RevenueDrivers":
        """Seasonality must have exactly 12 values if provided."""
        if self.seasonality_factors is not None:
            if len(self.seasonality_factors) != 12:
                raise ValueError(
                    f"seasonality_factors must have 12 values, "
                    f"got {len(self.seasonality_factors)}"
                )
        return self


class CapExDrivers(BaseModel):
    """Capital expenditure drivers."""

    capex_pct_of_revenue: float = Field(
        ge=0, le=100,
        description="CapEx as % of revenue",
    )
    depreciation_years: int = Field(
        ge=1, le=40,
        description="Depreciation period (years)",
    )


class FinancingDrivers(BaseModel):
    """Financing and tax drivers."""

    interest_rate_pct: float = Field(
        ge=0, le=50,
        description="Interest rate on debt (%)",
    )
    debt_to_equity: float = Field(
        ge=0, le=10,
        description="Debt/Equity ratio",
    )
    tax_rate_pct: float = Field(
        ge=0, le=50,
        description="Tax rate (%)",
    )


class ForecastDrivers(BaseModel):
    """Complete set of drivers for cash flow forecasting.

    Only working_capital and revenue are required.
    CapEx and financing are optional.
    """

    working_capital: WorkingCapitalDrivers
    revenue: RevenueDrivers
    capex: Optional[CapExDrivers] = None
    financing: Optional[FinancingDrivers] = None
    industry: Optional[Industry] = None
