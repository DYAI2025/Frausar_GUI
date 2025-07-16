#!/usr/bin/env python3
"""
Marker Repair Engine - Phase 2
Automatische Vervollständigung und Reparatur von Marker-YAMLs

Basierend auf der Analyse aus Phase 1 werden hier die identifizierten
Strukturprobleme systematisch repariert.
"""

import yaml
import json
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkerRepairEngine:
    """
    Hauptklasse für die Reparatur von Marker-YAMLs
    """
    
    def __init__(self, markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.markers_directory = Path(markers_directory)
        self.templates = self._initialize_templates()
        self.repair_stats = {
            'processed': 0,
            'repaired': 0,
            'errors': 0,
            'skipped': 0
        }
        
    def _initialize_templates(self) -> Dict[str, Dict]:
        """
        Initialisiert die Level-Templates basierend auf identifizierten Strukturen
        """
        return {
            'level_1_atomic': {
                'required_fields': ['id', 'name', 'level', 'description', 'pattern', 'examples'],
                'template': {
                    'marker_name': '',
                    'marker': {
                        'id': '',
                        'name': '',
                        'level': 1,
                        'category': 'Atomic',
                        'description': '',
                        'pattern': [],
                        'examples': [],
                        'semantic_tags': [],
                        'semantic_grabber_id': '',
                        'context_rule': []
                    },
                    'kategorie': 'ATOMIC'
                }
            },
            'level_2_semantic': {
                'required_fields': ['id', 'name', 'level', 'description', 'semantic_tags', 'examples'],
                'template': {
                    'marker_name': '',
                    'marker': {
                        'id': '',
                        'name': '',
                        'level': 2,
                        'category': 'Semantic',
                        'description': '',
                        'semantic_tags': [],
                        'examples': [],
                        'pattern': [],
                        'semantic_grabber_id': '',
                        'context_rule': []
                    },
                    'kategorie': 'SEMANTIC'
                }
            },
            'level_3_cluster': {
                'required_fields': ['id', 'name', 'level', 'description', 'composed_of', 'examples'],
                'template': {
                    'marker_name': '',
                    'marker': {
                        'id': '',
                        'name': '',
                        'level': 3,
                        'category': 'Cluster',
                        'description': '',
                        'composed_of': [],
                        'examples': [],
                        'semantic_tags': [],
                        'semantic_grabber_id': '',
                        'context_rule': []
                    },
                    'kategorie': 'CLUSTER'
                }
            },
            'level_4_meta': {
                'required_fields': ['id', 'name', 'level', 'description', 'category', 'examples'],
                'template': {
                    'marker_name': '',
                    'marker': {
                        'id': '',
                        'name': '',
                        'level': 4,
                        'category': '',
                        'description': '',
                        'examples': [],
                        'semantic_tags': [],
                        'pattern': [],
                        'semantic_grabber_id': '',
                        'context_rule': []
                    },
                    'kategorie': 'META'
                }
            }
        }
    
    def detect_marker_level(self, marker_data: Dict) -> int:
        """
        Erkennt das Level eines Markers basierend auf seiner Struktur
        """
        # Explizite Level-Angabe
        if 'marker' in marker_data and 'level' in marker_data['marker']:
            level = marker_data['marker']['level']
            if isinstance(level, str):
                level_map = {'atomic': 1, 'semantic': 2, 'cluster': 3, 'meta': 4}
                return level_map.get(level.lower(), 1)
            elif isinstance(level, int):
                return level
        
        # Strukturbasierte Erkennung
        if 'marker' in marker_data:
            marker = marker_data['marker']
            
            # Level 3: Hat composed_of
            if 'composed_of' in marker:
                return 3
            
            # Level 4: Hat category oder ist als meta gekennzeichnet
            if 'category' in marker or marker.get('name', '').upper().endswith('_META'):
                return 4
            
            # Level 2: Hat semantic_tags
            if 'semantic_tags' in marker:
                return 2
        
        # Legacy-Format erkennen
        if 'beschreibung' in marker_data or 'szenarien' in marker_data:
            return 2  # Legacy meist semantic
        
        # Input/Output-Format
        marker_name = marker_data.get('marker_name', '')
        if any(key.endswith('marker') for key in marker_data.keys() if key != 'marker_name'):
            return 2  # Training-Format meist semantic
        
        return 1  # Default: Atomic
    
    def detect_marker_format(self, marker_data: Dict) -> str:
        """
        Erkennt das Format eines Markers
        """
        # Moderne Struktur
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            if 'id' in marker_data['marker'] and 'level' in marker_data['marker']:
                return 'modern_format'
        
        # Input/Output Training Format
        marker_name = marker_data.get('marker_name', '')
        if marker_name and any(isinstance(v, list) and 
                              all(isinstance(item, dict) and 'input' in item and 'output' in item 
                                  for item in v) for v in marker_data.values() if isinstance(v, list)):
            return 'input_output_format'
        
        # Legacy Format
        if 'beschreibung' in marker_data or 'szenarien' in marker_data:
            return 'legacy_format'
        
        # Simple Examples Format
        if 'beispiele' in marker_data or 'examples' in marker_data:
            return 'simple_examples_format'
        
        return 'unknown_format'
    
    def generate_marker_id(self, marker_name: str, level: int) -> str:
        """
        Generiert eine standardisierte Marker-ID
        """
        # Bereinige den Namen
        clean_name = re.sub(r'[^A-Z0-9_]', '', marker_name.upper())
        clean_name = re.sub(r'_MARKER$', '', clean_name)
        
        # Level-Präfix
        level_prefix = {1: 'M_', 2: 'S_', 3: 'C_', 4: 'META_'}
        
        return f"{level_prefix.get(level, 'M_')}{clean_name}"
    
    def generate_semantic_grabber_id(self, marker_id: str) -> str:
        """
        Generiert eine Semantic Grabber ID
        """
        return f"SGR_{marker_id.replace('M_', '').replace('S_', '').replace('C_', '').replace('META_', '')}_01"
    
    def extract_examples_from_legacy(self, marker_data: Dict) -> List[str]:
        """
        Extrahiert Beispiele aus Legacy-Format
        """
        examples = []
        
        # Direkte Beispiele
        if 'examples' in marker_data:
            if isinstance(marker_data['examples'], list):
                examples.extend(marker_data['examples'])
        
        if 'beispiele' in marker_data:
            if isinstance(marker_data['beispiele'], list):
                examples.extend(marker_data['beispiele'])
        
        # Input/Output Format
        for key, value in marker_data.items():
            if isinstance(value, list) and key != 'examples' and key != 'beispiele':
                for item in value:
                    if isinstance(item, dict) and 'input' in item:
                        examples.append(item['input'])
        
        return examples[:20]  # Limitiere auf 20 Beispiele
    
    def extract_description_from_legacy(self, marker_data: Dict) -> str:
        """
        Extrahiert Beschreibung aus Legacy-Format
        """
        # Direkte Beschreibung
        if 'description' in marker_data:
            return str(marker_data['description'])
        
        if 'beschreibung' in marker_data:
            return str(marker_data['beschreibung'])
        
        # Aus Marker-Struktur
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            if 'description' in marker_data['marker']:
                return str(marker_data['marker']['description'])
        
        # Fallback: Generiere aus Marker-Name
        marker_name = marker_data.get('marker_name', 'Unknown')
        return f"Automatisch generierte Beschreibung für {marker_name}"
    
    def extract_semantic_tags(self, marker_data: Dict) -> List[str]:
        """
        Extrahiert oder generiert Semantic Tags
        """
        # Direkte Tags
        if 'marker' in marker_data and 'semantic_tags' in marker_data['marker']:
            return marker_data['marker']['semantic_tags']
        
        if 'tags' in marker_data:
            return marker_data['tags']
        
        # Generiere aus Marker-Name
        marker_name = marker_data.get('marker_name', '')
        if marker_name:
            # Entferne _MARKER und konvertiere zu Tags
            base_name = marker_name.replace('_MARKER', '').lower()
            return [base_name.replace('_', '-')]
        
        return []
    
    def repair_marker(self, marker_data: Dict, filename: str) -> Dict:
        """
        Repariert einen einzelnen Marker
        """
        try:
            # Erkenne Format und Level
            format_type = self.detect_marker_format(marker_data)
            level = self.detect_marker_level(marker_data)
            
            logger.info(f"Repariere {filename}: Format={format_type}, Level={level}")
            
            # Wähle Template
            template_key = f"level_{level}_{['atomic', 'semantic', 'cluster', 'meta'][level-1]}"
            template = self.templates[template_key]['template'].copy()
            
            # Basis-Informationen
            marker_name = marker_data.get('marker_name', filename.replace('.yaml', ''))
            
            # Fülle Template
            template['marker_name'] = marker_name
            template['marker']['name'] = marker_name.replace('_MARKER', '')
            template['marker']['id'] = self.generate_marker_id(marker_name, level)
            template['marker']['level'] = level
            template['marker']['description'] = self.extract_description_from_legacy(marker_data)
            template['marker']['examples'] = self.extract_examples_from_legacy(marker_data)
            template['marker']['semantic_tags'] = self.extract_semantic_tags(marker_data)
            template['marker']['semantic_grabber_id'] = self.generate_semantic_grabber_id(template['marker']['id'])
            
            # Spezielle Felder je nach Level
            if level == 3:  # Cluster
                template['marker']['composed_of'] = marker_data.get('composed_of', [])
            
            if level == 4:  # Meta
                template['marker']['category'] = marker_data.get('category', 'Emotionsdynamik')
            
            # Pattern extrahieren
            if 'marker' in marker_data and 'pattern' in marker_data['marker']:
                template['marker']['pattern'] = marker_data['marker']['pattern']
            elif 'pattern' in marker_data:
                template['marker']['pattern'] = marker_data['pattern']
            
            # Context Rules
            if 'context_rule' in marker_data:
                template['marker']['context_rule'] = marker_data['context_rule']
            
            # Bewahre zusätzliche Felder
            if 'psychologischer_hintergrund' in marker_data:
                template['psychologischer_hintergrund'] = marker_data['psychologischer_hintergrund']
            
            if 'semantic_grab' in marker_data:
                template['semantic_grab'] = marker_data['semantic_grab']
            
            return template
            
        except Exception as e:
            logger.error(f"Fehler bei Reparatur von {filename}: {e}")
            return marker_data
    
    def validate_repaired_marker(self, marker_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validiert einen reparierten Marker
        """
        errors = []
        
        # Grundstruktur
        if 'marker' not in marker_data:
            errors.append("Fehlende 'marker' Struktur")
            return False, errors
        
        marker = marker_data['marker']
        
        # Erforderliche Felder
        required = ['id', 'name', 'level', 'description']
        for field in required:
            if field not in marker or not marker[field]:
                errors.append(f"Fehlendes Feld: {field}")
        
        # Level-spezifische Validierung
        level = marker.get('level', 1)
        if level == 3 and 'composed_of' not in marker:
            errors.append("Cluster-Marker benötigt 'composed_of'")
        
        if level == 4 and 'category' not in marker:
            errors.append("Meta-Marker benötigt 'category'")
        
        # Beispiele
        if 'examples' not in marker or not marker['examples']:
            errors.append("Fehlende Beispiele")
        
        return len(errors) == 0, errors
    
    def repair_all_markers(self, backup: bool = True) -> Dict:
        """
        Repariert alle Marker im Verzeichnis
        """
        if not self.markers_directory.exists():
            raise FileNotFoundError(f"Verzeichnis nicht gefunden: {self.markers_directory}")
        
        # Backup erstellen
        if backup:
            self._create_backup()
        
        results = {
            'processed': [],
            'repaired': [],
            'errors': [],
            'skipped': []
        }
        
        # Alle YAML-Dateien verarbeiten
        for yaml_file in self.markers_directory.glob("*.yaml"):
            try:
                self.repair_stats['processed'] += 1
                
                # Lade Marker
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    marker_data = yaml.safe_load(f)
                
                if not marker_data:
                    results['skipped'].append(yaml_file.name)
                    self.repair_stats['skipped'] += 1
                    continue
                
                # Repariere Marker
                repaired_data = self.repair_marker(marker_data, yaml_file.name)
                
                # Validiere
                is_valid, validation_errors = self.validate_repaired_marker(repaired_data)
                
                if is_valid:
                    # Speichere reparierte Version
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.dump(repaired_data, f, default_flow_style=False, 
                                allow_unicode=True, indent=2)
                    
                    results['repaired'].append(yaml_file.name)
                    self.repair_stats['repaired'] += 1
                    logger.info(f"✓ Repariert: {yaml_file.name}")
                else:
                    results['errors'].append({
                        'file': yaml_file.name,
                        'errors': validation_errors
                    })
                    self.repair_stats['errors'] += 1
                    logger.warning(f"✗ Validierung fehlgeschlagen: {yaml_file.name}")
                
                results['processed'].append(yaml_file.name)
                
            except Exception as e:
                results['errors'].append({
                    'file': yaml_file.name,
                    'errors': [str(e)]
                })
                self.repair_stats['errors'] += 1
                logger.error(f"Fehler bei {yaml_file.name}: {e}")
        
        return results
    
    def _create_backup(self):
        """
        Erstellt ein Backup des Marker-Verzeichnisses
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.markers_directory.parent / f"backup_{timestamp}"
        
        import shutil
        shutil.copytree(self.markers_directory, backup_dir)
        logger.info(f"Backup erstellt: {backup_dir}")
    
    def generate_repair_report(self, results: Dict) -> str:
        """
        Generiert einen Reparatur-Report
        """
        report = f"""
# Marker Repair Report - Phase 2
Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistiken
- Verarbeitete Dateien: {self.repair_stats['processed']}
- Erfolgreich repariert: {self.repair_stats['repaired']}
- Fehler: {self.repair_stats['errors']}
- Übersprungen: {self.repair_stats['skipped']}

## Erfolgreiche Reparaturen
{chr(10).join(f'- {file}' for file in results['repaired'])}

## Fehler
{chr(10).join(f'- {error["file"]}: {", ".join(error["errors"])}' for error in results['errors'])}

## Übersprungene Dateien
{chr(10).join(f'- {file}' for file in results['skipped'])}
"""
        return report
    
    def save_repair_report(self, results: Dict, filename: str = "repair_report_phase2.md"):
        """
        Speichert den Reparatur-Report
        """
        report = self.generate_repair_report(results)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report gespeichert: {filename}")

def main():
    """
    Hauptfunktion für Phase 2
    """
    print("🔧 Marker Repair Engine - Phase 2")
    print("=" * 50)
    
    # Initialisiere Engine
    engine = MarkerRepairEngine()
    
    # Repariere alle Marker
    print("Starte Reparatur aller Marker...")
    results = engine.repair_all_markers(backup=True)
    
    # Generiere Report
    engine.save_repair_report(results)
    
    print(f"\n✅ Phase 2 abgeschlossen!")
    print(f"Verarbeitet: {engine.repair_stats['processed']}")
    print(f"Repariert: {engine.repair_stats['repaired']}")
    print(f"Fehler: {engine.repair_stats['errors']}")

if __name__ == "__main__":
    main() 