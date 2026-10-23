# -*- coding: utf-8 -*-
"""
Quickstart Example for liqui_dach
"""

from liqui_dach import (
    LiquidityPlanInput,
    WeeklyCashflow,
    CashConversionCycleInput,
    calculate_13_week_plan,
    calculate_cash_conversion_cycle,
    Country,
)


def main():
    print("=== Beispiel 1: Rollierende 13-Wochen-Liquiditätsplanung ===")
    weeks = [
        WeeklyCashflow(
            week_number=i,
            customer_receipts=25000.0,
            material_costs=10000.0,
            personnel_costs=30000.0 if i in (4, 8, 12) else 0.0,
            tax_payments=7500.0 if i in (2, 6, 10) else 0.0,
            rent_leasing=5000.0 if i in (1, 5, 9) else 0.0,
        )
        for i in range(1, 14)
    ]
    inp = LiquidityPlanInput(
        starting_cash=100000.0,
        credit_limit=50000.0,
        safety_buffer=20000.0,
        country=Country.DE,
        weeks=weeks,
    )
    res = calculate_13_week_plan(inp)
    print(f"Anfangsbestand:     {res.starting_cash:,.2f} €")
    print(f"Gesamteinzahlungen: {res.total_inflows:,.2f} €")
    print(f"Gesamtauszahlungen: {res.total_outflows:,.2f} €")
    print(f"Endbestand W13:     {res.ending_cash:,.2f} €")
    print(f"Tiefststand:        {res.min_balance:,.2f} € in Woche {res.min_balance_week}")
    print(f"StaRUG Status:      {res.starug_status.value.upper()} ({res.starug_notice})\n")

    print("=== Beispiel 2: Cash Conversion Cycle (Working Capital Analyse) ===")
    ccc_inp = CashConversionCycleInput(
        annual_revenue=2400000.0,
        material_cost=1000000.0,
        inventory_balance=120000.0,
        receivables_balance=200000.0,
        payables_balance=80000.0,
    )
    ccc_res = calculate_cash_conversion_cycle(ccc_inp)
    print(f"DIO (Vorratsreichweite):  {ccc_res.dio_days:.1f} Tage")
    print(f"DSO (Debitorenziel):      {ccc_res.dso_days:.1f} Tage")
    print(f"DPO (Kreditorenziel):     {ccc_res.dpo_days:.1f} Tage")
    print(f"CCC (Geldumschlagsdauer): {ccc_res.ccc_days:.1f} Tage")
    print(f"Einstufung:               {ccc_res.assessment}")
    print(f"Liquiditätshebel:         {ccc_res.freed_cash_5d_dso:,.2f} € freies Cash bei 5 Tagen DSO-Senkung!")


if __name__ == "__main__":
    main()
