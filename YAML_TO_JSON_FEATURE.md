# YAML zu JSON Konvertierungs-Feature

## 🔀 Überblick

Die FRAUSAR GUI enthält jetzt eine integrierte YAML zu JSON Konvertierungs-Funktionalität, die es ermöglicht, YAML-Dateien verlustfrei in JSON-Dateien zu konvertieren.

## 📍 Wo finde ich die Funktion?

Der Button **"🔀 YAML → JSON konvertieren"** befindet sich in der rechten Spalte der GUI unter dem Abschnitt "YAML-Tools".

## 🎯 Funktionen

### 1. **Einzelne Dateien konvertieren**
- Wähle einzelne YAML-Dateien über einen Datei-Dialog aus
- Füge mehrere Dateien zur Konvertierung hinzu
- Entferne ausgewählte Dateien aus der Liste

### 2. **Ganze Ordner konvertieren**
- Konvertiere alle YAML-Dateien in einem ausgewählten Ordner
- Vordefinierte Marker-Ordner werden automatisch erkannt
- Zeigt die Anzahl der YAML-Dateien pro Ordner

### 3. **Schnellaktionen**
- **Aktuelle Datei konvertieren**: Konvertiert die aktuell ausgewählte YAML-Datei
- **Alle Marker konvertieren**: Konvertiert alle gefundenen YAML-Dateien im Projekt

## ⚙️ Optionen

- **Speicherort**: 
  - Im selben Ordner wie die YAML-Datei
  - In einem `json_out` Unterordner
  
- **JSON-Einrückung**: Wählbar von 0 bis 8 Leerzeichen

## 🔧 Technische Details

### Unterstützte YAML-Features:
- Einzelne und mehrere YAML-Dokumente (getrennt durch `---`)
- Erhaltung von Anführungszeichen
- UTF-8 Encoding
- Komplexe Datenstrukturen (Listen, Dictionaries, verschachtelte Strukturen)

### Implementierung:
- Nutzt `ruamel.yaml` für erweiterte YAML-Funktionalität (falls installiert)
- Fallback zu Standard `yaml` Modul
- Verlustfreie Konvertierung
- Fehlerbehandlung für problematische Dateien

## 📝 Beispiel-Nutzung

1. Klicke auf "🔀 YAML → JSON konvertieren"
2. Wähle einen der drei Tabs:
   - **📄 Einzelne Dateien**: Für spezifische Dateien
   - **📁 Ganze Ordner**: Für Batch-Konvertierung
   - **⚡ Schnellauswahl**: Für häufige Aktionen
3. Wähle deine Optionen (Speicherort, Einrückung)
4. Klicke auf "🚀 Konvertierung starten"
5. Nach Abschluss wird eine Zusammenfassung angezeigt

## 🎉 Vorteile

- **Integriert**: Direkt in der FRAUSAR GUI verfügbar
- **Benutzerfreundlich**: Keine Kommandozeilen-Kenntnisse erforderlich
- **Flexibel**: Verschiedene Modi für unterschiedliche Anforderungen
- **Sicher**: Originaldateien werden nicht verändert
- **Informativ**: Detaillierte Fortschritts- und Ergebnisanzeige

## 🐛 Fehlerbehebung

Falls die Konvertierung fehlschlägt:
1. Prüfe ob die YAML-Datei gültig ist
2. Stelle sicher, dass Schreibrechte im Zielordner vorhanden sind
3. Bei Encoding-Problemen wird automatisch UTF-8 verwendet

## 📚 Verwandte Funktionen

- **YAML-Struktur prüfen**: Validiert YAML-Dateien
- **YAML-Dateien zusammenführen**: Kombiniert mehrere YAML-Dateien
- **GPT-YAML generieren**: Erstellt optimierte YAML für GPT-Analyse 