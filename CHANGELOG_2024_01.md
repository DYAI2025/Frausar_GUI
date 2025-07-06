# FRAUSAR GUI - Changelog Januar 2024

## Implementierte Verbesserungen

### 1. ✅ Marker-Löschfunktion
- **Neuer Button**: "🗑️ Löschen" im Marker-Content-Tab
- **Sicherheit**: Bestätigungsdialog vor dem Löschen
- **Backup**: Gelöschte Dateien werden als `.deleted_TIMESTAMP` gesichert
- **Integration**: Löschungen müssen wie andere Änderungen genehmigt werden

### 2. ✅ Analysen immer aktuell
- **Problem gelöst**: Analysen zeigten veraltete Daten
- **Lösung**: Marker werden bei jeder Analyse neu gesammelt
- **Aktualisierung**: "🔄 Aktualisieren"-Button in allen Analyse-Dialogen

### 3. ✅ Erweiterte Semantic Grabber Analyse
- **Neue Features**:
  - Zeigt Anzahl der Grabber und zugeordnete Marker
  - Tab "Ohne Grabber" listet Marker ohne Grabber-Zuordnung
  - Button "🧲 Grabber zuweisen" für manuelle Zuordnung
  - Vorschläge für neue Grabber oder Verbindungen
- **3 Tabs**: 
  1. Grabber-Details (mit Marker-Zuordnung)
  2. Marker ohne Grabber (mit Zuweisungsfunktion)
  3. Überschneidungen (Merge-Vorschläge)

### 4. ✅ Grabber Library direkt öffnen
- **Neuer Button**: "📄 Grabber Library öffnen" in der rechten Spalte
- **Funktionalität**: Öffnet `semantic_grabber_library.yaml` im Standard-Editor
- **Plattform-Support**: macOS, Windows, Linux
- **Auto-Erstellung**: Erstellt die Datei, falls sie nicht existiert

### 5. ✅ Marker-Suchfunktion
- **Suchfeld**: Über der Marker-Liste mit 🔍 Icon
- **Live-Filter**: Filtert während der Eingabe
- **Clear-Button**: "✖" zum Zurücksetzen
- **Status**: Zeigt Anzahl gefundener Marker
- **Suche**: In Marker-Namen (ohne Icon-Präfixe)

### 6. 🚧 Erweiterte Struktur-Analyse (teilweise implementiert)
- **Geplant**: Löschfunktion in der Analyse für Marker ohne Beispiele
- **Geplant**: Duplikat-Erkennung
- **Geplant**: Kategorien-Übersicht mit Prozentangaben

## Zusätzliche Verbesserungen

### Benutzerfreundlichkeit
- Alle Dialoge haben "🔄 Aktualisieren"-Buttons
- Bessere Fehlerbehandlung mit aussagekräftigen Meldungen
- Konsistente Icon-Verwendung für bessere Übersicht

### Performance
- Marker werden nur bei Bedarf neu geladen
- Filter arbeitet effizient ohne komplette Neuladezyklen

## Bekannte Probleme
- Die Struktur-Analyse könnte noch erweitert werden um:
  - Direkte Löschfunktion für problematische Marker
  - Bessere Duplikat-Erkennung
  - Export-Funktionen für Analysen

## Nächste Schritte
1. Struktur-Analyse mit Löschfunktion erweitern
2. Export-Funktionen für alle Analysen
3. Batch-Operationen (mehrere Marker gleichzeitig bearbeiten)
4. Erweiterte Suche mit Regex-Support
5. Marker-Vorlagen für häufige Typen 