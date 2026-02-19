"""
Working capital metrics calculator based on financial drivers.

All formulas use annual basis (365 days).
Input amounts should be annual values.
"""

from typing import Dict

from drivers.models import WorkingCapitalDrivers

DAYS_IN_YEAR = 365


def calculate_accounts_receivable(annual_revenue: float, dso_days: float) -> float:
    """AR = (Revenue / 365) * DSO"""
    return (annual_revenue / DAYS_IN_YEAR) * dso_days


def calculate_accounts_payable(annual_cogs: float, dpo_days: float) -> float:
    """AP = (COGS / 365) * DPO"""
    return (annual_cogs / DAYS_IN_YEAR) * dpo_days


def calculate_inventory(annual_cogs: float, dio_days: float) -> float:
    """Inventory = (COGS / 365) * DIO"""
    return (annual_cogs / DAYS_IN_YEAR) * dio_days


def calculate_net_working_capital(
    accounts_receivable: float,
    inventory: float,
    accounts_payable: float,
) -> float:
    """NWC = AR + Inventory - AP"""
    return accounts_receivable + inventory - accounts_payable


def calculate_ccc(dso_days: float, dio_days: float, dpo_days: float) -> float:
    """Cash Conversion Cycle = DSO + DIO - DPO"""
    return dso_days + dio_days - dpo_days


def calculate_working_capital_from_drivers(
    annual_revenue: float,
    annual_cogs: float,
    drivers: WorkingCapitalDrivers,
) -> Dict[str, float]:
    """Full working capital calculation from drivers.

    Returns dict with: accounts_receivable, accounts_payable,
    inventory, net_working_capital, ccc_days.
    """
    ar = calculate_accounts_receivable(annual_revenue, drivers.dso_days)
    ap = calculate_accounts_payable(annual_cogs, drivers.dpo_days)
    inv = calculate_inventory(annual_cogs, drivers.dio_days)
    nwc = calculate_net_working_capital(ar, inv, ap)

    return {
        "accounts_receivable": round(ar, 2),
        "accounts_payable": round(ap, 2),
        "inventory": round(inv, 2),
        "net_working_capital": round(nwc, 2),
        "ccc_days": round(drivers.ccc_days, 1),
    }
