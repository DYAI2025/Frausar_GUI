# MarkerEngine API - Version 1.0

## 1. Übersicht & Zielsetzung

Willkommen bei der MarkerEngine API!

Dieses System ist das Herzstück der Marker-Analyse-Plattform. Es stellt eine programmierbare Schnittstelle (API) zur Verfügung, um Texte (wie Chats, Transkripte etc.) auf tiefgehende Kommunikationsmuster zu analysieren.

Die Kernidee ist, nicht nur einzelne Wörter zu finden, sondern übergeordnete Muster – sogenannte **"Marker"** – zu erkennen, zu gewichten und deren Entwicklung über die Zeit zu verfolgen.

Diese API ist so konzipiert, dass sie als zentrales Backend für verschiedenste Anwendungen dienen kann, z.B.:
- Eine **Chrome Extension**, die Webseiteninhalte analysiert.
- **Mobile Apps** (iOS/Android) für die Analyse von Chatverläufen.
- **Desktop-Anwendungen** (Mac/Windows) für professionelle Anwender.
- **B2B-Integrationen**, die die Analyse-Logik in eigene Produkte einbetten.

---

## 2. Architektur & Konzept: Die "Analyse-Profile"

Die größte Stärke dieser API ist ihre Flexibilität. Anstatt einer starren Analyse-Logik verwenden wir ein System von **"Analyse-Profilen"**.

- **`templates/*.yaml`**: Dies sind die Grundrisse oder Schablonen für verschiedene Analyse-Typen (z.B. eine Vorlage zur Analyse von Lücken in der Kommunikation, eine andere zur Analyse von Bedürfnissen).
- **`registry.yaml`**: Dies ist der zentrale Katalog. Er listet alle verfügbaren **Analyse-Profile** auf. Ein Profil ist wie ein "Rezept": Es nimmt sich eine Vorlage, gibt ihr einen klaren Namen (z.B. "Beziehungsanalyse bei Krisen") und legt fest, welche spezifischen Detektoren und Marker für genau diesen Anwendungsfall wichtig sind.
- **`profile_manager.py`**: Dies ist der "Bibliothekar". Er kennt die `registry.yaml` und hilft der API, schnell das richtige Profil für eine Anfrage zu finden, z.B. über Schlagworte wie "Krise" oder "Karriere".
- **`api.py`**: Das ist die eigentliche API-Anwendung. Sie nimmt Anfragen von außen entgegen, fragt den `ProfileManager`, welches Profil zu verwenden ist, und startet die Analyse.

Dieses System erlaubt es uns, sehr einfach neue Analyse-Typen hinzuzufügen, ohne den Kern-Code ändern zu müssen. Wir müssen nur ein neues Rezept in der `registry.yaml` anlegen.

---

## 3. Installation & Start

Um die API auf einem lokalen Rechner zu starten, folgen Sie diesen Schritten:

**Voraussetzung:** Python 3.9+ muss installiert sein.

**Schritt 1: Abhängigkeiten installieren**
Navigieren Sie in Ihrem Terminal in dieses Verzeichnis (`Marker_assist_bot/Schema_LOADER/`) und führen Sie den folgenden Befehl aus. Er installiert alle notwendigen Python-Pakete, die in der `requirements.txt`-Datei aufgelistet sind.

```bash
pip install -r requirements.txt
```

**Schritt 2: API-Server starten**
Führen Sie den folgenden Befehl im selben Verzeichnis aus. Er startet den `uvicorn`-Webserver, der unsere FastAPI-Anwendung ausführt.

```bash
uvicorn api:app --reload --port 8000
```
- `api:app`: Sagt uvicorn, dass es in der Datei `api.py` nach einer Variable namens `app` suchen soll.
- `--reload`: Sorgt dafür, dass der Server automatisch neu startet, wenn Sie Änderungen am Code speichern. Ideal für die Entwicklung.
- `--port 8000`: Legt fest, dass die API unter dem Port `8000` erreichbar ist.

Wenn alles geklappt hat, sehen Sie eine Ausgabe wie:
`Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`

Die API ist jetzt live und bereit, Anfragen entgegenzunehmen!

---

## 4. API-Dokumentation (Endpunkte)

Die API stellt die folgende Struktur zur Verfügung. Sie können die Endpunkte mit jedem HTTP-Client testen (z.B. `curl`, Postman, oder direkt aus Ihrer Anwendung).

**Basis-URL:** `http://127.0.0.1:8000`

### 4.1 Profile abrufen

- **Endpunkt:** `GET /api/v1/profiles`
- **Zweck:** Gibt eine Liste aller verfügbaren Analyse-Profile zurück. Dies ist ideal, um einer Benutzeroberfläche (z.B. einem Dropdown-Menü) mitzuteilen, welche Analyse-Möglichkeiten es gibt.
- **Beispiel-Antwort (`200 OK`):**
  ```json
  {
    "profiles": [
      {
        "id": "REL_CRISIS",
        "name": "Beziehungsanalyse – Krisenmanagement",
        "description": "Prüft Lücken, Rückzug und Eskalationen...",
        "focus_tags": ["relationship", "crisis"]
      }
    ]
  }
  ```

### 4.2 Analyse starten & Ergebnis abfragen

Dieser Prozess ist zweistufig, um zu verhindern, dass eine anfragende Anwendung lange auf eine Antwort warten muss.

**Schritt A: Analyse starten**

- **Endpunkt:** `POST /api/v1/analyses`
- **Zweck:** Startet eine neue Analyse für einen übergebenen Text mit einem spezifischen Profil.
- **Request-Body (JSON):**
  ```json
  {
    "profile_id": "REL_CRISIS",
    "text_content": "Ein langer Text, der hier analysiert werden soll..."
  }
  ```
- **Antwort (`202 Accepted`):** Die API bestätigt nur, dass die Aufgabe angenommen wurde und liefert eine ID zurück, unter der das Ergebnis später abgefragt werden kann.
  ```json
  {
    "status": "pending",
    "analysis_id": "GENERIERTE_UUID",
    "poll_url": "/api/v1/analyses/GENERIERTE_UUID"
  }
  ```

**Schritt B: Ergebnis abfragen**

- **Endpunkt:** `GET /api/v1/analyses/{analysis_id}`
- **Zweck:** Fragt den Status und das Ergebnis der zuvor gestarteten Analyse ab.
- **Platzhalter:** `{analysis_id}` muss durch die ID aus der vorherigen Antwort ersetzt werden.
- **Antwort (während der Verarbeitung, `200 OK`):**
  ```json
  {
    "status": "processing",
    "result": null
  }
  ```
- **Antwort (nach Fertigstellung, `200 OK`):**
  ```json
  {
    "status": "completed",
    "result": {
      "profile_used": "REL_CRISIS",
      "marker_counts": { "...": "..." },
      "drift_axis": { "...": "..." }
    }
  }
  ``` 