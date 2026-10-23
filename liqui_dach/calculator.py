# -*- coding: utf-8 -*-
"""
Core Calculation Logic for 13-Week Liquidity Planning & Cash Conversion Cycle
"""

from typing import Tuple, List
from .models import (
    Country,
    LiquidityPlanInput,
    LiquidityPlanResult,
    WeeklyCashflow,
    WeeklyResult,
    CashConversionCycleInput,
    CashConversionCycleResult,
    StaRUGStatus,
)
from .validator import validate_plan_input, validate_ccc_input


def assess_starug_risk(
    min_balance: float,
    credit_limit: float,
    safety_buffer: float,
    country: Country,
) -> Tuple[StaRUGStatus, str]:
    """
    Evaluates liquidity risk according to § 1 StaRUG (DE), Art. 725a OR (CH), or URG (AT).
    """
    max_borrowing_capacity = -credit_limit

    if min_balance < max_borrowing_capacity:
        shortfall = abs(min_balance - max_borrowing_capacity)
        if country == Country.DE:
            notice = (
                f"KRITISCH (§ 1 StaRUG / § 17 InsO): Deckungslücke von {shortfall:,.2f} € übersteigt die vereinbarte Kreditlinie. "
                "Es droht akute Zahlungsunfähigkeit nach BGH-Rechtsprechung. 3-Wochen-Prüffrist nach § 15a InsO beachten!"
            )
        elif country == Country.CH:
            notice = (
                f"KRITISCH (Art. 725a OR): Drohende Zahlungsunfähigkeit mit Unterdeckung von {shortfall:,.2f} CHF. "
                "Der Verwaltungsrat muss unverzüglich Sanierungsmaßnahmen einleiten."
            )
        else:
            notice = (
                f"KRITISCH (URG Österreich): Liquiditätsunterdeckung von {shortfall:,.2f} €. "
                "Reorganisationsbedarf und Insolvenztatbestand gem. IO prüfen."
            )
        return StaRUGStatus.CRITICAL, notice

    elif min_balance < safetyBuffer if (safetyBuffer := safety_buffer) else False:
        if country == Country.DE:
            notice = "WARNUNG: Mindestliquidität / Sicherheitspuffer wird im Planungszeitraum unterschritten. Kontokorrentlinie wird beansprucht."
        elif country == Country.CH:
            notice = "WARNUNG: Liquiditätsreserve wird temporär beansprucht. Kreditlimite deckt den Bedarf ab."
        else:
            notice = "WARNUNG: Temporäre Inanspruchnahme der Betriebsmittelkredite unterhalb des Soll-Puffers."
        return StaRUGStatus.BUFFER_USED, notice

    else:
        if country == Country.DE:
            notice = "GRÜN: Ausreichende Liquidität über alle 13 Wochen gesichert. StaRUG § 1 Anforderungen erfüllt."
        elif country == Country.CH:
            notice = "GRÜN: Zahlungsfähigkeit nach Art. 725a OR jederzeit gewährleistet."
        else:
            notice = "GRÜN: Positive Liquiditätsausstattung. Kein URG-Reorganisationsbedarf erkennbar."
        return StaRUGStatus.HEALTHY, notice


def calculate_13_week_plan(inp: LiquidityPlanInput) -> LiquidityPlanResult:
    """Computes rolling 13-week forecast with weekly inflows, outflows, and ending balances."""
    validate_plan_input(inp)

    # Wenn weniger als 13 Wochen übergeben wurden, fülle bis Woche 13 mit Nullen auf
    weeks_map = {w.week_number: w for w in inp.weeks}
    complete_weeks: List[WeeklyCashflow] = []
    for i in range(1, 14):
        if i in weeks_map:
            complete_weeks.append(weeks_map[i])
        else:
            complete_weeks.append(WeeklyCashflow(week_number=i))

    current_balance = inp.starting_cash
    weekly_results: List[WeeklyResult] = []

    min_bal = float("inf")
    min_bal_week = 1
    max_bal = float("-inf")
    max_bal_week = 1

    total_in = 0.0
    total_out = 0.0

    for w in complete_weeks:
        w_in = round(w.customer_receipts + w.other_inflows, 2)
        w_out = round(
            w.material_costs
            + w.personnel_costs
            + w.rent_leasing
            + w.tax_payments
            + w.debt_service
            + w.other_outflows,
            2,
        )
        net_cf = round(w_in - w_out, 2)
        start_bal = current_balance
        end_bal = round(start_bal + net_cf, 2)

        total_in = round(total_in + w_in, 2)
        total_out = round(total_out + w_out, 2)

        # Utilization of credit line
        utilization_pct = 0.0
        shortfall = 0.0
        is_critical = False

        if end_bal < 0:
            if inp.credit_limit > 0:
                utilization_pct = round(min(100.0, (abs(end_bal) / inp.credit_limit) * 100.0), 2)
            if end_bal < -inp.credit_limit:
                shortfall = round(abs(end_bal + inp.credit_limit), 2)
                is_critical = True

        if end_bal < min_bal:
            min_bal = end_bal
            min_bal_week = w.week_number

        if end_bal > max_bal:
            max_bal = end_bal
            max_bal_week = w.week_number

        weekly_results.append(
            WeeklyResult(
                week_number=w.week_number,
                starting_balance=start_bal,
                total_inflows=w_in,
                total_outflows=w_out,
                net_cashflow=net_cf,
                ending_balance=end_bal,
                credit_line_utilization_pct=utilization_pct,
                shortfall=shortfall,
                is_critical=is_critical,
            )
        )

        current_balance = end_bal

    starug_status, starug_notice = assess_starug_risk(
        min_bal, inp.credit_limit, inp.safety_buffer, inp.country
    )

    disclaimer = (
        "Rechtlicher Hinweis: Rein technisches B2B-Kalkulationswerkzeug gem. § 2 RDG / § 5 StBerG. "
        "Keine Rechts-, Sanierungs- oder Steuerberatung. Gemäß BGH-Urteil (Az. I ZR 226/20 - Smartlaw) ist die "
        "algorithmenbasierte Modellberechnung zulässig. Für insolvenzrechtliche Gutachten konsultieren Sie einen Fachanwalt für Insolvenzrecht oder Wirtschaftsprüfer."
    )

    return LiquidityPlanResult(
        country=inp.country,
        starting_cash=inp.starting_cash,
        credit_limit=inp.credit_limit,
        safety_buffer=inp.safety_buffer,
        ending_cash=current_balance,
        min_balance=min_bal,
        min_balance_week=min_bal_week,
        max_balance=max_bal,
        max_balance_week=max_bal_week,
        total_inflows=total_in,
        total_outflows=total_out,
        net_total_cashflow=round(total_in - total_out, 2),
        starug_status=starug_status,
        starug_notice=starug_notice,
        weekly_results=weekly_results,
        disclaimer=disclaimer,
    )


def calculate_cash_conversion_cycle(inp: CashConversionCycleInput) -> CashConversionCycleResult:
    """Calculates Days Inventory, Days Sales, Days Payable, and Cash Conversion Cycle."""
    validate_ccc_input(inp)

    dio = round((inp.inventory_balance / inp.material_cost) * 365.0, 1)
    dso = round((inp.receivables_balance / inp.annual_revenue) * 365.0, 1)
    dpo = round((inp.payables_balance / inp.material_cost) * 365.0, 1)
    ccc = round(dio + dso - dpo, 1)

    if ccc < 30.0:
        assessment = "Exzellent (Geringe Working-Capital-Bindung, < 30 Tage)"
    elif ccc <= 60.0:
        assessment = "Moderat (Typischer Mittelstandswert, 30 bis 60 Tage)"
    else:
        assessment = "Kritisch (Hohe Kapitalbindung, > 60 Tage)"

    daily_rev = inp.annual_revenue / 365.0
    freed_cash_5d = round(daily_rev * 5.0, 2)

    return CashConversionCycleResult(
        dio_days=dio,
        dso_days=dso,
        dpo_days=dpo,
        ccc_days=ccc,
        assessment=assessment,
        freed_cash_5d_dso=freed_cash_5d,
    )
