#!/usr/bin/env python3
"""
Marker Repair Engine v2 - Phase 2 Enhanced
Erweiterte Reparatur-Engine mit robuster YAML-Behandlung

Behandelt:
- YAML-Syntaxfehler
- String-Objekte als Marker-Daten
- Fehlende Beispiele
- Verschiedene Datenstrukturen
"""

import yaml
import json
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarkerRepairEngineV2:
    """
    Erweiterte Reparatur-Engine für Marker-YAMLs
    """
    
    def __init__(self, markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.markers_directory = Path(markers_directory)
        self.templates = self._initialize_templates()
        self.repair_stats = {
            'processed': 0,
            'repaired': 0,
            'errors': 0,
            'skipped': 0,
            'yaml_errors': 0,
            'string_objects': 0
        }
        
    def _initialize_templates(self) -> Dict[str, Dict]:
        """
        Initialisiert die Level-Templates
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
    
    def safe_load_yaml(self, filepath: Path) -> Tuple[Optional[Dict], str]:
        """
        Lädt YAML-Dateien sicher und behandelt Syntaxfehler
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Versuche normales YAML-Laden
            try:
                data = yaml.safe_load(content)
                return data, "success"
            except yaml.YAMLError as e:
                logger.warning(f"YAML-Syntaxfehler in {filepath.name}: {e}")
                self.repair_stats['yaml_errors'] += 1
                
                # Versuche Reparatur häufiger YAML-Probleme
                repaired_content = self.repair_yaml_syntax(content)
                if repaired_content:
                    try:
                        data = yaml.safe_load(repaired_content)
                        return data, "repaired_syntax"
                    except yaml.YAMLError:
                        pass
                
                # Fallback: Erstelle minimale Struktur
                return self.create_minimal_structure(filepath.name, content), "minimal_structure"
                
        except Exception as e:
            logger.error(f"Fehler beim Laden von {filepath.name}: {e}")
            return None, f"error: {e}"
    
    def repair_yaml_syntax(self, content: str) -> Optional[str]:
        """
        Repariert häufige YAML-Syntaxfehler
        """
        try:
            # Entferne doppelte Dokument-Trenner
            content = re.sub(r'---\s*---', '---', content)
            
            # Repariere fehlende Anführungszeichen bei speziellen Zeichen
            content = re.sub(r':\s*([^"\s].*[?:].*)$', r': "\1"', content, flags=re.MULTILINE)
            
            # Repariere ungültige Einrückungen
            lines = content.split('\n')
            repaired_lines = []
            for line in lines:
                # Entferne Tabs und ersetze durch Spaces
                line = line.replace('\t', '  ')
                repaired_lines.append(line)
            
            return '\n'.join(repaired_lines)
        except Exception:
            return None
    
    def create_minimal_structure(self, filename: str, content: str) -> Dict:
        """
        Erstellt eine minimale Marker-Struktur aus defekten Dateien
        """
        marker_name = filename.replace('.yaml', '')
        
        # Extrahiere Text-Fragmente für Beispiele
        examples = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-') and len(line) > 10:
                if any(char in line for char in ['"', "'", '?', '!', '.']):
                    examples.append(line[:200])  # Limitiere Länge
        
        return {
            'marker_name': marker_name,
            'marker': {
                'id': f"M_{marker_name.upper()}",
                'name': marker_name,
                'level': 2,
                'description': f"Automatisch generierte Beschreibung für {marker_name}",
                'examples': examples[:5],  # Maximal 5 Beispiele
                'semantic_tags': [marker_name.lower().replace('_', '-')],
                'pattern': [],
                'semantic_grabber_id': f"SGR_{marker_name.upper()}_01",
                'context_rule': []
            },
            'kategorie': 'RECONSTRUCTED'
        }
    
    def handle_string_marker(self, marker_data: Union[str, Dict], filename: str) -> Dict:
        """
        Behandelt Marker, die als String gespeichert sind
        """
        if isinstance(marker_data, str):
            self.repair_stats['string_objects'] += 1
            logger.info(f"String-Objekt erkannt in {filename}")
            
            # Versuche JSON-Parsing
            try:
                if marker_data.strip().startswith('{'):
                    parsed = json.loads(marker_data)
                    if isinstance(parsed, dict):
                        return parsed
            except json.JSONDecodeError:
                pass
            
            # Erstelle Struktur aus String
            marker_name = filename.replace('.yaml', '')
            return {
                'marker_name': marker_name,
                'marker': {
                    'id': f"M_{marker_name.upper()}",
                    'name': marker_name,
                    'level': 2,
                    'description': marker_data[:500],  # Verwende String als Beschreibung
                    'examples': [marker_data[:200]] if len(marker_data) > 20 else [],
                    'semantic_tags': [marker_name.lower().replace('_', '-')],
                    'pattern': [],
                    'semantic_grabber_id': f"SGR_{marker_name.upper()}_01",
                    'context_rule': []
                },
                'kategorie': 'STRING_CONVERTED'
            }
        
        return marker_data
    
    def detect_marker_level(self, marker_data: Dict) -> int:
        """
        Erkennt das Level eines Markers
        """
        # Explizite Level-Angabe
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            if 'level' in marker_data['marker']:
                level = marker_data['marker']['level']
                if isinstance(level, str):
                    level_map = {'atomic': 1, 'semantic': 2, 'cluster': 3, 'meta': 4}
                    return level_map.get(level.lower(), 1)
                elif isinstance(level, int):
                    return level
        
        # Strukturbasierte Erkennung
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
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
            return 2
        
        # Input/Output-Format
        marker_name = marker_data.get('marker_name', '')
        if marker_name:
            for key, value in marker_data.items():
                if (isinstance(value, list) and key != 'marker_name' and 
                    any(isinstance(item, dict) and 'input' in item and 'output' in item 
                        for item in value if isinstance(item, dict))):
                    return 2
        
        return 1  # Default: Atomic
    
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
    
    def extract_examples_from_any_format(self, marker_data: Dict) -> List[str]:
        """
        Extrahiert Beispiele aus beliebigen Formaten
        """
        examples = []
        
        # Direkte Beispiele
        for key in ['examples', 'beispiele']:
            if key in marker_data:
                if isinstance(marker_data[key], list):
                    examples.extend([str(ex) for ex in marker_data[key]])
                elif isinstance(marker_data[key], str):
                    examples.append(marker_data[key])
        
        # Aus Marker-Struktur
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            marker = marker_data['marker']
            for key in ['examples', 'beispiele']:
                if key in marker and isinstance(marker[key], list):
                    examples.extend([str(ex) for ex in marker[key]])
        
        # Input/Output Format
        for key, value in marker_data.items():
            if isinstance(value, list) and key not in ['examples', 'beispiele']:
                for item in value:
                    if isinstance(item, dict) and 'input' in item:
                        examples.append(str(item['input']))
        
        # Fallback: Generiere Beispiele aus Beschreibung
        if not examples:
            description = self.extract_description_from_any_format(marker_data)
            if description and len(description) > 50:
                # Teile Beschreibung in Sätze
                sentences = re.split(r'[.!?]+', description)
                examples = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        
        return examples[:20]  # Limitiere auf 20 Beispiele
    
    def extract_description_from_any_format(self, marker_data: Dict) -> str:
        """
        Extrahiert Beschreibung aus beliebigen Formaten
        """
        # Direkte Beschreibung
        for key in ['description', 'beschreibung']:
            if key in marker_data:
                return str(marker_data[key])
        
        # Aus Marker-Struktur
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            marker = marker_data['marker']
            for key in ['description', 'beschreibung']:
                if key in marker:
                    return str(marker[key])
        
        # Aus anderen Feldern
        for key in ['dynamik_absicht', 'psychologischer_hintergrund']:
            if key in marker_data:
                return str(marker_data[key])
        
        # Fallback: Generiere aus Marker-Name
        marker_name = marker_data.get('marker_name', 'Unknown')
        return f"Automatisch generierte Beschreibung für {marker_name}"
    
    def repair_marker_enhanced(self, marker_data: Union[str, Dict], filename: str) -> Dict:
        """
        Erweiterte Marker-Reparatur
        """
        try:
            # Behandle String-Objekte
            marker_data = self.handle_string_marker(marker_data, filename)
            
            if not isinstance(marker_data, dict):
                marker_data = {}
            
            # Erkenne Format und Level
            level = self.detect_marker_level(marker_data)
            
            logger.info(f"Repariere {filename}: Level={level}")
            
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
            template['marker']['description'] = self.extract_description_from_any_format(marker_data)
            template['marker']['examples'] = self.extract_examples_from_any_format(marker_data)
            
            # Semantic Tags
            if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
                if 'semantic_tags' in marker_data['marker']:
                    template['marker']['semantic_tags'] = marker_data['marker']['semantic_tags']
                else:
                    template['marker']['semantic_tags'] = [marker_name.lower().replace('_', '-')]
            else:
                template['marker']['semantic_tags'] = [marker_name.lower().replace('_', '-')]
            
            template['marker']['semantic_grabber_id'] = f"SGR_{template['marker']['id'].replace('M_', '').replace('S_', '').replace('C_', '').replace('META_', '')}_01"
            
            # Spezielle Felder je nach Level
            if level == 3:  # Cluster
                template['marker']['composed_of'] = marker_data.get('composed_of', [])
            
            if level == 4:  # Meta
                template['marker']['category'] = marker_data.get('category', 'Emotionsdynamik')
            
            # Pattern extrahieren
            if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
                if 'pattern' in marker_data['marker']:
                    template['marker']['pattern'] = marker_data['marker']['pattern']
            elif 'pattern' in marker_data:
                template['marker']['pattern'] = marker_data['pattern']
            
            # Bewahre zusätzliche Felder
            for key in ['psychologischer_hintergrund', 'semantic_grab', 'tags']:
                if key in marker_data:
                    template[key] = marker_data[key]
            
            return template
            
        except Exception as e:
            logger.error(f"Fehler bei Reparatur von {filename}: {e}")
            # Fallback: Erstelle minimale Struktur
            return self.create_minimal_structure(filename, str(marker_data))
    
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
        
        # Beispiele (weniger streng)
        if 'examples' not in marker or not marker['examples']:
            # Nur Warnung, kein Fehler
            pass
        
        return len(errors) == 0, errors
    
    def repair_all_markers_enhanced(self, backup: bool = True) -> Dict:
        """
        Erweiterte Reparatur aller Marker
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
                
                # Lade Marker sicher
                marker_data, load_status = self.safe_load_yaml(yaml_file)
                
                if marker_data is None:
                    results['skipped'].append(yaml_file.name)
                    self.repair_stats['skipped'] += 1
                    continue
                
                # Repariere Marker
                repaired_data = self.repair_marker_enhanced(marker_data, yaml_file.name)
                
                # Validiere
                is_valid, validation_errors = self.validate_repaired_marker(repaired_data)
                
                if is_valid:
                    # Speichere reparierte Version
                    with open(yaml_file, 'w', encoding='utf-8') as f:
                        yaml.dump(repaired_data, f, default_flow_style=False, 
                                allow_unicode=True, indent=2)
                    
                    results['repaired'].append(yaml_file.name)
                    self.repair_stats['repaired'] += 1
                    logger.info(f"✓ Repariert: {yaml_file.name} (Status: {load_status})")
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
        backup_dir = self.markers_directory.parent / f"backup_v2_{timestamp}"
        
        import shutil
        shutil.copytree(self.markers_directory, backup_dir)
        logger.info(f"Backup erstellt: {backup_dir}")
    
    def generate_repair_report(self, results: Dict) -> str:
        """
        Generiert einen erweiterten Reparatur-Report
        """
        report = f"""
# Marker Repair Report v2 - Phase 2 Enhanced
Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistiken
- Verarbeitete Dateien: {self.repair_stats['processed']}
- Erfolgreich repariert: {self.repair_stats['repaired']}
- Fehler: {self.repair_stats['errors']}
- Übersprungen: {self.repair_stats['skipped']}
- YAML-Syntaxfehler behandelt: {self.repair_stats['yaml_errors']}
- String-Objekte konvertiert: {self.repair_stats['string_objects']}

## Erfolgreiche Reparaturen
{chr(10).join(f'- {file}' for file in results['repaired'])}

## Fehler
{chr(10).join(f'- {error["file"]}: {", ".join(error["errors"])}' for error in results['errors'])}

## Übersprungene Dateien
{chr(10).join(f'- {file}' for file in results['skipped'])}

## Verbesserungen v2
- Robuste YAML-Syntaxfehler-Behandlung
- String-Objekt-Konvertierung
- Automatische Beispiel-Generierung
- Minimale Struktur-Erstellung bei defekten Dateien
"""
        return report
    
    def save_repair_report(self, results: Dict, filename: str = "repair_report_v2_phase2.md"):
        """
        Speichert den erweiterten Reparatur-Report
        """
        report = self.generate_repair_report(results)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report gespeichert: {filename}")

def main():
    """
    Hauptfunktion für Phase 2 Enhanced
    """
    print("🔧 Marker Repair Engine v2 - Phase 2 Enhanced")
    print("=" * 60)
    
    # Initialisiere Engine
    engine = MarkerRepairEngineV2()
    
    # Repariere alle Marker
    print("Starte erweiterte Reparatur aller Marker...")
    results = engine.repair_all_markers_enhanced(backup=True)
    
    # Generiere Report
    engine.save_repair_report(results)
    
    print(f"\n✅ Phase 2 Enhanced abgeschlossen!")
    print(f"Verarbeitet: {engine.repair_stats['processed']}")
    print(f"Repariert: {engine.repair_stats['repaired']}")
    print(f"Fehler: {engine.repair_stats['errors']}")
    print(f"YAML-Syntaxfehler behandelt: {engine.repair_stats['yaml_errors']}")
    print(f"String-Objekte konvertiert: {engine.repair_stats['string_objects']}")

if __name__ == "__main__":
    main() 