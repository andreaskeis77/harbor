# Harbor Projektbericht — aktualisiert 2026-04-11 (nach H1–H4 Hardening)

**Basis:** Repository `andreaskeis77/harbor`, Branch `bolt/t4-5a-project-source-grounded-chat-baseline-v2`, Stand nach Abschluss von H1–H4 Hardening-Phasen.

---

## 1. Executive Summary

### Was ist Harbor?
Harbor ist ein **projektpartitioniertes Research Operating System** — kein generischer Chat-RAG. Die Leitidee: Recherchekontext, Quellen, Reviewzustände und Assistenz werden streng pro Projekt gekapselt und nur über explizite Operator-Schritte von „gefunden" zu „akzeptiertem Wissen" bewegt.

### Wo steht das Projekt heute?
Das Projekt ist funktional **deutlich weiter als das letzte formale Alpha-Release `v0.1.0-alpha`** und hat durch vier systematische Hardening-Phasen (H1–H4) einen **substanziellen Reifesprung in der nicht-funktionalen Qualität** gemacht. Auf `main` sind ein FastAPI-Backend, ein manueller Operator-Workflow, ein Operator-Web-Shell-Surface, ein OpenAI-Adapter, persistierte Dry-Run-Logs sowie ein persistierter projektbezogener Multi-Turn-Chat implementiert. T4.5A (project-source-grounded chat) ist auf dem aktuellen Branch abgeschlossen.

### Was hat sich seit dem letzten Bericht verändert?
Die vier Hardening-Phasen haben die zentralen Risiken des vorherigen Berichts systematisch adressiert:

| Vorheriges Risiko | Status nach H1–H4 |
|---|---|
| Gespaltener Migrationspfad | **Behoben.** Konsolidiert auf `migrations/`, 10 lineare Migrationen, 3 Integritätstests |
| Keine Observability | **Behoben.** Structured Request Logging, Request-ID-Propagation, Global Exception Handler |
| Keine Fehlerbehandlungs-Architektur | **Behoben.** Typed Domain Exceptions, Middleware-Handler, Transaction Middleware |
| Keine Coverage-Sicherung | **Behoben.** 70%-Gate, 96% effektive Coverage, 116 Tests |
| `config/.env.example` Widerspruch | **Behoben.** Bereinigt, nur noch Root `.env.example` |
| Fehlende CI/Review-Automation | **Offen.** Kein `.github/` im Repo |
| Fehlendes Inbound-Auth | **Offen.** Keine Security-Schicht für API/Operator-Flächen |
| Monolithische Web-Shell | **Offen.** 3.732 Zeilen Inline-HTML/CSS/JS |

### Was ist stark?
1. **Produktmodell:** Projektpartitionierung, explizite Promotionsgrenzen, keine stille Wissensübernahme.
2. **Engineering-Disziplin:** `origin/main` als kanonische Wahrheit, kleine Bolts, Handoffs, Validierungsprotokoll, Lessons Learned nach jeder Phase.
3. **Nicht-funktionale Reife (neu):** Typed Exceptions, Transaction Middleware, 96% Coverage, Migrationstests, Structured Logging, 9 Ruff-Rule-Sets.
4. **Testbare Architektur:** 116 Tests, E2E-Workflow-Lifecycle, Validierungs-Edge-Cases, Input-Boundary-Tests.
5. **LLM-Inspectability:** Dry-Run-Logs, Chat-Turns, Turn-Inspection, Compare-Surfaces.

### Was ist riskant?
1. **Fehlendes Inbound-Auth-Konzept** — für lokalen Betrieb tolerierbar, für öffentliche Exponierung nicht.
2. **Monolithische Web-Shell** (3.732 Zeilen) — wachsende Wartungslast ohne Template-/Static-Trennung.
3. **Keine sichtbare CI/CD** — Quality Gates sind lokal robust, aber nicht automatisiert erzwungen.
4. **Fehlende Current-State-Ops-Dokumente** — Security, Observability, Release-Management, VPS-Betrieb.
5. **OpenAI-Adapter-Registry-Tests** — indirekt via API getestet, aber keine isolierten Unit-Tests.

---

## 2. Methodik und Source of Truth

Dieser Bericht trennt vier Ebenen:

1. **Implementierter Ist-Zustand** — Code, Konfiguration, Tests, Migrationen, Tooling.
2. **Dokumentierter Ist-Zustand** — README, MASTERPLAN, PROJECT_STATE, Handoffs, Lessons Learned.
3. **Zielzustand** — formulierte nächste oder spätere Ausbaustufen.
4. **Historische Artefakte** — Alpha-Runbooks, v0.1-Dokumente.

Hierarchie: **Code > aktuelle Steuerdokumente > Governance > historische Artefakte.** Widersprüche werden offen behandelt. Code gilt vor Doku.

**Negativer Befund:** Folgende erwartete Dokumente existieren weiterhin nicht: `docs/SECURITY.md`, `docs/OBSERVABILITY.md`, `docs/RELEASE_MANAGEMENT.md`, `docs/RUNBOOK.md` (current-state), `.github/`, `deploy/`. Dieser fehlende Bestand ist ein Befund, kein Analysefehler.

---

## 3. Architektur und Architekturentscheidungen

### Stack
Python 3.12+, FastAPI, Uvicorn, Pydantic/Pydantic-Settings, SQLAlchemy, Psycopg, Alembic, OpenAI-SDK. Dev: pytest, pytest-cov, ruff, httpx.

### Schichten (nach H1–H4)

```
┌─────────────────────────────────────────────────────┐
│  Operator Web Shell (3.732 LOC, Inline HTML/CSS/JS) │
│  /operator/projects, /operator/projects/{id}, /chat │
├─────────────────────────────────────────────────────┤
│  API Routes (12 Dateien, ~900 LOC)                  │
│  Kein HTTPException, kein try/except KeyError        │
├─────────────────────────────────────────────────────┤
│  Middleware (132 LOC)                                │
│  Request Logging, Request-ID, 6 Exception Handler   │
├─────────────────────────────────────────────────────┤
│  Domain Logic / Registries (8 Module, ~1.700 LOC)   │
│  Typed Exceptions, session.flush(), kein commit()   │
├─────────────────────────────────────────────────────┤
│  OpenAI Adapter (441 LOC) + Chat Registry (266 LOC) │
│  Fake-Client-fähig, Dry-Run-Persistenz              │
├─────────────────────────────────────────────────────┤
│  Persistence (550 LOC)                               │
│  SQLAlchemy Models, Transaction Middleware            │
│  get_db_session: commit-on-success / rollback-on-err│
├─────────────────────────────────────────────────────┤
│  Alembic Migrations (10, linear, konsolidiert)       │
└─────────────────────────────────────────────────────┘
```

### Zentrale Architekturentscheidungen nach H1–H4

| Entscheidung | Rationale | Status |
|---|---|---|
| Typed Domain Exceptions | Eliminiert 48 string-basierte KeyError, 17 try/except in Routes | Vollständig umgesetzt |
| Middleware Exception Handler | Zentrale HTTP-Status-Zuordnung, keine HTTPException in Routes | 6 Handler, alle getestet |
| Request-Scoped Transaction | commit-on-success/rollback-on-error, flush() in Registries | Alle 16 commit()-Aufrufe migriert |
| Konsolidierter Migrationspfad | Einziger `migrations/`-Pfad, lineare Kette, Integritätstests | 10 Migrationen, 3 Tests |
| Structured Request Logging | Method, Path, Status, Duration, Request-ID in jedem Request | Middleware + 2 Log-Verifikationstests |
| Coverage-Gate mit Ausschlüssen | 70% Minimum, CLI-Surfaces ausgeschlossen (95% effektiv) | In pyproject.toml verankert |
| Ruff 9-Rule-Set | E, F, I, B, UP, SIM, PIE, LOG, RUF permanent | Manifest-Regel |

### Architektur-Stärken
- **Projektpartitionierung** als harte Grenze für Kontext, Quellen und Chat
- **Promotion-Grenzen** (Candidate → Review → Source) verhindern stille Wissensübernahme
- **Backend-first** mit dünner Web-Schicht (topologisch, nicht wartungsmäßig)
- **Adapter-Seam** vor tieferer Chat-Funktionalität (Runtime/Probe → Dry-Run → Chat)
- **Testbare Architektur** durch saubere Schichttrennung

### Architektur-Schwächen
- **Monolithische Web-Shell** (3.732 LOC in einer Datei mit Inline-HTML/CSS/JS)
- **Keine Security-Schicht** (kein Inbound-Auth für API/Operator/Chat)
- **Keine CI/CD-Pipeline** (Quality Gates nur lokal)
- **OpenAI-Adapter-Registry** nur indirekt via API getestet

---

## 4. Lessons Learned — Konsolidierte Analyse aller Hardening-Phasen

### Überblick der vier Phasen

| Phase | Fokus | Tests vorher | Tests nachher | Schlüsselerkenntnis |
|---|---|---|---|---|
| H1 | Migration, Observability, Test-Infra | 56 | 62 | Split-Migrationspfad war unsichtbar, weil Tests `create_all()` statt Alembic nutzten |
| H2 | Typed Exceptions, Transaction Middleware | 59 | 65 | Bulk-Edits können Indentation-Varianten übersehen; grep-verify ist Pflicht |
| H3 | Coverage-Tiefe, Observability, Lint | 65 | 82 | Alembic `fileConfig()` deaktiviert alle Logger — subtilster Bug der gesamten Hardening-Serie |
| H4 | Validierungs-Edge-Cases, E2E-Workflow | 82 | 116 | Coverage-Prozent versteckt, wo die Lücken liegen; 84% bei review_queue war 100% Validierungslogik |

### Die wichtigsten Erkenntnisse über alle Phasen

**1. Tests gegen `create_all()` maskieren Migrationsprobleme (H1)**
Das schwerwiegendste Risiko im vorherigen Bericht — der gespaltene Migrationspfad — war vollständig unsichtbar, weil alle Tests `Base.metadata.create_all()` statt dem echten Alembic-Upgrade-Pfad nutzten. Jetzt gibt es 3 dedizierte Migrationstests, die `alembic upgrade head` gegen eine leere DB fahren und Ketten-Linearität, Tabellen-Vollständigkeit und ORM-Parität validieren.

**2. Typed Exceptions eliminieren eine ganze Fehlerklasse (H2)**
48 string-basierte `KeyError`-Raises und 17 `except KeyError`-Blöcke in Routes wurden durch 5 typisierte Exception-Klassen und 6 Middleware-Handler ersetzt. Das eliminiert nicht nur Code, sondern macht Fehlerpfade testbar — jeder Handler hat jetzt einen dedizierten Test.

**3. Globale Logger-Mutation ist ein latentes Risiko (H3)**
Der subtilste Bug der gesamten Serie: Alembics `fileConfig()` mit `disable_existing_loggers=True` (Standard) deaktiviert alle Harbor-Logger, wenn Alembic-Tests vor Logging-Tests laufen. Symptom: Tests bestehen einzeln, scheitern im Suite-Lauf. Die Reihenfolge ist determiniert (alphabetisch), wirkt aber nichtdeterministisch. Fix: `disable_existing_loggers=False`. **Permanente Regel:** Jeder `fileConfig()`/`dictConfig()`-Aufruf ohne dieses Flag ist ein latenter Bug.

**4. Coverage-Prozent versteckt die Lücken-Location (H4)**
84% Coverage in `review_queue_registry.py` klingt gut. Aber die fehlenden 16% waren ausschließlich Validierungslogik: Entity-Not-Found-Checks, Cross-Entity-Ownership-Mismatches und Lineage-Integritätsguards. 17 gezielte Tests schlossen diese Lücken. **Permanente Regel:** Immer prüfen, *welche* Zeilen nicht abgedeckt sind, nicht nur die Zahl.

**5. E2E-Tests fangen Annahme-Mismatches (H4)**
Der E2E-Lifecycle-Test entdeckte einen echten Ordering-Bug: Workflow-Summary-Lineage-Items werden nach Erstellungszeit sortiert, nicht nach Disposition. Die initiale Annahme, der erste Eintrag sei der promoted Kandidat, war falsch. Genau diese Art von Annahme verursacht UI-Rendering-Fehler in Produktion.

### Permanente Methodik-Änderungen (kumuliert)

Über die vier Phasen wurden **24 permanente Manifest-Regeln** etabliert:

- Migration-Integrität ist First-Class-Test
- Observability ist nicht optional
- Single Source of Configuration
- Test-Fixtures sind Shared Infrastructure
- Typed Exceptions statt String-Matching
- Request-Scoped Transaction Boundary
- Coverage Quality Gate
- Kein HTTPException in Routes
- Coverage-Ausschlüsse für CLI-Surfaces
- `fileConfig(disable_existing_loggers=False)` ist Pflicht
- Error Paths müssen getestet sein
- Expanded Lint Rules sind permanent
- Validierungs-Edge-Cases am Registry-Boundary testen
- Input-Validation am API-Boundary testen
- E2E-Workflow-Tests für State-Transitions
- Coverage-Gate ratchet forward

### Metriken-Entwicklung

| Metrik | Vor H1 | Nach H1 | Nach H2 | Nach H3 | Nach H4 |
|---|---|---|---|---|---|
| Tests | 56 | 62 | 65 | 82 | 116 |
| Coverage | unbekannt | unbekannt | 67% | 95% | 96% |
| Coverage-Gate | — | — | 60% | 70% | 70% |
| Ruff Rules | 4 | 4 | 4 | 9 | 9 |
| Exception Handlers | 1 | 1 | 6 | 6 | 6 |
| Migrationstests | 0 | 3 | 3 | 3 | 3 |
| Error-Path-Tests | 0 | 0 | 0 | 11 | 11 |
| E2E-Tests | 0 | 0 | 0 | 0 | 1 |
| Validation-Edge-Tests | 0 | 0 | 0 | 0 | 17 |
| Input-Boundary-Tests | 0 | 0 | 0 | 0 | 15 |
| Manifest-Regeln | 12 | 16 | 20 | 24 | 24 |

---

## 5. Roadmap — Wo stehen wir, was steht an?

### Akzeptierte Sequenz

```
A0  ✅  Accepted Product / Architecture / Governance Baseline
T1  ✅  Local Technical Bootstrap and Manual Operator Flow
T2  ✅  Operator Web Surface
T3  ✅  OpenAI Adapter and Dry-Run Surfaces
T4  ⬛  Chat Surface and Operator-Facing Chat Hardening
    T4.0A–T4.4B  ✅  Chat Baseline bis Readability Hardening
    T4.5A        ✅  Project-Source-Grounded Chat (auf Branch)
    T4.5B        ⏳  Source Attribution / Source Visibility in Chat
H1–H4  ✅  Cross-Cutting Hardening (Migration, Exceptions, Coverage, E2E)
T5  ⏳  Source-Grounded Knowledge and Operator Action Surfaces
T6  ⏳  Deeper Automation / Monitoring Evolution
```

### Aktueller Standort
Harbor steht am Übergang von **T4.5A → T4.5B**, mit abgeschlossenem H1–H4 Hardening. Der aktuelle Branch (`bolt/t4-5a-project-source-grounded-chat-baseline-v2`) enthält T4.5A plus alle vier Hardening-Phasen, ist aber noch nicht in `main` gemerged.

### Nächste Schritte — priorisiert

#### P0 — Unmittelbar (0–14 Tage)

1. **Branch mergen.** T4.5A + H1–H4 in `main` überführen. Dieser Branch ist grün und vollständig validiert.

2. **T4.5B — Source Attribution in Chat.** Sichtbar machen, welche Projektquellen in einen Chat-Turn eingeflossen sind. Ohne das ist „grounded chat" für den Operator nicht nachvollziehbar.

3. **README und INDEX aktualisieren.** README zeigt noch „H1 — Phase 1 hardening" als Current Phase. INDEX fehlen H2–H4 Updates.

#### P1 — Kurzfristig (14–30 Tage)

4. **Current-State-Runbook schreiben.** Nicht als Alpha-Ergänzung, sondern für den heutigen `main` mit Chat, OpenAI, H1–H4 Hardening.

5. **CI/CD einrichten.** GitHub Actions für `quality-gates` und Migrationstests. Die lokale Quality-Gate-Disziplin ist stark — jetzt technisch erzwingen.

6. **Security-Entscheidung treffen.** Harbor explizit als lokal-only deklarieren oder ein minimales Inbound-Auth-Gate einführen.

7. **T5 erste Scheibe konkretisieren.** Source-grounded Knowledge Surfaces als nächster Produktschritt nach T4.5B.

#### P2 — Mittelfristig (30–60 Tage)

8. **Web-Shell aufteilen.** 3.732 Zeilen Inline-HTML/CSS/JS in Templates/Static oder kleinere Module überführen.

9. **OpenAI-Registry Unit-Tests.** Isolierte Tests für `openai_chat_session_registry.py` (aktuell nur via API getestet).

10. **ADRs beginnen.** Mindestens für Projektpartitionierung, Promotion-Grenzen, Transaction-Boundary-Ownership, Web-Shell-Ansatz.

11. **Release-Management nachziehen.** Versionierung, Release Notes, Cut-Regeln.

### Explizite Nicht-Ziele (unverändert)
- Autonome Tool-Orchestrierung
- Automatisierte Suchausführung
- Handbook-Synthese ohne Operator-Aktion
- Vektor-/Embedding-Subsystem
- Multi-User-Kollaboration
- Background Agents

---

## 6. UI / UX — Bestandsaufnahme und Handlungsbedarf

### Aktuelle UI-Flächen

Harbor hat drei UI-Flächen, alle aus einer einzigen Python-Datei (`operator_web.py`, 3.732 LOC) generiert:

| Fläche | URL | Zweck |
|---|---|---|
| Projects | `/operator/projects` | Projektliste, Projekt-Erstellung |
| Project Detail | `/operator/projects/{id}` | Workflow-Summary, OpenAI Dry-Run, manuelle Aktionen, Datentabellen, Promotion |
| Chat | `/chat` | Projektbezogener Multi-Turn-Chat mit Session-Persistenz |

### Was die UI heute kann

**Projects Page:**
- Projektliste mit 6 Spalten (Title, Status, Type, Blueprint, Updated, Description)
- Create-Project-Form (Title, Short Description)
- Links zu /chat, /healthz, /runtime

**Project Detail Page:**
- Projekt-Metadaten (Status, Timestamps)
- Workflow Summary (Grid mit Zähler-Cards)
- OpenAI Dry-Run Section (Input, Instructions, Persist-Toggle, History-Tabelle)
- 5 manuelle Create-Formulare (Campaign, Run, Candidate, Review Item, Project Source)
- 5 Datentabellen (Campaigns, Runs, Candidates, Review Queue, Project Sources)
- Promotion-Actions (Candidate → Review, Review → Source)
- Lineage-Tabelle

**Chat Page:**
- Projekt-Selector und Session-Selector
- Message-Composer mit Instructions-Textarea
- 3 Instruction-Presets (research-plan, evidence-summary, decision-brief)
- Persistierte Chat-History mit Turn-Inspector
- Turn-Comparison-View
- Retry-Panel für fehlgeschlagene Requests
- Collapsible Content für lange Antworten

### Architektur-Analyse der UI

```
operator_web.py (3.732 LOC)
├── BASE_CSS (391 LOC)      — Dark-Mode Stylesheet, globaler Scope
├── BASE_SCRIPT (1.210 LOC) — 337 JS-Funktionen, Operator Shell
├── CHAT_SCRIPT (1.164 LOC) — Chat-spezifisches JS
├── HTML-Templates (~800 LOC) — f-String-basierte HTML-Generierung
└── Route-Handler (~170 LOC) — 4 GET-Endpoints
```

**Probleme:**
1. **Keine Trennung von Concerns.** HTML, CSS, JS und Python-Routing in einer Datei. Jede UI-Änderung erfordert Python-Code-Edits.
2. **Kein JS-Tooling.** 2.374 Zeilen JavaScript als String-Literale — kein Linting, kein Minification, keine Module.
3. **Kein Template-Engine.** HTML wird per f-String generiert, was XSS-Oberfläche und fehlende Wiederverwendbarkeit erzeugt.
4. **Globaler JS-Scope.** Alle 337 Funktionen leben im globalen Scope, keine Module.
5. **Keine Paginierung.** Alle Daten werden auf einmal geladen (Campaigns, Runs, Candidates).
6. **Brüchige Tests.** UI-Tests basieren auf String-Suche in HTML-Output.

### UX-Stärken
- **Dark-Mode-Design** mit konsistenter visueller Sprache
- **Operator-fokussiert:** Aktionen sind direkt am Datenpunkt (Promote-Buttons in Tabellen)
- **Chat-Presets** (research-plan, evidence-summary, decision-brief) sind fachlich sinnvoll
- **Turn-Inspector und Compare-View** gehen über Minimal-UI hinaus
- **Retry-Handling** für fehlgeschlagene Chat-Requests

### UX-Schwächen und Handlungsbedarf

#### Kurzfristig (P0/P1)
- **Source-Grounding-Transparenz:** Chat zeigt nicht, welche Quellen in einen Turn eingeflossen sind. T4.5B adressiert das.
- **No-Source-Fallback:** Wenn keine akzeptierten Quellen vorliegen, muss das explizit sichtbar sein, statt einen implizit „wissenden" Chat zu simulieren.
- **Operator-Flow-Fokus:** Project Detail ist aktuell eine Sammlung technischer Teilflächen. Stärker auf die Hauptaktionen gruppieren (Research → Review → Accept).

#### Mittelfristig (P2)
- **Web-Shell aufteilen:** Templates für HTML, Static-Dateien für CSS/JS, Jinja2 oder ähnlich.
- **JS-Module einführen:** Mindestens ES-Modules statt 337 globale Funktionen.
- **Paginierung:** Datentabellen werden mit wachsenden Datenmengen unbenutzbar.
- **Source Inspector / Evidence View:** Recherchewissen und Chat-Grounding konsistent lesbar machen.

#### Langfristig (P3)
- **Informationshierarchie professionalisieren:** Weniger Inline-Technik, klarere Zustandsanzeigen.
- **Responsive Layout:** Aktuell nur Desktop-optimiert.
- **Keyboard Navigation / Accessibility:** Nicht vorhanden.

---

## 7. Testability und Qualitätsmaßstäbe

### Test-Pyramide (nach H4)

```
                    ┌─────────────┐
                    │   1 E2E     │  Voller Workflow-Lifecycle
                    │   Workflow  │  (Projekt → Source)
                    ├─────────────┤
                 ┌──┤  35+ API   ├──┐  CRUD + Error Paths
                 │  │  Integration│  │  für alle Entitäten
                 │  ├─────────────┤  │
              ┌──┤  │  17 Edge   │  ├──┐  Validierungs-Branches
              │  │  │  Cases     │  │  │  in Registries
              │  │  ├─────────────┤  │  │
           ┌──┤  │  │  15 Input  │  │  ├──┐  Pydantic Constraints
           │  │  │  │  Boundary  │  │  │  │  (422 Rejection)
           │  │  │  ├─────────────┤  │  │  │
        ┌──┤  │  │  │  11 Error  │  │  │  ├──┐  503, Redaction,
        │  │  │  │  │  Path      │  │  │  │  │  Connectivity
        │  │  │  │  ├─────────────┤  │  │  │  │
     ┌──┤  │  │  │  │  10 Middle-│  │  │  │  ├──┐  Exception Handler,
     │  │  │  │  │  │  ware      │  │  │  │  │  │  Logging, Request-ID
     │  │  │  │  │  ├─────────────┤  │  │  │  │  │
     │  │  │  │  │  │  3 Migra-  │  │  │  │  │  │  Chain, Tables, ORM
     │  │  │  │  │  │  tion      │  │  │  │  │  │
     └──┴──┴──┴──┴──┴─────────────┴──┴──┴──┴──┴──┘
              116 Tests, 96% Coverage
```

### Quality Gates

```
compileall (Syntax-Check) → ruff (9 Rule-Sets) → pytest (116 Tests + 70% Coverage-Gate)
```

Lokal robust, aber nicht CI-erzwungen.

### Coverage nach Modul (Top 10 Lücken)

| Modul | Coverage | Fehlende Zeilen | Art |
|---|---|---|---|
| openai_adapter.py | 85% | 27 LOC | Defensive Error-Envelopes, Client-Factory |
| openai_chat_session_registry.py | 92% | 9 LOC | Validation Checks in Registry-Funktionen |
| search_run_registry.py | 92% | 7 LOC | Not-Found-Checks, Status-Updates |
| search_result_candidate_registry.py | 93% | 6 LOC | Not-Found-Checks, Disposition-Updates |
| review_queue_registry.py | 97% | 5 LOC | Defensive Data-Corruption-Guards |
| source_registry.py | 96% | 3 LOC | IntegrityError-Handling |
| Alle anderen Module | 97–100% | — | — |

### Verbleibende Test-Gaps

1. **OpenAI-Chat-Session-Registry:** `create_openai_project_chat_session()`, `ensure_openai_project_chat_session()`, `create_openai_project_chat_turn()` — nur via API-Tests exercised, keine isolierten Registry-Tests.
2. **OpenAI-Adapter Defensive Envelopes:** Exception-Handling in `openai_project_chat_turn_payload()`, `openai_probe_payload()`, `openai_project_dry_run_payload()` — markiert als `# pragma: no cover`.
3. **Web-Shell UI:** Verifiziert via String-Suche in HTML, nicht via Browser-Automation.

---

## 8. Resilienz-Bewertung

### Was resilient ist

| Bereich | Bewertung | Evidenz |
|---|---|---|
| Migrationspfad | **Stark** | 10 lineare Migrationen, 3 Integritätstests, kein Split mehr |
| Fehlerbehandlung | **Stark** | 5 typed Exceptions, 6 Middleware-Handler, alle getestet |
| Transaktionssicherheit | **Stark** | Request-scoped commit/rollback, flush() in Registries |
| Validierungslogik | **Stark** | 17 Edge-Case-Tests, 15 Input-Boundary-Tests |
| Workflow-Integrität | **Stark** | E2E-Lifecycle-Test, Duplicate Guards, Promotion-State-Machine |
| Observability | **Mittel** | Request-Logging + Request-ID, aber kein Metriken/Alerting/Tracing |
| Security | **Schwach** | Kein Inbound-Auth, keine Firewall-/Proxy-Konzeption |
| Deployment-Resilienz | **Schwach** | Kein CI/CD, keine automatisierte Release-Pipeline |

### Was seit dem letzten Bericht behoben wurde

- **Split-Migrationspfad:** Vollständig konsolidiert und getestet
- **Zero Observability:** Structured Logging mit Request-ID etabliert
- **String-basierte Fehlerbehandlung:** Durch typed Exceptions ersetzt
- **Fehlende Coverage-Sicherung:** 70% Gate, 96% effektiv
- **Doppelte Env-Konfiguration:** Bereinigt
- **Stale Alembic-Verzeichnis:** Entfernt
- **Logger-Kontamination durch Alembic:** Gefixt und getestet

---

## 9. Schlussfazit

Harbor ist nach vier systematischen Hardening-Phasen ein **deutlich reiferes System** als zum Zeitpunkt des letzten Berichts. Die zentralen nicht-funktionalen Risiken — gespaltener Migrationspfad, fehlende Observability, fragile Fehlerbehandlung, keine Coverage-Sicherung — sind adressiert und durch permanente Manifest-Regeln abgesichert.

**Die größte Veränderung ist methodischer Natur:** Harbor hat jetzt einen funktionierenden Continuous-Improvement-Zyklus. Jede Phase produziert Lessons Learned, aktualisiert das Engineering Manifest, erweitert das Validierungsprotokoll und hinterlässt eine messbar bessere Codebasis. Das ist für ein System in diesem Stadium bemerkenswert.

**Die verbleibenden Hauptaufgaben** liegen nicht mehr in der Grundlagen-Resilienz, sondern in der **operativen Reifung:** CI/CD-Automation, Security-Perimeter, Web-Shell-Modularisierung, Current-State-Betriebsdokumentation und Release-Management. Parallel dazu ist der nächste fachliche Schritt klar: **T4.5B Source Attribution** und danach **T5 Source-Grounded Knowledge Surfaces**.

Harbor ist ein ernsthaft aufgebautes, fachlich fokussiertes Research Operating System mit jetzt auch belastbarer nicht-funktionaler Qualität. Die größte Aufgabe ist der Übergang von lokal-robustem Engineering zu belastbarem Systembetrieb.

---

## 10. Appendix

### A. Projekt-Statistiken (Stand 2026-04-11)

| Kategorie | Dateien | LOC |
|---|---|---|
| Source (src/harbor/) | 38 | ~9.600 |
| Tests (tests/) | 23 | ~3.600 |
| Tools | 2 | 293 |
| Docs | 71 | — |
| Migrationen | 10 | — |
| **Gesamt** | **144** | **~13.500** |

### B. Lessons-Learned-Dokumente

- `docs/LESSONS_LEARNED_T4_5A_2026-04-10.md` — Delivery-Disziplin, Artefakt-Integrität
- `docs/LESSONS_LEARNED_H1_2026-04-11.md` — Migration-Split, Zero Observability, Fixture-Duplication
- `docs/LESSONS_LEARNED_H2_2026-04-11.md` — Typed Exceptions, Transaction Boundary, Bulk-Edit-Risiken
- `docs/LESSONS_LEARNED_H3_2026-04-11.md` — Coverage-Ausschlüsse, Alembic Logger-Bug, Expanded Lint
- `docs/LESSONS_LEARNED_H4_2026-04-11.md` — Coverage-Lücken-Location, E2E-Ordering-Bug, Input-Boundaries

### C. Verbleibende Widersprüche

| Widerspruch | Status |
|---|---|
| ~~Gespaltener Migrationspfad~~ | **Behoben** (H1) |
| ~~Root vs. config/.env.example~~ | **Behoben** (H1) |
| Code-Version `0.1.4a0` vs. Release `v0.1.0-alpha` | **Offen** — Release-Management fehlt |
| README zeigt „H1" als Current Phase | **Offen** — muss auf H4 aktualisiert werden |
| INDEX fehlen H2–H4 Updates | **Offen** — muss ergänzt werden |
| „Thin web shell" vs. 3.732 LOC Inline | **Offen** — topologisch dünn, wartungsmäßig nicht |
| Alpha-Runbook vs. aktueller Funktionsstand | **Offen** — Current-State-Runbook fehlt |

### D. Referenz-Dateien

**Steuerung:** README.md, docs/MASTERPLAN.md, docs/PROJECT_STATE.md, docs/INDEX.md
**Governance:** docs/ENGINEERING_MANIFEST.md, docs/VALIDATION_PROTOCOL.md, docs/DELIVERY_PROTOCOL.md
**Architektur:** src/harbor/app.py, src/harbor/api/middleware.py, src/harbor/exceptions.py, src/harbor/persistence/session.py
**Qualität:** pyproject.toml, tools/run_quality_gates.py, tests/conftest.py
**UI:** src/harbor/api/routes/operator_web.py
