# Harbor – Masterplan

Status: aktiv  
Letzte Aktualisierung: 2026-04-06  
Aktueller Programmstand: **A0 akzeptiert**

## 1. Zielbild

Harbor ist ein projektpartitioniertes Research Operating System mit:

- sauber getrennten Projekten
- versionierten Research Handbooks
- kontrollierter Quellen- und Evidenzverwaltung
- Review- und Resume-Fähigkeit
- gemeinsamem Backend für Website und Custom GPT
- späterem Refresh-, Discovery-, Monitoring- und Agentenhorizont

## 2. Phasenübersicht

### A0 – Produkt-, Modell- und Architekturdefinition
Ziel:
- Scope, Modell, Workflows, Architektur und technische Startlinie definieren

Status:
- **abgeschlossen und akzeptiert**

### T1 – Technical Bootstrap and Foundation
Ziel:
- Repo-Scaffold
- Python-Grundstruktur
- minimale App
- Konfiguration
- Health
- erste Tests/Gates

Status:
- **nächste Phase**

### T2 – First Vertical Slice
Ziel:
- erstes durchgehendes Harbor-Produktinkrement
- wahrscheinlich: Projects + Handbook als erster Fachslice

Status:
- noch nicht gestartet

### T3 – Source and Evidence Slice
Ziel:
- Source
- ProjectSource
- Snapshot
- manuelle Evidenzaufnahme
- erste projektbezogene Review-Zustände

Status:
- noch nicht gestartet

### T4 – Search / Refresh Slice
Ziel:
- Search Campaign
- Refresh Run
- Kandidaten
- erste Delta-/Freshness-Logik

Status:
- noch nicht gestartet

### T5 – Web / GPT Operational Surface
Ziel:
- Web UI auf stabilem Backend
- GPT-Actions gegen dasselbe Backend

Status:
- noch nicht gestartet

### T6 – VPS / Operational Hosting
Ziel:
- stabiler VPS-Betrieb
- Health, Logging, Runbooks, Deploy-Pfade

Status:
- noch nicht gestartet

### T7 – Monitoring / Agentic Expansion
Ziel:
- geplante Refresh-Zyklen
- Discovery-Kampagnen
- agentische Beobachtung mit Review-Grenzen

Status:
- ausdrücklich später

## 3. Aktuelle Reihenfolge

Die aktuell empfohlene Reihenfolge lautet:

1. A0 akzeptieren
2. T1.0 scaffolden
3. T1.x Foundation stabilisieren
4. ersten Vertical Slice bauen
5. Sources/Evidence ergänzen
6. Search/Refresh ergänzen
7. Web/GPT anbinden
8. VPS sauber etablieren
9. Monitoring/Agenten erst danach

## 4. Nicht jetzt

Bewusst nicht frühe Priorität:

- Multi-User-Kollaboration
- aggressive autonome Agentik
- komplexe Live-Vererbungsmodelle für Blueprints
- unkontrollierte Login-/Paywall-Automation
- Enterprise-Ausbau

## 5. Steuerungsregel

Jeder größere Schritt aktualisiert:

- `docs/MASTERPLAN.md`
- `docs/PROJECT_STATE.md`
- ein `docs/_handoff/HANDOFF_*.md`

## 6. Eintrittskriterium für T1.0

T1.0 darf beginnen, wenn:

- die A0-Baseline akzeptiert ist,
- keine offenen Widersprüche in den Kernentscheidungen bestehen,
- der nächste technische Scope bewusst klein gehalten wird,
- die Arbeitsreihenfolge klar ist.

Dieses Eintrittskriterium gilt mit der vorliegenden A0-Abnahme als erfüllt.
