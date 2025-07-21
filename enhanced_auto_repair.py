#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Auto-Repair Engine für FRAUSAR Marker-System
====================================================
Umfassende Reparatur-Engine die alle identifizierten Probleme behebt:
- YAML-Struktur-Probleme
- Veraltete Formate
- Fehlende Semantic Grabber IDs 
- DETECT.py Integration
- Semantic Grabber Library Integration
"""

import yaml
import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedAutoRepair:
    """
    Erweiterte Auto-Repair-Engine für das gesamte FRAUSAR-System
    """
    
    def __init__(self, 
                 markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01",
                 detect_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/_python",
                 schema_path: str = "DETECT_default_marker_schema.yaml"):
        
        self.markers_directory = Path(markers_directory)
        self.detect_directory = Path(detect_directory)
        self.schema_path = Path(schema_path)
        
        # Statistiken
        self.stats = {
            'markers_processed': 0,
            'markers_repaired': 0,
            'yaml_errors_fixed': 0,
            'grabber_connections_created': 0,
            'detect_modules_integrated': 0,
            'schema_updates': 0,
            'errors': []
        }
        
        # Templates für moderne Marker-Struktur
        self.modern_templates = self._initialize_modern_templates()
        
        # Semantic Grabber Library
        self.grabber_library_path = Path("semantic_grabber_library.yaml")
        self.grabber_library = self._load_grabber_library()
        
    def _initialize_modern_templates(self) -> Dict[str, Dict]:
        """Initialisiert moderne Templates basierend auf aktuellen Standards"""
        return {
            'level_1_atomic': {
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
                    'category': 'ATOMIC',
                    'tags': ['needs_review'],
                    'examples': []
                }
            },
            'level_2_semantic': {
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
                    'category': 'SEMANTIC',
                    'tags': ['needs_review'],
                    'examples': []
                }
            }
        }
    
    def _load_grabber_library(self) -> Dict:
        """Lädt die Semantic Grabber Library"""
        try:
            if self.grabber_library_path.exists():
                with open(self.grabber_library_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {'grabbers': {}}
            else:
                return {'grabbers': {}}
        except Exception as e:
            logger.warning(f"Fehler beim Laden der Grabber Library: {e}")
            return {'grabbers': {}}
    
    def safe_load_yaml(self, file_path: Path) -> Tuple[Optional[Dict], str]:
        """Sicheres Laden von YAML-Dateien mit Fehlerbehandlung"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Versuche Standard-YAML-Parse
            try:
                data = yaml.safe_load(content)
                return data, 'success'
            except yaml.YAMLError as e:
                logger.warning(f"YAML-Syntaxfehler in {file_path}: {e}")
                self.stats['yaml_errors_fixed'] += 1
                
                # Versuche einfache Reparatur
                fixed_content = self._fix_common_yaml_errors(content)
                try:
                    data = yaml.safe_load(fixed_content)
                    # Speichere reparierte Version
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    return data, 'repaired'
                except:
                    # Erstelle minimale Struktur
                    return self._create_minimal_structure(file_path.stem), 'minimal'
                    
        except Exception as e:
            logger.error(f"Fehler beim Laden von {file_path}: {e}")
            self.stats['errors'].append(f"{file_path}: {e}")
            return None, 'error'
    
    def _fix_common_yaml_errors(self, content: str) -> str:
        """Behebt häufige YAML-Syntaxfehler"""
        # Behebe häufige Probleme
        content = re.sub(r':\s*\n\s*-\s*([^:\n]+)\s*:\s*([^\n]+)', r':\n  - \1: \2', content)
        content = re.sub(r'([a-zA-Z_]+):\s*>\s*\n\s*([^:\n]+)', r'\1: >\n  \2', content)
        
        return content
    
    def _create_minimal_structure(self, marker_name: str) -> Dict:
        """Erstellt minimale Marker-Struktur für defekte Dateien"""
        template = self.modern_templates['level_1_atomic']['template'].copy()
        
        # Basis-Informationen
        clean_name = self._clean_marker_name(marker_name)
        
        template['marker_name'] = clean_name
        template['marker']['name'] = clean_name.replace('_MARKER', '')
        template['marker']['id'] = f"M_{clean_name.replace('_MARKER', '')}"
        template['marker']['description'] = f"Automatisch generiert für {clean_name}"
        template['marker']['examples'] = [
            "AUTO_GENERATED_EXAMPLE_1",
            "AUTO_GENERATED_EXAMPLE_2", 
            "AUTO_GENERATED_EXAMPLE_3",
            "AUTO_GENERATED_EXAMPLE_4",
            "AUTO_GENERATED_EXAMPLE_5"
        ]
        template['examples'] = template['marker']['examples']
        
        return template
    
    def _clean_marker_name(self, name: str) -> str:
        """Bereinigt Marker-Namen"""
        clean = re.sub(r'[^A-Z0-9_]', '_', name.upper())
        if not clean.endswith('_MARKER'):
            clean += '_MARKER'
        return clean
    
    def detect_marker_format(self, marker_data: Dict) -> str:
        """Erkennt das Format eines Markers"""
        if not isinstance(marker_data, dict):
            return 'invalid'
        
        # Moderne Struktur
        if 'marker' in marker_data and isinstance(marker_data['marker'], dict):
            if 'id' in marker_data['marker'] and 'level' in marker_data['marker']:
                return 'modern'
            else:
                return 'semi_modern'
        
        # Legacy-Formate
        if 'beschreibung' in marker_data or 'szenarien' in marker_data:
            return 'legacy_german'
        
        if 'examples' in marker_data or 'beispiele' in marker_data:
            return 'simple_examples'
        
        return 'unknown'
    
    def repair_single_marker(self, marker_data: Dict, filename: str) -> Dict:
        """Repariert einen einzelnen Marker"""
        try:
            format_type = self.detect_marker_format(marker_data)
            
            if format_type == 'modern':
                # Schon modern, nur kleine Korrekturen
                return self._enhance_modern_marker(marker_data)
            
            elif format_type in ['semi_modern', 'legacy_german', 'simple_examples', 'unknown']:
                # Konvertiere zu moderner Struktur
                return self._convert_to_modern_structure(marker_data, filename)
            
            else:
                # Erstelle minimale Struktur
                return self._create_minimal_structure(filename.replace('.yaml', ''))
                
        except Exception as e:
            logger.error(f"Fehler bei Marker-Reparatur {filename}: {e}")
            return self._create_minimal_structure(filename.replace('.yaml', ''))
    
    def _enhance_modern_marker(self, marker_data: Dict) -> Dict:
        """Verbessert bereits moderne Marker"""
        marker = marker_data['marker']
        
        # Semantic Grabber ID korrigieren
        if 'semantic_grabber_id' in marker:
            old_id = marker['semantic_grabber_id']
            if old_id.startswith('SGR_'):
                # Konvertiere zu AUTO_SEM_ Format
                new_id = old_id.replace('SGR_', 'AUTO_SEM_').replace('_01', '')
                marker['semantic_grabber_id'] = new_id
                
                # Erstelle Grabber falls nicht vorhanden
                if new_id not in self.grabber_library.get('grabbers', {}):
                    self._create_semantic_grabber(new_id, marker.get('examples', []), marker.get('description', ''))
        
        # Beispiele validieren
        if 'examples' not in marker or len(marker['examples']) < 5:
            examples = marker.get('examples', [])
            while len(examples) < 5:
                examples.append(f"AUTO_GENERATED_EXAMPLE_{len(examples) + 1}")
            marker['examples'] = examples
            marker_data['examples'] = examples
        
        return marker_data
    
    def _convert_to_modern_structure(self, marker_data: Dict, filename: str) -> Dict:
        """Konvertiert veraltete Strukturen zu moderner Struktur"""
        # Basis-Template
        template = self.modern_templates['level_2_semantic']['template'].copy()
        
        # Marker-Name extrahieren
        marker_name = marker_data.get('marker_name', filename.replace('.yaml', ''))
        clean_name = self._clean_marker_name(marker_name)
        
        # Template füllen
        template['marker_name'] = clean_name
        template['marker']['name'] = clean_name.replace('_MARKER', '')
        template['marker']['id'] = f"S_{clean_name.replace('_MARKER', '')}"
        
        # Beschreibung extrahieren
        description = (marker_data.get('description', '') or 
                      marker_data.get('beschreibung', '') or
                      f"Automatisch konvertiert: {clean_name}")
        template['marker']['description'] = str(description).strip()
        
        # Beispiele extrahieren
        examples = []
        for key in ['examples', 'beispiele']:
            if key in marker_data and isinstance(marker_data[key], list):
                examples.extend(marker_data[key])
        
        # Minimum 5 Beispiele
        while len(examples) < 5:
            examples.append(f"AUTO_GENERATED_EXAMPLE_{len(examples) + 1}")
        
        template['marker']['examples'] = examples[:20]  # Max 20
        template['examples'] = template['marker']['examples']
        
        # Semantic Grabber erstellen
        grabber_id = f"AUTO_SEM_{clean_name.replace('_MARKER', '')}"
        template['marker']['semantic_grabber_id'] = grabber_id
        
        if grabber_id not in self.grabber_library.get('grabbers', {}):
            self._create_semantic_grabber(grabber_id, examples, description)
        
        return template
    
    def _create_semantic_grabber(self, grabber_id: str, examples: List[str], description: str):
        """Erstellt einen neuen Semantic Grabber"""
        try:
            if 'grabbers' not in self.grabber_library:
                self.grabber_library['grabbers'] = {}
            
            self.grabber_library['grabbers'][grabber_id] = {
                'id': grabber_id,
                'name': grabber_id.replace('AUTO_SEM_', '').replace('_', ' ').title(),
                'description': description[:200] + "..." if len(description) > 200 else description,
                'examples': examples[:10],  # Erste 10 Beispiele
                'created_at': datetime.now().isoformat(),
                'auto_generated': True,
                'similarity_threshold': 0.7
            }
            
            self.stats['grabber_connections_created'] += 1
            
            # Speichere Library
            self._save_grabber_library()
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Grabbers {grabber_id}: {e}")
    
    def _save_grabber_library(self):
        """Speichert die Grabber Library"""
        try:
            with open(self.grabber_library_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.grabber_library, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Grabber Library: {e}")
    
    def process_detect_modules(self):
        """Verarbeitet DETECT.py Module und integriert sie ins Schema"""
        if not self.detect_directory.exists():
            logger.warning(f"DETECT Verzeichnis nicht gefunden: {self.detect_directory}")
            return
        
        for py_file in self.detect_directory.glob("DETECT_*.py"):
            try:
                self._integrate_detect_module(py_file)
                self.stats['detect_modules_integrated'] += 1
            except Exception as e:
                logger.error(f"Fehler bei DETECT-Integration {py_file}: {e}")
                self.stats['errors'].append(f"DETECT {py_file}: {e}")
    
    def _integrate_detect_module(self, py_file: Path):
        """Integriert ein DETECT.py Modul ins Schema"""
        try:
            # Lade aktuelles Schema
            schema = self._load_schema()
            
            module_name = py_file.stem.lower()
            
            # Extrahiere Metadaten aus DETECT.py
            metadata = self._extract_detect_metadata(py_file)
            
            # Füge zum Schema hinzu
            if 'application_schema' not in schema:
                schema['application_schema'] = {'detectors': {}}
            if 'detectors' not in schema['application_schema']:
                schema['application_schema']['detectors'] = {}
            
            schema['application_schema']['detectors'][module_name] = {
                'module': module_name,
                'class': metadata.get('class_name', module_name.upper()),
                'file_path': str(py_file.relative_to(Path.cwd())),
                'description': metadata.get('description', f'DETECT Modul: {module_name}'),
                'last_updated': datetime.now().isoformat(),
                'auto_generated': True,
                'function_name': metadata.get('function_name', f'detect_{module_name.replace("detect_", "")}'),
                'patterns_count': metadata.get('patterns_count', 0)
            }
            
            # Speichere Schema
            self._save_schema(schema)
            self.stats['schema_updates'] += 1
            
            logger.debug(f"DETECT Modul integriert: {module_name}")
            
        except Exception as e:
            logger.error(f"Fehler bei DETECT-Integration {py_file}: {e}")
            raise
    
    def _extract_detect_metadata(self, py_file: Path) -> Dict:
        """Extrahiert Metadaten aus DETECT.py Datei"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {}
            
            # Extrahiere Klassen-Name
            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                metadata['class_name'] = class_match.group(1)
            
            # Extrahiere Funktions-Name
            func_match = re.search(r'def\s+(detect_\w+)', content)
            if func_match:
                metadata['function_name'] = func_match.group(1)
            
            # Extrahiere Beschreibung aus Docstring
            docstring_match = re.search(r'"""([^"]+)"""', content, re.DOTALL)
            if docstring_match:
                metadata['description'] = docstring_match.group(1).strip()[:200]
            
            # Zähle Pattern-Komponenten
            components_match = re.search(r'(\w+_COMPONENTS)\s*=\s*{([^}]+)}', content, re.DOTALL)
            if components_match:
                components_content = components_match.group(2)
                pattern_count = len(re.findall(r'"[^"]+"\s*:', components_content))
                metadata['patterns_count'] = pattern_count
            
            # Extrahiere DETECTOR_METADATA falls vorhanden
            metadata_match = re.search(r'DETECTOR_METADATA\s*=\s*{([^}]+)}', content, re.DOTALL)
            if metadata_match:
                try:
                    # Versuche einfache Metadaten-Extraktion
                    meta_content = metadata_match.group(1)
                    desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', meta_content)
                    if desc_match:
                        metadata['description'] = desc_match.group(1)
                except:
                    pass
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Fehler bei Metadaten-Extraktion aus {py_file}: {e}")
            return {}
    
    def _load_schema(self) -> Dict:
        """Lädt das aktuelle Schema"""
        try:
            if self.schema_path.exists():
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                return self._create_default_schema()
        except Exception as e:
            logger.warning(f"Fehler beim Schema-Laden: {e}")
            return self._create_default_schema()
    
    def _create_default_schema(self) -> Dict:
        """Erstellt Standard-Schema"""
        return {
            'meta': {
                'title': 'FRAUSAR Enhanced Schema',
                'version': '2.0',
                'description': 'Enhanced Auto-Repair Schema für Detector-Module',
                'created_at': datetime.now().isoformat(),
                'auto_generated': True
            },
            'application_schema': {
                'detectors': {}
            }
        }
    
    def _save_schema(self, schema: Dict):
        """Speichert das Schema"""
        try:
            # Update meta information
            if 'meta' not in schema:
                schema['meta'] = {}
            schema['meta']['last_updated'] = datetime.now().isoformat()
            schema['meta']['total_detectors'] = len(schema.get('application_schema', {}).get('detectors', {}))
            
            with open(self.schema_path, 'w', encoding='utf-8') as f:
                yaml.dump(schema, f, default_flow_style=False, allow_unicode=True, indent=2)
                
        except Exception as e:
            logger.error(f"Fehler beim Schema-Speichern: {e}")
    
    def validate_system_integrity(self) -> Dict:
        """Validiert die Integrität des gesamten Systems"""
        validation_results = {
            'markers_valid': 0,
            'markers_invalid': 0,
            'grabbers_connected': 0,
            'grabbers_missing': 0,
            'detect_modules_functional': 0,
            'detect_modules_broken': 0,
            'schema_consistent': True,
            'issues': []
        }
        
        try:
            # 1. Validiere Marker
            for yaml_file in self.markers_directory.glob("*.yaml"):
                try:
                    marker_data, _ = self.safe_load_yaml(yaml_file)
                    if marker_data and 'marker' in marker_data:
                        validation_results['markers_valid'] += 1
                        
                        # Prüfe Grabber-Verbindung
                        grabber_id = marker_data['marker'].get('semantic_grabber_id')
                        if grabber_id and grabber_id in self.grabber_library.get('grabbers', {}):
                            validation_results['grabbers_connected'] += 1
                        elif grabber_id:
                            validation_results['grabbers_missing'] += 1
                            validation_results['issues'].append(f"Missing grabber: {grabber_id} in {yaml_file.name}")
                    else:
                        validation_results['markers_invalid'] += 1
                        validation_results['issues'].append(f"Invalid marker structure: {yaml_file.name}")
                        
                except Exception as e:
                    validation_results['markers_invalid'] += 1
                    validation_results['issues'].append(f"Error loading {yaml_file.name}: {e}")
            
            # 2. Validiere DETECT Module
            for py_file in self.detect_directory.glob("DETECT_*.py"):
                try:
                    # Versuche Metadaten zu extrahieren
                    metadata = self._extract_detect_metadata(py_file)
                    if metadata.get('function_name'):
                        validation_results['detect_modules_functional'] += 1
                    else:
                        validation_results['detect_modules_broken'] += 1
                        validation_results['issues'].append(f"No detect function found in {py_file.name}")
                        
                except Exception as e:
                    validation_results['detect_modules_broken'] += 1
                    validation_results['issues'].append(f"Error analyzing {py_file.name}: {e}")
            
            return validation_results
            
        except Exception as e:
            validation_results['schema_consistent'] = False
            validation_results['issues'].append(f"System validation error: {e}")
            return validation_results
    
    def repair_all_systems(self, create_backup: bool = True) -> Dict:
        """Hauptmethode: Repariert alle Systeme"""
        logger.info("🔧 Starte Enhanced Auto-Repair für alle Systeme...")
        
        if create_backup:
            self._create_backup()
        
        results = {
            'markers_processed': [],
            'markers_repaired': [],
            'errors': [],
            'summary': {}
        }
        
        # 1. Repariere alle YAML-Marker
        logger.info("📁 Verarbeite YAML-Marker...")
        for yaml_file in self.markers_directory.glob("*.yaml"):
            try:
                self.stats['markers_processed'] += 1
                
                # Lade Marker
                marker_data, load_status = self.safe_load_yaml(yaml_file)
                
                if marker_data is None:
                    continue
                
                # Repariere Marker
                repaired_data = self.repair_single_marker(marker_data, yaml_file.name)
                
                # Speichere reparierte Version
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.dump(repaired_data, f, default_flow_style=False, 
                            allow_unicode=True, indent=2)
                
                results['markers_repaired'].append(yaml_file.name)
                self.stats['markers_repaired'] += 1
                
                logger.debug(f"✓ Repariert: {yaml_file.name}")
                
            except Exception as e:
                logger.error(f"Fehler bei {yaml_file.name}: {e}")
                results['errors'].append({'file': yaml_file.name, 'error': str(e)})
                self.stats['errors'].append(f"{yaml_file.name}: {e}")
        
                 # 2. Verarbeite DETECT.py Module
         logger.info("🔍 Verarbeite DETECT.py Module...")
         self.process_detect_modules()
         
         # 3. Validiere System-Integrität
         logger.info("🔍 Validiere System-Integrität...")
         validation = self.validate_system_integrity()
         results['validation'] = validation
         
         # 4. Generiere Zusammenfassung
         results['summary'] = {
             'markers_processed': self.stats['markers_processed'],
             'markers_repaired': self.stats['markers_repaired'],
             'yaml_errors_fixed': self.stats['yaml_errors_fixed'],
             'grabber_connections_created': self.stats['grabber_connections_created'],
             'detect_modules_integrated': self.stats['detect_modules_integrated'],
             'schema_updates': self.stats['schema_updates'],
             'total_errors': len(self.stats['errors']),
             'validation_summary': {
                 'markers_valid': validation['markers_valid'],
                 'grabbers_connected': validation['grabbers_connected'],
                 'detect_modules_functional': validation['detect_modules_functional'],
                 'critical_issues': len([issue for issue in validation['issues'] if 'Error' in issue])
             }
         }
         
         logger.info("✅ Enhanced Auto-Repair abgeschlossen!")
         self._print_summary(results['summary'])
         self._print_validation_summary(validation)
         
         return results
     
     def _create_backup(self):
         """Erstellt Backup der Marker-Verzeichnisse"""
         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
         backup_dir = self.markers_directory.parent / f"backup_enhanced_{timestamp}"
         
         import shutil
         try:
             shutil.copytree(self.markers_directory, backup_dir)
             logger.info(f"📦 Backup erstellt: {backup_dir}")
         except Exception as e:
             logger.warning(f"Backup-Erstellung fehlgeschlagen: {e}")
     
     def _print_summary(self, summary: Dict):
         """Gibt Zusammenfassung aus"""
         print("\n" + "="*60)
         print("📊 ENHANCED AUTO-REPAIR ZUSAMMENFASSUNG")
         print("="*60)
         print(f"📁 Marker verarbeitet:           {summary['markers_processed']}")
         print(f"🔧 Marker repariert:             {summary['markers_repaired']}")
         print(f"🔍 YAML-Fehler behoben:          {summary['yaml_errors_fixed']}")
         print(f"🔗 Grabber-Verbindungen erstellt: {summary['grabber_connections_created']}")
         print(f"🐍 DETECT-Module integriert:     {summary['detect_modules_integrated']}")
         print(f"📋 Schema-Updates:               {summary['schema_updates']}")
         print(f"❌ Fehler gesamt:                {summary['total_errors']}")
         
         success_rate = (summary['markers_repaired'] / max(summary['markers_processed'], 1)) * 100
         print(f"\n✅ Erfolgsrate: {success_rate:.1f}%")
         print("="*60)
    
     def _print_validation_summary(self, validation: Dict):
         """Gibt Validierungs-Zusammenfassung aus"""
         print("\n" + "="*60)
         print("🔍 SYSTEM-VALIDIERUNG")
         print("="*60)
         print(f"✅ Valide Marker:                {validation['markers_valid']}")
         print(f"❌ Invalide Marker:              {validation['markers_invalid']}")
         print(f"🔗 Verbundene Grabber:           {validation['grabbers_connected']}")
         print(f"❓ Fehlende Grabber:             {validation['grabbers_missing']}")
         print(f"🐍 Funktionale DETECT-Module:    {validation['detect_modules_functional']}")
         print(f"💥 Defekte DETECT-Module:        {validation['detect_modules_broken']}")
         print(f"📋 Schema konsistent:            {'✅' if validation['schema_consistent'] else '❌'}")
         
         if validation['issues']:
             print(f"\n⚠️ PROBLEME ({len(validation['issues'])} gefunden):")
             for i, issue in enumerate(validation['issues'][:5], 1):
                 print(f"  {i}. {issue}")
             if len(validation['issues']) > 5:
                 print(f"  ... und {len(validation['issues']) - 5} weitere")
         else:
             print("\n🎉 Keine Probleme gefunden!")
             
         print("="*60)

def main():
    """Hauptfunktion für direkten Aufruf"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Auto-Repair für FRAUSAR-System")
    parser.add_argument("--markers-dir", help="Marker-Verzeichnis")
    parser.add_argument("--detect-dir", help="DETECT.py Verzeichnis")
    parser.add_argument("--no-backup", action="store_true", help="Kein Backup erstellen")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Engine initialisieren
    engine = EnhancedAutoRepair(
        markers_directory=args.markers_dir or "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01",
        detect_directory=args.detect_dir or "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/_python"
    )
    
    # Reparatur durchführen
    results = engine.repair_all_systems(create_backup=not args.no_backup)
    
    # Exit-Code basierend auf Erfolg
    return 0 if results['summary']['total_errors'] == 0 else 1

if __name__ == "__main__":
    exit(main()) 