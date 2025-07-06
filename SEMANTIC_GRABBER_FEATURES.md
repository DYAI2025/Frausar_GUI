# 🧲 Semantic Grabber System - FRAUSAR Bot

## Übersicht

Das Semantic Grabber System ist eine intelligente Erweiterung des FRAUSAR Bots, die automatisch semantische Verbindungen zwischen Markern erkennt und verwaltet.

## Features

### 1. **Automatische Grabber-Erkennung**
- Bei jedem neuen Marker werden die Beispiele analysiert
- Ähnliche Grabber werden automatisch gefunden (Schwellwert: 72%)
- Neue Grabber werden bei Bedarf automatisch erstellt

### 2. **Python & YAML Support**
- Import von YAML-formatierten Markern
- Import von Python-basierten Markern
- Automatische Extraktion von:
  - Marker-Namen
  - Beschreibungen
  - Beispielen/Patterns
  - Semantic Grabber IDs

### 3. **Grabber-Verwaltung**
- **Analyse**: Überschneidungen zwischen Grabbern finden
- **Optimierung**: Ähnliche Grabber zusammenführen
- **Bibliothek**: Zentrale `semantic_grabber_library.yaml`

## Schwellwerte

| Ähnlichkeit | Aktion |
|-------------|---------|
| ≥ 85% | Merge empfohlen |
| ≥ 72% | Existierenden verwenden |
| < 72% | Neuen Grabber erstellen |

## Beispiel: YAML-Import mit Grabber

```yaml
BOUNDARY_SETTING_MARKER:
  beschreibung: >
    Erkennt wenn jemand klare Grenzen setzt
  beispiele:
    - "Das geht zu weit"
    - "Ich möchte das nicht"
    - "Bitte respektiere meine Grenze"
  semantische_grabber_id: BOUNDARY_SEM_a4f2
```

## Beispiel: Python-Import

```python
class TRUST_EROSION_MARKER:
    """
    Erkennt schleichenden Vertrauensverlust
    """
    
    examples = [
        "Ich weiß nicht mehr, ob ich dir glauben kann",
        "Du hast schon so oft versprochen...",
        "Wie soll ich dir noch vertrauen?"
    ]
    
    semantic_grabber_id = "TRUST_LOSS_SEM_9b3f"
```

## GUI-Funktionen

### 🧲 Grabber analysieren
- Zeigt alle Grabber und ihre Überschneidungen
- Identifiziert Duplikate und ähnliche Grabber
- Empfiehlt Optimierungen

### 🔄 Grabber optimieren
- Führt ähnliche Grabber zusammen
- Bereinigt die Grabber-Bibliothek
- Verbessert die Erkennungsgenauigkeit

## Automatische Aktionen

1. **Bei Marker-Erstellung**:
   - Semantic Grabber wird automatisch zugewiesen oder erstellt
   - Info wird im Chat angezeigt

2. **Bei YAML/Python-Import**:
   - Grabber-ID wird erkannt und validiert
   - Fehlende Grabber werden automatisch erstellt

3. **Bei Analyse**:
   - Überschneidungen werden identifiziert
   - Merge-Vorschläge werden generiert

## Dateien

- `semantic_grabber_library.yaml` - Zentrale Grabber-Bibliothek
- `semantic_grabber_rules.yaml` - Regelset für automatische Aktionen
- `frausar_gui.py` - Erweiterte GUI mit Grabber-Support

## Vorteile

✅ **Konsistenz**: Ähnliche Marker verwenden denselben Grabber  
✅ **Skalierbarkeit**: Automatische Verwaltung bei wachsender Marker-Anzahl  
✅ **Intelligenz**: Semantische Ähnlichkeit statt exakter Textvergleiche  
✅ **Wartbarkeit**: Zentrale Bibliothek statt verteilter Definitionen 