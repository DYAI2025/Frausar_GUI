#!/usr/bin/env python3
"""
Fix Remaining Errors - Phase 3
Repariert die verbleibenden 6 Dateien mit leeren Beschreibungen
"""

import yaml
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemainingErrorsFixer:
    """
    Repariert die verbleibenden 6 Fehler-Dateien
    """
    
    def __init__(self, markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.markers_directory = Path(markers_directory)
        self.error_files = [
            "MARKER_MARKER.yaml",
            "STYLE_SYNC_MARKER.yaml", 
            "SEMANTIC_MARKER_RULES_MARKER.yaml",
            "SELF_DISCLOSURE_DRIFT_AXES_MARKER.yaml",
            "-_ID_MARKER.yaml",
            "MARKER.yaml"
        ]
        
        # Beschreibungen für die Marker
        self.descriptions = {
            "MARKER_MARKER": "Generischer Marker-Platzhalter für Marker-System-Entwicklung und -Tests",
            "STYLE_SYNC_MARKER": "Erkennt Synchronisation von Kommunikationsstilen zwischen Gesprächspartnern",
            "SEMANTIC_MARKER_RULES_MARKER": "Definiert Regeln und Muster für semantische Marker-Erkennung",
            "SELF_DISCLOSURE_DRIFT_AXES_MARKER": "Misst Verschiebungen in der Selbstoffenbarung entlang verschiedener Achsen",
            "-_ID_MARKER": "Temporärer ID-Marker für System-interne Verarbeitungszwecke",
            "MARKER": "Basis-Marker-Template für die Marker-Erstellung"
        }
    
    def fix_empty_description(self, filepath: Path) -> bool:
        """
        Repariert eine Datei mit leerer Beschreibung
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content:
                logger.error(f"Leere Datei: {filepath.name}")
                return False
            
            marker_name = content.get('marker_name', filepath.stem)
            
            # Repariere leere Beschreibung
            if 'beschreibung' in content and not content['beschreibung'].strip():
                description = self.descriptions.get(marker_name, 
                    f"Automatisch generierte Beschreibung für {marker_name}")
                content['beschreibung'] = description
                logger.info(f"Beschreibung hinzugefügt für {marker_name}")
            
            # Konvertiere zu Standard-Format wenn nötig
            if 'marker' not in content:
                # Erstelle Standard-Marker-Struktur
                marker_id = f"S_{marker_name.replace('_MARKER', '').replace('-_ID', 'ID')}"
                
                standard_marker = {
                    'marker_name': marker_name,
                    'marker': {
                        'id': marker_id,
                        'name': marker_name.replace('_MARKER', ''),
                        'level': 2,
                        'category': 'Semantic',
                        'description': content.get('beschreibung', self.descriptions.get(marker_name, '')),
                        'examples': content.get('beispiele', []),
                        'semantic_tags': [marker_name.lower().replace('_', '-')],
                        'pattern': [],
                        'semantic_grabber_id': content.get('semantische_grabber_id', f"SGR_{marker_name}_01"),
                        'context_rule': []
                    },
                    'kategorie': content.get('kategorie', 'SEMANTIC')
                }
                
                # Bewahre zusätzliche Felder
                for key in ['metadata', 'tags', 'semantic_grab']:
                    if key in content:
                        standard_marker[key] = content[key]
                
                content = standard_marker
            
            # Stelle sicher, dass marker.description gefüllt ist
            if 'marker' in content and 'description' in content['marker']:
                if not content['marker']['description']:
                    content['marker']['description'] = self.descriptions.get(marker_name, 
                        f"Automatisch generierte Beschreibung für {marker_name}")
            
            # Speichere reparierte Datei
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"✓ Repariert: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei {filepath.name}: {e}")
            return False
    
    def fix_all_remaining_errors(self) -> dict:
        """
        Repariert alle verbleibenden Fehler-Dateien
        """
        results = {
            'fixed': [],
            'errors': []
        }
        
        for filename in self.error_files:
            filepath = self.markers_directory / filename
            
            if not filepath.exists():
                logger.warning(f"Datei nicht gefunden: {filename}")
                results['errors'].append(f"{filename}: Datei nicht gefunden")
                continue
            
            if self.fix_empty_description(filepath):
                results['fixed'].append(filename)
            else:
                results['errors'].append(filename)
        
        return results
    
    def generate_report(self, results: dict) -> str:
        """
        Generiert einen Reparatur-Report
        """
        report = f"""
# Remaining Errors Fix Report - Phase 3
Reparatur der verbleibenden 6 Fehler-Dateien

## Ergebnisse
- Reparierte Dateien: {len(results['fixed'])}
- Fehler: {len(results['errors'])}

## Erfolgreich repariert:
{chr(10).join(f'- {file}' for file in results['fixed'])}

## Fehler:
{chr(10).join(f'- {error}' for error in results['errors'])}

## Hinzugefügte Beschreibungen:
{chr(10).join(f'- {name}: {desc}' for name, desc in self.descriptions.items())}
"""
        return report

def main():
    """
    Hauptfunktion
    """
    print("🔧 Remaining Errors Fixer - Phase 3")
    print("=" * 50)
    
    fixer = RemainingErrorsFixer()
    results = fixer.fix_all_remaining_errors()
    
    report = fixer.generate_report(results)
    
    # Speichere Report
    with open("remaining_errors_fix_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Reparatur abgeschlossen!")
    print(f"Repariert: {len(results['fixed'])}")
    print(f"Fehler: {len(results['errors'])}")
    
    if results['errors']:
        print(f"\n❌ Fehler:")
        for error in results['errors']:
            print(f"  - {error}")

if __name__ == "__main__":
    main() 