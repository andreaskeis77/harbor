# Harbor Strategy Roadmap v0.1

Stand: 2026-04-08

## Zielbild

Harbor wird schrittweise als **projektbasiertes Recherche-, Wissens- und Monitoring-System** aufgebaut. Die Architektur bleibt bewusst modular:

1. **Core Harbor Backend**
   - Persistenz
   - Migrationen
   - Registries / Services
   - REST-API
   - Smoke-Slices
   - Quality Gates

2. **Operator UX / Web Shell**
   - dünne Weboberfläche
   - arbeitet ausschließlich über Harbor-APIs
   - keine zweite Logikspur neben dem Backend

3. **AI Adapter Layer**
   - OpenAI/LLM-Integration als klar getrennte Schicht
   - Tool-Aufrufe gegen Harbor
   - keine direkten DB-Schreibpfade aus Modelllogik

4. **Automation / Monitoring Layer**
   - Scheduler
   - Refresh-Läufe
   - Alerts
   - später kontrollierte agentische oder halbautomatische Flows

Grundsatz: **Harbor bleibt immer System of record.**

---

## Aktueller Stand

Der aktuelle funktionale Alpha-Kern ist:

**Project → Search Campaign → Search Run → Search Result Candidate → Review Queue → Source / ProjectSource**

Zusätzlich bereits vorhanden:
- Duplicate Guards / Idempotenz für Promotion-Schritte
- Workflow Summary / Lineage Surface
- Alpha Runbook
- Alpha Release Checklist
- Tag und GitHub Release `v0.1.0-alpha`

Dieser Stand ist bewusst **operator-driven**:
- keine echte Websuche
- keine Agentik
- keine erweiterte Deduplizierung / Merge-Logik
- keine UI für Endnutzer

---

## Engineering-Prinzipien

### 1. Kleine Bolts
Änderungen werden als kleine, klar geschnittene Bolts umgesetzt.

Ein Bolt enthält idealerweise nur:
- einen fachlichen Schwerpunkt
- betroffene API-Fläche
- Tests
- passenden Smoke-Slice
- PR / Merge
- Doku-Sync, wenn Benutzerverhalten betroffen ist

### 2. API-first
UI, AI und spätere Automatisierung laufen über Harbor-APIs, nicht direkt gegen die DB.

### 3. Strikte Schichtentrennung
- keine KI-Logik in Persistenz / Registry-Core
- keine UI-Logik in Modellen
- keine direkten DB-Schreibpfade außerhalb kontrollierter Harbor-Services

### 4. Qualität vor Scope
Ein Schritt gilt erst als fertig, wenn:
- `quality-gates` grün sind
- relevante Smoke-Slices grün sind
- PR gemerged ist
- `main` lokal aktualisiert und erneut geprüft wurde

### 5. Änderungsübergabe
Bei Mehrdatei-Änderungen werden bevorzugt **ZIP-Artefakte mit korrekter Ordnerstruktur** verwendet.  
Direkte Chat-Patches nur für kleine Einzeländerungen oder kurze Validierungsblöcke.

---

## Release-Strategie

### v0.1.0-alpha — erreicht
Erster manueller Operator-Release.

Enthalten:
- Projects
- Handbook persistence
- Sources / ProjectSources
- Search Campaigns
- Search Runs
- Search Result Candidates
- Candidate → Review Queue
- Review Queue → Source
- Duplicate Guards
- Workflow Summary / Lineage
- Docs / Runbook / Release Hygiene

### v0.2.0-alpha — nächste sinnvolle Stufe
Erste nutzbare **Operator Web Shell**.

### v0.3.0-alpha
OpenAI-gestützte Assistenz:
- Candidate-Triage-Vorschläge
- Source-Drafting / Bewertungsentwürfe
- weiterhin menschlich freigegeben

### v0.4.0-beta
Chat-gestützte Bedienung / kontrollierte Assistenz-Workflows.

### v1.0.0
Stärker gehärteter, betriebsfähiger Kern mit:
- Monitoring
- Scheduler
- Observability
- reiferer Deduplizierung / Merge-Strategie

---

## Produkt-Roadmap

## Phase A — Web-Nutzbarkeit

### T2.0 — Operator Web Shell
Ziel:
- erste dünne Weboberfläche für den bestehenden Harbor-Flow

Geplanter Scope:
- Projektliste
- Projekt-Detail mit Workflow Summary
- Ansichten für:
  - Search Campaigns
  - Runs
  - Candidates
  - Review Queue
  - Project Sources

Nicht in T2.0:
- keine neue Persistenzlogik
- keine OpenAI-Integration
- keine Search-Automation
- keine Agentik

### T2.1 — Operator Actions UI
Ziel:
- Candidate → Review
- Review → Source
- Statusänderungen
- Duplicate-Fehler sauber anzeigen

### T2.2 — UX / API Hardening
Ziel:
- Filter
- Sortierung
- Pagination
- bessere Fehlermeldungen
- Demo-/Testfluss

**Release-Ziel nach Phase A:** `v0.2.0-alpha`

---

## Phase B — OpenAI Adapter Layer

### T2.3 — OpenAI Adapter
Ziel:
- Harbor-Funktionen als kontrollierte Tools nutzbar machen
- strukturierte Outputs
- klarer Audit-/Fehlerpfad

Leitplanken:
- keine direkten Modell-Schreibrechte auf DB
- KI spricht nur mit Harbor-API / Harbor-Tools
- keine versteckte Fachlogik in Prompts

### T2.4 — Assisted Candidate Triage
KI schlägt Dispositionen vor, Mensch entscheidet.

### T2.5 — Assisted Source Drafting
KI schlägt Summary, Trust Tier, Relevance und Notizen vor, Mensch entscheidet.

**Release-Ziel nach Phase B:** `v0.3.0-alpha`

---

## Phase C — Chat Surface / AI UX

### T2.6 — Chat Surface
Optionen:
- Harbor-eigene Web-Chatfläche
- ChatKit-basierte Oberfläche
- später optional GPT Actions / Custom GPT / Agents SDK

Ziel:
- natürlichere Bedienung
- aber weiterhin kontrollierte Tool-Aufrufe und menschliche Freigaben

### T2.7 — Controlled Workflow Assistants
Ziel:
- dialoggestützte Recherche-Unterstützung
- geführte Entscheidungs- und Review-Flows
- keine unkontrollierte Vollagentik

**Release-Ziel nach Phase C:** `v0.4.0-beta`

---

## Phase D — Betriebsreife / Automation

### T3.x — Monitoring und Scheduler
Ziel:
- geplante Refresh-Läufe
- Beobachtungsfunktionen
- Alerts / Benachrichtigungen

### T3.x — Observability & Ops
Ziel:
- Logging
- Traceability
- Fehlerbilder systematischer analysieren
- Betriebsrunbooks erweitern

### T3.x — Erweiterte Deduplizierung / Merge-Strategie
Ziel:
- echte Merge-Entscheidungen
- Konfliktbehandlung
- robustere Wiederaufnahme- und Korrekturpfade

**Release-Ziel:** `v1.0.0`

---

## Nächster konkreter Schritt

**T2.0 — Operator Web Shell**

Warum genau jetzt:
- Backend-Kern ist nutzbar
- Workflow Summary existiert bereits
- Duplicate Guards sind vorhanden
- erste echte Nutzbarkeit entsteht über Sichtbarkeit und Bedienung, nicht sofort über KI

Architekturregel:
Die Web Shell darf **nur über Harbor-APIs** arbeiten, nicht direkt an der Datenbank vorbei.
