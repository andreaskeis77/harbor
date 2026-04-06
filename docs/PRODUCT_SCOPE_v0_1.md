# Harbor – Product Scope v0.1

Status: Draft zur Scope- und Definitionsphase  
Produktname: **Harbor**  
Systemrolle: Projektbasiertes Recherche-, Wissens- und Monitoring-System  
System of Record: **Postgres**

---

## 1. Zweck dieses Dokuments

Dieses Dokument definiert den fachlichen Scope von Harbor in einer frühen, aber belastbaren Form.

Harbor ist **kein gewöhnliches RAG-Projekt** im Sinne einer reinen Chat-Oberfläche mit Vektorsuche. Harbor ist ein **projektpartitioniertes Research System** mit versionierter Projektdefinition, kontrollierter Quellenaufnahme, nachvollziehbarer Evidenzspeicherung, Wiederaufnahmefähigkeit und späterer Monitoring-/Agentenfähigkeit.

Dieses Scope-Dokument dient als Grundlage für:

- Architekturentscheidungen
- User Stories
- Domänenmodell
- funktionale Anforderungen
- Nicht-Ziele
- Engineering Manifest
- spätere Runtime- und Betriebsentscheidungen

---

## 2. Produktziel

Harbor soll es ermöglichen, zu beliebigen Themen **sauber getrennte Rechercheprojekte** anzulegen, weiterzuführen, zu reviewen, zu aktualisieren und später gezielt wiederzuverwenden.

Jedes Projekt soll:

- eine eigene fachliche Definition besitzen,
- einen eigenen versionierten Research Scope besitzen,
- eigene Quellen und Evidenzen verwalten,
- eigene Analysen und Research Gaps enthalten,
- separat weiterbearbeitet, reviewed oder archiviert werden können,
- später als Vorlage oder teilweise als Blueprint für neue Projekte dienen können.

Harbor soll sowohl für **kleine, kurze Recherchen** als auch für **größere, länger laufende Themenräume** geeignet sein.

---

## 3. Produktdefinition in einem Satz

**Harbor ist ein projektpartitioniertes Recherche- und Monitoring-System, in dem jedes Projekt einen eigenständigen, versionierten Wissens- und Arbeitsraum bildet und über Website sowie Custom GPT mit demselben Backend bearbeitet werden kann.**

---

## 4. Kernprinzipien

### 4.1 Projektpartitionierung ist ein Architekturprinzip

Harbor darf keine globale Wissenssuppe erzeugen.

Jedes Projekt ist ein eigener Recherche-Raum mit:

- eigenem Scope
- eigener Historie
- eigenen Quellenzuordnungen
- eigenem Review-Status
- eigenem Analysekontext

### 4.2 Das Backend ist kanonisch

Website und Custom GPT müssen dasselbe Backend und denselben Projektzustand nutzen.

Es darf keine getrennte Logik geben, bei der GPT und Weboberfläche unterschiedliche Wahrheiten sehen.

### 4.3 Der Chat ist nicht das System of Record

Der Gesprächsverlauf ist nur eine Interaktionsschicht.

Der fachliche Zustand liegt in Harbor selbst:

- Projektdefinition
- Quellenbestand
- Evidenzen
- Reviews
- Analysen
- Monitoring-Status

### 4.4 Quellen, Evidenz und Analyse sind getrennte Ebenen

Harbor muss sauber unterscheiden zwischen:

- Quelle
- Snapshot / Artefakt
- Extrakt / Chunk / Claim
- Analyse / Synthese
- Entscheidung / Review

KI-generierte Texte dürfen nicht implizit den gleichen Status wie Primärquellen erhalten.

### 4.5 Wiederaufnahmefähigkeit ist Pflicht

Ein Projekt muss jederzeit später wieder geöffnet und verständlich fortgesetzt werden können.

Harbor muss daher jederzeit beantworten können:

- Was ist der aktuelle Scope?
- Welche Quellen gibt es?
- Was ist neu seit dem letzten Review?
- Was ist offen?
- Was ist die nächste sinnvolle Aktion?

### 4.6 Wiederverwendung ist explizit, nicht implizit

Archivierte Projekte können als Blueprints dienen.

Blueprint-Nutzung erfolgt zunächst als **expliziter Import-Snapshot**, nicht als verdeckte Live-Vererbung.

---

## 5. Zielnutzer und Nutzungskontext

Primärer Nutzer ist zunächst Andreas als Einzelanwender.

Typische Nutzung:

- neue Rechercheprojekte definieren
- projektweise Quellen sammeln
- projektweise Scope und Fragestellungen verfeinern
- Ergebnisse über Website oder Custom GPT ansehen und weiterentwickeln
- bestehende Projekte später wieder aufnehmen
- Quellen-Updates gezielt anstoßen
- abgeschlossene Projekte als Vorlagen wiederverwenden

Harbor wird initial auf einem VPS betrieben und soll browserbasiert sowie über Custom GPT nutzbar sein.

---

## 6. Projekttypen

Harbor soll mindestens drei Projektmodi unterstützen.

### 6.1 Quick Project

Charakteristik:

- kurze Recherche
- überschaubarer Scope
- wenige Unterfragen
- begrenzte Quellenanzahl
- meist kein langfristiges Monitoring

### 6.2 Standard Project

Charakteristik:

- mehrere Unterfragen
- strukturierter Scope
- mehrere Suchläufe und Reviews
- Updates sinnvoll

### 6.3 Deep Project

Charakteristik:

- langfristiger Themenraum
- viele Quellen und Teildomänen
- wiederholte Aktualisierung
- hoher Analyse- und Review-Anteil
- spätere Monitoring-/Agentenfähigkeit besonders relevant

---

## 7. Projektlebenszyklus

Jedes Projekt durchläuft fachlich einen Lebenszyklus.

### 7.1 Draft

- Projektidee existiert
- Scope ist noch unvollständig
- Handbook ist in Arbeit

### 7.2 Active Research

- Scope ist arbeitsfähig
- Quellen werden gesammelt
- Analysen und Gaps entstehen

### 7.3 Review

- Projekt wird bewusst geprüft
- Scope, Quellenlage, Aktualität und Gaps werden bewertet
- Änderungen seit letztem Stand werden gesichtet

### 7.4 Archived

- Projekt ist fachlich abgeschlossen oder pausiert
- Inhalte bleiben vollständig erhalten
- Projekt ist nicht mehr im aktiven Arbeitsfokus

### 7.5 Blueprint-eligible / Blueprint

- archiviertes Projekt kann gezielt als Vorlage markiert werden
- es wird nicht automatisch Blueprint
- Eignung und Wiederverwendungswert werden bewusst festgehalten

---

## 8. Kernobjekte des fachlichen Modells

Harbor soll mindestens folgende fachliche Kernobjekte kennen.

### 8.1 Project

Das zentrale Rechercheobjekt.

### 8.2 Research Handbook

Das Herzstück eines Projekts.

### 8.3 Handbook Version

Versionierter Stand des Handbooks mit Änderungsverlauf.

### 8.4 Research Question

Einzelne Haupt- oder Unterfragen innerhalb eines Projekts.

### 8.5 Source

Eine logisch identifizierte Quelle.

### 8.6 ProjectSource

Projektbezogene Einordnung einer Quelle.

### 8.7 Source Snapshot / Artifact

Gespeicherter Zustand einer Quelle zu einem Zeitpunkt.

### 8.8 Extract / Chunk / Claim

Such- und analysefähige Informationseinheiten aus einer Quelle.

### 8.9 Analysis Artifact

Abgeleitete Ergebnisse, Vergleiche, Zusammenfassungen oder Entscheidungen.

### 8.10 Research Gap

Explizite Wissenslücke oder unbeantwortete Frage.

### 8.11 Search Campaign

Ein gezielter Suchlauf innerhalb eines Projekts.

### 8.12 Refresh Run

Ein Lauf, der bekannte Quellen erneut auf Änderungen prüft.

### 8.13 Review Decision

Dokumentierte Entscheidung zur Einordnung von Quellen, Kandidaten, Änderungen oder Analysen.

### 8.14 Blueprint

Bewusst freigegebene Vorlage auf Basis eines archivierten Projekts.

---

## 9. Research Handbook als Herzstück

Der Research Handbook ist das zentrale Steuerungsobjekt pro Projekt.

Ein vollständiger Handbook soll mindestens folgende Abschnitte enthalten:

1. Projektziel
2. Kurzbeschreibung des Rechercheanliegens
3. Zentrale Fragestellung
4. Unterfragen
5. In-Scope
6. Out-of-Scope
7. Bewertungs- und Entscheidungskriterien
8. Prioritäten / Reihenfolge der Recherche
9. Relevante Quelltypen
10. Zu meidende oder niedrig priorisierte Quelltypen
11. Suchstrategie / Suchbegriffe / Heuristiken
12. Wichtige Annahmen / Hypothesen
13. Offene Fragen / Research Gaps
14. Research Operations Policy
15. Änderungshistorie / Versionshinweise

Der Handbook muss versioniert und diffbar sein.

---

## 10. Quellenmodell und Evidenzmodell

Harbor soll nicht nur URLs sammeln, sondern nachvollziehbare Evidenzräume pro Projekt aufbauen.

Quellen sollen mindestens klassifizierbar sein nach:

- Quellentyp
- Relevanz
- Vertrauensniveau
- Zugriffsmethode
- Auth-Bedarf
- Aktualitätscharakter
- Projektkontext
- Review-Status

Harbor soll, wo sinnvoll, nicht nur auf Live-Quellen zeigen, sondern konkrete Snapshots oder Artefakte speichern.

---

## 11. Projekttrennung und Wiederverwendung

### 11.1 Strikte Projekttrennung

Harbor muss sicherstellen, dass Projekte fachlich sauber getrennt bleiben.

### 11.2 Technische Wiederverwendung erlaubt

Intern darf Harbor Artefakte, Snapshots oder Deduplizierungsmechanismen technisch wiederverwenden, wenn das fachliche Modell sauber getrennt bleibt.

### 11.3 Blueprint-Prinzip

Archivierte Projekte können bewusst als Blueprint markiert werden.

### 11.4 Blueprint-Nutzung in v1

In v1 soll Blueprint-Nutzung so funktionieren:

- Ein archiviertes Projekt kann als Vorlage ausgewählt werden.
- Ein neues Projekt wird aus diesem Stand erzeugt.
- Das neue Projekt ist danach eigenständig.
- Harbor speichert einen Herkunftsverweis auf Blueprint und Version.

### 11.5 Partielle Wiederverwendung

Harbor soll perspektivisch auch Teilaspekte aus alten Projekten wiederverwendbar machen.

---

## 12. Review- und Resume-Modell

Harbor soll pro Projekt zwei zentrale Arbeitsmodi unterstützen.

### 12.1 Review Mode

Review soll unter anderem sichtbar machen:

- neue Quellen seit letztem Review
- geänderte Quellen
- offene Gaps
- unreviewte Kandidaten
- veraltete Analysen

### 12.2 Resume Mode

Resume soll mindestens zeigen:

- aktueller Scope
- letzter signifikanter Stand
- Änderungen seit dem letzten Arbeitsstand
- offene Punkte
- nächste sinnvolle Aktionen

---

## 13. Such-, Refresh- und Monitoring-Modell

Harbor soll Recherche nicht nur einmalig, sondern iterativ unterstützen.

### 13.1 Initial Search

- neue Quellen finden
- erste Evidenzbasis aufbauen
- Projektgrundlage schaffen

### 13.2 Refresh

- bekannte Quellen erneut prüfen
- Änderungen oder Updates feststellen
- veraltete Inhalte markieren

### 13.3 Discovery

- neue, bislang unbekannte Quellen identifizieren
- Suchraum erweitern

### 13.4 Monitoring

- projektbezogene Beobachtung über Zeit
- regelmäßige Prüfung auf Änderungen oder neue Quellen

### 13.5 V1-Entscheidung

In v1 muss Harbor mindestens manuell ausgelöste Initial Search und Refresh unterstützen.

### 13.6 V2/V3-Perspektive

Später sollen hinzukommen:

- geplante Refresh-Zyklen
- Discovery-Kampagnen
- agentische Monitoring-Läufe
- Alerting
- Delta- und Kandidaten-Queues

---

## 14. Agentenperspektive (nicht Kern von v1)

Harbor soll perspektivisch agentische Recherchestrategien unterstützen.

Wichtig ist dabei:

- Agenten schreiben nicht ungeprüft in den kanonischen Wissensbestand.
- Agenten erzeugen Kandidaten, Deltas, Hinweise und Review-Arbeit.
- Menschliche oder regelbasierte Review-Schritte bleiben Teil des Systems.

---

## 15. Bedienoberflächen

Harbor soll mindestens zwei primäre Bedienoberflächen erhalten.

### 15.1 Weboberfläche

Die Website dient als operativer Arbeitsraum.

### 15.2 Custom GPT

Der Custom GPT dient als natürliche Interaktionsoberfläche mit Harbor.

Website und GPT müssen mit demselben Projektzustand arbeiten.

---

## 16. Kernfunktionen für v1

Harbor v1 soll mindestens folgende Funktionen enthalten:

- Projekt anlegen, auswählen, archivieren, als Blueprint markieren
- Scope/Handbook erzeugen, anzeigen, bearbeiten, versionieren
- Quellen projektbezogen aufnehmen und klassifizieren
- Snapshot/Artefakt speichern
- projektspezifische Suche auslösen
- bekannte Quellen refreshen
- Analysen und Gaps speichern
- Änderungen seit letztem Stand anzeigen
- VPS-Betrieb, Health-Checks, Logging, Run-Historie

---

## 17. Nicht-Ziele für v1

Nicht Ziel von v1 sind insbesondere:

- Multi-User-Kollaboration mit komplexen Rollenmodellen
- aggressive autonome Langzeitagenten ohne Review-Grenzen
- vollständige Automatisierung geschützter Login-/Paywall-Inhalte
- unbegrenztes globales Wissensarchiv ohne Projektgrenzen
- ausgefeilte Live-Vererbungsmodelle zwischen Blueprints und abgeleiteten Projekten
- vollständig autonome Entscheidungsfindung ohne Evidenz- und Reviewmodell
- frühzeitige Enterprise-Features

---

## 18. Qualitätsanforderungen auf Scope-Ebene

Harbor muss fachlich folgende Qualitätseigenschaften anstreben:

- Nachvollziehbarkeit
- Wiederaufnahmefähigkeit
- Änderbarkeit
- Robustheit
- saubere Wiederverwendung

---

## 19. Offene Punkte für die nächste Iteration

Die folgenden Punkte sind als Nächstes auszuarbeiten:

1. User Stories v0.1
2. Functional Requirements v0.1
3. Domain Model v0.1
4. Research Handbook Specification v0.1
5. Blueprint Model v0.1
6. Search / Refresh / Review Workflow v0.1
7. System Architecture v0.1
8. Engineering Manifest refinement

---

## 20. Scope-Fazit

Harbor ist fachlich als **projektpartitioniertes Research Operating System** zu behandeln, nicht als bloßes Chat-RAG.

Der Fokus in v1 liegt auf:

- sauber getrennten Projekten
- versioniertem Scope/Handbook
- kontrollierter Quellen- und Evidenzverwaltung
- Review- und Resume-Fähigkeit
- Wiederverwendbarkeit archivierter Projekte als Blueprints
- gemeinsamem Backend für Website und Custom GPT
- sowie einem Design, das später Refresh, Discovery, Monitoring und Agenten sauber aufnehmen kann
