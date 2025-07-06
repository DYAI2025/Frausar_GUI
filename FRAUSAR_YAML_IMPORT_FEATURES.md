# 🚀 FRAUSAR GUI - YAML Import Features

## Neue Features für intelligenten Marker-Import

### 1. 📋 YAML Import
Beim Erstellen neuer Marker gibt es jetzt drei Tabs:

**Tab 1: Formular** (klassisch)
- Wie bisher: Name, Beschreibung, Beispiele einzeln eingeben

**Tab 2: YAML Import** (NEU!)
- Füge YAML-formatierten Marker direkt ein
- System erkennt automatisch:
  - Marker-Name
  - Beschreibung
  - Beispiele
- Perfekt wenn du bereits strukturierte Marker hast

**Tab 3: Multi-Import** (NEU!)
- Mehrere Marker auf einmal importieren
- Trenne Marker durch Leerzeile oder `---`
- Erstellt automatisch einzelne Dateien für jeden Marker

### Beispiel YAML-Format:
```yaml
BOUNDARY_SETTING_MARKER:
  beschreibung: >
    Klarheit und Kommunikation eigener Grenzen, Selbstschutz.
  beispiele:
    - "Hey, ich schaffe es heute Abend nicht."
    - "Ich möchte über dieses Thema jetzt nicht sprechen."
    - "Das geht mir zu schnell. Ich brauche mehr Zeit."
```

### Verwendung:

1. **Einzelner YAML-Import:**
   - Klicke "➕ Neu"
   - Wähle Tab "📋 YAML Import"
   - Füge deinen YAML-Code ein
   - Klicke "📁 Aus YAML erstellen"

2. **Multi-Import:**
   - Klicke "➕ Neu"
   - Wähle Tab "📚 Multi-Import"
   - Füge mehrere YAML-Marker ein (getrennt durch Leerzeile)
   - Klicke "📚 Alle erstellen"

### Vorteile:
- ⚡ Schneller Import vorstrukturierter Marker
- 🎯 Keine manuelle Eingabe nötig
- 📚 Batch-Import mehrerer Marker
- 🔍 Intelligente Erkennung der Struktur

Die GUI erkennt automatisch das YAML-Format und extrahiert alle relevanten Informationen! 