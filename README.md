# DACH Liquiditätsplaner & Cashflow-Forecaster 2026 (Rollierende 13-Wochen-Planung & StaRUG § 1)

[![CI Tests](https://github.com/DACHDigitalwerk/liquiditaetsplaner-cashflow-rechner-dach/actions/workflows/python-tests.yml/badge.svg)](https://github.com/DACHDigitalwerk/liquiditaetsplaner-cashflow-rechner-dach/actions)
[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/liqui-dach/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![DACH Region](https://img.shields.io/badge/DACH-DE%20%E2%80%A2%20AT%20%E2%80%A2%20CH-emerald.svg)](https://dachdigitalwerk.github.io/)

**Produktionsreife Open-Source Python Engine & CLI** für die betriebswirtschaftliche und insolvenzrechtliche **rollierende 13-Wochen-Liquiditätsplanung** nach dem Standard **IDW S11**, **StaRUG § 1 Krisenfrüherkennung** (Deutschland), **Art. 725a OR** (Schweiz), **URG** (Österreich) sowie zur Berechnung des **Cash Conversion Cycle (CCC = DIO + DSO - DPO)**.

> 🌐 **Interaktive Web-Applikation & DIN-A4 PDF-Export:**  
> Nutzen Sie das kostenlose Browser-Tool ohne Installation oder Registrierung unter:  
> **👉 [https://dachdigitalwerk.github.io/liquiditaetsplaner-cashflow-rechner/](https://dachdigitalwerk.github.io/liquiditaetsplaner-cashflow-rechner/)**

---

## 📚 Fach-Ratgeber & Hintergrundwissen

* 📖 [13-Wochen-Liquiditätsplanung Muster & Vorlage nach IDW S11](https://dachdigitalwerk.github.io/13-wochen-liquiditaetsplanung-muster-vorlage.html)
* 📖 [Cash Conversion Cycle berechnen: Formel für DSO, DPO & DIO im KMU-Leitfaden](https://dachdigitalwerk.github.io/cash-conversion-cycle-berechnen-dso-dpo-dio.html)
* 📖 [StaRUG § 1 Frühwarnsystem: Drohende Zahlungsunfähigkeit & Haftung vermeiden](https://dachdigitalwerk.github.io/starug-fruehwarnsystem-drohende-zahlungsunfaehigkeit-kmu.html)

---

## 🚀 Features & Rechtskonformität

* ✅ **Rollierende 13-Wochen-Matrix:** Wöchentliche Gegenüberstellung von Zahlungsströmen (Debitoren, Löhne, Lieferanten, Steuern, Zins/Tilgung, CapEx).
* ✅ **Kontokorrent- & Kreditlinien-Überwachung:** Exakte Ermittlung der Linienauslastung in Prozent und Erkennung von Deckungslücken.
* ✅ **StaRUG § 1 Krisenfrüherkennung (Deutschland):** Frühzeitige Identifikation drohender Zahlungsunfähigkeit gem. § 18 InsO zur Abwehr persönlicher Geschäftsführerhaftung nach § 15b InsO.
* ✅ **Schweizer Aktienrecht (Art. 725a OR):** Prüfung der Zahlungsfähigkeit zur Erfüllung der gesetzlichen Überwachungspflichten des Verwaltungsrats.
* ✅ **Österreichisches URG:** Früherkennung von Reorganisationsbedarf nach den Kennzahlen der Insolvenzordnung.
* ✅ **Cash Conversion Cycle (Geldumschlagsdauer):**
  * Vorratsreichweite (DIO - Days Inventory Outstanding)
  * Debitorenlaufzeit (DSO - Days Sales Outstanding)
  * Lieferantenziel (DPO - Days Payable Outstanding)
  * Hebelberechnung: Sofortige Freisetzung freier Liquidität durch DSO-Reduktion.
* ✅ **BGH Smartlaw-Konformität:** Rein deterministische Algorithmen ohne unzulässige Rechtsberatung gem. § 2 RDG / § 5 StBerG.

---

## 📦 Installation

```bash
pip install liqui-dach
```

Oder direkt aus dem Repository:

```bash
git clone https://github.com/DACHDigitalwerk/liquiditaetsplaner-cashflow-rechner-dach.git
cd liquiditaetsplaner-cashflow-rechner-dach
pip install -e .
```

---

## 💻 CLI-Nutzung (`dach-liqui`)

### 1. 13-Wochen-Mittelstandsplanung ausführen

```bash
dach-liqui 100000 --credit-limit 50000 --safety-buffer 20000 --demo
```

**Ausgabe:**
```text
==========================================================================
  DACH LIQUIDITÄTSPLANER & CASHFLOW-FORECASTER 2026
  Rollierende 13-Wochen-Planung (IDW S11, StaRUG § 1, Art. 725a OR)
==========================================================================
 Land / Rechtsraum:        DE
 Anfangsbestand (W0):      100.000,00 €
 Kontokorrentlinie:        50.000,00 €
 Mindestliquiditaet:       20.000,00 €
 Summe Einzahlungen (13W): +357.000,00 €
 Summe Auszahlungen (13W): -298.500,00 €
 Netto-Gesamt-Cashflow:    +58.500,00 €
 Endbestand (Woche 13):    158.500,00 €
 Tiefststand:              82.400,00 € (in Woche 8)
 Hoechststand:             158.500,00 € (in Woche 13)
--------------------------------------------------------------------------
 StaRUG / OR Status:       HEALTHY
 Hinweistext:              GRÜN: Ausreichende Liquidität über alle 13 Wochen gesichert.
==========================================================================
```

### 2. Cash Conversion Cycle (Working Capital Analyse)

```bash
dach-liqui --ccc --revenue 2400000 --material 1000000 --inventory 120000 --receivables 200000 --payables 80000
```

**Ausgabe:**
```text
==========================================================================
  CASH CONVERSION CYCLE (WORKING CAPITAL ANALYSE)
==========================================================================
 DIO (Vorratsreichweite):  43.8 Tage
 DSO (Debitorenziel):      30.4 Tage
 DPO (Kreditorenziel):     29.2 Tage
 CCC (Geldumschlagsdauer): 45.0 Tage (DIO + DSO - DPO)
 Einstufung:               Moderat (Typischer Mittelstandswert, 30 bis 60 Tage)
 Liquiditaetspotenzial:    32.876,71 € freies Cash bei 5 Tagen DSO-Senkung!
==========================================================================
```

### 3. JSON-Export für API & ERP-Integration

```bash
dach-liqui 150000 --demo --json
```

---

## 🐍 Python API

```python
from liqui_dach import (
    LiquidityPlanInput,
    WeeklyCashflow,
    CashConversionCycleInput,
    calculate_13_week_plan,
    calculate_cash_conversion_cycle,
)

# 1. 13-Wochen-Plan berechnen
plan = calculate_13_week_plan(LiquidityPlanInput(starting_cash=100000.0, credit_limit=50000.0))
print(f"Endbestand: {plan.ending_cash:,.2f} €")
print(f"StaRUG Status: {plan.starug_status.value}")

# 2. Cash Conversion Cycle berechnen
ccc = calculate_cash_conversion_cycle(CashConversionCycleInput(
    annual_revenue=1200000.0,
    material_cost=600000.0,
    inventory_balance=100000.0,
    receivables_balance=150000.0,
    payables_balance=50000.0,
))
print(f"CCC: {ccc.ccc_days:.1f} Tage")
```

---

## 🧪 Unit Tests

Das Projekt verfügt über 29 automatisierte Unit Tests:

```bash
pytest tests/ -v
```

---

## ⚖️ Rechtlicher Hinweis & Haftungsausschluss

Dieses Software-Paket stellt eine **rein technische Modellberechnung und unverbindliche kaufmännische Hilfskalkulation** dar. Es ersetzt ausdrücklich **keine Rechts-, Steuer- oder Sanierungsberatung** im Sinne des Rechtsdienstleistungsgesetzes (§ 2 RDG) oder Steuerberatungsgesetzes (§ 5 StBerG). 

Gemäß der Grundsatzentscheidung des Bundesgerichtshofs (BGH, Urteil vom 09.09.2021 – I ZR 226/20, „Smartlaw“) ist die Bereitstellung algorithmenbasierter Generatoren und Berechnungstools zulässig. Für insolvenzrechtliche Gutachten konsultieren Sie bitte einen zugelassenen Fachanwalt für Insolvenzrecht oder Wirtschaftsprüfer.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert – siehe die [LICENSE](LICENSE) Datei für Details.
Publiziert durch **[DACH Digitalwerk](https://dachdigitalwerk.github.io/)**.
