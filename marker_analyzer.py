#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Marker Analyzer Tool
====================
Analysiert alle Marker-YAML-Dateien und identifiziert:
- Level (1-4) basierend auf Struktur
- Fehlende Pflichtfelder
- Inkonsistenzen
- Problematische Marker
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

class MarkerAnalyzer:
    def __init__(self, marker_directory="../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.marker_dir = Path(marker_directory)
        self.analysis_results = {}
        self.level_templates = self._load_level_templates()
        
    def _load_level_templates(self):
        """Lädt die Level-Vorlagen aus ME_WT_Project_rules"""
        templates = {}
        template_files = {
            1: "ME_WT_Project_rules/level_01_exampl.yaml",
            2: "ME_WT_Project_rules/level_02_example.yaml", 
            3: "ME_WT_Project_rules/level_o3_example.yaml",
            4: "ME_WT_Project_rules/level_04-example.yaml"
        }
        
        for level, file_path in template_files.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, list) and len(content) > 0:
                        templates[level] = content[0]  # Erstes Element der Liste
                    else:
                        templates[level] = content
            except Exception as e:
                print(f"⚠️ Konnte Template Level {level} nicht laden: {e}")
                templates[level] = {}
        
        return templates
    
    def analyze_marker_level(self, marker_data: Dict) -> Optional[int]:
        """
        Identifiziert Level anhand vorhandener Schlüssel:
        - Level 1 (Atomic): Hat 'atomic_pattern', keine 'composed_of'
        - Level 2 (Semantic): Hat 'composed_of' mit type='atomic' 
        - Level 3 (Cluster): Hat 'composed_of' mit type='semantic'
        - Level 4 (Meta): Hat 'composed_of' mit type='cluster'
        """
        # Prüfe explizites Level-Feld
        if 'level' in marker_data:
            level_value = marker_data['level']
            # Konvertiere String zu Integer falls nötig
            if isinstance(level_value, str):
                if level_value.isdigit():
                    return int(level_value)
                elif level_value.lower() == 'atomic':
                    return 1
                elif level_value.lower() == 'semantic':
                    return 2
                elif level_value.lower() == 'cluster':
                    return 3
                elif level_value.lower() in ['meta', 'meta_marker']:
                    return 4
            elif isinstance(level_value, int):
                return level_value
        
        # Level 1: Atomic Marker
        if 'atomic_pattern' in marker_data and 'composed_of' not in marker_data:
            return 1
        
        # Level 2-4: Basierend auf composed_of
        if 'composed_of' in marker_data:
            composed_of = marker_data['composed_of']
            if not isinstance(composed_of, list):
                return None
            
            types = []
            for item in composed_of:
                if isinstance(item, dict) and 'type' in item:
                    types.append(item['type'])
            
            if 'atomic' in types:
                return 2  # Semantic
            elif 'semantic' in types:
                return 3  # Cluster  
            elif 'cluster' in types:
                return 4  # Meta
        
        # Fallback: Versuche anhand ID-Präfix zu erkennen
        marker_id = marker_data.get('id', '')
        if marker_id.startswith('A_'):
            return 1
        elif marker_id.startswith('S_'):
            return 2
        elif marker_id.startswith('C_'):
            return 3
        elif marker_id.startswith('MM_'):
            return 4
        
        return None  # Unbestimmbar
    
    def detect_marker_format(self, marker_data: Dict) -> str:
        """Erkennt das Format/Schema des Markers"""
        if 'input' in marker_data and 'output' in marker_data:
            return 'input_output_format'
        elif 'szenarien' in marker_data or 'dynamik_absicht' in marker_data:
            return 'legacy_detailed_format'
        elif 'pattern' in marker_data and 'semantic_tags' in marker_data:
            return 'modern_pattern_format'
        elif 'atomic_pattern' in marker_data:
            return 'atomic_format'
        elif 'composed_of' in marker_data:
            return 'composed_format'
        elif 'beispiele' in marker_data or 'examples' in marker_data:
            return 'simple_examples_format'
        else:
            return 'unknown_format'
    
    def extract_marker_examples(self, marker_data: Dict) -> List[str]:
        """Extrahiert Beispiele aus verschiedenen Formaten"""
        examples = []
        
        # Standard examples/beispiele
        if 'examples' in marker_data:
            examples.extend(marker_data['examples'])
        if 'beispiele' in marker_data:
            examples.extend(marker_data['beispiele'])
        
        # Input/Output Format
        if isinstance(marker_data, list):
            for item in marker_data:
                if isinstance(item, dict) and 'input' in item:
                    examples.append(item['input'])
        
        # Nested in anderen Strukturen
        for key, value in marker_data.items():
            if isinstance(value, list) and key.lower() in ['beispiele', 'examples', 'patterns']:
                examples.extend([str(v) for v in value if isinstance(v, str)])
        
        return examples
    
    def count_structure_issues(self, marker_data: Dict) -> Dict:
        """Zählt verschiedene Struktur-Probleme"""
        issues = {
            'missing_id': 'id' not in marker_data,
            'missing_name': 'name' not in marker_data and 'marker_name' not in marker_data,
            'missing_description': 'description' not in marker_data and 'beschreibung' not in marker_data,
            'missing_examples': len(self.extract_marker_examples(marker_data)) == 0,
            'inconsistent_naming': False,
            'mixed_languages': False
        }
        
        # Prüfe inkonsistente Benennung
        has_german = any(key in marker_data for key in ['beschreibung', 'beispiele', 'marker_name'])
        has_english = any(key in marker_data for key in ['description', 'examples', 'name'])
        issues['mixed_languages'] = has_german and has_english
        
        return issues
    
    def get_required_fields_for_level(self, level: int) -> List[str]:
        """Gibt Pflichtfelder für ein Level zurück"""
        base_fields = ['id', 'name', 'level', 'description']
        
        if level == 1:
            return base_fields + ['atomic_pattern']
        elif level == 2:
            return base_fields + ['composed_of', 'rules']
        elif level == 3:
            return base_fields + ['composed_of', 'activation_logic']
        elif level == 4:
            return base_fields + ['composed_of', 'trigger_threshold']
        
        return base_fields
    
    def validate_marker_structure(self, marker_data: Dict, detected_level: int) -> Dict:
        """Validiert Marker-Struktur gegen Level-Anforderungen"""
        issues = []
        required_fields = self.get_required_fields_for_level(detected_level)
        
        # Prüfe Pflichtfelder
        missing_fields = []
        for field in required_fields:
            if field not in marker_data:
                missing_fields.append(field)
        
        if missing_fields:
            issues.append(f"Fehlende Pflichtfelder: {', '.join(missing_fields)}")
        
        # Prüfe ID-Format
        marker_id = marker_data.get('id', '')
        expected_prefixes = {1: 'A_', 2: 'S_', 3: 'C_', 4: 'MM_'}
        expected_prefix = expected_prefixes.get(detected_level, '')
        
        if expected_prefix and not marker_id.startswith(expected_prefix):
            issues.append(f"ID sollte mit '{expected_prefix}' beginnen, ist aber '{marker_id}'")
        
        # Level-spezifische Validierung
        if detected_level == 1:
            if 'atomic_pattern' not in marker_data:
                issues.append("Level 1 Marker braucht 'atomic_pattern'")
            elif not isinstance(marker_data['atomic_pattern'], list):
                issues.append("'atomic_pattern' muss eine Liste sein")
        
        elif detected_level >= 2:
            if 'composed_of' not in marker_data:
                issues.append(f"Level {detected_level} Marker braucht 'composed_of'")
            else:
                composed_of = marker_data['composed_of']
                if not isinstance(composed_of, list):
                    issues.append("'composed_of' muss eine Liste sein")
                else:
                    for item in composed_of:
                        if not isinstance(item, dict):
                            issues.append("'composed_of' Einträge müssen Dictionaries sein")
                        elif 'type' not in item or 'marker_ids' not in item:
                            issues.append("'composed_of' Einträge brauchen 'type' und 'marker_ids'")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'missing_fields': missing_fields
        }
    
    def analyze_single_file(self, file_path: Path) -> Dict:
        """Analysiert eine einzelne YAML-Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not content:
                return {
                    'error': 'Leere Datei',
                    'markers': []
                }
            
            # Behandle sowohl einzelne Marker als auch Listen
            if isinstance(content, dict):
                markers = [content]
            elif isinstance(content, list):
                markers = content
            else:
                return {
                    'error': 'Unbekanntes YAML-Format',
                    'markers': []
                }
            
            analyzed_markers = []
            for i, marker_data in enumerate(markers):
                if not isinstance(marker_data, dict):
                    continue
                
                detected_level = self.analyze_marker_level(marker_data)
                validation = self.validate_marker_structure(marker_data, detected_level) if detected_level else {'valid': False, 'issues': ['Level unbestimmbar'], 'missing_fields': []}
                
                # Neue Analyse-Funktionen
                marker_format = self.detect_marker_format(marker_data)
                examples = self.extract_marker_examples(marker_data)
                structure_issues = self.count_structure_issues(marker_data)
                
                analyzed_markers.append({
                    'index': i,
                    'id': marker_data.get('id', marker_data.get('marker_name', f'UNKNOWN_{i}')),
                    'name': marker_data.get('name', marker_data.get('marker_name', 'Unbenannt')),
                    'detected_level': detected_level,
                    'declared_level': marker_data.get('level'),
                    'validation': validation,
                    'format': marker_format,
                    'examples_count': len(examples),
                    'structure_issues': structure_issues
                })
            
            return {
                'markers': analyzed_markers,
                'total_markers': len(analyzed_markers)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'markers': []
            }
    
    def analyze_all_markers(self) -> Dict:
        """Analysiert alle Marker-Dateien im Verzeichnis"""
        print(f"🔍 Analysiere Marker in: {self.marker_dir}")
        
        if not self.marker_dir.exists():
            return {'error': f'Verzeichnis existiert nicht: {self.marker_dir}'}
        
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'marker_directory': str(self.marker_dir),
            'files': {},
            'summary': {
                'total_files': 0,
                'total_markers': 0,
                'level_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 'unknown': 0},
                'validation_summary': {
                    'valid': 0,
                    'invalid': 0,
                    'total_issues': 0
                },
                'common_issues': {},
                'format_distribution': {},
                'structure_issues_summary': {
                    'missing_id': 0,
                    'missing_name': 0,
                    'missing_description': 0,
                    'missing_examples': 0,
                    'mixed_languages': 0
                }
            }
        }
        
        # Scanne alle YAML-Dateien
        yaml_files = list(self.marker_dir.glob("*.yaml")) + list(self.marker_dir.glob("*.yml"))
        
        # Scanne auch Unterordner
        for subfolder in self.marker_dir.iterdir():
            if subfolder.is_dir() and not subfolder.name.startswith('.'):
                yaml_files.extend(subfolder.glob("*.yaml"))
                yaml_files.extend(subfolder.glob("*.yml"))
        
        results['summary']['total_files'] = len(yaml_files)
        
        for file_path in yaml_files:
            relative_path = file_path.relative_to(self.marker_dir)
            print(f"  📄 Analysiere: {relative_path}")
            
            file_analysis = self.analyze_single_file(file_path)
            results['files'][str(relative_path)] = file_analysis
            
            # Update Summary
            if 'markers' in file_analysis:
                for marker in file_analysis['markers']:
                    results['summary']['total_markers'] += 1
                    
                    # Level-Verteilung
                    level = marker['detected_level']
                    if level in [1, 2, 3, 4]:
                        results['summary']['level_distribution'][level] += 1
                    else:
                        results['summary']['level_distribution']['unknown'] += 1
                    
                    # Format-Verteilung
                    marker_format = marker['format']
                    if marker_format not in results['summary']['format_distribution']:
                        results['summary']['format_distribution'][marker_format] = 0
                    results['summary']['format_distribution'][marker_format] += 1
                    
                    # Struktur-Probleme
                    for issue_key, has_issue in marker['structure_issues'].items():
                        if has_issue and issue_key in results['summary']['structure_issues_summary']:
                            results['summary']['structure_issues_summary'][issue_key] += 1
                    
                    # Validierung
                    if marker['validation']['valid']:
                        results['summary']['validation_summary']['valid'] += 1
                    else:
                        results['summary']['validation_summary']['invalid'] += 1
                        results['summary']['validation_summary']['total_issues'] += len(marker['validation']['issues'])
                        
                        # Sammle häufige Probleme
                        for issue in marker['validation']['issues']:
                            if issue not in results['summary']['common_issues']:
                                results['summary']['common_issues'][issue] = 0
                            results['summary']['common_issues'][issue] += 1
        
        self.analysis_results = results
        return results
    
    def generate_report(self, output_file: str = "marker_analysis_report.json"):
        """Generiert einen detaillierten Analysebericht"""
        if not self.analysis_results:
            print("❌ Keine Analyseergebnisse vorhanden. Führe zuerst analyze_all_markers() aus.")
            return
        
        # Speichere JSON-Report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Analysebericht gespeichert: {output_file}")
        
        # Generiere Zusammenfassung
        summary = self.analysis_results['summary']
        
        print("\n" + "="*60)
        print("📊 MARKER-ANALYSE ZUSAMMENFASSUNG")
        print("="*60)
        print(f"📁 Verzeichnis: {self.analysis_results['marker_directory']}")
        print(f"📄 Dateien gescannt: {summary['total_files']}")
        print(f"🎯 Marker gefunden: {summary['total_markers']}")
        
        print(f"\n📈 Level-Verteilung:")
        for level, count in summary['level_distribution'].items():
            if count > 0:
                level_name = {1: 'Atomic', 2: 'Semantic', 3: 'Cluster', 4: 'Meta', 'unknown': 'Unbestimmt'}[level]
                print(f"  Level {level} ({level_name}): {count}")
        
        print(f"\n📋 Format-Verteilung:")
        for format_type, count in summary['format_distribution'].items():
            format_names = {
                'input_output_format': 'Input/Output Training Format',
                'legacy_detailed_format': 'Legacy Detailed Format',
                'modern_pattern_format': 'Modern Pattern Format',
                'atomic_format': 'Atomic Pattern Format',
                'composed_format': 'Composed Marker Format',
                'simple_examples_format': 'Simple Examples Format',
                'unknown_format': 'Unbekanntes Format'
            }
            format_name = format_names.get(format_type, format_type)
            print(f"  {format_name}: {count}")
        
        print(f"\n🔧 Struktur-Probleme:")
        structure_issues = summary['structure_issues_summary']
        for issue, count in structure_issues.items():
            if count > 0:
                issue_names = {
                    'missing_id': 'Fehlende ID',
                    'missing_name': 'Fehlender Name',
                    'missing_description': 'Fehlende Beschreibung',
                    'missing_examples': 'Fehlende Beispiele',
                    'mixed_languages': 'Gemischte Sprachen'
                }
                issue_name = issue_names.get(issue, issue)
                print(f"  {issue_name}: {count}")
        
        print(f"\n✅ Validierung:")
        print(f"  Gültige Marker: {summary['validation_summary']['valid']}")
        print(f"  Problematische Marker: {summary['validation_summary']['invalid']}")
        print(f"  Gesamte Probleme: {summary['validation_summary']['total_issues']}")
        
        if summary['common_issues']:
            print(f"\n⚠️ Häufigste Probleme:")
            sorted_issues = sorted(summary['common_issues'].items(), key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:10]:
                print(f"  {count}x: {issue}")
        
        print("="*60)
    
    def get_problematic_markers(self) -> List[Dict]:
        """Gibt Liste der problematischen Marker zurück"""
        problematic = []
        
        if not self.analysis_results:
            return problematic
        
        for file_path, file_data in self.analysis_results['files'].items():
            if 'markers' in file_data:
                for marker in file_data['markers']:
                    if not marker['validation']['valid'] or marker['detected_level'] is None:
                        problematic.append({
                            'file': file_path,
                            'marker': marker
                        })
        
        return problematic

def main():
    """Hauptfunktion für CLI-Verwendung"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Marker-Analyse Tool')
    parser.add_argument('--directory', '-d', default='../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01',
                       help='Marker-Verzeichnis')
    parser.add_argument('--output', '-o', default='marker_analysis_report.json',
                       help='Output-Datei für Report')
    parser.add_argument('--problematic-only', action='store_true',
                       help='Zeige nur problematische Marker')
    
    args = parser.parse_args()
    
    analyzer = MarkerAnalyzer(args.directory)
    
    print("🚀 Starte Marker-Analyse...")
    results = analyzer.analyze_all_markers()
    
    if 'error' in results:
        print(f"❌ Fehler: {results['error']}")
        return
    
    analyzer.generate_report(args.output)
    
    if args.problematic_only:
        problematic = analyzer.get_problematic_markers()
        print(f"\n🚨 {len(problematic)} problematische Marker gefunden:")
        for item in problematic[:20]:  # Zeige erste 20
            marker = item['marker']
            print(f"  📄 {item['file']} -> {marker['id']}: {', '.join(marker['validation']['issues'])}")

if __name__ == "__main__":
    main() 