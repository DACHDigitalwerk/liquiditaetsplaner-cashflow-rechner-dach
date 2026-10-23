# -*- coding: utf-8 -*-
"""
Validation rules and constraints for Liquidity Planning and CCC
"""

from typing import List
from .models import LiquidityPlanInput, CashConversionCycleInput


class ValidationError(ValueError):
    """Raised when liquidity or CCC inputs fail validation."""
    pass


def validate_plan_input(inp: LiquidityPlanInput) -> List[str]:
    """Validates 13-week plan inputs and returns notices."""
    warnings: List[str] = []

    if inp.credit_limit < 0:
        raise ValidationError(f"Kreditlinie muss >= 0 sein, erhalten: {inp.credit_limit}")

    if inp.safety_buffer < 0:
        raise ValidationError(f"Sicherheitspuffer muss >= 0 sein, erhalten: {inp.safety_buffer}")

    if inp.starting_cash < -inp.credit_limit:
        warnings.append("Achtung: Der Anfangsbestand übersteigt bereits zu Beginn die verfügbare Kreditlinie (Unterdeckung!).")

    for w in inp.weeks:
        if w.week_number < 1 or w.week_number > 52:
            raise ValidationError(f"Wochennummer muss zwischen 1 und 52 liegen, erhalten: {w.week_number}")
        if w.customer_receipts < 0 or w.other_inflows < 0:
            raise ValidationError(f"Einzahlungen müssen >= 0 sein in Woche {w.week_number}")
        if (
            w.material_costs < 0
            or w.personnel_costs < 0
            or w.rent_leasing < 0
            or w.tax_payments < 0
            or w.debt_service < 0
            or w.other_outflows < 0
        ):
            raise ValidationError(f"Auszahlungen müssen >= 0 sein in Woche {w.week_number}")

    return warnings


def validate_ccc_input(inp: CashConversionCycleInput) -> List[str]:
    """Validates inputs for Cash Conversion Cycle."""
    warnings: List[str] = []

    if inp.annual_revenue <= 0:
        raise ValidationError(f"Jahresumsatz muss > 0 sein, erhalten: {inp.annual_revenue}")

    if inp.material_cost <= 0:
        raise ValidationError(f"Materialaufwand muss > 0 sein, erhalten: {inp.material_cost}")

    if inp.inventory_balance < 0:
        raise ValidationError(f"Lagerbestand muss >= 0 sein, erhalten: {inp.inventory_balance}")

    if inp.receivables_balance < 0:
        raise ValidationError(f"Forderungsbestand muss >= 0 sein, erhalten: {inp.receivables_balance}")

    if inp.payables_balance < 0:
        raise ValidationError(f"Verbindlichkeiten müssen >= 0 sein, erhalten: {inp.payables_balance}")

    return warnings
