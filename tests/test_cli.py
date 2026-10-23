# -*- coding: utf-8 -*-
import json
import pytest
from liqui_dach.cli import main, parse_args


def test_parse_args_defaults():
    args = parse_args(["100000"])
    assert args.start_cash == 100000.0
    assert args.credit_limit == 50000.0
    assert args.safety_buffer == 20000.0
    assert args.country == "DE"
    assert args.demo is False
    assert args.ccc is False
    assert args.json is False


def test_cli_stdout_default_run(capsys):
    main(["150000"])
    captured = capsys.readouterr()
    assert "DACH LIQUIDITÄTSPLANER & CASHFLOW-FORECASTER 2026" in captured.out
    assert "Anfangsbestand (W0):      150.000,00 €" in captured.out
    assert "W13" in captured.out


def test_cli_stdout_demo_flag(capsys):
    main(["--demo", "-l", "80000"])
    captured = capsys.readouterr()
    assert "Kontokorrentlinie:        80.000,00 €" in captured.out
    assert "WÖCHENTLICHE LIQUIDITÄTSÜBERSICHT" in captured.out


def test_cli_json_output(capsys):
    main(["100000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "DE"
    assert data["starting_cash"] == 100000.0
    assert data["credit_limit"] == 50000.0
    assert len(data["weekly_results"]) == 13


def test_cli_ccc_stdout(capsys):
    main(["--ccc", "--revenue", "2000000", "--material", "800000"])
    captured = capsys.readouterr()
    assert "CASH CONVERSION CYCLE" in captured.out
    assert "DIO (Vorratsreichweite):" in captured.out
    assert "CCC (Geldumschlagsdauer):" in captured.out


def test_cli_ccc_json(capsys):
    main(["--ccc", "--revenue", "2000000", "--material", "800000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "cash_conversion_cycle" in data
    assert "ccc_days" in data["cash_conversion_cycle"]
    assert "freed_cash_5d_dso" in data["cash_conversion_cycle"]


def test_cli_country_ch(capsys):
    main(["50000", "-c", "CH", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "CH"
    assert "Art. 725a OR" in data["starug_notice"]


def test_cli_country_at(capsys):
    main(["50000", "-c", "AT", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["country"] == "AT"
    assert "URG" in data["starug_notice"]


def test_cli_custom_credit_and_buffer(capsys):
    main(["200000", "-l", "120000", "-b", "40000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["credit_limit"] == 120000.0
    assert data["safety_buffer"] == 40000.0


def test_cli_alt_start_param(capsys):
    main(["-s", "85000", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["starting_cash"] == 85000.0
