# Harbor auf dem VPS + OpenAI-Key einrichten

**Einfache Anleitung in Alltagssprache.** Dieses Dokument ergänzt die technische Roadmap ([STRATEGY_ROADMAP_v0_1.md](STRATEGY_ROADMAP_v0_1.md)) um eine Version, die ohne Entwickler-Jargon lesbar ist.

Stand: 2026-04-12.

---

## Teil 1 — Der OpenAI-Key

### Worum es geht

Harbor benutzt für seine KI-Funktionen (Chat, Quellen-Vorschläge, Handbook-Entwürfe) die OpenAI-API. Dafür braucht Harbor einen **API-Key** — das ist im Grunde ein langes Passwort, das so aussieht:

```
sk-proj-AbC1234567890XyZ...
```

Mit diesem Key "loggt" sich Harbor bei OpenAI ein und bezahlt die Nutzung. Ohne Key → kein Chat, keine Vorschläge, keine LLM-Funktionen. Der Rest von Harbor (Projekte, Quellen, Review-Queue) funktioniert auch ohne.

### Kann ich mehrere Keys anlegen? Ja — sogar empfohlen.

Du hast schon einen Key für ein anderes Projekt. Das ist gut, aber **benutze ihn nicht für Harbor**. Lege einen zweiten Key nur für Harbor an. Warum?

1. **Rotation ohne Kollateralschaden.** Wenn ein Key kompromittiert wird (aus Versehen im Screenshot, versehentlich commited, etc.), widerrufst du genau den einen. Das andere Projekt läuft weiter.
2. **Kostentrennung.** Du siehst in der OpenAI-Konsole unter "Usage" pro Key, wie viel er verbraucht hat. Wenn Harbor plötzlich teuer wird, weißt du sofort, *welches* Projekt die Kosten erzeugt — nicht erst nach Detektivarbeit.
3. **Separates Limit.** Du kannst pro Key ein Budget setzen. Wenn du Harbor "nur zum Probieren" willst, gib ihm 10 €/Monat und schlaf ruhig.
4. **Saubere Audit-Trails.** Wenn OpenAI Missbrauch meldet oder du zurückverfolgen willst, welches Projekt was gemacht hat, ist das mit getrennten Keys trivial.

**Meine Empfehlung konkret**: Lege für Harbor **zwei Keys an** — einen für Entwicklung auf deinem Windows-PC und einen für den VPS (Produktion). Benenne sie sprechend.

### Keys anlegen — Schritt für Schritt

1. Gehe zu https://platform.openai.com/api-keys
2. Klicke **"Create new secret key"**
3. Gib einen sinnvollen Namen ein:
   - `harbor-dev-local` (für deinen Entwicklungs-PC)
   - `harbor-vps-prod` (für den VPS, später)
4. Optional: Scope auf "Restricted" setzen und nur die benötigten Bereiche erlauben. Für den Anfang reicht "All" mit Standard-Berechtigungen.
5. **Kopiere den Key sofort** — OpenAI zeigt ihn nur **einmal**. Wenn du das Fenster schließt, musst du einen neuen anlegen.
6. Klick **"Done"**.

### Budget setzen — wichtig, nicht optional

Bevor du den Key in Harbor einsetzt, **setze ein hartes Monatslimit** in OpenAI:

1. Gehe zu https://platform.openai.com/account/billing/limits
2. Setze **"Monthly budget"** auf einen Betrag, mit dem du im Worst-Case leben kannst. Empfehlung Anfang:
   - 20 € für reines Ausprobieren
   - 50 € für regelmäßige Nutzung
3. Setze zusätzlich **"Email alerts"** auf z.B. 80% deines Budgets — dann bekommst du eine Mail, bevor es eng wird.

Das Budget ist die eigentliche Sicherheit, nicht der Key. Selbst wenn jemand den Key klaut, kann er maximal dein Budget ausgeben.

### Wo der Key in Harbor abgelegt wird

Harbor liest den Key aus einer Datei namens `.env` (Punkt-ENV). Diese Datei:
- liegt **nicht** im Git-Repo (steht in `.gitignore`)
- wird **nicht** committed
- taucht **nicht** in Logs auf
- taucht **nicht** in API-Responses auf (Harbor meldet nur "key ist da: ja/nein")

**Auf deinem Entwicklungs-PC** (`C:\projekte\Harbor\`):

1. Im Projektordner gibt es eine Vorlage namens `.env.example`. Kopiere sie:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Öffne die neue `.env` in einem Editor (Notepad, VS Code, ...).
3. Suche die Zeile mit `HARBOR_OPENAI_API_KEY` und mach sie aktiv — also Hash-Zeichen entfernen und echten Key einsetzen:
   ```
   HARBOR_OPENAI_API_KEY=sk-proj-dein-echter-dev-key-hier
   HARBOR_OPENAI_MODEL=gpt-5
   ```
4. Speichern.
5. Harbor-Server neu starten (uvicorn killen und neu starten).
6. Im Browser `http://127.0.0.1:8000/api/v1/openai/runtime` aufrufen. Du solltest sehen:
   ```json
   {"configured": true, "api_key_present": true, "model": "gpt-5", ...}
   ```
   → Harbor sieht den Key. **Der Key selbst wird nirgendwo angezeigt** — nur `true`.

**Auf dem VPS** (später, wenn Harbor dort läuft): Gleiche Prozedur mit dem Production-Key (`harbor-vps-prod`), abgelegt in `C:\harbor\.env`. Details siehe Teil 2.

### Was darf mit dem Key passieren — was nicht

**Darf**:
- In `.env` auf deinem PC / VPS gespeichert werden.
- In einem Passwort-Manager (1Password, Bitwarden, KeePass) als Backup liegen.

**Darf nicht**:
- In Git committed werden. Niemals. Auch nicht "nur kurz zum Testen".
- Per Screenshot in Chats, Issues, Slack verschickt werden.
- In Mails, Tickets, StackOverflow-Fragen auftauchen.
- In einer unverschlüsselten Notiz auf dem Desktop liegen.

**Wenn doch mal etwas passiert** (Screenshot zu viel, versehentlich in Git gepusht):
1. **Sofort** zur https://platform.openai.com/api-keys gehen.
2. Den betroffenen Key anklicken → **Revoke**. Er ist in Sekunden tot.
3. Einen neuen Key anlegen.
4. In `.env` ersetzen, Harbor neu starten.
5. **Erst danach** aufräumen (Git-History bereinigen etc.). Die Reihenfolge ist entscheidend: Revoke first, cleanup later.

---

## Teil 2 — Harbor auf deinem Windows-VPS

### Vorneweg: wann kannst du das überhaupt machen?

Harbor läuft heute schon — auf `localhost`. Aber für einen **produktiven VPS-Einsatz** brauchst du ein paar Dinge, die Harbor derzeit noch nicht hat:

| Was fehlt | Wofür nötig | Geplant in Bolt |
|---|---|---|
| Zugangs-Token (Auth) | Ohne Login könnte jeder deine Harbor-Instanz benutzen | **D1** (Phase P4) |
| Mobile-freundliche Oberfläche | Vom Handy aus bedienbar | **D2** (Phase P4) |
| Export-Funktionen | Handbook als Markdown rausziehen | **D3** (Phase P4) |
| Postgres-Deploy-Doku | Saubere Deploy-Anleitung | **D4** (Phase P4) |
| Tastatur-Shortcuts & A11y | Komfortable Bedienung | **D5** (Phase P4) |

Bis diese Bolts (ca. 2–3 Entwicklungs-Sessions) fertig sind, kannst du Harbor auf dem VPS **nur im geschützten Modus** betreiben (siehe "Übergangs-Setup" unten). Danach kommt die richtige Produktions-Variante.

### Übergangs-Setup (jetzt sofort möglich, nicht öffentlich)

Funktioniert ab heute, solange du den VPS **nicht öffentlich ins Internet exponierst**:

**Voraussetzungen**:
- Windows Server auf dem VPS
- Python 3.11 installiert
- Git installiert
- Zugriff per RDP

**Schritte** (einmalig):
1. Per RDP auf den VPS.
2. Ordner anlegen: `C:\harbor\`
3. Repo klonen:
   ```powershell
   cd C:\
   git clone https://github.com/andreaskeis77/harbor.git harbor
   cd harbor
   ```
4. Virtuelle Umgebung:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
5. `.env` anlegen (gleicher Weg wie am Dev-PC, aber mit `harbor-vps-prod`-Key):
   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```
   Inhalt mindestens:
   ```
   HARBOR_ENVIRONMENT=prod
   HARBOR_HOST=127.0.0.1
   HARBOR_PORT=8000
   HARBOR_RELOAD=false
   HARBOR_SQLALCHEMY_DATABASE_URL=sqlite+pysqlite:///C:/harbor/var/harbor.db
   HARBOR_OPENAI_API_KEY=sk-proj-dein-vps-key-hier
   HARBOR_OPENAI_MODEL=gpt-5
   ```
6. `.env` gegen fremde Augen sperren:
   ```powershell
   icacls C:\harbor\.env /inheritance:r /grant:r "Administrators:(R)"
   ```
7. Datenbank initialisieren:
   ```powershell
   alembic upgrade head
   ```
8. Harbor starten:
   ```powershell
   .\.venv\Scripts\uvicorn.exe harbor.app:app --host 127.0.0.1 --port 8000
   ```
9. Im **VPS-Browser** `http://127.0.0.1:8000/operator/projects` aufrufen — Harbor läuft.

**Wichtige Einschränkungen** in diesem Übergangs-Modus:
- Harbor hört **nur auf localhost** (`127.0.0.1`). Von außen nicht erreichbar, auch nicht aus deinem Heimnetz.
- Du bedienst es ausschließlich per RDP-Session auf dem VPS.
- Es gibt noch keinen Login. Wenn du es öffentlich erreichbar machst, ohne Auth-Bolt D1, dann kann **jeder** im Internet deine Projekte und deinen OpenAI-Key-Verbrauch sehen/missbrauchen. **Nicht machen.**

### Produktiv-Setup (nach Phase P4)

Wenn die D-Bolts gelandet sind, sieht das Deployment so aus:

**Komponenten auf dem VPS**:
- Harbor (Python, uvicorn) → läuft als **Windows-Dienst**, startet automatisch nach Reboot
- Postgres → statt SQLite, robuster für Produktion
- Caddy (oder IIS) → **HTTPS-Terminierung**, automatisches Let's-Encrypt-Zertifikat, Weiterleitung `https://harbor.deine-domain → 127.0.0.1:8000`
- Windows Task Scheduler → ruft regelmäßig `POST /scheduler/tick` auf (die Harbor-Automation ist extern getriggert)
- Tägliches `pg_dump` → Backup nach `C:\harbor\backups\`, 14 Tage aufgehoben

**Ablauf pro Release**:

Wenn es ein neues Harbor-Release gibt (`v0.2.0`, `v0.3.0`, ...), machst du auf dem VPS:

```powershell
cd C:\harbor
git fetch --tags
git checkout v0.2.0
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
Restart-Service Harbor
# Prüfen ob alles läuft:
Invoke-WebRequest https://harbor.deine-domain/healthz
```

Das ist die gesamte Deploy-Prozedur. Kein Docker-Cluster, kein Kubernetes, kein CI/CD-System. Ein Git-Checkout, ein DB-Upgrade, ein Neustart.

### Release-Strategie — wie Versionen auf den VPS kommen

Wir arbeiten in **Release-Ankern**:

| Version | Wann | Was drin |
|---|---|---|
| **v0.2.0** | Nach Phase P1 | Quellen-Inhalte werden gefetched; Scheduler läuft autonom |
| **v0.3.0** | Nach Phase P2 | Bleibt nutzbar bei vielen Zeilen; Dashboard; Suche |
| **v0.4.0** | Nach Phase P3 | KI-Funktionen erweitert (Quellen-Vorschläge, Handbook-Entwurf automatisch) |
| **v1.0.0-beta** | Nach Phase P4 | Alles VPS-tauglich: Auth, Mobile, Export |
| **v1.0.0** | Nach Beta-Burn-in auf VPS | Erste stabile Produktiv-Version |

**Meine Empfehlung für dich**: VPS-Deployment erst nach **v1.0.0-beta** produktiv nutzen. Bis dahin nur im Übergangs-Modus (nicht öffentlich). So läufst du nicht Gefahr, dass jemand deinen OpenAI-Key über eine ungeschützte Harbor-Instanz leerbrennt.

### Was kostet das?

- **OpenAI**: dein Monatslimit, siehe oben. Realistisch 5–30 €/Monat für Einzelnutzer.
- **VPS**: hast du schon.
- **Domain + HTTPS**: Domain ca. 10 €/Jahr, HTTPS gratis via Caddy + Let's Encrypt.
- **Harbor**: open source, kein Lizenzkosten.

Gesamt also: OpenAI-Verbrauch + Domain-Registrierung. Keine laufenden Dienst-Kosten.

---

## Kurz-Checkliste

### Jetzt (heute)
- [ ] Auf platform.openai.com einen Key `harbor-dev-local` anlegen.
- [ ] Monatliches Budget in OpenAI setzen (z.B. 20 €).
- [ ] `.env` auf deinem Dev-PC anlegen, Key eintragen.
- [ ] Harbor neu starten, unter `/api/v1/openai/runtime` prüfen, dass `configured: true` steht.
- [ ] Im Chat (`/chat`) einen Turn senden — das ist der End-to-End-Test.

### Wenn P4 fertig ist (später)
- [ ] Zweiten Key `harbor-vps-prod` anlegen.
- [ ] VPS vorbereiten (Python, Postgres, Caddy).
- [ ] Harbor als Windows-Dienst einrichten.
- [ ] HTTPS + Domain konfigurieren.
- [ ] Erstes Tag-Release (`v1.0.0-beta`) deployen.
- [ ] `/healthz` aus dem Internet prüfen — grün? Dann läuft es.

---

## Fragen, die ich dir beantworten kann

Wenn etwas unklar bleibt, frag einfach. Typische Stolpersteine die ich sofort auflösen kann:
- "Mein Key klappt nicht, was prüfe ich?" → `/api/v1/openai/runtime` zeigt dir `configured: false` oder `true`.
- "Wie sehe ich, wie viel der Key verbraucht hat?" → OpenAI-Konsole → Usage → Filter nach Key-Name.
- "Darf ich denselben VPS für andere Dinge nutzen?" → ja, Harbor bindet nur Port 8000 (umkonfigurierbar).
- "Was passiert, wenn OpenAI mal down ist?" → Harbor-Chat gibt Fehlermeldung, der Rest (Projekte, Quellen) funktioniert weiter.
