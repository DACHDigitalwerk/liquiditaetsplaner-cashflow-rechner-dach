# -*- coding: utf-8 -*-
"""
Data Models for 13-Week Liquidity Planning and Cash Conversion Cycle
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class Country(str, Enum):
    DE = "DE"  # Deutschland (StaRUG § 1, IDW S11)
    AT = "AT"  # Österreich (URG Reorganisationsbedarf)
    CH = "CH"  # Schweiz (Art. 725a OR)


class StaRUGStatus(str, Enum):
    HEALTHY = "healthy"         # Liquidität gesichert, Puffer intakt
    BUFFER_USED = "buffer_used" # Puffer angegriffen, aber noch im Kontokorrentrahmen
    CRITICAL = "critical"       # Deckungslücke / Insolvenzgefahr (§ 17 InsO / § 1 StaRUG)


@dataclass
class WeeklyCashflow:
    """Cashflow positions for a single week (W1..W13)."""
    week_number: int
    customer_receipts: float = 0.0      # Einzahlungen aus Forderungen (Debitoren)
    other_inflows: float = 0.0          # Sonstige Einzahlungen (z.B. USt-Erstattung)
    material_costs: float = 0.0         # Wareneinsatz / Lieferanten (Kreditoren)
    personnel_costs: float = 0.0        # Löhne, Gehälter, SV-Beiträge
    rent_leasing: float = 0.0           # Miete, Pacht, Leasing
    tax_payments: float = 0.0           # Steuern (USt, GewSt, KSt/ESt)
    debt_service: float = 0.0           # Zins- und Tilgungsdienst
    other_outflows: float = 0.0         # Sonstige Auszahlungen & CapEx


@dataclass
class WeeklyResult:
    """Result status for a single week."""
    week_number: int
    starting_balance: float
    total_inflows: float
    total_outflows: float
    net_cashflow: float
    ending_balance: float
    credit_line_utilization_pct: float
    shortfall: float
    is_critical: bool


@dataclass
class LiquidityPlanInput:
    """Input parameters for rolling 13-week forecast."""
    starting_cash: float
    credit_limit: float = 0.0
    safety_buffer: float = 0.0
    country: Country = Country.DE
    weeks: List[WeeklyCashflow] = field(default_factory=list)


@dataclass
class LiquidityPlanResult:
    """Complete 13-week calculation result."""
    country: Country
    starting_cash: float
    credit_limit: float
    safety_buffer: float
    ending_cash: float
    min_balance: float
    min_balance_week: int
    max_balance: float
    max_balance_week: int
    total_inflows: float
    total_outflows: float
    net_total_cashflow: float
    starug_status: StaRUGStatus
    starug_notice: str
    weekly_results: List[WeeklyResult] = field(default_factory=list)
    disclaimer: str = ""


@dataclass
class CashConversionCycleInput:
    """Inputs for Cash Conversion Cycle (CCC)."""
    annual_revenue: float
    material_cost: float
    inventory_balance: float
    receivables_balance: float
    payables_balance: float


@dataclass
class CashConversionCycleResult:
    """Results for Cash Conversion Cycle (CCC)."""
    dio_days: float  # Days Inventory Outstanding
    dso_days: float  # Days Sales Outstanding
    dpo_days: float  # Days Payable Outstanding
    ccc_days: float  # Cash Conversion Cycle = DIO + DSO - DPO
    assessment: str
    freed_cash_5d_dso: float  # Cash freigesetzt durch 5 Tage DSO-Senkung
