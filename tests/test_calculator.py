# -*- coding: utf-8 -*-
import pytest
from liqui_dach.models import (
    Country,
    LiquidityPlanInput,
    WeeklyCashflow,
    StaRUGStatus,
    CashConversionCycleInput,
)
from liqui_dach.calculator import (
    calculate_13_week_plan,
    calculate_cash_conversion_cycle,
    assess_starug_risk,
)
from liqui_dach.validator import ValidationError, validate_plan_input, validate_ccc_input


def test_basic_13_week_plan():
    weeks = [
        WeeklyCashflow(week_number=i, customer_receipts=10000.0, material_costs=8000.0)
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
    assert res.starting_cash == 100000.0
    assert res.total_inflows == 130000.0
    assert res.total_outflows == 104000.0
    assert res.net_total_cashflow == 26000.0
    assert res.ending_cash == 126000.0
    assert res.min_balance == 102000.0
    assert res.max_balance == 126000.0
    assert res.starug_status == StaRUGStatus.HEALTHY
    assert len(res.weekly_results) == 13


def test_detailed_cashflow_categories():
    w1 = WeeklyCashflow(
        week_number=1,
        customer_receipts=30000.0,
        other_inflows=2000.0,
        material_costs=10000.0,
        personnel_costs=12000.0,
        rent_leasing=3000.0,
        tax_payments=2000.0,
        debt_service=1000.0,
        other_outflows=500.0,
    )
    inp = LiquidityPlanInput(starting_cash=50000.0, weeks=[w1])
    res = calculate_13_week_plan(inp)
    res_w1 = res.weekly_results[0]
    assert res_w1.total_inflows == 32000.0
    assert res_w1.total_outflows == 28500.0
    assert res_w1.net_cashflow == 3500.0
    assert res_w1.ending_balance == 53500.0


def test_padding_incomplete_weeks():
    weeks = [WeeklyCashflow(week_number=1, customer_receipts=5000.0, material_costs=3000.0)]
    inp = LiquidityPlanInput(starting_cash=50000.0, weeks=weeks)
    res = calculate_13_week_plan(inp)
    assert len(res.weekly_results) == 13
    assert res.weekly_results[0].net_cashflow == 2000.0
    assert res.weekly_results[1].net_cashflow == 0.0
    assert res.ending_cash == 52000.0


def test_buffer_used_status():
    weeks = [WeeklyCashflow(week_number=1, material_costs=85000.0)]
    inp = LiquidityPlanInput(
        starting_cash=100000.0,
        credit_limit=50000.0,
        safety_buffer=20000.0,
        weeks=weeks,
    )
    res = calculate_13_week_plan(inp)
    assert res.min_balance == 15000.0
    assert res.starug_status == StaRUGStatus.BUFFER_USED
    assert "WARNUNG" in res.starug_notice


def test_credit_line_utilization():
    weeks = [WeeklyCashflow(week_number=1, material_costs=130000.0)]
    inp = LiquidityPlanInput(
        starting_cash=100000.0,
        credit_limit=50000.0,
        safety_buffer=20000.0,
        weeks=weeks,
    )
    res = calculate_13_week_plan(inp)
    w1 = res.weekly_results[0]
    assert w1.ending_balance == -30000.0
    assert w1.credit_line_utilization_pct == 60.0
    assert w1.shortfall == 0.0
    assert w1.is_critical is False
    assert res.starug_status == StaRUGStatus.BUFFER_USED


def test_critical_insolvency_shortfall():
    weeks = [WeeklyCashflow(week_number=1, material_costs=170000.0)]
    inp = LiquidityPlanInput(
        starting_cash=100000.0,
        credit_limit=50000.0,
        safety_buffer=20000.0,
        country=Country.DE,
        weeks=weeks,
    )
    res = calculate_13_week_plan(inp)
    w1 = res.weekly_results[0]
    assert w1.ending_balance == -70000.0
    assert w1.shortfall == 20000.0
    assert w1.is_critical is True
    assert res.starug_status == StaRUGStatus.CRITICAL
    assert "KRITISCH" in res.starug_notice
    assert "StaRUG" in res.starug_notice


def test_country_ch_notice():
    status, notice = assess_starug_risk(-60000.0, 50000.0, 10000.0, Country.CH)
    assert status == StaRUGStatus.CRITICAL
    assert "Art. 725a OR" in notice


def test_country_at_notice():
    status, notice = assess_starug_risk(-60000.0, 50000.0, 10000.0, Country.AT)
    assert status == StaRUGStatus.CRITICAL
    assert "URG" in notice


def test_country_healthy_statuses():
    st_de, msg_de = assess_starug_risk(50000.0, 10000.0, 20000.0, Country.DE)
    assert st_de == StaRUGStatus.HEALTHY
    assert "GRÜN" in msg_de

    st_ch, msg_ch = assess_starug_risk(50000.0, 10000.0, 20000.0, Country.CH)
    assert st_ch == StaRUGStatus.HEALTHY
    assert "Art. 725a OR" in msg_ch

    st_at, msg_at = assess_starug_risk(50000.0, 10000.0, 20000.0, Country.AT)
    assert st_at == StaRUGStatus.HEALTHY
    assert "URG" in msg_at


def test_cash_conversion_cycle_calculation():
    ccc_inp = CashConversionCycleInput(
        annual_revenue=1200000.0,
        material_cost=600000.0,
        inventory_balance=100000.0,
        receivables_balance=150000.0,
        payables_balance=50000.0,
    )
    res = calculate_cash_conversion_cycle(ccc_inp)
    assert res.dio_days == 60.8
    assert res.dso_days == 45.6
    assert res.dpo_days == 30.4
    assert res.ccc_days == 76.0
    assert "Kritisch" in res.assessment


def test_ccc_excellent_case():
    ccc_inp = CashConversionCycleInput(
        annual_revenue=2000000.0,
        material_cost=1000000.0,
        inventory_balance=41095.89,
        receivables_balance=27397.26,
        payables_balance=82191.78,
    )
    res = calculate_cash_conversion_cycle(ccc_inp)
    assert res.ccc_days < 30.0
    assert "Exzellent" in res.assessment


def test_freed_cash_calculation():
    ccc_inp = CashConversionCycleInput(
        annual_revenue=2400000.0,
        material_cost=1000000.0,
        inventory_balance=100000.0,
        receivables_balance=100000.0,
        payables_balance=100000.0,
    )
    res = calculate_cash_conversion_cycle(ccc_inp)
    assert res.freed_cash_5d_dso == 32876.71


def test_validation_negative_credit_limit():
    inp = LiquidityPlanInput(starting_cash=50000.0, credit_limit=-1000.0)
    with pytest.raises(ValidationError):
        calculate_13_week_plan(inp)


def test_validation_negative_safety_buffer():
    inp = LiquidityPlanInput(starting_cash=50000.0, safety_buffer=-500.0)
    with pytest.raises(ValidationError):
        calculate_13_week_plan(inp)


def test_validation_invalid_week_number():
    weeks = [WeeklyCashflow(week_number=0)]
    inp = LiquidityPlanInput(starting_cash=50000.0, weeks=weeks)
    with pytest.raises(ValidationError):
        calculate_13_week_plan(inp)


def test_validation_negative_cashflow_entries():
    weeks = [WeeklyCashflow(week_number=1, customer_receipts=-200.0)]
    inp = LiquidityPlanInput(starting_cash=50000.0, weeks=weeks)
    with pytest.raises(ValidationError):
        calculate_13_week_plan(inp)


def test_validation_starting_cash_undercover_warning():
    inp = LiquidityPlanInput(starting_cash=-60000.0, credit_limit=50000.0)
    warnings = validate_plan_input(inp)
    assert any("Anfangsbestand" in w for w in warnings)


def test_validation_ccc_zero_revenue():
    ccc_inp = CashConversionCycleInput(
        annual_revenue=0.0,
        material_cost=100000.0,
        inventory_balance=10000.0,
        receivables_balance=10000.0,
        payables_balance=10000.0,
    )
    with pytest.raises(ValidationError):
        calculate_cash_conversion_cycle(ccc_inp)


def test_validation_ccc_negative_inventory():
    ccc_inp = CashConversionCycleInput(
        annual_revenue=1000000.0,
        material_cost=500000.0,
        inventory_balance=-5000.0,
        receivables_balance=10000.0,
        payables_balance=10000.0,
    )
    with pytest.raises(ValidationError):
        calculate_cash_conversion_cycle(ccc_inp)
