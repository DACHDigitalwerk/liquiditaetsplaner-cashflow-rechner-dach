# -*- coding: utf-8 -*-
"""
Command-Line Interface for DACH 13-Week Liquidity Planner (dach-liqui)
"""

import argparse
import json
import sys
from typing import Any, Dict, List

from .models import (
    Country,
    LiquidityPlanInput,
    WeeklyCashflow,
    CashConversionCycleInput,
)
from .calculator import calculate_13_week_plan, calculate_cash_conversion_cycle


def format_currency(val: float) -> str:
    return f"{val:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="dach-liqui",
        description="DACH Liquiditätsplaner & Cashflow-Forecaster 2026 (Rollierende 13-Wochen-Planung & StaRUG § 1)",
        epilog="Entwickelt von DACH Digitalwerk • https://dachdigitalwerk.github.io/liquiditaetsplaner-cashflow-rechner/",
    )

    parser.add_argument(
        "start_cash",
        type=float,
        nargs="?",
        default=None,
        help="Anfangsbestand an liquiden Mitteln in Euro (Girokonten + Kasse)",
    )
    parser.add_argument(
        "-s", "--start",
        dest="start_alt",
        type=float,
        default=None,
        help="Alternativer Parameter fuer Anfangsbestand in Euro",
    )
    parser.add_argument(
        "-l", "--credit-limit",
        type=float,
        default=50000.0,
        help="Vereinbarte Kontokorrentlinie / Betriebsmittelkreditlinie in Euro (Standard: 50.000)",
    )
    parser.add_argument(
        "-b", "--safety-buffer",
        type=float,
        default=20000.0,
        help="Mindestliquiditaet / Sicherheitspuffer in Euro (Standard: 20.000)",
    )
    parser.add_argument(
        "-c", "--country",
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Rechtsraum: DE (Deutschland StaRUG Paragraph 1), AT (Oesterreich URG), CH (Schweiz Art. 725a OR)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Laedt einen realistischen 13-Wochen-Mittelstandsfall mit Gehältern, USt und Lieferanten",
    )
    parser.add_argument(
        "--ccc",
        action="store_true",
        help="Berechnet zusaetzlich den Cash Conversion Cycle (Geldumschlagsdauer)",
    )
    parser.add_argument(
        "--revenue",
        type=float,
        default=1200000.0,
        help="Jahresumsatz fuer CCC-Berechnung in Euro",
    )
    parser.add_argument(
        "--material",
        type=float,
        default=500000.0,
        help="Materialaufwand fuer CCC-Berechnung in Euro",
    )
    parser.add_argument(
        "--inventory",
        type=float,
        default=80000.0,
        help="Durchschnittlicher Lagerbestand fuer CCC-Berechnung in Euro",
    )
    parser.add_argument(
        "--receivables",
        type=float,
        default=115000.0,
        help="Forderungen aus L+L (Debitoren) fuer CCC-Berechnung in Euro",
    )
    parser.add_argument(
        "--payables",
        type=float,
        default=65000.0,
        help="Verbindlichkeiten aus L+L (Kreditoren) fuer CCC-Berechnung in Euro",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe als maschinenlesbares JSON-Format",
    )

    return parser.parse_args(args)


def create_sample_weeks() -> List[WeeklyCashflow]:
    weeks: List[WeeklyCashflow] = []
    for i in range(1, 14):
        # Basis-Umsätze & Kosten
        w_rev = 24000.0 + (i % 3) * 4000.0
        w_other_in = 3000.0 if i in (4, 8, 12) else 0.0
        w_mat = 9500.0
        w_sal = 32000.0 if i in (4, 8, 12) else 0.0  # Monatsende Gehälter
        w_rent = 5500.0 if i in (1, 5, 9) else 0.0    # Monatsanfang Miete
        w_tax = 7200.0 if i in (2, 6, 10) else 0.0    # USt am 10.
        w_debt = 2200.0 if i in (1, 5, 9, 13) else 0.0
        w_other_out = 1200.0

        weeks.append(
            WeeklyCashflow(
                week_number=i,
                customer_receipts=w_rev,
                other_inflows=w_other_in,
                material_costs=w_mat,
                personnel_costs=w_sal,
                rent_leasing=w_rent,
                tax_payments=w_tax,
                debt_service=w_debt,
                other_outflows=w_other_out,
            )
        )
    return weeks


def main(args=None):
    parsed = parse_args(args)

    amt = parsed.start_cash if parsed.start_cash is not None else parsed.start_alt
    if amt is None:
        if parsed.ccc:
            amt = 0.0  # Bei reinem CCC-Aufruf
        else:
            amt = 100000.0  # Standard-Anfangsbestand bei Demo

    c_map = {"DE": Country.DE, "AT": Country.AT, "CH": Country.CH}
    country = c_map.get(parsed.country, Country.DE)

    weeks = create_sample_weeks() if (parsed.demo or not parsed.ccc) else []

    plan_input = LiquidityPlanInput(
        starting_cash=amt,
        credit_limit=parsed.credit_limit,
        safety_buffer=parsed.safety_buffer,
        country=country,
        weeks=weeks,
    )

    plan_result = calculate_13_week_plan(plan_input)

    ccc_result = None
    if parsed.ccc:
        ccc_inp = CashConversionCycleInput(
            annual_revenue=parsed.revenue,
            material_cost=parsed.material,
            inventory_balance=parsed.inventory,
            receivables_balance=parsed.receivables,
            payables_balance=parsed.payables,
        )
        ccc_result = calculate_cash_conversion_cycle(ccc_inp)

    if parsed.json:
        data: Dict[str, Any] = {
            "country": plan_result.country.value,
            "starting_cash": plan_result.starting_cash,
            "credit_limit": plan_result.credit_limit,
            "safety_buffer": plan_result.safety_buffer,
            "ending_cash": plan_result.ending_cash,
            "min_balance": plan_result.min_balance,
            "min_balance_week": plan_result.min_balance_week,
            "max_balance": plan_result.max_balance,
            "max_balance_week": plan_result.max_balance_week,
            "total_inflows": plan_result.total_inflows,
            "total_outflows": plan_result.total_outflows,
            "net_total_cashflow": plan_result.net_total_cashflow,
            "starug_status": plan_result.starug_status.value,
            "starug_notice": plan_result.starug_notice,
            "weekly_results": [
                {
                    "week": w.week_number,
                    "start": w.starting_balance,
                    "inflows": w.total_inflows,
                    "outflows": w.total_outflows,
                    "net_cashflow": w.net_cashflow,
                    "end": w.ending_balance,
                    "credit_line_util_pct": w.credit_line_utilization_pct,
                    "shortfall": w.shortfall,
                    "is_critical": w.is_critical,
                }
                for w in plan_result.weekly_results
            ],
            "disclaimer": plan_result.disclaimer,
        }
        if ccc_result:
            data["cash_conversion_cycle"] = {
                "dio_days": ccc_result.dio_days,
                "dso_days": ccc_result.dso_days,
                "dpo_days": ccc_result.dpo_days,
                "ccc_days": ccc_result.ccc_days,
                "assessment": ccc_result.assessment,
                "freed_cash_5d_dso": ccc_result.freed_cash_5d_dso,
            }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Text UI Output
    print("\n" + "=" * 74)
    print("  DACH LIQUIDITÄTSPLANER & CASHFLOW-FORECASTER 2026")
    print("  Rollierende 13-Wochen-Planung (IDW S11, StaRUG § 1, Art. 725a OR)")
    print("=" * 74)
    print(f" Land / Rechtsraum:        {plan_result.country.value}")
    print(f" Anfangsbestand (W0):      {format_currency(plan_result.starting_cash)}")
    print(f" Kontokorrentlinie:        {format_currency(plan_result.credit_limit)}")
    print(f" Mindestliquiditaet:       {format_currency(plan_result.safety_buffer)}")
    print(f" Summe Einzahlungen (13W): +{format_currency(plan_result.total_inflows)}")
    print(f" Summe Auszahlungen (13W): -{format_currency(plan_result.total_outflows)}")
    print(f" Netto-Gesamt-Cashflow:    {format_currency(plan_result.net_total_cashflow)}")
    print(f" Endbestand (Woche 13):    {format_currency(plan_result.ending_cash)}")
    print(f" Tiefststand:              {format_currency(plan_result.min_balance)} (in Woche {plan_result.min_balance_week})")
    print(f" Hoechststand:             {format_currency(plan_result.max_balance)} (in Woche {plan_result.max_balance_week})")
    print("-" * 74)
    print(f" StaRUG / OR Status:       {plan_result.starug_status.value.upper()}")
    print(f" Hinweistext:              {plan_result.starug_notice}")
    print("=" * 74)

    print("\n[WÖCHENTLICHE LIQUIDITÄTSÜBERSICHT]")
    print(f" {'Wo':<3} | {'Anfang':>12} | {'Ein (+)':>10} | {'Aus (-)':>10} | {'Netto':>10} | {'Endbestand':>12} | {'Status':<8}")
    print("-" * 74)
    for w in plan_result.weekly_results:
        st = "LÜCKE!" if w.is_critical else (f"{w.credit_line_util_pct:.0f}% Kred" if w.ending_balance < 0 else "OK")
        print(
            f" W{w.week_number:<2} | {format_currency(w.starting_balance):>12} | {format_currency(w.total_inflows):>10} | "
            f"{format_currency(w.total_outflows):>10} | {format_currency(w.net_cashflow):>10} | {format_currency(w.ending_balance):>12} | {st:<8}"
        )
    print("-" * 74)

    if ccc_result:
        print("\n" + "=" * 74)
        print("  CASH CONVERSION CYCLE (WORKING CAPITAL ANALYSE)")
        print("=" * 74)
        print(f" DIO (Vorratsreichweite):  {ccc_result.dio_days:.1f} Tage")
        print(f" DSO (Debitorenziel):      {ccc_result.dso_days:.1f} Tage")
        print(f" DPO (Kreditorenziel):     {ccc_result.dpo_days:.1f} Tage")
        print(f" CCC (Geldumschlagsdauer): {ccc_result.ccc_days:.1f} Tage (DIO + DSO - DPO)")
        print(f" Einstufung:               {ccc_result.assessment}")
        print(f" Liquiditaetspotenzial:    {format_currency(ccc_result.freed_cash_5d_dso)} freies Cash bei 5 Tagen DSO-Senkung!")
        print("=" * 74)

    print("\n" + plan_result.disclaimer + "\n")


if __name__ == "__main__":
    main()
