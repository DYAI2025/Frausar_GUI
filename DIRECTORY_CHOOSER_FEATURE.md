# Verzeichnisauswahl-Feature

## 📂 Überblick

Die FRAUSAR GUI enthält jetzt eine flexible Verzeichnisauswahl-Funktion, die es ermöglicht, beliebige Ordner mit Marker-Dateien zu laden und zu bearbeiten.

## 📍 Wo finde ich die Funktion?

Der Button **"📂 Verzeichnis wählen"** befindet sich oben links in der Marker-Liste, direkt über dem Suchfeld.

## 🎯 Funktionen

### Hauptfunktionen:
- **Flexibles Arbeitsverzeichnis**: Wähle beliebige Ordner auf deinem System
- **Automatische Dateierkennung**: Lädt automatisch alle unterstützten Dateitypen
- **Unterordner-Support**: Scannt auch alle direkten Unterordner
- **Pfadanzeige**: Zeigt das aktuelle Verzeichnis über dem Button an

### Unterstützte Dateitypen:
- 📄 **TXT** - Textdateien
- 📊 **YAML/YML** - YAML-Dateien  
- 📊 **JSON** - JSON-Dateien
- 📊 **CSV** - CSV-Dateien
- 🐍 **PY** - Python-Skripte

## 📝 Verwendung

1. **Klicke auf "📂 Verzeichnis wählen"**
   - Ein Datei-Dialog öffnet sich
   
2. **Wähle einen Ordner**
   - Navigiere zu dem gewünschten Ordner
   - Klicke auf "Ordner auswählen"
   
3. **Automatisches Laden**
   - Alle unterstützten Dateien werden geladen
   - Die Marker-Liste wird aktualisiert
   - Eine Bestätigung erscheint im Chat

## 🔧 Technische Details

### Verzeichnis-Struktur:
```
Gewähltes Verzeichnis/
├── datei1.yaml
├── datei2.txt
├── datei3.json
├── datei4.csv
├── script.py
└── Unterordner/
    ├── weitere_datei.yaml
    └── noch_eine.txt
```

### Automatische Anpassungen:
- Alle Pfade werden relativ zum gewählten Verzeichnis aufgelöst
- Unterordner werden automatisch gescannt
- Versteckte Ordner (beginnend mit `.`) werden ignoriert

## 🎉 Vorteile

- **Flexibilität**: Arbeite mit beliebigen Verzeichnissen
- **Keine Pfad-Probleme**: Wähle Verzeichnisse visuell aus
- **Projekt-übergreifend**: Nutze die GUI für verschiedene Projekte
- **Einfache Bedienung**: Ein Klick genügt

## 💡 Tipps

1. **Standard-Verzeichnis**: Beim Start wird automatisch `../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01` geladen
2. **Relative Pfade**: Die GUI merkt sich das gewählte Verzeichnis für die aktuelle Sitzung
3. **Alle Funktionen verfügbar**: Alle GUI-Funktionen arbeiten mit dem gewählten Verzeichnis

## 🚨 Wichtige Hinweise

- **Backup**: Erstelle Backups wichtiger Dateien vor Bearbeitungen
- **Schreibrechte**: Stelle sicher, dass du Schreibrechte im gewählten Verzeichnis hast
- **Große Verzeichnisse**: Bei sehr vielen Dateien kann das Laden einen Moment dauern 