#!/usr/bin/env python3
"""
AUTO_SEM Naming Fix - Phase 3
Repariert die Naming-Pattern-Probleme mit AUTO_SEM IDs
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoSemNamingFixer:
    """
    Repariert AUTO_SEM Naming-Pattern-Probleme
    """
    
    def __init__(self, markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.markers_directory = Path(markers_directory)
        self.semantic_grabber_file = self.markers_directory / "SemanticGrabberLibrary" / "semantic_grabber_library.yaml"
        self.markers = {}
        self.semantic_grabbers = {}
        self.load_data()
    
    def load_data(self):
        """
        Lädt alle Marker und Semantic Grabber
        """
        # Lade Marker
        self.load_all_markers()
        
        # Lade Semantic Grabbers
        self.load_semantic_grabbers()
        
        logger.info(f"Loaded {len(self.markers)} markers and {len(self.semantic_grabbers)} semantic grabbers")
    
    def load_all_markers(self):
        """
        Lädt alle Marker aus dem Verzeichnis
        """
        for file_path in self.markers_directory.glob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if content:
                    marker_name = file_path.stem
                    self.markers[marker_name] = {
                        'file_path': file_path,
                        'content': content
                    }
            except Exception as e:
                logger.warning(f"Could not load marker {file_path}: {e}")
    
    def load_semantic_grabbers(self):
        """
        Lädt die Semantic Grabber Library
        """
        if not self.semantic_grabber_file.exists():
            logger.warning(f"Semantic Grabber Library not found: {self.semantic_grabber_file}")
            return
        
        try:
            with open(self.semantic_grabber_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Extrahiere Grabber aus der Struktur
            if 'semantic_grabbers' in data:
                self.semantic_grabbers = data['semantic_grabbers']
            else:
                self.semantic_grabbers = data
                
        except Exception as e:
            logger.error(f"Error loading semantic grabbers: {e}")
    
    def analyze_naming_patterns(self) -> dict:
        """
        Analysiert die aktuellen Naming-Patterns
        """
        analysis = {
            'total_grabbers': len(self.semantic_grabbers),
            'correct_auto_sem': 0,
            'incorrect_sgr': 0,
            'correct_manual_sem': 0,
            'other_patterns': 0,
            'problems': []
        }
        
        # Definiere korrekte Patterns
        auto_sem_pattern = re.compile(r'^AUTO_SEM_\d{8}_[A-Z0-9]{4}$')
        manual_sem_pattern = re.compile(r'^[A-Z][A-Z_]+_SEM$')
        sgr_pattern = re.compile(r'^SGR_.*_01$')
        
        for grabber_id in self.semantic_grabbers:
            if auto_sem_pattern.match(grabber_id):
                analysis['correct_auto_sem'] += 1
            elif manual_sem_pattern.match(grabber_id):
                analysis['correct_manual_sem'] += 1
            elif sgr_pattern.match(grabber_id):
                analysis['incorrect_sgr'] += 1
                analysis['problems'].append({
                    'type': 'incorrect_sgr_pattern',
                    'grabber_id': grabber_id,
                    'description': f"Grabber {grabber_id} verwendet SGR_ statt AUTO_SEM_ Pattern"
                })
            else:
                analysis['other_patterns'] += 1
                analysis['problems'].append({
                    'type': 'unknown_pattern',
                    'grabber_id': grabber_id,
                    'description': f"Grabber {grabber_id} verwendet unbekanntes Naming-Pattern"
                })
        
        return analysis
    
    def generate_auto_sem_id(self) -> str:
        """
        Generiert eine korrekte AUTO_SEM ID
        """
        date_str = datetime.now().strftime('%Y%m%d')
        unique_num = str(uuid.uuid4())[:4].upper()
        return f"AUTO_SEM_{date_str}_{unique_num}"
    
    def fix_naming_patterns(self) -> dict:
        """
        Repariert fehlerhafte Naming-Patterns
        """
        analysis = self.analyze_naming_patterns()
        fix_results = {
            'fixed_grabbers': 0,
            'updated_marker_references': 0,
            'errors': []
        }
        
        # Erstelle Mapping von alten zu neuen IDs
        id_mapping = {}
        
        for problem in analysis['problems']:
            if problem['type'] == 'incorrect_sgr_pattern':
                old_id = problem['grabber_id']
                new_id = self.generate_auto_sem_id()
                id_mapping[old_id] = new_id
                
                # Kopiere Grabber-Daten
                self.semantic_grabbers[new_id] = self.semantic_grabbers[old_id].copy()
                
                # Füge Metadaten hinzu
                self.semantic_grabbers[new_id]['migrated_from'] = old_id
                self.semantic_grabbers[new_id]['migration_date'] = datetime.now().isoformat()
                
                # Entferne alten Grabber
                del self.semantic_grabbers[old_id]
                
                fix_results['fixed_grabbers'] += 1
                logger.info(f"Fixed: {old_id} → {new_id}")
        
        # Aktualisiere Marker-Referenzen
        for marker_name, marker_info in self.markers.items():
            content = marker_info['content']
            grabber_id = self.find_grabber_reference(content)
            
            if grabber_id and grabber_id in id_mapping:
                new_id = id_mapping[grabber_id]
                
                # Aktualisiere Referenz im Marker
                self.update_grabber_reference(content, new_id)
                
                # Speichere aktualisierte Marker-Datei
                try:
                    with open(marker_info['file_path'], 'w', encoding='utf-8') as f:
                        yaml.dump(content, f, default_flow_style=False, allow_unicode=True, indent=2)
                    
                    fix_results['updated_marker_references'] += 1
                    logger.info(f"Updated marker {marker_name}: {grabber_id} → {new_id}")
                    
                except Exception as e:
                    fix_results['errors'].append(f"Error updating marker {marker_name}: {e}")
        
        # Speichere aktualisierte Grabber Library
        if fix_results['fixed_grabbers'] > 0:
            self.save_semantic_grabbers()
        
        return fix_results
    
    def find_grabber_reference(self, content: dict) -> str:
        """
        Findet Grabber-Referenzen in Marker-Content
        """
        # Verschiedene mögliche Felder für Grabber-Referenzen
        grabber_fields = [
            'semantic_grabber_id',
            'semantische_grabber_id',
            'grabber_id',
            'semantic_grab_id'
        ]
        
        # Suche in verschiedenen Strukturen
        for field in grabber_fields:
            if field in content:
                return content[field]
        
        # Suche in nested structures
        if 'marker' in content and isinstance(content['marker'], dict):
            for field in grabber_fields:
                if field in content['marker']:
                    return content['marker'][field]
        
        return None
    
    def update_grabber_reference(self, content: dict, new_id: str):
        """
        Aktualisiert Grabber-Referenz in Marker-Content
        """
        # Verschiedene mögliche Felder für Grabber-Referenzen
        grabber_fields = [
            'semantic_grabber_id',
            'semantische_grabber_id',
            'grabber_id',
            'semantic_grab_id'
        ]
        
        # Aktualisiere in verschiedenen Strukturen
        for field in grabber_fields:
            if field in content:
                content[field] = new_id
                return
        
        # Aktualisiere in nested structures
        if 'marker' in content and isinstance(content['marker'], dict):
            for field in grabber_fields:
                if field in content['marker']:
                    content['marker'][field] = new_id
                    return
    
    def save_semantic_grabbers(self):
        """
        Speichert die aktualisierte Semantic Grabber Library
        """
        try:
            # Erstelle Backup
            backup_file = self.semantic_grabber_file.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if self.semantic_grabber_file.exists():
                backup_file.write_text(self.semantic_grabber_file.read_text(encoding='utf-8'), encoding='utf-8')
            
            # Speichere aktualisierte Daten
            data = {
                'marker_name': 'semantic_grabber_library',
                'semantic_grabbers': self.semantic_grabbers
            }
            
            with open(self.semantic_grabber_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Saved updated semantic grabber library to {self.semantic_grabber_file}")
            
        except Exception as e:
            logger.error(f"Error saving semantic grabbers: {e}")
    
    def generate_naming_report(self) -> str:
        """
        Generiert einen umfassenden Naming-Report
        """
        analysis = self.analyze_naming_patterns()
        
        report = f"""
# AUTO_SEM Naming Fix Report - Phase 3

## 📊 Naming-Pattern-Analyse

### Statistiken:
- **Gesamte Grabber:** {analysis['total_grabbers']}
- **Korrekte AUTO_SEM IDs:** {analysis['correct_auto_sem']} ({analysis['correct_auto_sem']/analysis['total_grabbers']*100:.1f}%)
- **Korrekte Manual _SEM IDs:** {analysis['correct_manual_sem']} ({analysis['correct_manual_sem']/analysis['total_grabbers']*100:.1f}%)
- **Falsche SGR_ IDs:** {analysis['incorrect_sgr']} ({analysis['incorrect_sgr']/analysis['total_grabbers']*100:.1f}%)
- **Andere Patterns:** {analysis['other_patterns']} ({analysis['other_patterns']/analysis['total_grabbers']*100:.1f}%)

## 🔍 Probleme gefunden: {len(analysis['problems'])}

### SGR_ Pattern (falsch):
"""
        
        sgr_problems = [p for p in analysis['problems'] if p['type'] == 'incorrect_sgr_pattern']
        if sgr_problems:
            for problem in sgr_problems[:10]:  # Zeige ersten 10
                report += f"- **{problem['grabber_id']}** (sollte AUTO_SEM_ sein)\n"
            if len(sgr_problems) > 10:
                report += f"- ... und {len(sgr_problems) - 10} weitere\n"
        else:
            report += "- Keine SGR_ Pattern gefunden ✅\n"
        
        report += f"""
### Unbekannte Patterns:
"""
        
        unknown_problems = [p for p in analysis['problems'] if p['type'] == 'unknown_pattern']
        if unknown_problems:
            for problem in unknown_problems[:5]:  # Zeige ersten 5
                report += f"- **{problem['grabber_id']}**\n"
            if len(unknown_problems) > 5:
                report += f"- ... und {len(unknown_problems) - 5} weitere\n"
        else:
            report += "- Keine unbekannten Patterns gefunden ✅\n"
        
        report += f"""
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

**Status:** {"⚠️ Naming-Probleme gefunden" if analysis['problems'] else "✅ Alle Naming-Patterns korrekt"}
"""
        
        return report

def main():
    """
    Hauptfunktion
    """
    print("🔧 AUTO_SEM Naming Fix - Phase 3")
    print("=" * 50)
    
    # Initialisiere Fixer
    fixer = AutoSemNamingFixer()
    
    # Analysiere Naming-Patterns
    analysis = fixer.analyze_naming_patterns()
    
    print(f"📊 Analysiert: {analysis['total_grabbers']} Grabber")
    print(f"✅ Korrekte AUTO_SEM: {analysis['correct_auto_sem']}")
    print(f"✅ Korrekte Manual _SEM: {analysis['correct_manual_sem']}")
    print(f"❌ Falsche SGR_: {analysis['incorrect_sgr']}")
    print(f"❓ Andere Patterns: {analysis['other_patterns']}")
    print(f"🔍 Probleme: {len(analysis['problems'])}")
    
    # Repariere Naming-Patterns
    if analysis['problems']:
        print("\n🔧 Repariere Naming-Patterns...")
        fix_results = fixer.fix_naming_patterns()
        print(f"✅ Reparierte Grabber: {fix_results['fixed_grabbers']}")
        print(f"✅ Aktualisierte Marker: {fix_results['updated_marker_references']}")
        if fix_results['errors']:
            print(f"❌ Fehler: {len(fix_results['errors'])}")
    
    # Generiere Report
    report = fixer.generate_naming_report()
    
    # Speichere Report
    with open("auto_sem_naming_fix_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n✅ AUTO_SEM Naming-Fix abgeschlossen!")
    print("📊 Report gespeichert: auto_sem_naming_fix_report.md")

if __name__ == "__main__":
    main() 