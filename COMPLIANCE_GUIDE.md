# 📋 Semantic Marker Framework - Compliance Guide

## Übersicht

Dieses Dokument beschreibt die Standards und Regeln für das Semantic Marker Framework. Alle Tools, Skripte und Prozesse müssen diesen Standards entsprechen.

## 🎯 Projekt-Standards

### 1. Marker-Struktur

**Format**: YAML-Dateien (`.yaml`)

**Pflichtfelder**:
```yaml
marker_name: EXAMPLE_MARKER        # ALL_CAPS + _MARKER
beschreibung: >                    # Mehrzeilige Beschreibung
  Beschreibungstext hier
beispiele:                         # Liste von Beispielen
  - "Beispiel 1"
  - "Beispiel 2"
semantische_grabber_id: EXAMPLE_SEM  # Referenz zum Grabber
```

**Naming Convention**: 
- Marker-Namen: `ALL_CAPS_MARKER` (z.B. `TRUST_EROSION_MARKER`)
- Keine Sonderzeichen außer Unterstrich
- Immer mit `_MARKER` endend

### 2. Grabber-Struktur

**Speicherort**: `semantic_grabber_library.yaml`

**Format**:
```yaml
semantic_grabbers:
  EXAMPLE_SEM:                     # Grabber-ID
    beschreibung: "Beschreibung"   # Was wird erkannt
    patterns:                      # Kern-Patterns
      - "Pattern 1"
      - "Pattern 2"
    created_from: "EXAMPLE_MARKER" # Ursprungs-Marker
    created_at: "2024-01-20T10:00:00"  # Zeitstempel
```

**Naming Convention**:
- Manuelle IDs: `ALL_CAPS_SEM` (z.B. `TRUST_EROSION_SEM`)
- Auto-generierte IDs: `AUTO_SEM_YYYYMMDD_XXXX` (z.B. `AUTO_SEM_20240120_A1B2`)

### 3. Referenzierung

- Jeder Marker MUSS eine `semantische_grabber_id` haben
- Die ID MUSS in der `semantic_grabber_library.yaml` existieren
- Keine verwaisten Referenzen erlaubt

### 4. Automatisierung

**Ähnlichkeitsschwellen**:
- ≥ 85%: Grabber sollten gemerged werden
- ≥ 72%: Existierenden Grabber verwenden
- < 72%: Neuen Grabber erstellen

**Auto-Generierung**:
- Wenn keine `semantische_grabber_id` vorhanden → automatisch erstellen
- Format: `AUTO_SEM_<datum>_<uuid>`

## 🛠️ Tools für Compliance

### 1. Compliance Checker
```bash
python3 compliance_checker.py
```
- Prüft alle Marker und Grabber
- Identifiziert Regelverletzungen
- Generiert detaillierten Report

### 2. Migration Tool
```bash
python3 migrate_to_standard.py
```
- Konvertiert TXT → YAML
- Korrigiert Grabber-IDs
- Erstellt Backups

### 3. FRAUSAR GUI
```bash
python3 start_frausar.py
```
- Erstellt automatisch konforme Marker
- Verwaltet Grabber-Library
- Zeigt Compliance-Warnungen

## 📁 Dateiorganisation

```
Marker_assist_bot/
├── semantic_marker_rules.yaml      # Projekt-Regeln
├── semantic_grabber_library.yaml   # Zentrale Grabber
├── compliance_checker.py           # Prüf-Tool
├── migrate_to_standard.py          # Migrations-Tool
└── frausar_gui.py                 # GUI mit Standards

ALL_SEMANTIC_MARKER_TXT/
├── ALL_NEWMARKER01/
│   ├── *.yaml                     # Neue Marker (Standard)
│   └── *.txt                      # Legacy (zu migrieren)
└── Former_NEW_MARKER_FOLDERS/
    └── ...                        # Unterordner-Struktur
```

## ✅ Best Practices

### Beim Erstellen neuer Marker:

1. **Verwende YAML-Format** (nicht TXT)
2. **Fülle alle Pflichtfelder** aus
3. **Prüfe ob passender Grabber existiert** (Ähnlichkeitssuche)
4. **Verwende aussagekräftige Namen** (selbsterklärend)
5. **Füge mindestens 3 Beispiele** hinzu

### Beim Arbeiten mit Grabbern:

1. **Vermeide Duplikate** - prüfe erst ob ähnlicher existiert
2. **Halte Patterns prägnant** - Kernaussagen, nicht wörtlich
3. **Dokumentiere Ursprung** - `created_from` Feld
4. **Merge ähnliche Grabber** - bei > 85% Ähnlichkeit

### Wartung:

1. **Führe regelmäßig Compliance-Checks durch**
2. **Migriere Legacy-Formate zeitnah**
3. **Bereinige ungenutzte Grabber**
4. **Dokumentiere Änderungen**

## 🚨 Häufige Fehler

### ❌ Falsch:
```yaml
# Marker ohne Grabber
marker_name: TEST_MARKER
beschreibung: "Test"
beispiele: ["Test"]
# FEHLT: semantische_grabber_id
```

### ✅ Richtig:
```yaml
marker_name: TEST_MARKER
beschreibung: "Test"
beispiele: ["Test"]
semantische_grabber_id: TEST_SEM
```

### ❌ Falsch:
```yaml
# Falsche Naming Convention
marker_name: test-marker
semantische_grabber_id: TestSem
```

### ✅ Richtig:
```yaml
marker_name: TEST_MARKER
semantische_grabber_id: TEST_SEM
```

## 📊 Compliance-Metriken

Ein System gilt als compliant wenn:
- 100% der Marker haben `semantische_grabber_id`
- 100% der Marker-Namen folgen der Convention
- 100% der Grabber-IDs folgen der Convention
- 0 verwaiste Grabber-Referenzen
- Alle Marker im YAML-Format

## 🔄 Migration von Legacy-Systemen

1. **Backup erstellen**
2. **Migration Tool ausführen**
3. **Compliance Check durchführen**
4. **Manuelle Nacharbeit** wo nötig
5. **Alte Dateien archivieren**

## 📞 Support

Bei Fragen zur Compliance:
1. Konsultiere `semantic_marker_rules.yaml`
2. Führe `compliance_checker.py` aus
3. Nutze die FRAUSAR GUI für konforme Erstellung

---

Version: 1.0  
Stand: Januar 2024  
Regelwerk: semantic_marker_rules.yaml 