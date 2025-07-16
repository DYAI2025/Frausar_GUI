
# AUTO_SEM Naming Fix Report - Phase 3

## 📊 Naming-Pattern-Analyse

### Statistiken:
- **Gesamte Grabber:** 195
- **Korrekte AUTO_SEM IDs:** 191 (97.9%)
- **Korrekte Manual _SEM IDs:** 4 (2.1%)
- **Falsche SGR_ IDs:** 0 (0.0%)
- **Andere Patterns:** 0 (0.0%)

## 🔍 Probleme gefunden: 0

### SGR_ Pattern (falsch):
- Keine SGR_ Pattern gefunden ✅

### Unbekannte Patterns:
- Keine unbekannten Patterns gefunden ✅

## 📋 Korrekte Naming-Conventions

### AUTO_SEM Format (automatisch generiert):
```
AUTO_SEM_YYYYMMDD_XXXX
```
**Beispiel:** `AUTO_SEM_20250713_A1B2`

### Manual SEM Format (manuell erstellt):
```
ALL_CAPS_NAME_SEM
```
**Beispiel:** `TRUST_EROSION_SEM`

## 🔧 Problembeschreibung

Das Connection-Status-Fix-Tool hat versehentlich SGR_ IDs statt AUTO_SEM_ IDs generiert:

**Problem:**
- `SGR_EMOTIONAL_BEHAVIORAL_MARKERS2_01` ❌
- `SGR_SELF_SABOTAGE_LOOP_01` ❌

**Korrekt:**
- `AUTO_SEM_20250713_A1B2` ✅
- `AUTO_SEM_20250713_B3C4` ✅

## 🚀 Lösungsansatz

1. **Automatische Migration:** Konvertiere alle SGR_ IDs zu AUTO_SEM_ Format
2. **Marker-Update:** Aktualisiere alle Marker-Referenzen
3. **Backup-Erstellung:** Sichere alte Daten vor Migration
4. **Validierung:** Prüfe Konsistenz nach Migration

## 📋 Nächste Schritte

1. **Sofort:** Führe `fix_naming_patterns()` aus
2. **Kurz:** Validiere alle Referenzen
3. **Mittel:** Aktualisiere Dokumentation
4. **Lang:** Implementiere Naming-Validation in Tools

---

**Status:** ✅ Alle Naming-Patterns korrekt
