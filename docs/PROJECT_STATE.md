# PROJECT_STATE – Harbor

Stand: 2026-04-06 (Europe/Berlin)

## 1. Aktueller Status

**Aktuelle Phase:** A0 abgeschlossen und akzeptiert  
**Nächster empfohlener Schritt:** T1.0 – Repository Scaffold and Technical Bootstrap Implementation

Harbor hat die dokumentations- und definitionsgetriebene A0-Phase inhaltlich abgeschlossen. Die Produkt- und Architekturgrundlagen gelten nun als belastbare Startlinie für den technischen Einstieg.

## 2. Was als A0-Baseline akzeptiert ist

Die A0-Baseline umfasst mindestens:

- Produkt-Scope
- Domain Model
- User Stories
- Functional Requirements
- Handbook-Spezifikation
- Blueprint-Modell
- Workflow-Modell
- System Architecture
- Runtime Boundaries
- Technical Bootstrap
- Repository Scaffolding
- Masterplan- und Handoff-Governance
- A0-Konsolidierung und Acceptance-Steuerung

## 3. Bedeutung der Abnahme

Die A0-Abnahme bedeutet ausdrücklich nicht, dass Harbor bereits technisch implementiert ist.

Die Abnahme bedeutet:

- die Richtung ist fachlich und architektonisch definiert,
- die zentralen Modellierungsentscheidungen sind getroffen,
- die nächsten technischen Schritte sind eingegrenzt,
- T1.0 kann kontrolliert gestartet werden, ohne dass wesentliche Produktgrundlagen fehlen.

## 4. Was jetzt nicht passieren soll

Mit diesem Stand soll **nicht**:

- weiterer unstrukturierter Konzepttext produziert werden,
- Scope und Implementierung vermischt werden,
- die Produktgrenzen stillschweigend geändert werden,
- T1.0 ohne Bezug auf die akzeptierte A0-Baseline gestartet werden.

## 5. T1.0-Zielbild

T1.0 soll bewusst klein und technisch sauber bleiben.

T1.0 soll mindestens vorbereiten oder liefern:

- grundlegendes Repo-Scaffold
- Python-Projektstruktur
- minimale App-Struktur
- Konfigurationsoberfläche
- Health-Endpoint
- lokale Startfähigkeit
- erste Tests
- erste Quality-Gate-Basis

## 6. Risikohinweise

Weiterhin zu beachten:

- Es darf keine globale Wissenssuppe entstehen; Projektpartitionierung bleibt Kernprinzip.
- GPT und Web müssen dauerhaft auf dasselbe Backend zeigen.
- Quellen, Snapshots, Evidenz, Analyse und Review dürfen nicht vermischt werden.
- Monitoring und Agenten bleiben spätere Ausbaustufen, nicht T1.0-Kern.

## 7. Nächste Arbeitslogik

Der nächste saubere Übergang ist:

1. A0-Abnahme dokumentiert und gepusht
2. T1.0-Implementierungs-Bolt vorbereiten
3. lokales Scaffold implementieren
4. Health/Tests/Gates prüfen
5. erst danach weitere fachliche Tiefe in Runtime umsetzen
