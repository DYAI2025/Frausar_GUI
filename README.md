# MARSAP - Marker Analysis & Recognition System for Adaptive Patterns

## 🔍 Semantisch-psychologischer Resonanz- und Manipulations-Detektor

MARSAP ist ein fortschrittliches System zur Erkennung psychologischer Kommunikationsmuster, manipulativer Techniken und emotionaler Dynamiken in Texten. Es nutzt einen umfangreichen Katalog von 72+ Markern zur Live-Analyse von Kommunikationsmustern.

## 🎯 Features

- **72 psychologische Marker** für Manipulation, emotionale Dynamik und Beziehungsmuster
- **Vierstufiges Risk-Level-System** (🟢 Grün, 🟡 Gelb, 🟠 Blinkend, 🔴 Rot)
- **Mehrere Interfaces**: CLI, Python-API und REST-API
- **Real-time Analyse** für Chat-Monitoring
- **Batch-Processing** für Archiv-Scans
- **Modulare Erweiterbarkeit** für neue Marker

## 🚀 Quick Start

```bash
# 1. Repository klonen
git clone https://github.com/Narion2025/MARSAP.git
cd MARSAP

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. System testen
python3 marker_matcher.py

# 4. Text analysieren
python3 marker_cli.py -t "Das hast du dir nur eingebildet."
```

## 💻 Verwendung

### Command Line Interface
```bash
# Einzeltext analysieren
python3 marker_cli.py -t "Zu analysierender Text"

# Datei analysieren
python3 marker_cli.py -f chat_log.txt

# Alle Marker auflisten
python3 marker_cli.py --list-markers
```

### Python API
```python
from marker_matcher import MarkerMatcher

matcher = MarkerMatcher()
result = matcher.analyze_text("Dein Text hier...")
print(f"Risk-Level: {result.risk_level}")
```

### REST API
```bash
# Server starten
python3 marker_api.py

# Text via API analysieren
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Zu analysierender Text"}'
```

## 📊 Erkannte Muster

### Manipulationstechniken
- **GASLIGHTING** - Realitätsverzerrung und Selbstzweifel
- **LOVE_BOMBING** - Überwältigende Zuneigung als Manipulation
- **BLAME_SHIFT** - Verantwortung auf andere verschieben
- **SILENT_TREATMENT** - Schweigen als Bestrafung

### Emotionale Dynamiken
- **AMBIVALENCE** - Hin- und hergerissen zwischen Optionen
- **ESCALATION** - Konflikteskalation
- **AROUSAL** - Emotionale Erregung

### Beziehungsmuster
- **DRAMA_TRIANGLE** - Opfer-Täter-Retter-Dynamik
- **ISOLATION** - Soziale Isolation fördern
- **COMPARISON_GHOST** - Vergleiche mit Ex-Partnern

## 📁 Projektstruktur

```
MARSAP/
├── README.md                     # Dieses File
├── requirements.txt              # Python Dependencies
├── marker_master_export.yaml     # Zentrale Marker-Datenbank
├── marker_master_export.json     # JSON-Version der Marker
├── create_marker_master.py       # Marker-Konsolidierungs-Skript
├── marker_matcher.py             # Core-Engine für Pattern-Matching
├── marker_api.py                 # REST-API Server
├── marker_cli.py                 # Command-Line Interface
├── MARKER_SYSTEM_README.md       # Detaillierte Systemdokumentation
└── MARKER_MASTER_README.md       # Marker-spezifische Dokumentation
```

## 🔧 Erweiterte Nutzung

Siehe [MARKER_SYSTEM_README.md](MARKER_SYSTEM_README.md) für:
- Detaillierte API-Dokumentation
- Erweiterung mit neuen Markern
- Integration in bestehende Systeme
- Troubleshooting

## 📈 Statistiken

Das System enthält aktuell:
- 72 eindeutige Marker
- 1000+ Beispiel-Patterns
- 20 semantische Detektoren
- 4 Risiko-Stufen

## 🤝 Beitragen

Neue Marker, Verbesserungen und Fehlerkorrekturen sind willkommen!

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/neue-marker`)
3. Committe deine Änderungen (`git commit -am 'Füge neue Marker hinzu'`)
4. Push zum Branch (`git push origin feature/neue-marker`)
5. Erstelle einen Pull Request

## ⚠️ Disclaimer

MARSAP ist ein Hilfsmittel zur Textanalyse und ersetzt keine professionelle psychologische Beratung. Die Ergebnisse sollten immer im Kontext interpretiert werden.

## 📝 Lizenz

Dieses System ist für Forschungs- und Bildungszwecke gedacht. Bei kommerzieller Nutzung bitte Rücksprache halten.

---

**MARSAP** - *Marker Analysis & Recognition System for Adaptive Patterns*  
Entwickelt für die semantisch-psychologische Kommunikationsanalyse 