# Harbor Chat Handoff — Next Chat

Stand: 2026-04-08

## Ziel dieses Handoffs

Dieses Dokument dient als kompakte Startgrundlage für das nächste Chatfenster, damit Harbor kontrolliert weitergeführt wird, ohne Scope-Drift oder unklare Arbeitsweise.

---

## Repo / Arbeitskontext

- **Repo:** `https://github.com/andreaskeis77/harbor`
- **Lokaler Pfad:** `C:\projekte\Harbor`
- **Aktueller Hauptzweig:** `main`
- **Release:** `v0.1.0-alpha`

---

## Sauber abgeschlossener Stand

Folgende Schritte sind inhaltlich umgesetzt und nacheinander integriert worden:

### T1.7B — Search Result Candidate Baseline
- `SearchResultCandidate` Registry
- Migration `20260408_0007`
- API-Routen
- Tests
- Smoke-Slice

### T1.8 — Candidate → Review Queue
- Candidate-Promotion in die Review Queue
- Review Queue erweitert um Candidate-/Run-Bezug
- Tests + Smoke

### T1.9 — Review Queue → Source / ProjectSource
- Review-Queue-Item kann zu `Source` + `ProjectSource` promoted werden
- Candidate wird auf `accepted` gesetzt
- Tests + Smoke

### T1.10 — Duplicate Guards / Idempotenz
- 409 bei doppelter Candidate→Review-Promotion
- 409 bei Review→Source-Promotion mit bereits vorhandener `canonical_url`
- Smoke für Duplicate Guards

### T1.11 — Workflow Summary / Lineage Surface
- Projektweite Summary-Zähler
- einfache Lineage Candidate → Review Queue → ProjectSource
- Smoke + Tests

### T1.12 — Docs + Runbook + Release Hygiene
- README / PROJECT_STATE / INDEX synchronisiert
- Alpha Runbook hinzugefügt
- Alpha Release Checklist hinzugefügt

### T1.13 — Release Cut
- Tag `v0.1.0-alpha`
- GitHub Release veröffentlicht

---

## Aktueller funktionaler Produktstand

Harbor hat aktuell einen funktionierenden manuellen Flow:

**Project → Search Campaign → Search Run → Search Result Candidate → Review Queue → Source / ProjectSource**

Zusätzlich vorhanden:
- Duplicate Guards
- Workflow Summary / Lineage
- Alpha Runbook
- Release Checklist

---

## Letzter bestätigter Qualitätsstand

Bestätigt im laufenden Chat:
- `quality-gates` grün
- zuletzt **27 Tests grün**
- relevante Smoke-Slices grün, u. a.:
  - `smoke-search-result-candidate-slice`
  - `smoke-candidate-review-promotion-slice`
  - `smoke-review-queue-source-promotion-slice`
  - `smoke-promotion-duplicate-guard-slice`
  - `smoke-workflow-summary-slice`

Arbeitsmuster:
- Branch → PR → Merge
- danach `main` lokal aktualisieren und erneut prüfen

---

## Wichtige Arbeitsregeln des Nutzers

Diese Punkte im neuen Chat aktiv beachten:

1. **Präzise sagen, wo etwas passiert**
   - **PowerShell**
   - **GitHub im Browser**
   - oder nur lesend / prüfend

2. **Kurz und handlungsorientiert**
   - keine überflüssigen langen Erklärungen
   - klare nächste Aktion

3. **Bei Mehrdatei-Änderungen ZIP bevorzugen**
   - ZIP mit korrekter Ordnerstruktur statt langer Inline-Patches

4. **`run-dev` nicht unnötig starten**
   - nur wenn wirklich gebraucht

5. **Kleine, saubere Bolts**
   - kein Scope-Mix
   - keine Mischänderungen über mehrere Themen

---

## Strategische Guidance

Die nächste sinnvolle Entwicklungsreihenfolge ist:

1. **T2.0 — Operator Web Shell**
2. **T2.1 — Operator Actions UI**
3. **T2.2 — UX / API Hardening**
4. **danach:** OpenAI Adapter Layer
5. **danach:** Chat Surface

Leitidee:
- zuerst **Nutzbarkeit**
- dann **Assistenz**
- dann **Chat / Automation**

---

## Nächster konkreter Schritt

### T2.0 — Operator Web Shell

Ziel:
- erste dünne Weboberfläche für den bestehenden Harbor-Backend-Flow

Scope-Vorschlag:
- Projektliste
- Projekt-Detailseite mit Workflow Summary
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

Architekturregel:
Die Web Shell darf **nur über Harbor-APIs** arbeiten.

---

## Startblock für den neuen Chat

```text
Wir setzen Harbor kontrolliert nach v0.1.0-alpha fort.

Repo:
- GitHub: https://github.com/andreaskeis77/harbor
- lokal: C:\projekte\Harbor

Aktueller Stand:
- v0.1.0-alpha ist veröffentlicht
- manueller Flow steht:
  Project -> Search Campaign -> Search Run -> Search Result Candidate -> Review Queue -> Source / ProjectSource
- Duplicate Guards und Workflow Summary sind vorhanden

Wichtige Arbeitsregeln:
1. Bitte immer klar sagen, ob etwas in PowerShell oder in GitHub im Browser passiert.
2. Bitte kurze, präzise Anweisungen statt langer Erklärungen.
3. Bei mehreren Dateien bitte ZIP-Artefakte mit korrekter Ordnerstruktur bevorzugen.
4. Kein unnötiges run-dev starten.
5. Kleine, saubere Bolts. Kein Scope-Mix.

Nächster Zielschritt:
- T2.0 Operator Web Shell

Bitte zuerst den echten Repo-Stand analysieren und dann einen sauberen, kleinen Scope für T2.0 vorschlagen.
```
