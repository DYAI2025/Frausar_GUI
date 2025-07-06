# 🚀 FRAUSAR Bot v2.0 - Release Notes

## 🎉 Neue Features

### 🧲 Semantic Grabber System
Ein intelligentes System zur automatischen Verwaltung semantischer Verbindungen zwischen Markern.

#### Kernfunktionen:
- **Automatische Grabber-Erkennung**: Bei jedem neuen Marker werden ähnliche Grabber gefunden oder neue erstellt
- **Python & YAML Import**: Unterstützt jetzt beide Formate mit automatischer Erkennung
- **Grabber-Bibliothek**: Zentrale `semantic_grabber_library.yaml` für alle Grabber
- **Intelligente Ähnlichkeitsanalyse**: Findet semantisch ähnliche Marker (nicht nur Textvergleiche)

#### GUI-Erweiterungen:
- **🧲 Grabber analysieren**: Zeigt Überschneidungen und Duplikate
- **🔄 Grabber optimieren**: Führt ähnliche Grabber automatisch zusammen
- **YAML/Python Tab**: Erweitert um Python-Code-Import

### 📊 Verbesserte Import-Funktionen
- YAML-Import erkennt jetzt `semantische_grabber_id` Felder
- Python-Import extrahiert Klassen, Patterns und Grabber-IDs
- Automatische Grabber-Zuweisung bei Import

### 🤖 Automatisierung
- Grabber werden automatisch erstellt wenn keine passenden gefunden werden
- Ähnlichkeitsschwellen:
  - ≥ 85%: Merge-Vorschlag
  - ≥ 72%: Existierenden verwenden
  - < 72%: Neuen erstellen

## 📁 Neue Dateien
- `semantic_grabber_library.yaml` - Zentrale Grabber-Sammlung
- `semantic_grabber_rules.yaml` - Regelset für automatische Aktionen
- `SEMANTIC_GRABBER_FEATURES.md` - Detaillierte Dokumentation

## 🔧 Technische Verbesserungen
- Erweiterte `FRAUSARAssistant` Klasse mit Grabber-Management
- Neue Parser für Python-Code
- Ähnlichkeitsberechnung mit `difflib.SequenceMatcher`
- UUID-basierte Grabber-ID-Generierung

## 💡 Anwendungsbeispiele

### YAML mit Grabber:
```yaml
TRUST_MARKER:
  beschreibung: "Vertrauensprobleme erkennen"
  beispiele:
    - "Ich vertraue dir nicht mehr"
  semantische_grabber_id: TRUST_EROSION_SEM_a1b2
```

### Python-Marker:
```python
class BOUNDARY_MARKER:
    """Grenzüberschreitungen erkennen"""
    examples = ["Das geht zu weit"]
    semantic_grabber_id = "BOUNDARY_SEM_c3d4"
```

## 🚀 Vorteile
- **Konsistenz**: Ähnliche Marker teilen sich Grabber
- **Wartbarkeit**: Zentrale Verwaltung statt verteilter Definitionen
- **Skalierbarkeit**: Automatische Verwaltung bei wachsender Anzahl
- **Intelligenz**: Semantische statt exakter Textvergleiche

## 🐛 Bekannte Einschränkungen
- Ähnlichkeitsberechnung basiert noch auf Textvergleichen (Embeddings folgen)
- Maximal 20 Patterns pro Grabber
- Python-Parser erkennt nur einfache Pattern-Definitionen

## 📈 Nächste Schritte
- [ ] Embedding-basierte Ähnlichkeitsberechnung
- [ ] Grabber-Visualisierung (Netzwerk-Graph)
- [ ] Export/Import von Grabber-Bibliotheken
- [ ] API für externe Grabber-Nutzung

---
Version: 2.0.0  
Datum: Januar 2024  
Entwickelt mit ❤️ für bessere Marker-Verwaltung 