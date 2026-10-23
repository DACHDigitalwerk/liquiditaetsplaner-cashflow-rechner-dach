# -*- coding: utf-8 -*-
"""
DACH Liquiditätsplaner & Cashflow-Forecaster 2026 (IDW S11 & StaRUG § 1)
========================================================================

Open-Source Python Core Engine für die rollierende 13-Wochen-Liquiditätsplanung
von KMU, Cash Conversion Cycle (DSO, DPO, DIO) und Krisenfrüherkennung
gem. § 1 StaRUG (DE), Art. 725a OR (CH) und URG (AT).

Entwickelt von DACH Digitalwerk (https://dachdigitalwerk.github.io).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__license__ = "MIT"

from .models import (
    Country,
    WeeklyCashflow,
    LiquidityPlanInput,
    LiquidityPlanResult,
    CashConversionCycleInput,
    CashConversionCycleResult,
    StaRUGStatus,
)
from .calculator import (
    calculate_13_week_plan,
    calculate_cash_conversion_cycle,
    assess_starug_risk,
)
from .validator import validate_plan_input, validate_ccc_input

__all__ = [
    "Country",
    "WeeklyCashflow",
    "LiquidityPlanInput",
    "LiquidityPlanResult",
    "CashConversionCycleInput",
    "CashConversionCycleResult",
    "StaRUGStatus",
    "calculate_13_week_plan",
    "calculate_cash_conversion_cycle",
    "assess_starug_risk",
    "validate_plan_input",
    "validate_ccc_input",
]
