"""
Soft validation of financial drivers.

Returns warnings (not errors) for values that are technically valid
but look unusual. Empty list means everything looks reasonable.
"""

from typing import List

from drivers.models import ForecastDrivers


def validate_drivers(drivers: ForecastDrivers) -> List[str]:
    """Check drivers for unusual values and return warnings."""
    warnings: List[str] = []
    wc = drivers.working_capital

    # Working capital checks
    if wc.dso_days > 120:
        warnings.append(
            f"DSO ({wc.dso_days} days) is unusually high - "
            f"customers take over 4 months to pay"
        )

    if wc.dpo_days > 90:
        warnings.append(
            f"DPO ({wc.dpo_days} days) is unusually high - "
            f"supplier payments delayed over 3 months"
        )

    if wc.dio_days > 180:
        warnings.append(
            f"DIO ({wc.dio_days} days) is unusually high - "
            f"inventory turns over more than 6 months"
        )

    if wc.dpo_days > wc.dso_days + wc.dio_days:
        warnings.append(
            f"DPO ({wc.dpo_days}) exceeds DSO + DIO "
            f"({wc.dso_days + wc.dio_days}) - verify DPO"
        )

    ccc = wc.ccc_days
    if ccc < 0:
        warnings.append(
            f"Negative CCC ({ccc:.1f} days) - "
            f"normal for retail/platforms, unusual for other industries"
        )

    # Revenue checks
    rev = drivers.revenue
    if rev.gross_margin_pct < 10:
        warnings.append(
            f"Gross margin ({rev.gross_margin_pct}%) below 10% - "
            f"extremely low margin"
        )

    if rev.gross_margin_pct > 80:
        warnings.append(
            f"Gross margin ({rev.gross_margin_pct}%) above 80% - "
            f"typical only for SaaS/digital products"
        )

    if rev.revenue_growth_pct > 100:
        warnings.append(
            f"Revenue growth ({rev.revenue_growth_pct}%) above 100% - "
            f"verify this is not an input error"
        )

    if rev.seasonality_factors is not None:
        total = sum(rev.seasonality_factors)
        if abs(total - 12.0) > 0.5:
            warnings.append(
                f"Seasonality factors sum ({total:.2f}) "
                f"significantly deviates from 12.0"
            )

    # CapEx checks
    if drivers.capex is not None and drivers.capex.capex_pct_of_revenue > 30:
        warnings.append(
            f"CapEx ({drivers.capex.capex_pct_of_revenue}% of revenue) - "
            f"unusually high capital expenditure"
        )

    # Financing checks
    if drivers.financing is not None:
        if drivers.financing.debt_to_equity > 3:
            warnings.append(
                f"D/E ({drivers.financing.debt_to_equity}) above 3 - "
                f"high debt load"
            )

    return warnings
