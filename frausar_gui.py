#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRAUSAR GUI - Marker Management Interface
==========================================
Benutzerfreundliche GUI für die Verwaltung der Love Scammer Erkennungsmarker
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from pathlib import Path
import re
import json
from detect_creator import create_detect_from_dialog_data
from gui_schema_creator import SchemaCreatorWindow  # KORRIGIERTER IMPORT
from marker_matcherv2 import MarkerMatcherV2 # KORRIGIERTER IMPORT

class FRAUSARAssistant:
    def __init__(self, marker_directory="../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.marker_dir = Path(marker_directory)
        self.pending_changes = []
        self.semantic_grabber_library_path = Path("semantic_grabber_library.yaml")
        self.semantic_grabbers = self._load_semantic_grabbers()
        self.embeddings_cache = {}
        self.update_status_callback = None # Callback für Status-Updates
    
    def set_marker_directory(self, directory):
        """Setzt ein neues Marker-Verzeichnis"""
        self.marker_dir = Path(directory)
        return self.get_marker_list()
    
    def get_marker_list(self):
        """Lädt alle Marker aus Hauptordner und Unterordnern"""
        markers = []
        if not self.marker_dir.exists():
            return markers
        
        # Hauptordner scannen - ALLE unterstützten Dateitypen
        # Text-Dateien
        for file in self.marker_dir.glob("*.txt"):
            markers.append(f"📄 {file.name}")
        
        # YAML-Dateien
        for file in self.marker_dir.glob("*.yaml"):
            markers.append(f"📊 {file.name}")
        
        for file in self.marker_dir.glob("*.yml"):
            markers.append(f"📊 {file.name}")
        
        # JSON-Dateien
        for file in self.marker_dir.glob("*.json"):
            markers.append(f"📊 {file.name}")
        
        # CSV-Dateien
        for file in self.marker_dir.glob("*.csv"):
            markers.append(f"📊 {file.name}")
        
        # Python-Skripte
        for file in self.marker_dir.glob("*.py"):
            markers.append(f"🐍 {file.name}")
        
        # Unterordner scannen (alle direkten Unterordner)
        try:
            for subfolder in self.marker_dir.iterdir():
                if subfolder.is_dir() and not subfolder.name.startswith('.'):
                    folder_name = subfolder.name
                    
                    # Text-Dateien
                    for file in subfolder.glob("*.txt"):
                        markers.append(f"📁 {folder_name}/{file.name}")
                    
                    # Python-Skripte
                    for file in subfolder.glob("*.py"):
                        markers.append(f"🐍 {folder_name}/{file.name}")
                    
                    # JSON/YAML/CSV Dateien
                    for file in subfolder.glob("*.json"):
                        markers.append(f"📊 {folder_name}/{file.name}")
                    
                    for file in subfolder.glob("*.yaml"):
                        markers.append(f"📊 {folder_name}/{file.name}")
                    
                    for file in subfolder.glob("*.yml"):
                        markers.append(f"📊 {folder_name}/{file.name}")
                    
                    for file in subfolder.glob("*.csv"):
                        markers.append(f"📊 {folder_name}/{file.name}")
        except Exception as e:
            print(f"Fehler beim Scannen der Unterordner: {e}")
        
        return sorted(markers)
    
    def read_marker(self, marker_name):
        """Liest Marker-Inhalt aus Hauptordner oder Unterordnern"""
        # Entferne Icon-Präfixe
        clean_name = marker_name
        for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
            if clean_name.startswith(prefix):
                clean_name = clean_name[2:]
                break
        
        # Prüfe ob es ein Unterordner-Pfad ist
        if '/' in clean_name:
            # Unterordner-Datei
            parts = clean_name.split('/', 1)
            folder_name = parts[0]
            file_name = parts[1]
            file_path = self.marker_dir / folder_name / file_name
        else:
            # Hauptordner-Datei
            file_path = self.marker_dir / clean_name
        
        if file_path.exists():
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback für andere Encodings
                try:
                    return file_path.read_text(encoding='latin1')
                except:
                    return f"[Fehler beim Lesen der Datei: {file_path}]"
        return ""
    
    def add_examples_to_marker(self, marker_name, new_examples):
        """Fügt Beispiele zu einem Marker hinzu (verschiedene Formate unterstützt)"""
        content = self.read_marker(marker_name)
        if not content:
            return False
        
        # Entferne Icon-Präfixe für Dateityp-Erkennung
        clean_name = marker_name
        for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
            if clean_name.startswith(prefix):
                clean_name = clean_name[2:]
                break
        
        # Python-Dateien haben andere Struktur
        if clean_name.endswith('.py'):
            # Für Python-Dateien: Füge zu examples Liste hinzu
            examples_pattern = r'(examples\s*=\s*\[)(.*?)(\])'
            match = re.search(examples_pattern, content, re.DOTALL)
            if match:
                new_content = content
                for example in new_examples:
                    if example.strip() and example not in content:
                        formatted_example = f'\n        "{example.strip()}",'
                        insertion_point = match.end(2)
                        new_content = new_content[:insertion_point] + formatted_example + new_content[insertion_point:]
                return new_content
            else:
                # Füge examples-Liste am Ende hinzu
                new_examples_section = '\n\n# Neue Beispiele hinzugefügt\nexamples = [\n'
                for example in new_examples:
                    if example.strip():
                        new_examples_section += f'    "{example.strip()}",\n'
                new_examples_section += ']\n'
                return content + new_examples_section
        
        # CSV-Dateien
        elif clean_name.endswith('.csv'):
            # Für CSV-Dateien: Füge neue Zeilen hinzu
            lines = content.strip().split('\n')
            if lines:
                # Behalte Header bei
                new_content = lines[0] + '\n'
                # Füge existierende Daten hinzu
                if len(lines) > 1:
                    new_content += '\n'.join(lines[1:]) + '\n'
                # Füge neue Beispiele als Zeilen hinzu
                for example in new_examples:
                    if example.strip() and example not in content:
                        new_content += example.strip() + '\n'
                return new_content
            else:
                # Neue CSV mit Header
                new_content = "example\n"
                for example in new_examples:
                    if example.strip():
                        new_content += example.strip() + '\n'
                return new_content
        
        # YAML/JSON Dateien
        elif clean_name.endswith(('.json', '.yaml', '.yml')):
            # Für strukturierte Dateien: Versuche beispiele/examples zu finden
            for pattern in [r'(["\'"]beispiele["\'"]:\s*\[)(.*?)(\])', 
                           r'(["\'"]examples["\'"]:\s*\[)(.*?)(\])']:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    new_content = content
                    for example in new_examples:
                        if example.strip() and example not in content:
                            formatted_example = f',\n        "{example.strip()}"'
                            insertion_point = match.end(2)
                            new_content = new_content[:insertion_point] + formatted_example + new_content[insertion_point:]
                    return new_content
        
        # Standard TXT-Dateien (YAML-Format)
        beispiele_match = re.search(r'(beispiele:\s*\n)(.*?)(?=\n\w+:|$)', content, re.DOTALL)
        if beispiele_match:
            new_content = content
            for example in new_examples:
                if example.strip() and example not in content:
                    formatted_example = f'  - "{example.strip()}"\n'
                    insertion_point = beispiele_match.end(1)
                    new_content = new_content[:insertion_point] + formatted_example + new_content[insertion_point:]
            return new_content
        
        # Fallback: Füge am Ende hinzu
        new_content = content + '\n\n# Neue Beispiele hinzugefügt:\n'
        for example in new_examples:
            if example.strip():
                new_content += f'# - "{example.strip()}"\n'
        
        return new_content
    
    def generate_unified_yaml_for_gpt(self, output_file="marker_unified_for_gpt.yaml"):
        """Generiert eine vereinheitlichte YAML-Datei für GPT-Analyse"""
        import yaml
        from datetime import datetime
        
        # Sammle alle Marker
        all_markers = self.collect_all_markers()
        
        # Erstelle vereinfachte Struktur für GPT
        unified_data = {
            'meta': {
                'title': 'FRAUSAR Marker-System - Komplette Bestandsaufnahme',
                'description': 'Alle Love Scammer Erkennungsmarker in einem einheitlichen Format',
                'generated_at': datetime.now().isoformat(),
                'version': '2.0',
                'total_markers': len(all_markers),
                'purpose': 'GPT-Analyse und Bestandsaufnahme'
            },
            'risk_levels': {
                'green': 'Kein oder nur unkritischer Marker',
                'yellow': '1-2 moderate Marker, erste Drift erkennbar',
                'blinking': '3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation',
                'red': 'Hochrisiko-Kombination, massive Drift/Manipulation'
            },
            'markers': all_markers,
            'statistics': self.analyze_marker_structure()
        }
        
        # Speichere als YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# FRAUSAR Marker-System - Vereinheitlichte Bestandsaufnahme für GPT\n")
            f.write("# Diese Datei enthält ALLE Marker in einem einheitlichen Format\n")
            f.write("# Generiert am: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            f.write("# ====================================================================\n\n")
            yaml.dump(unified_data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
        
        return output_file
    
    def collect_all_markers(self):
        """Sammelt alle Marker aus allen Quellen"""
        markers = {}
        
        # Sammle aus Hauptordner
        if self.marker_dir.exists():
            for file in self.marker_dir.iterdir():
                if file.is_file() and self._is_marker_file(file):
                    content = self.read_marker(file.name)
                    marker_data = self._parse_marker_content(content, file.name)
                    if marker_data:
                        markers[marker_data['name']] = marker_data
        
        # Sammle aus Unterordnern
        try:
            for subfolder in self.marker_dir.iterdir():
                if subfolder.is_dir() and not subfolder.name.startswith('.'):
                    for file in subfolder.iterdir():
                        if file.is_file() and self._is_marker_file(file):
                            try:
                                content = file.read_text(encoding='utf-8')
                                marker_data = self._parse_marker_content(content, file.name)
                                if marker_data:
                                    markers[marker_data['name']] = marker_data
                            except:
                                pass  # Ignoriere Dateien die nicht gelesen werden können
        except Exception as e:
            print(f"Fehler beim Sammeln aus Unterordnern: {e}")
        
        return markers
    
    def _is_marker_file(self, file_path):
        """Prüft ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        # Alle unterstützten Dateitypen
        valid_extensions = ['.txt', '.yaml', '.yml', '.json', '.csv', '.py']
        has_valid_extension = any(name.endswith(ext) for ext in valid_extensions)
        
        # Für YAML, JSON, CSV und TXT Dateien keine Keyword-Prüfung
        if any(name.endswith(ext) for ext in ['.yaml', '.yml', '.json', '.csv', '.txt']):
            return has_valid_extension
        
        # Für Python-Dateien prüfe auf Keywords
        if name.endswith('.py'):
            return any(keyword in name for keyword in ['marker', 'pattern', 'knot', 'spiral'])
        
        return False
    
    def _parse_marker_content(self, content, filename):
        """Parst Marker-Inhalt und extrahiert strukturierte Daten"""
        import re
        
        marker_data = {
            'name': filename.replace('.txt', '').replace('_MARKER', ''),
            'beschreibung': 'Keine Beschreibung verfügbar',
            'beispiele': [],
            'kategorie': 'UNCATEGORIZED',
            'risk_score': 1,
            'tags': []
        }
        
        # Extrahiere Beschreibung
        desc_match = re.search(r'beschreibung:\s*(.+?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            marker_data['beschreibung'] = desc_match.group(1).strip()
        
        # Extrahiere Beispiele
        beispiele_match = re.search(r'beispiele:(.*?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if beispiele_match:
            beispiele_text = beispiele_match.group(1)
            beispiele = re.findall(r'-\s*"([^"]+)"', beispiele_text)
            marker_data['beispiele'] = beispiele
        
        # Extrahiere Tags
        tags_match = re.search(r'tags:\s*\[(.*?)\]', content, re.IGNORECASE)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',')]
            marker_data['tags'] = tags
        
        return marker_data
    
    def analyze_marker_structure(self):
        """Analysiert die Marker-Struktur und gibt Statistiken zurück - immer aktueller Stand"""
        # Sammle Marker neu für aktuelle Analyse
        markers = self.collect_all_markers()
        
        categories = {}
        total_examples = 0
        markers_without_examples = []
        
        for name, data in markers.items():
            category = data.get('kategorie', 'UNCATEGORIZED')
            categories[category] = categories.get(category, 0) + 1
            
            examples = len(data.get('beispiele', []))
            total_examples += examples
            
            if examples == 0:
                markers_without_examples.append(name)
        
        return {
            'total_markers': len(markers),
            'total_examples': total_examples,
            'average_examples_per_marker': round(total_examples / len(markers), 2) if markers else 0,
            'categories': categories,
            'markers_without_examples': markers_without_examples,
            'coverage_score': round((len(markers) - len(markers_without_examples)) / len(markers) * 100, 1) if markers else 0
        }
    
    def validate_yaml_structure(self, file_path):
        """Validiert eine YAML-Datei auf vollständige Struktur"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe auf erforderliche Felder
            required_fields = ['marker_name', 'beschreibung', 'examples', 'kategorie', 'tags', 'semantische_grabber_id']
            issues = []
            
            for field in required_fields:
                if field not in content:
                    issues.append(f"Fehlendes Feld: {field}")
            
            # Prüfe Beispiele-Anzahl
            examples_match = re.search(r'examples:\s*\n(.*?)(?=\n\w+:|$)', content, re.DOTALL)
            if examples_match:
                examples_text = examples_match.group(1)
                example_count = len(re.findall(r'^\s*-\s*"', examples_text, re.MULTILINE))
                if example_count < 10:
                    issues.append(f"Zu wenige Beispiele: {example_count} (mindestens 10 erforderlich)")
            else:
                issues.append("Keine Beispiele gefunden")
            
            # Prüfe marker_name Format
            marker_name_match = re.search(r'marker_name:\s*(\w+)', content)
            if marker_name_match:
                marker_name = marker_name_match.group(1)
                if not marker_name.endswith('_MARKER'):
                    issues.append(f"Marker-Name muss mit '_MARKER' enden: {marker_name}")
            
            # Prüfe Beschreibung Länge
            desc_match = re.search(r'beschreibung:\s*(.+)', content)
            if desc_match:
                description = desc_match.group(1).strip()
                if len(description) < 10:
                    issues.append(f"Beschreibung zu kurz: {len(description)} Zeichen (mindestens 10)")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'file_path': file_path
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Fehler beim Lesen der Datei: {str(e)}"],
                'file_path': file_path
            }
    
    def get_invalid_yaml_markers(self):
        """Sammelt alle YAML-Dateien und prüft ihre Struktur"""
        invalid_markers = []
        
        # Durchsuche alle relevanten Verzeichnisse
        search_dirs = [
            self.marker_dir,
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/fraud",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/emotions",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/tension",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/resonance",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/dynamic_knots",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS",
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/extended_marker_yaml_bundle",
            self.marker_dir.parent / "RELATIONSHIP_MARKERS"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                # Suche nach YAML-Dateien
                for file_path in search_dir.glob("*.yaml"):
                    validation_result = self.validate_yaml_structure(file_path)
                    if not validation_result['valid']:
                        invalid_markers.append(validation_result)
                
                for file_path in search_dir.glob("*.yml"):
                    validation_result = self.validate_yaml_structure(file_path)
                    if not validation_result['valid']:
                        invalid_markers.append(validation_result)
        
        return invalid_markers
    
    def merge_yaml_files(self, file_paths, output_filename="merged_markers.yaml"):
        """Vereint mehrere YAML-Dateien zu einer großen strukturierten Datei"""
        merged_content = {
            'meta': {
                'title': 'Vereinte Marker-Sammlung',
                'created_at': datetime.now().isoformat(),
                'source_files': [str(p) for p in file_paths],
                'total_files': len(file_paths)
            },
            'markers': {}
        }
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrahiere Marker-Daten
                marker_data = self._parse_marker_content(content, file_path.name)
                if marker_data:
                    # Verwende Dateiname als Schlüssel wenn kein marker_name
                    marker_key = marker_data.get('name', file_path.stem)
                    merged_content['markers'][marker_key] = {
                        'marker_name': marker_data.get('name', marker_key),
                        'beschreibung': marker_data.get('beschreibung', ''),
                        'examples': marker_data.get('beispiele', []),
                        'kategorie': marker_data.get('kategorie', 'UNCATEGORIZED'),
                        'tags': marker_data.get('tags', []),
                        'semantische_grabber_id': marker_data.get('semantische_grabber_id', ''),
                        'source_file': str(file_path),
                        'merged_at': datetime.now().isoformat()
                    }
                    
            except Exception as e:
                print(f"Fehler beim Verarbeiten von {file_path}: {e}")
        
        # Speichere vereinte Datei
        import yaml
        output_path = Path(output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Vereinte Marker-Sammlung\n")
            f.write(f"# Erstellt am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Anzahl Quell-Dateien: {len(file_paths)}\n")
            f.write("# ====================================================================\n\n")
            yaml.dump(merged_content, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return output_path
    
    def identify_marker_gaps(self):
        """Identifiziert Lücken in der Marker-Abdeckung - immer aktueller Stand"""
        # Sammle Marker neu für aktuelle Analyse
        markers = self.collect_all_markers()
        
        # Bekannte Scam-Kategorien die abgedeckt sein sollten
        required_categories = {
            'love_bombing': 'Übermäßige Zuneigung und Komplimente',
            'gaslighting': 'Realitätsverzerrung und Verwirrung',
            'financial_request': 'Geldforderungen und finanzielle Manipulation',
            'isolation': 'Soziale Isolation vom Umfeld',
            'future_faking': 'Falsche Zukunftsversprechen',
            'emotional_manipulation': 'Emotionale Erpressung',
            'identity_fraud': 'Gefälschte Identitäten',
            'urgency_pressure': 'Zeitdruck und Dringlichkeit',
            'victim_playing': 'Opferrolle spielen',
            'triangulation': 'Dritte Personen einbeziehen'
        }
        
        # Prüfe welche Kategorien fehlen
        covered = set()
        for marker_name, data in markers.items():
            for category in required_categories:
                if category in marker_name.lower() or category in str(data.get('tags', [])).lower():
                    covered.add(category)
        
        missing = set(required_categories.keys()) - covered
        
        gaps = {
            'missing_categories': [
                {'category': cat, 'description': required_categories[cat]} 
                for cat in missing
            ],
            'low_coverage_markers': [
                {'name': name, 'examples': len(data.get('beispiele', []))}
                for name, data in markers.items() 
                if len(data.get('beispiele', [])) < 3
            ],
            'recommendations': self._generate_recommendations(markers, missing)
        }
        
        return gaps
    
    def _generate_recommendations(self, markers, missing_categories):
        """Generiert Empfehlungen basierend auf der Analyse"""
        recommendations = []
        
        # Empfehlungen für fehlende Kategorien
        if missing_categories:
            recommendations.append(f"Erstelle Marker für: {', '.join(missing_categories)}")
        
        # Empfehlungen für schwache Marker
        weak_markers = [name for name, data in markers.items() 
                       if len(data.get('beispiele', [])) < 5]
        if weak_markers:
            recommendations.append(f"Füge mehr Beispiele hinzu zu: {', '.join(weak_markers[:3])}...")
        
        # Allgemeine Empfehlungen
        if len(markers) < 50:
            recommendations.append("Erweitere das System um spezifischere Marker")
        
        return recommendations
    
    def _load_semantic_grabbers(self):
        """Lädt die Semantic Grabber Library"""
        if self.semantic_grabber_library_path.exists():
            try:
                import yaml
                with open(self.semantic_grabber_library_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                grabbers = data.get('semantic_grabbers', {})
                
                # Konvertiere alte 'patterns' zu 'examples' für Konsistenz
                for gid, grabber in grabbers.items():
                    if 'patterns' in grabber and 'examples' not in grabber:
                        grabber['examples'] = grabber['patterns']
                    elif 'patterns' not in grabber and 'examples' in grabber:
                        grabber['patterns'] = grabber['examples']  # Behalte patterns für Rückwärtskompatibilität
                
                return grabbers
            except:
                return {}
        return {}
    
    def _save_semantic_grabbers(self):
        """Speichert die Semantic Grabber Library"""
        import yaml
        data = {'semantic_grabbers': self.semantic_grabbers}
        with open(self.semantic_grabber_library_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def _generate_grabber_id(self, base_name):
        """Generiert eine neue eindeutige Grabber ID nach Projekt-Standard"""
        import uuid
        from datetime import datetime
        
        # Entferne _MARKER Suffix falls vorhanden
        clean_name = base_name.upper().replace('_MARKER', '').replace(' ', '_')[:20]
        
        # Generiere ID nach Standard: AUTO_SEM_<datum>_<nummer>
        date_str = datetime.now().strftime('%Y%m%d')
        unique_num = str(uuid.uuid4())[:4].upper()
        
        return f"AUTO_SEM_{date_str}_{unique_num}"
    
    def _calculate_similarity(self, text1, text2):
        """Berechnet semantische Ähnlichkeit zwischen zwei Texten"""
        try:
            # Vereinfachte Ähnlichkeitsberechnung (kann später durch Embeddings ersetzt werden)
            import difflib
            return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        except:
            return 0.0
    
    def find_similar_grabber(self, examples, threshold=0.72):
        """Findet ähnliche Semantic Grabber basierend auf Beispielen"""
        if not examples:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        # Vergleiche mit allen existierenden Grabbern
        for grabber_id, grabber_data in self.semantic_grabbers.items():
            # Unterstütze sowohl 'examples' als auch 'patterns' für Rückwärtskompatibilität
            grabber_examples = grabber_data.get('examples', grabber_data.get('patterns', []))
            
            # Berechne durchschnittliche Ähnlichkeit
            total_score = 0
            comparisons = 0
            
            for new_ex in examples[:5]:  # Nur erste 5 für Performance
                for grab_ex in grabber_examples[:5]:
                    score = self._calculate_similarity(new_ex, grab_ex)
                    total_score += score
                    comparisons += 1
            
            if comparisons > 0:
                avg_score = total_score / comparisons
                if avg_score > best_score:
                    best_score = avg_score
                    best_match = grabber_id
        
        if best_score >= threshold:
            return best_match, best_score
        
        return None, best_score
    
    def create_semantic_grabber(self, marker_name, examples, description=""):
        """Erstellt einen neuen Semantic Grabber"""
        # Prüfe ob ähnlicher Grabber existiert
        similar_id, similarity = self.find_similar_grabber(examples)
        
        if similar_id and similarity >= 0.85:
            # Sehr ähnlich - schlage Merge vor
            return {
                'action': 'merge_suggestion',
                'existing_id': similar_id,
                'similarity': similarity
            }
        elif similar_id and similarity >= 0.72:
            # Ähnlich genug - verwende existierenden
            return {
                'action': 'use_existing',
                'grabber_id': similar_id,
                'similarity': similarity
            }
        else:
            # Erstelle neuen Grabber
            new_id = self._generate_grabber_id(marker_name)
            self.semantic_grabbers[new_id] = {
                'beschreibung': description or f"Automatisch erkannt aus {marker_name}",
                'examples': examples[:10],  # Verwende 'examples' statt 'patterns'
                'patterns': examples[:10],  # Behalte patterns für Rückwärtskompatibilität
                'created_from': marker_name,
                'created_at': datetime.now().isoformat()
            }
            self._save_semantic_grabbers()
            
            return {
                'action': 'created_new',
                'grabber_id': new_id
            }
    
    def merge_grabbers(self, grabber_ids, new_name=None):
        """Vereint mehrere Grabber zu einem"""
        if len(grabber_ids) < 2:
            return False
        
        # Sammle alle Patterns/Examples
        all_examples = []
        descriptions = []
        
        for gid in grabber_ids:
            if gid in self.semantic_grabbers:
                grabber = self.semantic_grabbers[gid]
                # Unterstütze sowohl 'examples' als auch 'patterns'
                examples = grabber.get('examples', grabber.get('patterns', []))
                all_examples.extend(examples)
                descriptions.append(grabber.get('beschreibung', ''))
        
        # Entferne Duplikate
        unique_examples = list(dict.fromkeys(all_examples))
        
        # Erstelle neuen Grabber
        merged_id = new_name or f"MERGED_{grabber_ids[0]}"
        self.semantic_grabbers[merged_id] = {
            'beschreibung': f"Vereint aus: {', '.join(descriptions[:3])}",
            'examples': unique_examples[:20],  # Verwende 'examples'
            'patterns': unique_examples[:20],  # Behalte patterns für Rückwärtskompatibilität
            'merged_from': grabber_ids,
            'created_at': datetime.now().isoformat()
        }
        
        # Lösche alte Grabber
        for gid in grabber_ids:
            if gid in self.semantic_grabbers and gid != merged_id:
                del self.semantic_grabbers[gid]
        
        self._save_semantic_grabbers()
        return True
    
    def analyze_grabber_overlaps(self, threshold=0.85):
        """Analysiert Überschneidungen zwischen Grabbern"""
        overlaps = []
        grabber_ids = list(self.semantic_grabbers.keys())
        
        for i, id1 in enumerate(grabber_ids):
            for id2 in grabber_ids[i+1:]:
                # Unterstütze sowohl 'examples' als auch 'patterns'
                examples1 = self.semantic_grabbers[id1].get('examples', self.semantic_grabbers[id1].get('patterns', []))
                examples2 = self.semantic_grabbers[id2].get('examples', self.semantic_grabbers[id2].get('patterns', []))
                
                # Berechne Ähnlichkeit
                if examples1 and examples2:
                    _, similarity = self.find_similar_grabber(examples1[:5])
                    
                    if similarity >= threshold:
                        overlaps.append({
                            'grabber1': id1,
                            'grabber2': id2,
                            'similarity': similarity,
                            'recommendation': 'merge' if similarity > 0.9 else 'review'
                        })
        
        return overlaps
    
    def convert_yaml_to_json(self, yaml_files, output_same_folder=True, indent=2):
        """Konvertiert YAML-Dateien zu JSON"""
        try:
            from ruamel.yaml import YAML
        except ImportError:
            # Fallback zu standard yaml
            import yaml as yaml_module
            yaml = None
        else:
            yaml = YAML(typ="safe")
            yaml.preserve_quotes = True
        
        results = []
        errors = []
        
        for yaml_file in yaml_files:
            try:
                yaml_path = Path(yaml_file)
                
                # Lade YAML
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    if yaml:
                        # ruamel.yaml - kann mehrere Dokumente laden
                        docs = list(yaml.load_all(f))
                        data = docs[0] if len(docs) == 1 else docs
                    else:
                        # standard yaml
                        data = yaml_module.safe_load(f)
                
                # Bestimme Output-Pfad
                if output_same_folder:
                    json_path = yaml_path.with_suffix('.json')
                else:
                    json_dir = yaml_path.parent / "json_out"
                    json_dir.mkdir(exist_ok=True)
                    json_path = json_dir / (yaml_path.stem + '.json')
                
                # Schreibe JSON
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=indent)
                
                results.append({
                    'yaml_file': str(yaml_path),
                    'json_file': str(json_path),
                    'status': 'success'
                })
                
            except Exception as e:
                errors.append({
                    'file': str(yaml_file),
                    'error': str(e)
                })
        
        return {
            'converted': results,
            'errors': errors,
            'total': len(yaml_files),
            'success': len(results),
            'failed': len(errors)
        }
    
    def find_yaml_files(self, directory=None):
        """Findet alle YAML-Dateien im Projekt"""
        if directory is None:
            directory = self.marker_dir.parent
        
        yaml_files = []
        search_dirs = [
            directory,
            self.marker_dir,
            self.marker_dir.parent / "Former_NEW_MARKER_FOLDERS",
            self.marker_dir.parent / "RELATIONSHIP_MARKERS",
            self.marker_dir.parent / "MARKERBOOK_YAML_CANVAS"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                yaml_files.extend(search_dir.rglob("*.yaml"))
                yaml_files.extend(search_dir.rglob("*.yml"))
        
        # Entferne Duplikate und sortiere
        yaml_files = sorted(list(set(yaml_files)))
        return yaml_files
    
    def generate_unified_python_detectors(self, output_file="unified_detectors.py"):
        """Sammelt alle Python-Detector-Dateien und führt sie in einer einzigen Datei zusammen."""
        from datetime import datetime
        
        header = f'''"""
Unified Python Detectors
========================
This file is auto-generated by the FRAUSAR Marker Assistant.
It combines all Python-based detectors found in the marker directories.

Generated at: {datetime.now().isoformat()}
"""

# ====================================================================\n\n
'''
        
        all_content = [header]
        
        # Finde alle Python-Dateien rekursiv
        try:
            py_files = sorted(list(self.marker_dir.rglob("*.py")))
        except Exception as e:
            print(f"Error finding python files: {e}")
            py_files = [] # Continue with empty list

        for py_file in py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                relative_path = "N/A"
                try:
                    relative_path = py_file.relative_to(self.marker_dir.parent)
                except ValueError:
                    relative_path = py_file.name

                separator = f'''
# ====================================================================
# START OF FILE: {relative_path}
# ====================================================================
'''
                all_content.append(separator)
                all_content.append(content)
                
                separator_end = f'''
# ====================================================================
# END OF FILE: {relative_path}
# ====================================================================
\n\n
'''
                all_content.append(separator_end)
            except Exception as e:
                print(f"Could not read file {py_file}: {e}")

        # Speichere als Python-Datei
        output_path = Path(output_file)
        output_path.write_text("\n".join(all_content), encoding='utf-8')

        return str(output_path)

class FRAUSARGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 FRAUSAR Marker Assistant")
        # self.root.geometry("1200x800") # Diese Zeile entfernen

        self.assistant = FRAUSARAssistant()
        self.assistant.update_status_callback = self.update_status # Callback setzen
        self.pending_changes = []
        
        self.setup_gui()
    
    def setup_gui(self):
        # Hauptrahmen
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titel
        title_label = ttk.Label(main_frame, text="🤖 FRAUSAR Marker Assistant", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Obere Leiste für alle Buttons
        top_button_panel = ttk.Frame(main_frame)
        top_button_panel.pack(fill=tk.X, pady=(0, 10), padx=5)

        # Container für die Button-Gruppen
        groups_container = ttk.Frame(top_button_panel)
        groups_container.pack()

        # Einzelne Gruppen-Frames, die horizontal angeordnet werden
        group1 = ttk.LabelFrame(groups_container, text="🚀 Aktionen")
        group1.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)
        
        group2 = ttk.LabelFrame(groups_container, text="📊 Analyse")
        group2.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)

        group3 = ttk.LabelFrame(groups_container, text="🔧 Automatisierung")
        group3.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)

        group4 = ttk.LabelFrame(groups_container, text="📁 Datei-Operationen")
        group4.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)
        
        group5 = ttk.LabelFrame(groups_container, text="🛠️ Tools")
        group5.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)

        # Buttons den Gruppen zuweisen (vorher in approval_frame)
        ttk.Button(group1, text="➕ Neuen Marker erstellen", command=self.create_new_marker_dialog).pack(fill=tk.X, pady=2, padx=5)
        
        # NEUER BUTTON FÜR SCHEMA-CREATOR
        ttk.Button(group1, text="📈 Neues Analyse-Schema", command=self.open_schema_creator).pack(fill=tk.X, pady=2, padx=5)

        ttk.Button(group1, text="🔍 DETECT.py erstellen", command=self.create_detect_dialog).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group1, text="✅ Genehmigen", command=self.approve_suggestions).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group1, text="❌ Ablehnen", command=self.reject_suggestions).pack(fill=tk.X, pady=2, padx=5)

        ttk.Button(group2, text="🤖 GPT-YAML generieren", command=self.generate_gpt_yaml).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group2, text="🐍 Python Detectors generieren", command=self.generate_gpt_python).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group2, text="📊 Struktur analysieren", command=self.analyze_structure).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group2, text="🔍 Lücken identifizieren", command=self.identify_gaps).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group2, text="🧲 Grabber analysieren", command=self.analyze_grabbers).pack(fill=tk.X, pady=2, padx=5)
        
        ttk.Button(group3, text="🔧 Auto-Repair Markers", command=self.auto_repair_markers).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group3, text="🔄 Refresh Detectors", command=self.refresh_detectors).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group3, text="🔄 Grabber optimieren", command=self.optimize_grabbers).pack(fill=tk.X, pady=2, padx=5)

        ttk.Button(group4, text="🔀 YAML → JSON konvertieren", command=self.yaml_to_json_dialog).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group4, text="🔄 YAML-Dateien zusammenführen", command=self.merge_yaml_files_dialog).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group4, text="🔍 YAML-Struktur prüfen", command=self.validate_yaml_structure_dialog).pack(fill=tk.X, pady=2, padx=5)

        ttk.Button(group5, text="📝 Beispiele hinzufügen", command=self.add_examples_dialog).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(group5, text="📄 Grabber Library öffnen", command=self.open_grabber_library).pack(fill=tk.X, pady=2, padx=5)

        # Hauptbereich mit 2 Spalten
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Marker-Liste (schmaler)
        left_frame = ttk.LabelFrame(content_frame, text="📋 Marker-Liste", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 5))
        
        # Verzeichnis-Auswahl Button
        dir_frame = ttk.Frame(left_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.current_dir_label = ttk.Label(dir_frame, text=f"📁 {self.assistant.marker_dir}", 
                                          font=('Arial', 9), foreground="gray")
        self.current_dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="📂 Verzeichnis wählen", 
                  command=self.choose_directory).pack(side=tk.RIGHT)
        
        # Suchfeld
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_markers)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Clear-Button
        ttk.Button(search_frame, text="✖", width=3,
                  command=lambda: self.search_var.set("")).pack(side=tk.RIGHT, padx=(2, 0))
        
        self.marker_listbox = tk.Listbox(left_frame, width=25, height=20) # Breite von 30 auf 25 reduziert
        self.marker_listbox.pack(fill=tk.BOTH, expand=True)
        self.marker_listbox.bind('<<ListboxSelect>>', self.on_marker_select)
        
        marker_buttons = ttk.Frame(left_frame)
        marker_buttons.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(marker_buttons, text="🔄 Aktualisieren", 
                  command=self.refresh_marker_list).pack(side=tk.LEFT, padx=(0, 5))
        
        # Rechter Bereich für Viewer und Chat (vorher "middle_frame")
        right_content_frame = ttk.LabelFrame(content_frame, text="📄 Marker-Details & Chat", padding="5")
        right_content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Notebook für Chat und Marker-Inhalt
        self.middle_notebook = ttk.Notebook(right_content_frame)
        self.middle_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Chat-Tab (minimiert)
        chat_tab = ttk.Frame(self.middle_notebook)
        self.middle_notebook.add(chat_tab, text="💬 Chat")
        
        self.chat_display = scrolledtext.ScrolledText(chat_tab, height=8, state='disabled')  # Von 20 auf 8 reduziert
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Marker-Content-Tab
        content_tab = ttk.Frame(self.middle_notebook)
        self.middle_notebook.add(content_tab, text="📄 Marker-Inhalt")
        
        # Marker-Info-Header
        marker_info_frame = ttk.Frame(content_tab)
        marker_info_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.current_marker_info = ttk.Label(marker_info_frame, text="Kein Marker ausgewählt", 
                                           font=('Arial', 10, 'bold'))
        self.current_marker_info.pack(side=tk.LEFT)
        
        ttk.Button(marker_info_frame, text="✏️ Bearbeiten", 
                  command=self.edit_current_marker).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(marker_info_frame, text="🗑️ Löschen", 
                  command=self.delete_current_marker).pack(side=tk.RIGHT)
        
        # Marker-Content-Viewer
        self.marker_content_display = scrolledtext.ScrolledText(content_tab, font=('Consolas', 10))
        self.marker_content_display.pack(fill=tk.BOTH, expand=True)
        
        # Chat-Eingabe (minimiert)
        chat_input_frame = ttk.Frame(right_content_frame)
        chat_input_frame.pack(fill=tk.X)
        
        self.chat_entry = tk.Text(chat_input_frame, height=2)  # Von 4 auf 2 reduziert
        self.chat_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Control-Return>', self.send_chat_message)
        
        send_button_frame = ttk.Frame(chat_input_frame)
        send_button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(send_button_frame, text="📤", width=4,
                  command=self.send_chat_message).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(send_button_frame, text="📁", width=4,
                  command=self.create_file_from_chat).pack(fill=tk.X)
        
        # Status Text und Log-Bereich (unten links oder in einem neuen Bereich)
        status_frame = ttk.LabelFrame(left_frame, text="📝 Status Log", padding="5")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.status_text = scrolledtext.ScrolledText(status_frame, height=6)
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Initialisierung
        self.refresh_marker_list()

        # NEUER BEREICH FÜR SCHEMA-ANALYSE
        schema_analysis_frame = ttk.LabelFrame(groups_container, text="📈 Schema-Analyse")
        schema_analysis_frame.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.N, fill=tk.Y)

        self.schema_var = tk.StringVar()
        self.schema_combo = ttk.Combobox(schema_analysis_frame, textvariable=self.schema_var, state="readonly", width=30)
        self.schema_combo.pack(fill=tk.X, pady=2, padx=5)
        self.schema_combo.set("Kein Schema ausgewählt")

        ttk.Button(schema_analysis_frame, text="🔄 Schemata neu laden", command=self.load_analysis_schemas).pack(fill=tk.X, pady=2, padx=5)
        ttk.Button(schema_analysis_frame, text="🚀 Analyse mit Schema starten", command=self.run_schema_analysis).pack(fill=tk.X, pady=2, padx=5)
    
    def choose_directory(self):
        """Öffnet Dialog zur Verzeichnisauswahl"""
        from tkinter import filedialog
        
        # Öffne Verzeichnis-Dialog
        selected_dir = filedialog.askdirectory(
            title="Wähle ein Verzeichnis mit Marker-Dateien",
            initialdir=str(self.assistant.marker_dir.parent)
        )
        
        if selected_dir:
            # Setze neues Verzeichnis
            self.assistant.set_marker_directory(selected_dir)
            
            # Update Label
            self.current_dir_label.config(text=f"📁 {selected_dir}")
            
            # Lade Marker neu
            self.refresh_marker_list()
            
            # Zeige Info
            self.add_chat_message("🤖 Assistant", 
                                f"Verzeichnis gewechselt!\n\n"
                                f"📁 Neues Verzeichnis: {selected_dir}\n"
                                f"📊 Gefundene Dateien: {len(self.all_markers)}\n\n"
                                f"Alle YAML, JSON, TXT und CSV Dateien wurden geladen.")
    
    def refresh_marker_list(self):
        self.marker_listbox.delete(0, tk.END)
        self.all_markers = self.assistant.get_marker_list()  # Speichere alle Marker
        
        # Wende Filter an, falls vorhanden
        if hasattr(self, 'search_var') and self.search_var.get():
            self.filter_markers()
        else:
            for marker in self.all_markers:
                self.marker_listbox.insert(tk.END, marker)
        
        self.update_status(f"📊 {len(self.all_markers)} Marker geladen")
    
    def filter_markers(self, *args):
        """Filtert die Marker-Liste basierend auf dem Suchtext"""
        search_text = self.search_var.get().lower()
        
        # Lösche aktuelle Liste
        self.marker_listbox.delete(0, tk.END)
        
        if not search_text:
            # Zeige alle Marker wenn kein Suchtext
            for marker in self.all_markers:
                self.marker_listbox.insert(tk.END, marker)
        else:
            # Filtere Marker
            filtered_markers = []
            for marker in self.all_markers:
                # Suche in Marker-Namen (ohne Icons)
                clean_name = marker
                for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
                    if clean_name.startswith(prefix):
                        clean_name = clean_name[2:]
                        break
                
                if search_text in clean_name.lower():
                    filtered_markers.append(marker)
            
            # Zeige gefilterte Marker
            for marker in filtered_markers:
                self.marker_listbox.insert(tk.END, marker)
            
            # Update Status mit Anzahl
            if filtered_markers:
                self.update_status(f"🔍 {len(filtered_markers)} von {len(self.all_markers)} Markern gefunden")
            else:
                self.update_status(f"🔍 Keine Marker gefunden für '{search_text}'")
    
    def on_marker_select(self, event):
        selection = self.marker_listbox.curselection()
        if selection:
            marker_name = self.marker_listbox.get(selection[0])
            self.current_marker = marker_name
            
            # Sofort Marker-Inhalt anzeigen
            self.show_marker_content(marker_name)
            
            # Automatisch zum Marker-Inhalt-Tab wechseln
            self.middle_notebook.select(1)  # Index 1 ist der Marker-Inhalt-Tab
    
    def show_marker_content(self, marker_name):
        """Zeigt den Marker-Inhalt im Viewer an"""
        try:
            content = self.assistant.read_marker(marker_name)
            
            # Update Marker-Info
            file_type = "🔍 Unbekannt"
            if marker_name.startswith('📄'):
                file_type = "📄 Text-Marker"
            elif marker_name.startswith('🐍'):
                file_type = "🐍 Python-Skript"
            elif marker_name.startswith('📊'):
                file_type = "📊 Strukturierte Daten"
            elif marker_name.startswith('📁'):
                file_type = "📁 Unterordner-Marker"
            
            # Zähle Beispiele abhängig vom Format
            example_count = 0
            if '.py' in marker_name:
                example_count = len(re.findall(r'"[^"]*"', content))
            elif '.json' in marker_name:
                example_count = content.count('"examples"') + content.count('"beispiele"')
            elif '.csv' in marker_name:
                # Für CSV zähle die Zeilen (minus Header)
                lines = content.strip().split('\n')
                example_count = max(0, len(lines) - 1)
            elif '.yaml' in marker_name or '.yml' in marker_name:
                # Für YAML zähle die Beispiele
                example_count = len(re.findall(r'^\s*-\s*["\']', content, re.MULTILINE))
            else:
                example_count = len(re.findall(r'- "', content))
            
            info_text = f"{file_type} | {example_count} Beispiele | {len(content.splitlines())} Zeilen"
            self.current_marker_info.config(text=info_text)
            
            # Zeige Content im Viewer
            self.marker_content_display.delete(1.0, tk.END)
            self.marker_content_display.insert(1.0, content)
            
        except Exception as e:
            self.current_marker_info.config(text=f"❌ Fehler beim Laden: {str(e)}")
            self.marker_content_display.delete(1.0, tk.END)
            self.marker_content_display.insert(1.0, f"Fehler beim Laden des Markers:\n{str(e)}")
    
    def edit_current_marker(self):
        """Öffnet Editor für aktuellen Marker"""
        if not hasattr(self, 'current_marker') or not self.current_marker:
            messagebox.showwarning("Warnung", "Kein Marker ausgewählt!")
            return
        
        # Content aus dem Viewer holen
        current_content = self.marker_content_display.get(1.0, tk.END).strip()
        
        # Editor-Dialog öffnen
        dialog = tk.Toplevel(self.root)
        dialog.title(f"✏️ Marker bearbeiten: {self.current_marker}")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Bearbeite: {self.current_marker}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Editor
        editor = scrolledtext.ScrolledText(main_frame, font=('Consolas', 10))
        editor.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        editor.insert(1.0, current_content)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_changes():
            new_content = editor.get(1.0, tk.END).strip()
            
            # Zur Genehmigung hinzufügen
            self.pending_changes.append({
                'type': 'edit_marker',
                'marker_name': self.current_marker,
                'old_content': current_content,
                'new_content': new_content,
                'description': f"Marker '{self.current_marker}' bearbeiten"
            })
            
            self.update_status(f"✅ Änderungen an '{self.current_marker}' zur Genehmigung vorgeschlagen")
            self.add_chat_message("🤖 Assistant", 
                                f"Änderungen an '{self.current_marker}' vorgeschlagen!\n"
                                f"⏳ Warte auf deine Genehmigung")
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="💾 Speichern", command=save_changes).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def delete_current_marker(self):
        """Löscht den aktuell ausgewählten Marker"""
        if not hasattr(self, 'current_marker') or not self.current_marker:
            messagebox.showwarning("Warnung", "Kein Marker ausgewählt!")
            return
        
        # Bestätigungsdialog
        result = messagebox.askyesno("Marker löschen", 
                                    f"Möchtest du wirklich den Marker\n'{self.current_marker}'\nlöschen?\n\n"
                                    "Diese Aktion kann nicht rückgängig gemacht werden!")
        
        if result:
            # Zur Genehmigung hinzufügen
            self.pending_changes.append({
                'type': 'delete_marker',
                'marker_name': self.current_marker,
                'description': f"Marker '{self.current_marker}' löschen"
            })
            
            self.update_status(f"🗑️ Löschung von '{self.current_marker}' zur Genehmigung vorgeschlagen")
            self.add_chat_message("🤖 Assistant", 
                                f"Löschung von '{self.current_marker}' vorgeschlagen!\n"
                                f"⚠️ Der Marker wird nach deiner Genehmigung gelöscht.\n"
                                f"⏳ Warte auf deine Genehmigung")
            
            # Leere die Anzeige
            self.marker_content_display.delete(1.0, tk.END)
            self.current_marker_info.config(text="Marker wird gelöscht...")
    
    def create_file_from_chat(self):
        """Erstellt Datei aus Chat-Eingabe"""
        message = self.chat_entry.get(1.0, tk.END).strip()
        if not message:
            messagebox.showwarning("Warnung", "Keine Eingabe im Chat-Feld!")
            return
        
        # Prüfe ob es Code-Blöcke gibt
        if "```" in message:
            # Code-Block extrahieren
            code_blocks = re.findall(r'```(?:yaml|txt|py|json)?\n?(.*?)\n?```', message, re.DOTALL)
            if code_blocks:
                code_content = code_blocks[0].strip()
            else:
                code_content = message
        else:
            code_content = message
        
        # Dialog für Datei-Details
        dialog = tk.Toplevel(self.root)
        dialog.title("📁 Datei aus Chat erstellen")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dateiname
        ttk.Label(main_frame, text="Dateiname:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        filename_frame = ttk.Frame(main_frame)
        filename_frame.pack(fill=tk.X, pady=(5, 15))
        
        filename_entry = ttk.Entry(filename_frame, font=('Arial', 10))
        filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Dateityp-Auswahl mit intelligenter Vorhersage
        predicted_extension = ".txt"  # Default
        if "marker:" in code_content.lower() or "beispiele:" in code_content.lower():
            predicted_extension = ".yaml"
        elif "def " in code_content or "import " in code_content or "class " in code_content:
            predicted_extension = ".py"
        elif ("{" in code_content and "}" in code_content) or code_content.strip().startswith('['):
            predicted_extension = ".json"
        
        extension_var = tk.StringVar(value=predicted_extension)
        extension_combo = ttk.Combobox(filename_frame, textvariable=extension_var, 
                                      values=[".txt", ".yaml", ".py", ".json"], width=10, state="readonly")
        extension_combo.pack(side=tk.RIGHT)
        
        # Erklärung der Vorhersage
        prediction_label = ttk.Label(main_frame, text=f"💡 Vorhersage: {predicted_extension} (du kannst es ändern)", 
                                    font=('Arial', 9), foreground="gray")
        prediction_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Ordner-Auswahl
        ttk.Label(main_frame, text="Zielordner:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        
        folder_var = tk.StringVar(value="AUTO")
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Radiobutton(folder_frame, text="�� Automatisch wählen", variable=folder_var, value="AUTO").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="📁 ALL_NEWMARKER01", variable=folder_var, value="ALL_NEWMARKER01").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="📁 fraud", variable=folder_var, value="fraud").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="📁 emotions", variable=folder_var, value="emotions").pack(anchor=tk.W)
        ttk.Radiobutton(folder_frame, text="📁 resonance", variable=folder_var, value="resonance").pack(anchor=tk.W)
        
        # Content-Preview
        ttk.Label(main_frame, text="Inhalt:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        content_preview = scrolledtext.ScrolledText(main_frame, height=15, font=('Consolas', 9))
        content_preview.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        content_preview.insert(1.0, code_content)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def create_file():
            filename = filename_entry.get().strip()
            extension = extension_var.get()
            folder = folder_var.get()
            content = content_preview.get(1.0, tk.END).strip()
            
            if not filename:
                messagebox.showerror("Fehler", "Dateiname erforderlich!")
                return
            
            # Vollständiger Dateiname
            if not filename.endswith(extension):
                full_filename = filename + extension
            else:
                full_filename = filename
            
            # Ordner bestimmen
            if folder == "AUTO":
                if "fraud" in filename.lower() or "scam" in filename.lower():
                    target_folder = "fraud"
                elif "emotion" in filename.lower() or "gefühl" in filename.lower():
                    target_folder = "emotions"
                elif "resona" in filename.lower():
                    target_folder = "resonance"
                else:
                    target_folder = "ALL_NEWMARKER01"
            else:
                target_folder = folder
            
            # Zur Genehmigung hinzufügen
            self.pending_changes.append({
                'type': 'create_file',
                'filename': full_filename,
                'folder': target_folder,
                'content': content,
                'description': f"Neue Datei '{full_filename}' in '{target_folder}' erstellen"
            })
            
            self.update_status(f"✅ Datei '{full_filename}' zur Genehmigung vorgeschlagen")
            self.add_chat_message("🤖 Assistant", 
                                f"Datei '{full_filename}' erstellt!\n"
                                f"📁 Zielordner: {target_folder}\n"
                                f"⏳ Warte auf deine Genehmigung")
            
            # Chat leeren
            self.chat_entry.delete(1.0, tk.END)
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="📁 Erstellen", command=create_file).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def add_chat_message(self, sender, message):
        self.chat_display.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}:\n{message}\n{'-'*40}\n"
        
        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def send_chat_message(self, event=None):
        message = self.chat_entry.get(1.0, tk.END).strip()
        if not message:
            return
        
        self.add_chat_message("👤 Du", message)
        self.chat_entry.delete(1.0, tk.END)
        
        # Verarbeite Nachricht
        self.process_chat_message(message)
    
    def process_chat_message(self, message):
        message_lower = message.lower()
        
        if "beispiel" in message_lower:
            # Prüfe ob es sich um Beispiele handelt
            if '\n' in message and any(c in message for c in ['"', "'", ':']):
                self.add_chat_message("🤖 Assistant", 
                                    "Das sehen aus wie Beispiele! Zu welchem Marker soll ich sie hinzufügen?\n"
                                    "Wähle einen Marker aus der Liste oder erstelle einen neuen.")
                # Speichere Beispiele für später
                self.temp_examples = [line.strip().strip('"\'') for line in message.split('\n') if line.strip()]
            else:
                self.add_chat_message("🤖 Assistant", 
                                    "Gerne helfe ich dir mit Beispielen! Verwende den Button 'Beispiele hinzufügen' "
                                    "oder gib sie direkt hier ein (ein Beispiel pro Zeile).")
        
        elif "marker" in message_lower and ("neu" in message_lower or "erstell" in message_lower):
            self.add_chat_message("🤖 Assistant", 
                                "Perfekt! Klicke auf '➕ Neu' um einen neuen Marker zu erstellen, "
                                "oder beschreibe mir, was der neue Marker erkennen soll.")
        
        elif hasattr(self, 'temp_examples') and hasattr(self, 'current_marker'):
            # Benutzer hat Marker nach Beispielen gewählt
            self.add_examples_to_current_marker(self.temp_examples)
            delattr(self, 'temp_examples')
        
        else:
            self.add_chat_message("🤖 Assistant", 
                                f"Verstanden! Hier sind deine Optionen:\n\n"
                                f"📋 Marker verwalten:\n"
                                f"• Wähle einen Marker aus der Liste\n"
                                f"• Klicke '➕ Neu' für neue Marker\n"
                                f"• Verwende 'Beispiele hinzufügen'\n\n"
                                f"💬 Oder schreibe:\n"
                                f"• 'Beispiele hinzufügen'\n"
                                f"• 'Neuer Marker'\n"
                                f"• Beispiele direkt (ein pro Zeile)")
    
    def create_new_marker_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("🆕 Neuen Marker erstellen")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Notebook für verschiedene Eingabemethoden
        notebook = ttk.Notebook(dialog, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Formular-Eingabe (klassisch)
        form_tab = ttk.Frame(notebook)
        notebook.add(form_tab, text="📝 Formular")
        
        # Name
        ttk.Label(form_tab, text="Marker-Name:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        name_entry = ttk.Entry(form_tab, width=60, font=('Arial', 10))
        name_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Beschreibung
        ttk.Label(form_tab, text="Beschreibung:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        desc_text = tk.Text(form_tab, height=5, font=('Arial', 10))
        desc_text.pack(fill=tk.X, pady=(5, 15))
        
        # Beispiele
        ttk.Label(form_tab, text="Beispiele (ein Beispiel pro Zeile):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        examples_text = scrolledtext.ScrolledText(form_tab, height=12, font=('Arial', 10))
        examples_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        
        # Tab 2: YAML/Python-Import
        yaml_tab = ttk.Frame(notebook)
        notebook.add(yaml_tab, text="📋 YAML/Python Import")
        
        ttk.Label(yaml_tab, text="Füge deinen YAML-formatierten Marker oder Python-Code hier ein:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(yaml_tab, text="(Das System erkennt automatisch Name, Beschreibung, Beispiele und Semantic Grabber)", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        yaml_text = scrolledtext.ScrolledText(yaml_tab, height=20, font=('Consolas', 10))
        yaml_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Beispiel einfügen
        yaml_example = """BOUNDARY_SETTING_MARKER:
  beschreibung: >
    Klarheit und Kommunikation eigener Grenzen, Selbstschutz.
  beispiele:
    - "Hey, ich schaffe es heute Abend nicht."
    - "Ich möchte über dieses Thema jetzt nicht sprechen."
    - "Das geht mir zu schnell. Ich brauche mehr Zeit."
"""
        yaml_text.insert(1.0, yaml_example)
        
        # Tab 3: Multi-Import
        multi_tab = ttk.Frame(notebook)
        notebook.add(multi_tab, text="📚 Multi-Import")
        
        ttk.Label(multi_tab, text="Füge mehrere YAML-Marker auf einmal ein:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        ttk.Label(multi_tab, text="(Trenne verschiedene Marker durch eine Leerzeile oder '---')", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(0, 10))
        
        multi_text = scrolledtext.ScrolledText(multi_tab, height=20, font=('Consolas', 10))
        multi_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def create_from_form():
            """Erstellt Marker aus Formular-Eingabe"""
            name = name_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            examples = [ex.strip() for ex in examples_text.get(1.0, tk.END).strip().split('\n') if ex.strip()]
            
            if not name or not description:
                messagebox.showerror("Fehler", "Name und Beschreibung sind erforderlich!")
                return
            
            self._create_single_marker(name, description, examples)
            dialog.destroy()
        
        def create_from_yaml():
            """Erstellt Marker aus YAML-Eingabe"""
            yaml_content = yaml_text.get(1.0, tk.END).strip()
            if not yaml_content:
                messagebox.showerror("Fehler", "Kein YAML-Inhalt eingegeben!")
                return
            
            try:
                parsed = self._parse_yaml_marker(yaml_content)
                if parsed:
                    # Zeige Info über Semantic Grabber wenn vorhanden
                    if 'grabber_info' in parsed:
                        self.add_chat_message("🤖 Assistant", f"Semantic Grabber: {parsed['grabber_info']}")
                    
                    self._create_single_marker(
                        parsed['name'], 
                        parsed['description'], 
                        parsed['examples'],
                        parsed.get('semantic_grabber_id'),
                        parsed.get('is_python', False),
                        parsed.get('raw_code')
                    )
                    dialog.destroy()
                else:
                    messagebox.showerror("Fehler", "Konnte YAML/Python nicht parsen!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Parsen: {str(e)}")
        
        def create_multi():
            """Erstellt mehrere Marker aus Multi-Import"""
            multi_content = multi_text.get(1.0, tk.END).strip()
            if not multi_content:
                messagebox.showerror("Fehler", "Kein Inhalt eingegeben!")
                return
            
            # Teile in einzelne Marker auf
            markers = self._split_multi_yaml(multi_content)
            
            if not markers:
                messagebox.showerror("Fehler", "Keine gültigen Marker gefunden!")
                return
            
            # Erstelle alle Marker
            created = 0
            for marker_yaml in markers:
                try:
                    parsed = self._parse_yaml_marker(marker_yaml)
                    if parsed:
                        self._create_single_marker(
                            parsed['name'],
                            parsed['description'],
                            parsed['examples'],
                            parsed.get('semantic_grabber_id'),
                            parsed.get('is_python', False),
                            parsed.get('raw_code')
                        )
                        created += 1
                except:
                    continue
            
            if created > 0:
                messagebox.showinfo("Erfolg", f"{created} Marker erfolgreich erstellt!")
                dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Keine Marker konnten erstellt werden!")
        
        # Buttons je nach aktivem Tab
        def update_buttons(*args):
            current_tab = notebook.index(notebook.select())
            
            # Entferne alte Buttons
            for widget in button_frame.winfo_children():
                widget.destroy()
            
            if current_tab == 0:  # Formular
                ttk.Button(button_frame, text="📁 Erstellen", command=create_from_form).pack(side=tk.RIGHT, padx=(10, 0))
            elif current_tab == 1:  # YAML/Python
                ttk.Button(button_frame, text="📁 Aus YAML/Python erstellen", command=create_from_yaml).pack(side=tk.RIGHT, padx=(10, 0))
            elif current_tab == 2:  # Multi
                ttk.Button(button_frame, text="📚 Alle erstellen", command=create_multi).pack(side=tk.RIGHT, padx=(10, 0))
            
            ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
        
        notebook.bind("<<NotebookTabChanged>>", update_buttons)
        update_buttons()  # Initial
    
    def _parse_yaml_marker(self, yaml_content):
        """Parst YAML/Python-Content und extrahiert Marker-Daten"""
        import yaml
        import re
        
        # Prüfe ob es Python-Code ist
        if 'def ' in yaml_content or 'class ' in yaml_content or 'import ' in yaml_content:
            return self._parse_python_marker(yaml_content)
        
        # Versuche zuerst als reines YAML zu parsen
        try:
            data = yaml.safe_load(yaml_content)
            # NEU: Unterstützung für Marker-Listen (z.B. \"- id: NAME_MARKER\")
            if isinstance(data, list):
                # Wir verarbeiten nur den ersten Eintrag – ein Import soll genau einen Marker repräsentieren
                if data and isinstance(data[0], dict):
                    marker_dict = data[0]
                    marker_name = marker_dict.get('id') or marker_dict.get('marker') or marker_dict.get('marker_name') or 'UNKNOWN_MARKER'
                    description = marker_dict.get('beschreibung') or marker_dict.get('description', '')
                    examples = marker_dict.get('beispiele') or marker_dict.get('examples', [])
                    rules = marker_dict.get('rules', [])
                    result = {
                        'name': marker_name,
                        'description': description.strip() if isinstance(description, str) else description,
                        'examples': examples,
                        'rules': rules,
                        'semantic_grabber_id': marker_dict.get('semantische_grabber_id') or marker_dict.get('semantic_grabber_id')
                    }
                    # Erzeuge bzw. verknüpfe Semantic-Grabber analog zur bisherigen Logik
                    if not result['semantic_grabber_id'] and result['examples']:
                        grabber_result = self.assistant.create_semantic_grabber(
                            marker_name,
                            result['examples'],
                            result['description']
                        )
                        if grabber_result['action'] == 'use_existing':
                            result['semantic_grabber_id'] = grabber_result['grabber_id']
                            result['grabber_info'] = f"Automatisch verknüpft (Ähnlichkeit: {grabber_result['similarity']:.2%})"
                        elif grabber_result['action'] == 'created_new':
                            result['semantic_grabber_id'] = grabber_result['grabber_id']
                            result['grabber_info'] = "Neuer Semantic Grabber erstellt"
                        elif grabber_result['action'] == 'merge_suggestion':
                            result['grabber_info'] = f"Sehr ähnlich zu {grabber_result['existing_id']} - Merge empfohlen"
                    return result

            if isinstance(data, dict):
                # Prüfe auf verschiedene mögliche Feldnamen für den Marker-Namen
                if any(k in data for k in ['marker', 'marker_name', 'id']):
                    marker_name = data.get('marker') or data.get('marker_name') or data.get('id') or 'UNKNOWN_MARKER'
                    description = data.get('beschreibung') or data.get('description', '')
                    result = {
                        'name': marker_name,
                        'description': description.strip() if isinstance(description, str) else description,
                        'examples': data.get('beispiele') or data.get('examples', []),
                        'rules': data.get('rules', []),
                        'semantic_grabber_id': data.get('semantische_grabber_id') or data.get('semantic_grabber_id')
                    }
                else:
                    # Alternatives Format: NAME als Key
                    marker_name = list(data.keys())[0]
                    marker_data = data[marker_name]
                    description = marker_data.get('beschreibung') or marker_data.get('description', '')

                    result = {
                        'name': marker_name,
                        'description': description.strip() if isinstance(description, str) else description,
                        'examples': marker_data.get('beispiele') or marker_data.get('examples', []),
                        'rules': marker_data.get('rules', []),
                        'semantic_grabber_id': marker_data.get('semantische_grabber_id') or marker_data.get('semantic_grabber_id')
                    }

                # Wenn kein Grabber angegeben, versuche einen zu finden/erstellen
                if not result['semantic_grabber_id'] and result['examples']:
                    grabber_result = self.assistant.create_semantic_grabber(
                        result['name'],
                        result['examples'],
                        result['description']
                    )
                    if grabber_result['action'] == 'use_existing':
                        result['semantic_grabber_id'] = grabber_result['grabber_id']
                        result['grabber_info'] = f"Automatisch verknüpft (Ähnlichkeit: {grabber_result['similarity']:.2%})"
                    elif grabber_result['action'] == 'created_new':
                        result['semantic_grabber_id'] = grabber_result['grabber_id']
                        result['grabber_info'] = "Neuer Semantic Grabber erstellt"
                    elif grabber_result['action'] == 'merge_suggestion':
                        result['grabber_info'] = f"Sehr ähnlich zu {grabber_result['existing_id']} - Merge empfohlen"

                return result
        except:
            pass
        
        # Fallback: Manuelle Extraktion
        lines = yaml_content.split('\n')
        marker_name = None
        description = ""
        examples = []
        
        # Finde Marker-Namen
        for line in lines:
            if line.strip() and not line.startswith(' ') and ':' in line:
                marker_name = line.split(':')[0].strip()
                break
        
        # Extrahiere Beschreibung
        desc_match = re.search(r'beschreibung:\s*>?\s*\n?\s*(.+?)(?=\n\s*\w+:|$)', yaml_content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
        
        # Extrahiere Beispiele
        in_examples = False
        for line in lines:
            if 'beispiele:' in line.lower():
                in_examples = True
                continue
            if in_examples:
                if line.strip().startswith('-'):
                    example = line.strip()[1:].strip().strip('"\'')
                    if example:
                        examples.append(example)
                elif line.strip() and not line.startswith(' '):
                    break
        
        if marker_name:
            # NEUE KORREKTUR: 'rules' Sektion korrekt parsen
            rules = []
            rules_match = re.search(r'rules:(.*?)(?=\n\w+:|$)', yaml_content, re.IGNORECASE | re.DOTALL)
            if rules_match:
                rules_text = rules_match.group(1)
                # Finde alle 'type' und 'value' Paare
                rule_items = re.findall(r'-\s*type:\s*(\w+)\s*\n\s*value:\s*"([^"]+)"', rules_text, re.IGNORECASE)
                for r_type, r_value in rule_items:
                    rules.append({'type': r_type, 'value': r_value})

            return {
                'name': marker_name,
                'description': description,
                'examples': examples,
                'rules': rules # Hinzugefügte Regel-Daten
            }
        
        return None
    
    def _parse_python_marker(self, python_content):
        """Parst Python-Code und extrahiert Marker-Daten"""
        import re
        
        # Extrahiere Marker-Namen aus Klassennamen oder Variablen
        class_match = re.search(r'class\s+(\w+)', python_content)
        var_match = re.search(r'(\w+_MARKER)\s*=', python_content)
        
        marker_name = None
        if class_match:
            marker_name = class_match.group(1)
        elif var_match:
            marker_name = var_match.group(1)
        else:
            # Versuche aus Dateinamen zu raten
            marker_name = "PYTHON_MARKER"
        
        # Extrahiere Beschreibung aus Docstring
        description = ""
        docstring_match = re.search(r'"""(.*?)"""', python_content, re.DOTALL)
        if docstring_match:
            description = docstring_match.group(1).strip()
        
        # Extrahiere Beispiele aus Listen oder Arrays
        examples = []
        
        # Suche nach examples = [...] oder patterns = [...]
        list_pattern = r'(?:examples|patterns|beispiele)\s*=\s*\[(.*?)\]'
        list_match = re.search(list_pattern, python_content, re.DOTALL)
        if list_match:
            content = list_match.group(1)
            # Extrahiere Strings
            examples = re.findall(r'["\']([^"\']+)["\']', content)
        
        # Suche nach Pattern-Definitionen in Dictionaries
        if not examples:
            dict_pattern = r'["\']pattern["\']:\s*r?["\']([^"\']+)["\']'
            examples = re.findall(dict_pattern, python_content)
        
        result = {
            'name': marker_name,
            'description': description or f"Python-basierter Marker: {marker_name}",
            'examples': examples,
            'is_python': True,
            'raw_code': python_content  # vollständiger Code, um ihn 1:1 zu übernehmen
        }
        
        # Semantic Grabber für Python-Marker
        if examples:
            grabber_result = self.assistant.create_semantic_grabber(
                marker_name,
                examples,
                description
            )
            
            if grabber_result['action'] in ['use_existing', 'created_new']:
                result['semantic_grabber_id'] = grabber_result['grabber_id']
                result['grabber_info'] = grabber_result.get('grabber_info', 'Semantic Grabber zugewiesen')
        
        return result
    
    def _split_multi_yaml(self, content):
        """Teilt Multi-YAML in einzelne Marker auf - verbesserte Version"""
        import yaml
        import re
        
        markers = []
        
        # Methode 1: Durch --- getrennt
        if '---' in content:
            parts = content.split('---')
            for part in parts:
                if part.strip():
                    markers.append(part.strip())
            return markers
        
        # Methode 2: Erkennung durch "marker:" oder "- marker:" Pattern
        # Flexibler Parser für verschiedene YAML-Formate
        marker_pattern = re.compile(r'^[\s-]*(?:marker|id):\s*\w+', re.MULTILINE)
        matches = list(marker_pattern.finditer(content))
        
        if len(matches) > 1:
            # Mehrere Marker gefunden - teile sie auf
            for i, match in enumerate(matches):
                start = match.start()
                # Finde das Ende (nächster Marker oder Ende des Contents)
                if i < len(matches) - 1:
                    end = matches[i + 1].start()
                    # Entferne führendes "- " vom nächsten Marker
                    while end > 0 and content[end-1] in ['-', ' ', '\n']:
                        end -= 1
                else:
                    end = len(content)
                
                marker_content = content[start:end].strip()
                # Entferne führendes "- " wenn vorhanden
                if marker_content.startswith('- '):
                    marker_content = marker_content[2:]
                elif marker_content.startswith('-'):
                    marker_content = marker_content[1:].strip()
                
                markers.append(marker_content)
        
        # Methode 3: Versuche als YAML-Liste zu parsen
        elif not markers:
            try:
                # Versuche zuerst als normales YAML
                data = yaml.safe_load(content)
                if isinstance(data, list):
                    # Es ist eine Liste von Markern
                    for item in data:
                        if isinstance(item, dict):
                            # Konvertiere zurück zu YAML-String
                            yaml_str = yaml.dump(item, default_flow_style=False, allow_unicode=True)
                            markers.append(yaml_str.strip())
                elif isinstance(data, dict):
                    # Einzelner Marker als Dict
                    markers.append(content)
            except:
                # Methode 4: Suche nach Einrückungsmustern
                lines = content.split('\n')
                current_marker = []
                in_marker = False
                
                for line in lines:
                    # Erkenne Marker-Start durch "marker:" am Zeilenanfang (mit möglicher Einrückung)
                    if re.match(r'^[\s-]*marker:', line):
                        if current_marker:
                            # Speichere vorherigen Marker
                            marker_text = '\n'.join(current_marker).strip()
                            if marker_text.startswith('- '):
                                marker_text = marker_text[2:]
                            markers.append(marker_text)
                        current_marker = [line]
                        in_marker = True
                    elif in_marker:
                        current_marker.append(line)
                
                # Letzten Marker hinzufügen
                if current_marker:
                    marker_text = '\n'.join(current_marker).strip()
                    if marker_text.startswith('- '):
                        marker_text = marker_text[2:]
                    markers.append(marker_text)
        
        # Wenn immer noch keine Marker gefunden, behandle als einzelnen Marker
        if not markers and content.strip():
            markers.append(content)
        
        # Bereinige die Marker
        cleaned_markers = []
        for marker in markers:
            # Entferne leere Zeilen am Anfang/Ende
            cleaned = marker.strip()
            if cleaned:
                cleaned_markers.append(cleaned)
        
        return cleaned_markers
    
    def _create_single_marker(self, name, description, examples, semantic_grabber_id=None, is_python=False, raw_code=None):
        """Erstellt einen einzelnen Marker mit Semantic Grabber Support nach Projekt-Standard"""
        # Stelle sicher dass der Name den Konventionen entspricht
        name = name.upper().replace(' ', '_')
        if not name.endswith("_MARKER"):
            name = f"{name}_MARKER"
        
        # Entscheide Dateierweiterung basierend auf Typ
        file_extension = ".py" if is_python else ".yaml"  # Projekt-Standard
        # Python-Dateien landen zur Ordnung in einem Unterordner '_python'
        filename = ("_python/" + name + file_extension) if is_python else (name + file_extension)
        
        if is_python:
            # Wenn vollständiger Code geliefert wurde, übernehme diesen
            if raw_code:
                template = raw_code.strip()
            else:
                # Fallback: generiere Template
                template = f'''"""
{name} - Semantic Marker
{description}
"""

import re

class {name}:
    """
    {description}
    """
    
    examples = [
'''
                for example in examples:
                    if example.strip():
                        template += f'        "{example.strip()}",\n'
                template += f'''    ]
    
    patterns = [
        re.compile(r"(muster.*wird.*ergänzt)", re.IGNORECASE)
    ]
    
    semantic_grabber_id = "{semantic_grabber_id or 'AUTO_GENERATED'}"
    
    def match(self, text):
        """Prüft ob der Text zum Marker passt"""
        for pattern in self.patterns:
            if pattern.search(text):
                return True
        return False
'''
        else:
            # YAML Template nach Projekt-Standard
            template = f"""# {name} - Semantic Marker
marker_name: {name}
beschreibung: >
  {description}
beispiele:
"""
            
            for example in examples:
                if example.strip():
                    template += f'  - "{example.strip()}"\n'
            
            # Semantic Grabber ID ist Pflichtfeld nach Projekt-Standard
            if not semantic_grabber_id:
                # Erstelle automatisch einen Grabber wenn keiner vorhanden
                grabber_result = self.assistant.create_semantic_grabber(name, examples, description)
                if grabber_result['action'] in ['use_existing', 'created_new']:
                    semantic_grabber_id = grabber_result['grabber_id']
                else:
                    # Fallback: Generiere neue ID
                    semantic_grabber_id = self.assistant._generate_grabber_id(name)
            
            template += f"\nsemantische_grabber_id: {semantic_grabber_id}\n"
            
            # Zusätzliche Metadaten
            template += f"""
metadata:
  created_at: {datetime.now().isoformat()}
  created_by: FRAUSAR_GUI_v2
  version: 1.0
  tags: [neu_erstellt, needs_review]
"""
        
        # Zur Genehmigung hinzufügen
        self.pending_changes.append({
            'type': 'create_file',
            'filename': filename,
            'folder': 'ALL_NEWMARKER01',
            'content': template,
            'description': f"Neuen Marker '{name}' erstellen"
        })
        
        self.update_status(f"✅ Marker '{name}' zur Genehmigung vorgeschlagen")
        self.add_chat_message("🤖 Assistant", 
                            f"Marker '{name}' erstellt!\n"
                            f"📋 Beschreibung: {description[:100]}...\n"
                            f"📊 {len(examples)} Beispiele hinzugefügt\n"
                            f"⏳ Warte auf deine Genehmigung")
    
    def create_detect_dialog(self):
        """Dialog für die Erstellung von DETECT.py Modulen"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔍 DETECT.py Modul erstellen")
        dialog.geometry("800x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header mit Erklärung
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="🔍 DETECT.py Modul erstellen", 
                 font=('Arial', 16, 'bold')).pack(anchor=tk.W)
        
        info_text = ("DETECT.py Module sind funktionale Erkennungsmodule für die semantische Analyse langer Texte.\n"
                    "Sie werden automatisch ins Schema integriert und sind robust und konsistent.")
        ttk.Label(header_frame, text=info_text, 
                 font=('Arial', 10), foreground='gray', wraplength=750).pack(anchor=tk.W, pady=(5, 0))
        
        # Formular-Bereich
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Modulname
        ttk.Label(form_frame, text="Modulname:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        name_entry = ttk.Entry(form_frame, width=60, font=('Arial', 10))
        name_entry.pack(fill=tk.X, pady=(5, 5))
        ttk.Label(form_frame, text="Wird automatisch zu DETECT_[NAME] formatiert", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
        
        # Beschreibung
        ttk.Label(form_frame, text="Beschreibung:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(15, 0))
        desc_text = tk.Text(form_frame, height=4, font=('Arial', 10))
        desc_text.pack(fill=tk.X, pady=(5, 5))
        ttk.Label(form_frame, text="Beschreibe was das Modul erkennen soll (z.B. 'Hinhaltemanöver', 'Emotional Manipulation')", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
        
        # Erkennungsmuster
        ttk.Label(form_frame, text="Erkennungsmuster:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(15, 0))
        patterns_text = scrolledtext.ScrolledText(form_frame, height=12, font=('Arial', 10))
        patterns_text.pack(fill=tk.BOTH, expand=True, pady=(5, 5))
        
        # Beispiel einfügen
        example_patterns = """vielleicht später
schauen wir mal
mal sehen wie es läuft
bin mir nicht sicher
müssen wir spontan entscheiden"""
        patterns_text.insert(1.0, example_patterns)
        
        ttk.Label(form_frame, text="Ein Erkennungsmuster pro Zeile. Diese werden in semantische Komponenten gruppiert.", 
                 font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
        
        # Erweiterte Optionen
        advanced_frame = ttk.LabelFrame(form_frame, text="🔧 Erweiterte Optionen", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Semantic Grabber ID
        grabber_frame = ttk.Frame(advanced_frame)
        grabber_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(grabber_frame, text="Semantic Grabber ID (optional):").pack(side=tk.LEFT)
        grabber_entry = ttk.Entry(grabber_frame, width=30)
        grabber_entry.pack(side=tk.RIGHT)
        
        # Detection Threshold
        threshold_frame = ttk.Frame(advanced_frame)
        threshold_frame.pack(fill=tk.X)
        
        ttk.Label(threshold_frame, text="Erkennungsschwelle:").pack(side=tk.LEFT)
        threshold_var = tk.IntVar(value=2)
        threshold_spinbox = ttk.Spinbox(threshold_frame, from_=1, to=10, textvariable=threshold_var, width=10)
        threshold_spinbox.pack(side=tk.RIGHT)
        ttk.Label(threshold_frame, text="Mindestanzahl Komponenten für Erkennung", 
                 font=('Arial', 9), foreground='gray').pack(side=tk.RIGHT, padx=(0, 10))
        
        # Button-Bereich
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def create_detect_module():
            """Handler für DETECT.py Erstellung"""
            name = name_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            patterns_content = patterns_text.get(1.0, tk.END).strip()
            grabber_id = grabber_entry.get().strip() or None
            threshold = threshold_var.get()
            
            # Validierung
            if not name:
                messagebox.showerror("Fehler", "Modulname ist erforderlich!")
                return
            
            if not description:
                messagebox.showerror("Fehler", "Beschreibung ist erforderlich!")
                return
            
            if not patterns_content:
                messagebox.showerror("Fehler", "Mindestens ein Erkennungsmuster ist erforderlich!")
                return
            
            # Parse Patterns
            patterns = [line.strip() for line in patterns_content.split('\n') if line.strip()]
            
            if len(patterns) < 2:
                messagebox.showerror("Fehler", "Mindestens 2 Erkennungsmuster sind erforderlich!")
                return
            
            try:
                # Erstelle DETECT.py Modul
                success, message, metadata = create_detect_from_dialog_data(
                    name=name,
                    description=description,
                    examples=patterns,
                    semantic_grabber_id=grabber_id
                )
                
                if success:
                    # Erfolgreiche Erstellung
                    messagebox.showinfo("Erfolg", message)
                    
                    # Chat-Nachricht
                    self.add_chat_message("🤖 Assistant", 
                                        f"DETECT.py Modul '{metadata.get('module_name', name)}' erfolgreich erstellt!\n"
                                        f"📁 Datei: {metadata.get('file_path', 'N/A')}\n"
                                        f"🔧 {len(patterns)} Erkennungsmuster integriert\n"
                                        f"📊 Schema automatisch aktualisiert")
                    
                    # Status Update
                    self.update_status(f"✅ DETECT.py Modul '{metadata.get('module_name', name)}' erstellt")
                    
                    # Dialog schließen
                    dialog.destroy()
                    
                    # Marker-Liste aktualisieren
                    self.refresh_marker_list()
                    
                else:
                    messagebox.showerror("Fehler", message)
                    
            except Exception as e:
                messagebox.showerror("Fehler", f"Unerwarteter Fehler bei der Erstellung:\n{str(e)}")
        
        def preview_detect_module():
            """Zeigt eine Vorschau des generierten DETECT.py Moduls"""
            name = name_entry.get().strip()
            description = desc_text.get(1.0, tk.END).strip()
            patterns_content = patterns_text.get(1.0, tk.END).strip()
            
            if not name or not description or not patterns_content:
                messagebox.showwarning("Warnung", "Bitte fülle alle Felder aus für die Vorschau!")
                return
            
            patterns = [line.strip() for line in patterns_content.split('\n') if line.strip()]
            
            # Vorschau-Dialog
            preview_dialog = tk.Toplevel(dialog)
            preview_dialog.title(f"👁️ Vorschau: DETECT_{name.upper()}")
            preview_dialog.geometry("900x600")
            preview_dialog.transient(dialog)
            
            preview_text = scrolledtext.ScrolledText(preview_dialog, font=('Consolas', 10))
            preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Generiere Preview-Content (vereinfacht)
            preview_content = f"""# DETECT_{name.upper()}.py - Vorschau

import re

# Erkennungskomponenten (automatisch generiert):
DETECT_{name.upper()}_COMPONENTS = {{
"""
            for i, pattern in enumerate(patterns[:5]):  # Erste 5 für Preview
                component_name = f"COMPONENT_{i+1}"
                preview_content += f'    "{component_name}": [r"\\\\b{pattern}\\\\b"],\n'
            
            preview_content += f"""}}

def detect_{name.lower()}(text: str) -> dict:
    '''
    Analysiert Text auf "{description}"
    
    Returns:
        Dictionary mit Analyseergebnis
    '''
    # Implementierung wird automatisch generiert...
    
# Weitere Details in der finalen Version...
"""
            
            preview_text.insert(1.0, preview_content)
            preview_text.config(state=tk.DISABLED)
        
        # Buttons
        ttk.Button(button_frame, text="👁️ Vorschau", command=preview_detect_module).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="🔍 DETECT.py erstellen", command=create_detect_module).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Focus auf Namensfeld
        name_entry.focus()
    
    def add_examples_dialog(self):
        if not hasattr(self, 'current_marker'):
            messagebox.showwarning("Warnung", "Bitte wähle zuerst einen Marker aus der Liste!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📝 Beispiele zu '{self.current_marker}' hinzufügen")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Beispiele für: {self.current_marker}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(main_frame, text="Neue Beispiele (ein Beispiel pro Zeile):", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        examples_text = scrolledtext.ScrolledText(main_frame, font=('Arial', 10))
        examples_text.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        
        # Beispiel-Hinweis
        hint_text = """Beispiel-Format:
"Das ist ein typisches Scammer-Beispiel"
"Noch ein Beispiel für diesen Marker"
"Immer in Anführungszeichen für bessere Formatierung"""
        
        ttk.Label(main_frame, text=hint_text, foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=(0, 10))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def add_examples():
            examples = [ex.strip().strip('"\'') for ex in examples_text.get(1.0, tk.END).strip().split('\n') if ex.strip()]
            
            if not examples:
                messagebox.showwarning("Warnung", "Bitte gib mindestens ein Beispiel ein!")
                return
            
            # Neue Inhalte generieren
            new_content = self.assistant.add_examples_to_marker(self.current_marker, examples)
            
            if new_content:
                self.pending_changes.append({
                    'type': 'update_marker',
                    'marker_name': self.current_marker,
                    'content': new_content,
                    'description': f"{len(examples)} Beispiele zu '{self.current_marker}' hinzufügen"
                })
                
                self.update_status(f"✅ {len(examples)} Beispiele zur Genehmigung vorgeschlagen")
                self.add_chat_message("🤖 Assistant", 
                                    f"Perfekt! {len(examples)} Beispiele zu '{self.current_marker}' hinzugefügt.\n"
                                    f"⏳ Warte auf deine Genehmigung.\n\n"
                                    f"Beispiele:\n" + '\n'.join(f'• {ex[:60]}...' if len(ex) > 60 else f'• {ex}' for ex in examples[:3]))
                
                dialog.destroy()
            else:
                messagebox.showerror("Fehler", "Fehler beim Hinzufügen der Beispiele!")
        
        ttk.Button(button_frame, text="✅ Hinzufügen", command=add_examples).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def approve_suggestions(self):
        if not self.pending_changes:
            messagebox.showinfo("Info", "Keine ausstehenden Änderungen!")
            return
        
        approved_count = 0
        
        for change in self.pending_changes:
            try:
                if change['type'] == 'create_file':
                    # Neue Datei erstellen
                    folder = change['folder']
                    filename = change['filename']
                    content = change['content']
                    
                    # Bestimme Zielordner
                    if folder == "ALL_NEWMARKER01":
                        file_path = self.assistant.marker_dir / filename
                    else:
                        file_path = self.assistant.marker_dir.parent / f"Former_NEW_MARKER_FOLDERS/{folder}" / filename
                    
                    # Stelle sicher, dass der Ordner existiert
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Datei erstellen
                    file_path.write_text(content, encoding='utf-8')
                    
                    self.add_chat_message("🤖 Assistant", f"✅ {change['description']} - Erfolgreich erstellt!")
                    approved_count += 1
                    
                elif change['type'] in ['edit_marker', 'update_marker', 'create_marker']:
                    # Marker bearbeiten/erstellen/aktualisieren
                    marker_name = change['marker_name']
                    
                    # Entferne Icon-Präfixe
                    clean_name = marker_name
                    for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[2:]
                            break
                    
                    # Prüfe ob es ein Unterordner-Pfad ist
                    if '/' in clean_name:
                        # Unterordner-Datei
                        parts = clean_name.split('/')
                        folder_name = parts[0]
                        file_name = parts[1]
                        file_path = self.assistant.marker_dir.parent / f"Former_NEW_MARKER_FOLDERS/{folder_name}" / file_name
                    else:
                        # Hauptordner-Datei
                        file_path = self.assistant.marker_dir / clean_name
                    
                    # Backup erstellen falls Datei existiert
                    if file_path.exists():
                        backup_path = file_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                    
                    # Änderungen anwenden
                    file_path.write_text(change['content'], encoding='utf-8')
                    approved_count += 1
                    
                    self.add_chat_message("🤖 Assistant", f"✅ {change['description']} - Erfolgreich gespeichert!")
                
                elif change['type'] == 'delete_marker':
                    # Marker löschen
                    marker_name = change['marker_name']
                    
                    # Entferne Icon-Präfixe
                    clean_name = marker_name
                    for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[2:]
                            break
                    
                    # Prüfe ob es ein Unterordner-Pfad ist
                    if '/' in clean_name:
                        # Unterordner-Datei
                        parts = clean_name.split('/')
                        folder_name = parts[0]
                        file_name = parts[1]
                        file_path = self.assistant.marker_dir.parent / f"Former_NEW_MARKER_FOLDERS/{folder_name}" / file_name
                    else:
                        # Hauptordner-Datei
                        file_path = self.assistant.marker_dir / clean_name
                    
                    # Backup erstellen bevor gelöscht wird
                    if file_path.exists():
                        backup_path = file_path.with_suffix(f".deleted_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        file_path.rename(backup_path)
                        approved_count += 1
                        self.add_chat_message("🤖 Assistant", f"✅ {change['description']} - Erfolgreich gelöscht! (Backup: {backup_path.name})")
                    else:
                        self.add_chat_message("🤖 Assistant", f"⚠️ Datei nicht gefunden: {file_path}")
                
                elif change['type'] == 'edit_grabber_library':
                    # Grabber Library bearbeiten
                    file_path = Path(change['file_path'])
                    new_content = change['new_content']
                    
                    # Speichere die Änderungen
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    # Lade Grabber neu
                    self.assistant._load_semantic_grabbers()
                    
                    approved_count += 1
                    self.add_chat_message("🤖 Assistant", f"✅ {change['description']} - Erfolgreich gespeichert und neu geladen!")
                
                elif change['type'] == 'auto_fix_yaml':
                    # Auto-Fix für YAML-Dateien
                    file_path = Path(change['file_path'])
                    new_content = change['content']
                    
                    # Backup erstellen
                    if file_path.exists():
                        backup_path = file_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                    
                    # Änderungen anwenden
                    file_path.write_text(new_content, encoding='utf-8')
                    approved_count += 1
                    
                    self.add_chat_message("🤖 Assistant", f"✅ {change['description']} - Auto-Fix erfolgreich angewendet!")
                
            except Exception as e:
                self.add_chat_message("🤖 Assistant", f"❌ Fehler bei {change['description']}: {str(e)}")
        
        # Zurücksetzen
        self.pending_changes = []
        
        # Aktualisieren
        self.refresh_marker_list()
        
        self.update_status(f"✅ {approved_count} Änderungen genehmigt und gespeichert!")
        messagebox.showinfo("Erfolgreich", f"{approved_count} Änderungen wurden angewendet!")
    
    def reject_suggestions(self):
        rejected_count = len(self.pending_changes)
        self.pending_changes = []
        
        self.update_status("❌ Alle ausstehenden Änderungen abgelehnt")
        self.add_chat_message("🤖 Assistant", f"❌ {rejected_count} Änderungen abgelehnt und verworfen.")
        
        if rejected_count > 0:
            messagebox.showinfo("Abgelehnt", f"{rejected_count} Änderungen wurden abgelehnt.")
    
    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        
        # Zeige Anzahl ausstehender Änderungen
        if self.pending_changes:
            self.status_text.insert(tk.END, f"⏳ {len(self.pending_changes)} Änderungen warten auf Genehmigung\n")
    
    def generate_gpt_yaml(self):
        """Generiert GPT-YAML über GUI"""
        try:
            self.update_status("🔄 Generiere GPT-YAML...")
            
            # Dialog für Dateiname
            dialog = tk.Toplevel(self.root)
            dialog.title("🤖 GPT-YAML generieren")
            dialog.geometry("500x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            frame = ttk.Frame(dialog, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="GPT-YAML Datei generieren", 
                     font=('Arial', 12, 'bold')).pack(pady=(0, 20))
            
            ttk.Label(frame, text="Diese Funktion erstellt eine vereinheitlichte YAML-Datei\n"
                                 "mit allen Markern für GPT-Analyse.", 
                     justify=tk.CENTER).pack(pady=(0, 20))
            
            filename_var = tk.StringVar(value="marker_unified_for_gpt.yaml")
            ttk.Label(frame, text="Dateiname:").pack(anchor=tk.W)
            ttk.Entry(frame, textvariable=filename_var, width=50).pack(fill=tk.X, pady=(5, 20))
            
            def generate():
                filename = filename_var.get()
                dialog.destroy()
                
                # Generiere Datei
                output_file = self.assistant.generate_unified_yaml_for_gpt(filename)
                
                self.update_status(f"✅ GPT-YAML generiert: {output_file}")
                self.add_chat_message("🤖 Assistant", 
                                    f"GPT-YAML erfolgreich generiert!\n\n"
                                    f"📄 Datei: {output_file}\n"
                                    f"📊 Enthält: {len(self.assistant.collect_all_markers())} Marker\n\n"
                                    f"Die Datei kann jetzt an GPT übergeben werden für:\n"
                                    f"• Bestandsaufnahme aller Marker\n"
                                    f"• Analyse der Marker-Struktur\n"
                                    f"• Identifikation von Lücken\n"
                                    f"• Verbesserungsvorschläge")
                
                messagebox.showinfo("Erfolg", f"GPT-YAML wurde erfolgreich generiert:\n{output_file}")
            
            ttk.Button(frame, text="🚀 Generieren", command=generate).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Generieren:\n{str(e)}")
    
    def generate_gpt_python(self):
        """Generiert eine zusammengeführte Python-Detector-Datei."""
        try:
            self.update_status("🔄 Generiere Unified Python Detector...")
            from tkinter import simpledialog
            filename = simpledialog.askstring(
                "Unified Python Detector",
                "Dateiname für die Ausgabe:",
                initialvalue="unified_detectors.py"
            )

            if filename:
                output_file = self.assistant.generate_unified_python_detectors(filename)
                self.update_status(f"✅ Unified Python Detector generiert: {output_file}")
                self.add_chat_message("🤖 Assistant",
                                    f"Unified Python Detector erfolgreich generiert!\n\n"
                                    f"📄 Datei: {output_file}\n"
                                    f"Alle Python-Dateien wurden in diese Datei zusammengeführt.")
                messagebox.showinfo("Erfolg", f"Datei erfolgreich generiert:\n{output_file}")
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Generieren der Python-Datei:\n{str(e)}")

    def analyze_structure(self):
        """Analysiert die Marker-Struktur"""
        try:
            self.update_status("🔄 Analysiere Marker-Struktur...")
            
            analysis = self.assistant.analyze_marker_structure()
            
            # Zeige Ergebnisse in Dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("📊 Struktur-Analyse")
            dialog.geometry("600x500")
            dialog.transient(self.root)
            
            frame = ttk.Frame(dialog, padding="15")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Marker-Struktur Analyse", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Ergebnisse formatieren
            results_text = f"""
📊 GESAMT-STATISTIKEN:
• Marker insgesamt: {analysis['total_markers']}
• Beispiele insgesamt: {analysis['total_examples']}
• Durchschnitt pro Marker: {analysis['average_examples_per_marker']} Beispiele
• Abdeckungsgrad: {analysis['coverage_score']}%

📂 KATEGORIEN:
"""
            for cat, count in analysis['categories'].items():
                results_text += f"• {cat}: {count} Marker\n"
            
            if analysis['markers_without_examples']:
                results_text += f"\n⚠️ MARKER OHNE BEISPIELE ({len(analysis['markers_without_examples'])}):\n"
                for marker in analysis['markers_without_examples'][:10]:
                    results_text += f"• {marker}\n"
                if len(analysis['markers_without_examples']) > 10:
                    results_text += f"... und {len(analysis['markers_without_examples']) - 10} weitere\n"
            
            # Text-Widget für Ergebnisse
            text_widget = scrolledtext.ScrolledText(frame, height=20, width=60)
            text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            text_widget.insert(1.0, results_text)
            text_widget.config(state='disabled')
            
            ttk.Button(frame, text="Schließen", command=dialog.destroy).pack()
            
            self.update_status("✅ Struktur-Analyse abgeschlossen")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Analyse:\n{str(e)}")
    
    def identify_gaps(self):
        """Identifiziert Lücken in der Marker-Abdeckung"""
        try:
            self.update_status("🔄 Identifiziere Lücken...")
            
            gaps = self.assistant.identify_marker_gaps()
            
            # Zeige Ergebnisse
            dialog = tk.Toplevel(self.root)
            dialog.title("🔍 Lücken-Analyse")
            dialog.geometry("700x600")
            dialog.transient(self.root)
            
            frame = ttk.Frame(dialog, padding="15")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Marker-Lücken Analyse", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Notebook für verschiedene Bereiche
            notebook = ttk.Notebook(frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Tab 1: Fehlende Kategorien
            missing_tab = ttk.Frame(notebook)
            notebook.add(missing_tab, text="Fehlende Kategorien")
            
            missing_text = scrolledtext.ScrolledText(missing_tab, height=15, width=60)
            missing_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            if gaps['missing_categories']:
                missing_text.insert(1.0, "🚨 FEHLENDE KATEGORIEN:\n\n")
                for item in gaps['missing_categories']:
                    missing_text.insert(tk.END, f"❌ {item['category'].upper()}\n")
                    missing_text.insert(tk.END, f"   Beschreibung: {item['description']}\n\n")
            else:
                missing_text.insert(1.0, "✅ Alle wichtigen Kategorien sind abgedeckt!")
            
            missing_text.config(state='disabled')
            
            # Tab 2: Schwache Marker
            weak_tab = ttk.Frame(notebook)
            notebook.add(weak_tab, text="Schwache Marker")
            
            weak_text = scrolledtext.ScrolledText(weak_tab, height=15, width=60)
            weak_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            if gaps['low_coverage_markers']:
                weak_text.insert(1.0, "⚠️ MARKER MIT WENIGEN BEISPIELEN:\n\n")
                for item in gaps['low_coverage_markers'][:20]:
                    weak_text.insert(tk.END, f"• {item['name']}: nur {item['examples']} Beispiele\n")
                if len(gaps['low_coverage_markers']) > 20:
                    weak_text.insert(tk.END, f"\n... und {len(gaps['low_coverage_markers']) - 20} weitere")
            else:
                weak_text.insert(1.0, "✅ Alle Marker haben ausreichend Beispiele!")
            
            weak_text.config(state='disabled')
            
            # Tab 3: Empfehlungen
            rec_tab = ttk.Frame(notebook)
            notebook.add(rec_tab, text="Empfehlungen")
            
            rec_text = scrolledtext.ScrolledText(rec_tab, height=15, width=60)
            rec_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            rec_text.insert(1.0, "💡 EMPFEHLUNGEN:\n\n")
            for i, rec in enumerate(gaps['recommendations'], 1):
                rec_text.insert(tk.END, f"{i}. {rec}\n")
            
            rec_text.config(state='disabled')
            
            ttk.Button(frame, text="Schließen", command=dialog.destroy).pack()
            
            self.update_status("✅ Lücken-Analyse abgeschlossen")
            
            # Chat-Nachricht mit Zusammenfassung
            self.add_chat_message("🤖 Assistant",
                                f"Lücken-Analyse abgeschlossen!\n\n"
                                f"📊 Zusammenfassung:\n"
                                f"• Fehlende Kategorien: {len(gaps['missing_categories'])}\n"
                                f"• Schwache Marker: {len(gaps['low_coverage_markers'])}\n"
                                f"• Empfehlungen: {len(gaps['recommendations'])}\n\n"
                                f"Verwende die Ergebnisse um das Marker-System zu verbessern!")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Lücken-Analyse:\n{str(e)}")
    
    def analyze_grabbers(self):
        """Analysiert Semantic Grabbers - erweiterte Version mit Marker-Zuordnung"""
        try:
            self.update_status("🔄 Analysiere Semantic Grabbers...")
            
            # Sammle alle Marker und ihre Grabber-Zuordnungen
            markers = self.assistant.collect_all_markers()
            grabber_usage = {}
            markers_without_grabber = []
            
            for marker_name, marker_data in markers.items():
                grabber_id = marker_data.get('semantic_grabber_id')
                if grabber_id:
                    if grabber_id not in grabber_usage:
                        grabber_usage[grabber_id] = []
                    grabber_usage[grabber_id].append(marker_name)
                else:
                    markers_without_grabber.append(marker_name)
            
            overlaps = self.assistant.analyze_grabber_overlaps()
            
            # Zeige Ergebnisse
            dialog = tk.Toplevel(self.root)
            dialog.title("🧲 Semantic Grabber Analyse")
            dialog.geometry("900x700")
            dialog.transient(self.root)
            
            # Hauptframe mit Notebook
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Semantic Grabber Analyse", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Info-Zusammenfassung
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            info_text = f"""📊 Übersicht:
• Grabber gesamt: {len(self.assistant.semantic_grabbers)}
• Marker gesamt: {len(markers)}
• Marker mit Grabber: {len(markers) - len(markers_without_grabber)}
• Marker ohne Grabber: {len(markers_without_grabber)}
• Überschneidungen: {len(overlaps)}"""
            
            ttk.Label(info_frame, text=info_text, font=('Arial', 10)).pack(anchor=tk.W)
            
            # Notebook für verschiedene Ansichten
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            # Tab 1: Grabber-Details mit Marker-Zuordnung
            details_tab = ttk.Frame(notebook)
            notebook.add(details_tab, text="📌 Grabber-Details")
            
            details_text = scrolledtext.ScrolledText(details_tab, height=20, width=80)
            details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            for gid, grabber in self.assistant.semantic_grabbers.items():
                details_text.insert(tk.END, f"🧲 {gid}\n", 'bold')
                details_text.insert(tk.END, f"   Beschreibung: {grabber.get('beschreibung', 'N/A')}\n")
                # Zeige sowohl Examples als auch Patterns (falls vorhanden)
                examples_count = len(grabber.get('examples', grabber.get('patterns', [])))
                details_text.insert(tk.END, f"   Examples: {examples_count}\n")
                
                # Zeige zugeordnete Marker
                assigned_markers = grabber_usage.get(gid, [])
                details_text.insert(tk.END, f"   Zugeordnete Marker ({len(assigned_markers)}):\n")
                if assigned_markers:
                    for marker in assigned_markers[:5]:  # Zeige max 5
                        details_text.insert(tk.END, f"      • {marker}\n")
                    if len(assigned_markers) > 5:
                        details_text.insert(tk.END, f"      ... und {len(assigned_markers) - 5} weitere\n")
                else:
                    details_text.insert(tk.END, "      ⚠️ Keine Marker zugeordnet (ungenutzt)\n", 'warning')
                
                details_text.insert(tk.END, "\n")
            
            details_text.tag_config('bold', font=('Arial', 10, 'bold'))
            details_text.tag_config('warning', foreground='orange')
            details_text.config(state='disabled')
            
            # Tab 2: Marker ohne Grabber
            nograbber_tab = ttk.Frame(notebook)
            notebook.add(nograbber_tab, text=f"⚠️ Ohne Grabber ({len(markers_without_grabber)})")
            
            nograbber_frame = ttk.Frame(nograbber_tab)
            nograbber_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            ttk.Label(nograbber_frame, text="Marker ohne Semantic Grabber:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
            
            # Liste mit Scrollbar
            nograbber_listbox = tk.Listbox(nograbber_frame, height=15)
            nograbber_scrollbar = ttk.Scrollbar(nograbber_frame, orient="vertical")
            nograbber_listbox.config(yscrollcommand=nograbber_scrollbar.set)
            nograbber_scrollbar.config(command=nograbber_listbox.yview)
            
            nograbber_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            nograbber_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            for marker in markers_without_grabber:
                nograbber_listbox.insert(tk.END, marker)
            
            # Button zum Grabber zuweisen
            button_frame = ttk.Frame(nograbber_tab)
            button_frame.pack(fill=tk.X, pady=10)
            
            def assign_grabber():
                selection = nograbber_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Warnung", "Bitte wähle einen Marker aus!")
                    return
                
                marker_name = nograbber_listbox.get(selection[0])
                marker_data = markers.get(marker_name, {})
                
                # Erstelle Grabber für diesen Marker
                if marker_data.get('beispiele'):
                    result = self.assistant.create_semantic_grabber(
                        marker_name,
                        marker_data['beispiele'],
                        marker_data.get('beschreibung', '')
                    )
                    
                    if result['action'] in ['use_existing', 'created_new']:
                        messagebox.showinfo("Erfolg", 
                                          f"Grabber zugewiesen: {result['grabber_id']}\n"
                                          f"Aktion: {result['action']}")
                        # Aktualisiere Anzeige
                        dialog.destroy()
                        self.analyze_grabbers()
                else:
                    messagebox.showerror("Fehler", "Marker hat keine Beispiele!")
            
            ttk.Button(button_frame, text="🧲 Grabber zuweisen", 
                      command=assign_grabber).pack(side=tk.LEFT, padx=5)
            
            # Tab 3: Überschneidungen
            overlap_tab = ttk.Frame(notebook)
            notebook.add(overlap_tab, text=f"🔄 Überschneidungen ({len(overlaps)})")
            
            if overlaps:
                overlap_text = scrolledtext.ScrolledText(overlap_tab, height=20, width=80)
                overlap_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                for overlap in overlaps:
                    overlap_text.insert(tk.END, f"🔄 {overlap['grabber1']} ↔ {overlap['grabber2']}\n")
                    overlap_text.insert(tk.END, f"   Ähnlichkeit: {overlap['similarity']:.1%}\n")
                    overlap_text.insert(tk.END, f"   Empfehlung: {overlap['recommendation']}\n\n")
                
                overlap_text.config(state='disabled')
            else:
                ttk.Label(overlap_tab, text="✅ Keine signifikanten Überschneidungen gefunden!", 
                         font=('Arial', 12)).pack(expand=True)
            
            # Buttons am unteren Rand
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="🔄 Aktualisieren", 
                      command=lambda: [dialog.destroy(), self.analyze_grabbers()]).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="📄 Library öffnen", 
                      command=self.open_grabber_library).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="Schließen", command=dialog.destroy).pack(side=tk.RIGHT)
            
            self.update_status("✅ Grabber-Analyse abgeschlossen")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Grabber-Analyse:\n{str(e)}")
    
    def optimize_grabbers(self):
        """Optimiert Semantic Grabbers und verknüpft sie mit Markern"""
        try:
            self.update_status("🔄 Optimiere Semantic Grabbers und verknüpfe mit Markern...")
            
            # Dialog für Optimierungs-Optionen
            dialog = tk.Toplevel(self.root)
            dialog.title("🔄 Grabber Optimierung & Verknüpfung")
            dialog.geometry("900x700")
            dialog.transient(self.root)
            dialog.grab_set()
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Grabber Optimierung & Marker-Verknüpfung", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Notebook für verschiedene Optimierungen
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Tab 1: Marker ohne Grabber verknüpfen
            link_tab = ttk.Frame(notebook)
            notebook.add(link_tab, text="🔗 Marker verknüpfen")
            
            # Analysiere Marker ohne Grabber
            markers = self.assistant.collect_all_markers()
            unlinked_markers = []
            
            for marker_name, marker_data in markers.items():
                if not marker_data.get('semantic_grabber_id'):
                    unlinked_markers.append((marker_name, marker_data))
            
            # Info-Label
            info_label = ttk.Label(link_tab, 
                                  text=f"Gefunden: {len(unlinked_markers)} Marker ohne Semantic Grabber ID", 
                                  font=('Arial', 12, 'bold'))
            info_label.pack(pady=(10, 10))
            
            # Scrollbare Liste für unverknüpfte Marker
            list_frame = ttk.Frame(link_tab)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
            
            # Treeview für bessere Darstellung
            columns = ('Marker', 'Beispiele', 'Vorschlag', 'Ähnlichkeit')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
            
            # Spalten konfigurieren
            tree.heading('Marker', text='Marker Name')
            tree.heading('Beispiele', text='# Beispiele')
            tree.heading('Vorschlag', text='Grabber Vorschlag')
            tree.heading('Ähnlichkeit', text='Ähnlichkeit')
            
            tree.column('Marker', width=300)
            tree.column('Beispiele', width=100)
            tree.column('Vorschlag', width=200)
            tree.column('Ähnlichkeit', width=100)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Analysiere jeden unverknüpften Marker
            suggestions = []
            for marker_name, marker_data in unlinked_markers:
                beispiele = marker_data.get('beispiele', [])
                
                if beispiele:
                    # Finde passenden Grabber
                    similar_id, similarity = self.assistant.find_similar_grabber(beispiele)
                    
                    if similar_id and similarity >= 0.72:
                        suggestion = {
                            'marker_name': marker_name,
                            'marker_data': marker_data,
                            'grabber_id': similar_id,
                            'similarity': similarity,
                            'action': 'link'
                        }
                    else:
                        # Erstelle neuen Grabber
                        new_id = self.assistant._generate_grabber_id(marker_name)
                        suggestion = {
                            'marker_name': marker_name,
                            'marker_data': marker_data,
                            'grabber_id': new_id,
                            'similarity': 0.0,
                            'action': 'create'
                        }
                    
                    suggestions.append(suggestion)
                    
                    # Füge zur Tabelle hinzu
                    action_text = f"{similar_id} (verwenden)" if suggestion['action'] == 'link' else f"{new_id} (neu)"
                    tree.insert('', 'end', values=(
                        marker_name,
                        len(beispiele),
                        action_text,
                        f"{similarity:.1%}" if similarity > 0 else "Neu"
                    ))
            
            # Tab 2: Grabber Merge-Vorschläge
            merge_tab = ttk.Frame(notebook)
            notebook.add(merge_tab, text="🔄 Grabber zusammenführen")
            
            # Überschneidungen analysieren
            overlaps = self.assistant.analyze_grabber_overlaps(threshold=0.85)
            
            merge_info = ttk.Label(merge_tab, 
                                  text=f"Gefunden: {len(overlaps)} mögliche Grabber-Zusammenführungen", 
                                  font=('Arial', 12, 'bold'))
            merge_info.pack(pady=(10, 10))
            
            # Liste für Merge-Vorschläge
            merge_frame = ttk.Frame(merge_tab)
            merge_frame.pack(fill=tk.BOTH, expand=True, padx=10)
            
            merge_listbox = tk.Listbox(merge_frame, height=10, selectmode=tk.MULTIPLE)
            merge_scrollbar = ttk.Scrollbar(merge_frame, orient="vertical")
            merge_listbox.config(yscrollcommand=merge_scrollbar.set)
            merge_scrollbar.config(command=merge_listbox.yview)
            
            merge_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            merge_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            for overlap in overlaps:
                if overlap['recommendation'] == 'merge':
                    merge_listbox.insert(tk.END, 
                        f"{overlap['grabber1']} + {overlap['grabber2']} ({overlap['similarity']:.0%} ähnlich)")
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def apply_optimizations():
                applied_count = 0
                
                # 1. Verknüpfe Marker mit Grabbern
                for suggestion in suggestions:
                    marker_name = suggestion['marker_name']
                    grabber_id = suggestion['grabber_id']
                    
                    if suggestion['action'] == 'create':
                        # Erstelle neuen Grabber
                        self.assistant.semantic_grabbers[grabber_id] = {
                            'beschreibung': f"Automatisch erstellt für {marker_name}",
                            'examples': suggestion['marker_data'].get('beispiele', [])[:10],
                            'patterns': suggestion['marker_data'].get('beispiele', [])[:10],  # Rückwärtskompatibilität
                            'created_from': marker_name,
                            'created_at': datetime.now().isoformat()
                        }
                        self.assistant._save_semantic_grabbers()
                    
                    # Aktualisiere Marker-Datei mit semantische_grabber_id
                    # Finde die Datei des Markers
                    marker_files = []
                    search_dirs = [
                        self.assistant.marker_dir,
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/fraud",
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/emotions",
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/tension",
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/resonance",
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/dynamic_knots",
                        self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS"
                    ]
                    
                    for search_dir in search_dirs:
                        if search_dir.exists():
                            for file_path in search_dir.glob("*.yaml"):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                    if marker_name in content or marker_name.replace('_MARKER', '') in file_path.stem:
                                        marker_files.append(file_path)
                                except:
                                    pass
                    
                    # Aktualisiere die gefundene Datei
                    for file_path in marker_files:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Füge semantische_grabber_id hinzu wenn nicht vorhanden
                            if 'semantische_grabber_id:' not in content:
                                # Füge nach beispiele ein
                                if 'beispiele:' in content:
                                    lines = content.split('\n')
                                    new_lines = []
                                    in_beispiele = False
                                    
                                    for line in lines:
                                        new_lines.append(line)
                                        if 'beispiele:' in line:
                                            in_beispiele = True
                                        elif in_beispiele and line.strip() and not line.startswith(' '):
                                            # Ende der Beispiele erreicht
                                            new_lines.insert(-1, f"\nsemantische_grabber_id: {grabber_id}")
                                            in_beispiele = False
                                    
                                    if in_beispiele:  # Falls Beispiele am Ende der Datei
                                        new_lines.append(f"\nsemantische_grabber_id: {grabber_id}")
                                    
                                    new_content = '\n'.join(new_lines)
                                else:
                                    # Füge am Ende hinzu
                                    new_content = content + f"\n\nsemantische_grabber_id: {grabber_id}\n"
                                
                                # Zur Genehmigung hinzufügen
                                self.pending_changes.append({
                                    'type': 'update_marker',
                                    'marker_name': file_path.name,
                                    'content': new_content,
                                    'description': f"Verknüpfe {marker_name} mit Grabber {grabber_id}"
                                })
                                applied_count += 1
                                break  # Nur eine Datei pro Marker aktualisieren
                        except Exception as e:
                            print(f"Fehler beim Aktualisieren von {file_path}: {e}")
                
                # 2. Führe ausgewählte Grabber zusammen
                merge_selections = merge_listbox.curselection()
                for i in merge_selections:
                    overlap_text = merge_listbox.get(i)
                    # Extrahiere Grabber IDs aus dem Text
                    parts = overlap_text.split(' + ')
                    if len(parts) == 2:
                        grabber1 = parts[0]
                        grabber2 = parts[1].split(' (')[0]
                        
                        success = self.assistant.merge_grabbers([grabber1, grabber2])
                        if success:
                            applied_count += 1
                
                if applied_count > 0:
                    self.update_status(f"✅ {applied_count} Optimierungen zur Genehmigung vorgeschlagen")
                    self.add_chat_message("🤖 Assistant", 
                                        f"Optimierung abgeschlossen!\n\n"
                                        f"📊 {len(suggestions)} Marker-Verknüpfungen vorgeschlagen\n"
                                        f"🔄 {len(merge_selections)} Grabber-Zusammenführungen\n\n"
                                        f"⏳ Bitte genehmige die Änderungen")
                    messagebox.showinfo("Erfolg", 
                                      f"{applied_count} Optimierungen vorbereitet!\n"
                                      f"Bitte genehmige die Änderungen.")
                else:
                    messagebox.showinfo("Info", "Keine Optimierungen ausgewählt.")
                
                dialog.destroy()
            
            ttk.Button(button_frame, text="✅ Optimierungen anwenden", 
                      command=apply_optimizations).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Hilfe-Text
            help_text = """
Optimierungen:
1. Marker-Verknüpfung: Findet passende Grabber für Marker ohne semantische_grabber_id
2. Grabber-Zusammenführung: Vereint sehr ähnliche Grabber (>85% Ähnlichkeit)

Die Änderungen werden zur Genehmigung vorgeschlagen.
            """
            ttk.Label(button_frame, text=help_text, font=('Arial', 9), 
                     justify=tk.LEFT).pack(side=tk.LEFT, padx=(0, 20))
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Grabber-Optimierung:\n{str(e)}")
    
    def open_grabber_library(self):
        """Öffnet die semantic_grabber_library.yaml Datei im Editor-Dialog"""
        try:
            library_path = self.assistant.semantic_grabber_library_path
            
            # Lade den Inhalt der Library
            if library_path.exists():
                with open(library_path, 'r', encoding='utf-8') as f:
                    library_content = f.read()
            else:
                # Erstelle eine leere Library wenn sie nicht existiert
                self.assistant._save_semantic_grabbers()
                library_content = "# Semantic Grabber Library\n# Wird automatisch verwaltet\n\ngrabbers: {}\n"
            
            # Editor-Dialog öffnen (wie bei Marker-Bearbeitung)
            dialog = tk.Toplevel(self.root)
            dialog.title("📄 Semantic Grabber Library")
            dialog.geometry("900x700")
            dialog.transient(self.root)
            dialog.grab_set()
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Info-Header
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(header_frame, text=f"Bearbeite: {library_path.name}", 
                     font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
            
            info_label = ttk.Label(header_frame, 
                                  text=f"📊 {len(self.assistant.semantic_grabbers)} Grabber", 
                                  font=('Arial', 10))
            info_label.pack(side=tk.RIGHT)
            
            # Editor
            editor_frame = ttk.Frame(main_frame)
            editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            editor = scrolledtext.ScrolledText(editor_frame, font=('Consolas', 10), wrap=tk.WORD)
            editor.pack(fill=tk.BOTH, expand=True)
            editor.insert(1.0, library_content)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def save_changes():
                new_content = editor.get(1.0, tk.END).strip()
                
                # Zur Genehmigung hinzufügen
                self.pending_changes.append({
                    'type': 'edit_grabber_library',
                    'file_path': str(library_path),
                    'old_content': library_content,
                    'new_content': new_content,
                    'description': 'Semantic Grabber Library bearbeiten'
                })
                
                self.update_status("✅ Änderungen an Grabber Library zur Genehmigung vorgeschlagen")
                self.add_chat_message("🤖 Assistant", 
                                    "Änderungen an der Grabber Library vorgeschlagen!\n"
                                    "⏳ Warte auf deine Genehmigung\n\n"
                                    "💡 Nach Genehmigung werden alle Grabber neu geladen.")
                
                dialog.destroy()
            
            def reload_library():
                """Lädt die Library neu vom Dateisystem"""
                try:
                    self.assistant._load_semantic_grabbers()
                    with open(library_path, 'r', encoding='utf-8') as f:
                        new_content = f.read()
                    editor.delete(1.0, tk.END)
                    editor.insert(1.0, new_content)
                    info_label.config(text=f"📊 {len(self.assistant.semantic_grabbers)} Grabber")
                    self.update_status("🔄 Grabber Library neu geladen")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Neuladen:\n{str(e)}")
            
            ttk.Button(button_frame, text="💾 Speichern", command=save_changes).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="🔄 Neu laden", command=reload_library).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Hilfe-Text
            help_frame = ttk.LabelFrame(main_frame, text="💡 Hilfe", padding="10")
            help_frame.pack(fill=tk.X, pady=(10, 0))
            
            help_text = """Format für neue Grabber:
semantic_grabbers:
  GRABBER_NAME_SEM:
    beschreibung: "Beschreibung des Grabbers"
    examples:
      - "Beispiel 1"
      - "Beispiel 2"
    patterns:  # Optional für Rückwärtskompatibilität
      - "Beispiel 1"
      - "Beispiel 2"
    """
            ttk.Label(help_frame, text=help_text, font=('Consolas', 9)).pack(anchor=tk.W)
            
            self.update_status(f"📄 Grabber Library geöffnet: {library_path}")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Konnte Grabber Library nicht öffnen:\n{str(e)}")
    
    def validate_yaml_structure_dialog(self):
        """Dialog zur YAML-Struktur-Validierung"""
        try:
            self.update_status("🔄 Validiere YAML-Strukturen...")
            
            # Sammle alle invaliden Marker
            invalid_markers = self.assistant.get_invalid_yaml_markers()
            
            # Dialog erstellen
            dialog = tk.Toplevel(self.root)
            dialog.title("🔍 YAML-Struktur Validierung")
            dialog.geometry("900x700")
            dialog.transient(self.root)
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="YAML-Struktur Validierung", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Notebook für verschiedene Ansichten
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Tab 1: Übersicht
            overview_tab = ttk.Frame(notebook)
            notebook.add(overview_tab, text=f"📊 Übersicht ({len(invalid_markers)} Probleme)")
            
            # Zusammenfassung
            summary_frame = ttk.Frame(overview_tab)
            summary_frame.pack(fill=tk.X, pady=(0, 10))
            
            total_files = len(invalid_markers)
            if total_files == 0:
                ttk.Label(summary_frame, text="✅ Alle YAML-Dateien sind korrekt strukturiert!", 
                         font=('Arial', 12), foreground='green').pack()
            else:
                ttk.Label(summary_frame, text=f"⚠️ {total_files} Dateien haben Strukturprobleme", 
                         font=('Arial', 12), foreground='orange').pack()
            
            # Liste der problematischen Dateien
            if invalid_markers:
                overview_listbox = tk.Listbox(overview_tab, height=20)
                overview_scrollbar = ttk.Scrollbar(overview_tab, orient="vertical")
                overview_listbox.config(yscrollcommand=overview_scrollbar.set)
                overview_scrollbar.config(command=overview_listbox.yview)
                
                overview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                overview_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                for marker in invalid_markers:
                    filename = Path(marker['file_path']).name
                    issue_count = len(marker['issues'])
                    overview_listbox.insert(tk.END, f"❌ {filename} ({issue_count} Probleme)")
            
            # Tab 2: Details
            details_tab = ttk.Frame(notebook)
            notebook.add(details_tab, text="🔍 Details")
            
            details_text = scrolledtext.ScrolledText(details_tab, height=25, width=80)
            details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            if invalid_markers:
                details_text.insert(tk.END, "🔍 DETAILLIERTE PROBLEME:\n\n")
                for marker in invalid_markers:
                    filename = Path(marker['file_path']).name
                    details_text.insert(tk.END, f"📄 {filename}\n")
                    details_text.insert(tk.END, f"   Pfad: {marker['file_path']}\n")
                    details_text.insert(tk.END, f"   Probleme:\n")
                    for issue in marker['issues']:
                        details_text.insert(tk.END, f"      • {issue}\n")
                    details_text.insert(tk.END, "\n")
            else:
                details_text.insert(tk.END, "✅ Keine Probleme gefunden!")
            
            details_text.config(state='disabled')
            
            # Tab 3: Filter
            filter_tab = ttk.Frame(notebook)
            notebook.add(filter_tab, text="🔧 Filter")
            
            filter_frame = ttk.Frame(filter_tab, padding="10")
            filter_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(filter_frame, text="Filtere nach Problemtyp:", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            # Filter-Buttons
            button_frame = ttk.Frame(filter_frame)
            button_frame.pack(fill=tk.X, pady=(0, 10))
            
            def filter_by_type(filter_type):
                filtered_text = scrolledtext.ScrolledText(filter_frame, height=20, width=80)
                # Entferne vorherige Ergebnisse
                for widget in filter_frame.winfo_children():
                    if isinstance(widget, scrolledtext.ScrolledText):
                        widget.destroy()
                
                filtered_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
                
                filtered_text.insert(tk.END, f"🔍 FILTER: {filter_type}\n\n")
                
                count = 0
                for marker in invalid_markers:
                    matching_issues = []
                    for issue in marker['issues']:
                        if filter_type == "Fehlende Kategorie" and "kategorie" in issue.lower():
                            matching_issues.append(issue)
                        elif filter_type == "Fehlende Semantische_grabber_ID" and "semantische_grabber_id" in issue.lower():
                            matching_issues.append(issue)
                        elif filter_type == "Fehlende Beispiele" and ("beispiele" in issue.lower() or "zu wenige" in issue.lower()):
                            matching_issues.append(issue)
                    
                    if matching_issues:
                        filename = Path(marker['file_path']).name
                        filtered_text.insert(tk.END, f"📄 {filename}\n")
                        for issue in matching_issues:
                            filtered_text.insert(tk.END, f"   • {issue}\n")
                        filtered_text.insert(tk.END, "\n")
                        count += 1
                
                if count == 0:
                    filtered_text.insert(tk.END, f"✅ Keine Probleme vom Typ '{filter_type}' gefunden!")
                
                filtered_text.config(state='disabled')
            
            ttk.Button(button_frame, text="📂 Fehlende Kategorie", 
                      command=lambda: filter_by_type("Fehlende Kategorie")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="🧲 Fehlende Semantische_grabber_ID", 
                      command=lambda: filter_by_type("Fehlende Semantische_grabber_ID")).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="📝 Fehlende Beispiele", 
                      command=lambda: filter_by_type("Fehlende Beispiele")).pack(side=tk.LEFT)
            
            # Tab 4: Auto-Fix
            fix_tab = ttk.Frame(notebook)
            notebook.add(fix_tab, text="🔧 Auto-Fix")
            
            fix_frame = ttk.Frame(fix_tab, padding="10")
            fix_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(fix_frame, text="Automatische Korrekturen:", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            fix_info = ttk.Label(fix_frame, text="Diese Funktion kann einfache Strukturprobleme automatisch korrigieren.")
            fix_info.pack(anchor=tk.W, pady=(0, 20))
            
            def auto_fix():
                fixed_count = 0
                for marker in invalid_markers:
                    # Einfache Fixes implementieren
                    try:
                        with open(marker['file_path'], 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        modified = False
                        
                        # Fix 1: Füge fehlende Grundstruktur hinzu
                        if 'marker_name:' not in content:
                            filename = Path(marker['file_path']).stem
                            content = f"marker_name: {filename}\n" + content
                            modified = True
                        
                        # Fix 2: Füge fehlende Kategorie hinzu
                        if 'kategorie:' not in content:
                            content += "\nkategorie: UNCATEGORIZED\n"
                            modified = True
                        
                        # Fix 3: Füge fehlende Tags hinzu
                        if 'tags:' not in content:
                            content += "tags: [needs_review]\n"
                            modified = True
                        
                        if modified:
                            # Zur Genehmigung hinzufügen
                            self.pending_changes.append({
                                'type': 'auto_fix_yaml',
                                'file_path': marker['file_path'],
                                'content': content,
                                'description': f"Auto-Fix für {Path(marker['file_path']).name}"
                            })
                            fixed_count += 1
                    
                    except Exception as e:
                        print(f"Fehler beim Auto-Fix von {marker['file_path']}: {e}")
                
                if fixed_count > 0:
                    messagebox.showinfo("Auto-Fix", f"{fixed_count} Dateien für Auto-Fix vorbereitet!\nBitte genehmige die Änderungen.")
                    self.update_status(f"✅ {fixed_count} Auto-Fix-Vorschläge erstellt")
                else:
                    messagebox.showinfo("Auto-Fix", "Keine automatischen Korrekturen möglich.")
            
            ttk.Button(fix_frame, text="🔧 Auto-Fix starten", command=auto_fix).pack(anchor=tk.W)
            
            # Schließen-Button
            ttk.Button(main_frame, text="Schließen", command=dialog.destroy).pack(pady=(10, 0))
            
            self.update_status(f"✅ Validierung abgeschlossen: {len(invalid_markers)} Probleme gefunden")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Validierung:\n{str(e)}")
    
    def merge_yaml_files_dialog(self):
        """Dialog zum Zusammenführen von YAML-Dateien"""
        try:
            # Sammle alle YAML-Dateien
            yaml_files = []
            search_dirs = [
                self.assistant.marker_dir,
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/fraud",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/emotions",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/tension",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/resonance",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/dynamic_knots",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS",
                self.assistant.marker_dir.parent / "Former_NEW_MARKER_FOLDERS/extended_marker_yaml_bundle",
                self.assistant.marker_dir.parent / "RELATIONSHIP_MARKERS"
            ]
            
            for search_dir in search_dirs:
                if search_dir.exists():
                    for file_path in search_dir.glob("*.yaml"):
                        yaml_files.append(file_path)
                    for file_path in search_dir.glob("*.yml"):
                        yaml_files.append(file_path)
            
            # Dialog erstellen
            dialog = tk.Toplevel(self.root)
            dialog.title("🔄 YAML-Dateien zusammenführen")
            dialog.geometry("800x600")
            dialog.transient(self.root)
            dialog.grab_set()
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="YAML-Dateien zusammenführen", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Zwei-Spalten-Layout
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Linke Spalte: Verfügbare Dateien
            left_frame = ttk.LabelFrame(content_frame, text="📁 Verfügbare YAML-Dateien", padding="5")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            available_listbox = tk.Listbox(left_frame, height=20, selectmode=tk.MULTIPLE)
            available_scrollbar = ttk.Scrollbar(left_frame, orient="vertical")
            available_listbox.config(yscrollcommand=available_scrollbar.set)
            available_scrollbar.config(command=available_listbox.yview)
            
            available_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            available_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Fülle Liste mit Dateien
            for file_path in yaml_files:
                relative_path = str(file_path.relative_to(self.assistant.marker_dir.parent))
                available_listbox.insert(tk.END, relative_path)
            
            # Mittlere Spalte: Buttons
            middle_frame = ttk.Frame(content_frame)
            middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
            def add_selected():
                selections = available_listbox.curselection()
                for i in selections:
                    item = available_listbox.get(i)
                    if item not in [selected_listbox.get(j) for j in range(selected_listbox.size())]:
                        selected_listbox.insert(tk.END, item)
            
            def remove_selected():
                selections = selected_listbox.curselection()
                for i in reversed(selections):
                    selected_listbox.delete(i)
            
            def add_all():
                selected_listbox.delete(0, tk.END)
                for i in range(available_listbox.size()):
                    selected_listbox.insert(tk.END, available_listbox.get(i))
            
            def clear_all():
                selected_listbox.delete(0, tk.END)
            
            ttk.Button(middle_frame, text="→ Hinzufügen", command=add_selected).pack(pady=5)
            ttk.Button(middle_frame, text="← Entfernen", command=remove_selected).pack(pady=5)
            ttk.Button(middle_frame, text="→→ Alle", command=add_all).pack(pady=5)
            ttk.Button(middle_frame, text="✖ Leeren", command=clear_all).pack(pady=5)
            
            # Rechte Spalte: Ausgewählte Dateien
            right_frame = ttk.LabelFrame(content_frame, text="📋 Ausgewählte Dateien", padding="5")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            selected_listbox = tk.Listbox(right_frame, height=20, selectmode=tk.MULTIPLE)
            selected_scrollbar = ttk.Scrollbar(right_frame, orient="vertical")
            selected_listbox.config(yscrollcommand=selected_scrollbar.set)
            selected_scrollbar.config(command=selected_listbox.yview)
            
            selected_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Ausgabe-Optionen
            output_frame = ttk.LabelFrame(main_frame, text="📄 Ausgabe-Optionen", padding="10")
            output_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(output_frame, text="Ausgabe-Dateiname:").pack(anchor=tk.W)
            filename_var = tk.StringVar(value="merged_markers.yaml")
            ttk.Entry(output_frame, textvariable=filename_var, width=50).pack(fill=tk.X, pady=(5, 10))
            
            # Merge-Optionen
            options_frame = ttk.Frame(output_frame)
            options_frame.pack(fill=tk.X)
            
            preserve_structure = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Struktur beibehalten", variable=preserve_structure).pack(anchor=tk.W)
            
            add_metadata = tk.BooleanVar(value=True)
            ttk.Checkbutton(options_frame, text="Metadaten hinzufügen", variable=add_metadata).pack(anchor=tk.W)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            def perform_merge():
                if selected_listbox.size() == 0:
                    messagebox.showwarning("Warnung", "Bitte wähle mindestens eine Datei aus!")
                    return
                
                # Sammle ausgewählte Dateipfade
                selected_files = []
                for i in range(selected_listbox.size()):
                    relative_path = selected_listbox.get(i)
                    full_path = self.assistant.marker_dir.parent / relative_path
                    selected_files.append(full_path)
                
                output_filename = filename_var.get()
                if not output_filename:
                    output_filename = "merged_markers.yaml"
                
                try:
                    # Führe Merge durch
                    output_path = self.assistant.merge_yaml_files(selected_files, output_filename)
                    
                    messagebox.showinfo("Erfolg", 
                                      f"Merge erfolgreich!\n\n"
                                      f"📄 Ausgabe-Datei: {output_path}\n"
                                      f"📊 {len(selected_files)} Dateien zusammengeführt")
                    
                    self.update_status(f"✅ {len(selected_files)} YAML-Dateien zu {output_filename} zusammengeführt")
                    
                    # Chat-Nachricht
                    self.add_chat_message("🤖 Assistant", 
                                        f"YAML-Merge erfolgreich abgeschlossen!\n\n"
                                        f"📄 Ausgabe: {output_filename}\n"
                                        f"📊 {len(selected_files)} Dateien vereint\n"
                                        f"🔍 Struktur beibehalten: {'Ja' if preserve_structure.get() else 'Nein'}\n"
                                        f"📋 Metadaten hinzugefügt: {'Ja' if add_metadata.get() else 'Nein'}")
                    
                    dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Merge:\n{str(e)}")
            
            ttk.Button(button_frame, text="🔄 Zusammenführen", command=perform_merge).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="❌ Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Info-Label
            info_text = f"📊 {len(yaml_files)} YAML-Dateien gefunden"
            ttk.Label(button_frame, text=info_text, font=('Arial', 9)).pack(side=tk.LEFT)
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Merge-Dialog:\n{str(e)}")
    
    def yaml_to_json_dialog(self):
        """Dialog für YAML zu JSON Konvertierung"""
        try:
            self.update_status("🔄 Öffne YAML → JSON Konverter...")
            
            # Dialog erstellen
            dialog = tk.Toplevel(self.root)
            dialog.title("🔀 YAML → JSON Konverter")
            dialog.geometry("900x700")
            dialog.transient(self.root)
            dialog.grab_set()
            
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="YAML → JSON Konverter", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Notebook für verschiedene Modi
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Tab 1: Einzelne Dateien
            single_tab = ttk.Frame(notebook)
            notebook.add(single_tab, text="📄 Einzelne Dateien")
            
            # Dateiauswahl
            file_frame = ttk.LabelFrame(single_tab, text="Dateien auswählen", padding="10")
            file_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Liste der ausgewählten Dateien
            selected_files_var = tk.StringVar(value="")
            selected_files_listbox = tk.Listbox(file_frame, height=10, selectmode=tk.MULTIPLE)
            selected_files_scrollbar = ttk.Scrollbar(file_frame, orient="vertical")
            selected_files_listbox.config(yscrollcommand=selected_files_scrollbar.set)
            selected_files_scrollbar.config(command=selected_files_listbox.yview)
            
            selected_files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Buttons für Dateiauswahl
            button_frame = ttk.Frame(file_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def browse_files():
                from tkinter import filedialog
                files = filedialog.askopenfilenames(
                    title="YAML-Dateien auswählen",
                    filetypes=[("YAML Dateien", "*.yaml *.yml"), ("Alle Dateien", "*.*")],
                    initialdir=str(self.assistant.marker_dir)
                )
                for file in files:
                    if file not in [selected_files_listbox.get(i) for i in range(selected_files_listbox.size())]:
                        selected_files_listbox.insert(tk.END, file)
            
            def remove_selected():
                selections = selected_files_listbox.curselection()
                for i in reversed(selections):
                    selected_files_listbox.delete(i)
            
            def clear_all():
                selected_files_listbox.delete(0, tk.END)
            
            ttk.Button(button_frame, text="📁 Dateien hinzufügen", 
                      command=browse_files).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="❌ Ausgewählte entfernen", 
                      command=remove_selected).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="🗑️ Alle entfernen", 
                      command=clear_all).pack(side=tk.LEFT)
            
            # Tab 2: Ordner-Modus
            folder_tab = ttk.Frame(notebook)
            notebook.add(folder_tab, text="📁 Ganze Ordner")
            
            folder_frame = ttk.LabelFrame(folder_tab, text="Ordner mit YAML-Dateien", padding="10")
            folder_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Verfügbare Ordner
            ttk.Label(folder_frame, text="Wähle Ordner zum Konvertieren:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            folders_listbox = tk.Listbox(folder_frame, height=10, selectmode=tk.MULTIPLE)
            folders_scrollbar = ttk.Scrollbar(folder_frame, orient="vertical")
            folders_listbox.config(yscrollcommand=folders_scrollbar.set)
            folders_scrollbar.config(command=folders_listbox.yview)
            
            folders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            folders_listbox.pack(fill=tk.BOTH, expand=True)
            
            # Fülle mit bekannten Ordnern
            known_folders = [
                "ALL_NEWMARKER01",
                "Former_NEW_MARKER_FOLDERS/fraud",
                "Former_NEW_MARKER_FOLDERS/emotions",
                "Former_NEW_MARKER_FOLDERS/tension",
                "Former_NEW_MARKER_FOLDERS/resonance",
                "Former_NEW_MARKER_FOLDERS/dynamic_knots",
                "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS",
                "Former_NEW_MARKER_FOLDERS/extended_marker_yaml_bundle",
                "RELATIONSHIP_MARKERS"
            ]
            
            for folder in known_folders:
                folder_path = self.assistant.marker_dir.parent / folder
                if folder_path.exists():
                    yaml_count = len(list(folder_path.glob("*.yaml")) + list(folder_path.glob("*.yml")))
                    if yaml_count > 0:
                        folders_listbox.insert(tk.END, f"{folder} ({yaml_count} YAML-Dateien)")
            
            # Tab 3: Schnellauswahl
            quick_tab = ttk.Frame(notebook)
            notebook.add(quick_tab, text="⚡ Schnellauswahl")
            
            quick_frame = ttk.LabelFrame(quick_tab, text="Schnelle Aktionen", padding="10")
            quick_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ttk.Label(quick_frame, text="Häufig verwendete Konvertierungen:", 
                     font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 20))
            
            def convert_all_markers():
                yaml_files = self.assistant.find_yaml_files()
                self._perform_conversion(yaml_files, dialog)
            
            def convert_current_file():
                if hasattr(self, 'current_marker') and self.current_marker:
                    # Extrahiere Dateinamen
                    clean_name = self.current_marker
                    for prefix in ['📄 ', '🐍 ', '📁 ', '📊 ']:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[2:]
                            break
                    
                    # Finde die Datei
                    if '/' in clean_name:
                        parts = clean_name.split('/')
                        file_path = self.assistant.marker_dir.parent / f"Former_NEW_MARKER_FOLDERS/{parts[0]}" / parts[1]
                    else:
                        file_path = self.assistant.marker_dir / clean_name
                    
                    if file_path.suffix in ['.yaml', '.yml']:
                        self._perform_conversion([file_path], dialog)
                    else:
                        messagebox.showinfo("Info", "Die aktuelle Datei ist keine YAML-Datei.")
                else:
                    messagebox.showwarning("Warnung", "Keine Datei ausgewählt!")
            
            ttk.Button(quick_frame, text="📄 Aktuelle Datei konvertieren", 
                      command=convert_current_file).pack(fill=tk.X, pady=(0, 10))
            ttk.Button(quick_frame, text="🗂️ Alle Marker konvertieren", 
                      command=convert_all_markers).pack(fill=tk.X, pady=(0, 10))
            
            # Optionen (unten)
            options_frame = ttk.LabelFrame(main_frame, text="⚙️ Optionen", padding="10")
            options_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Output-Optionen
            output_var = tk.StringVar(value="same")
            ttk.Radiobutton(options_frame, text="Im selben Ordner speichern", 
                           variable=output_var, value="same").pack(anchor=tk.W)
            ttk.Radiobutton(options_frame, text="In 'json_out' Unterordner speichern", 
                           variable=output_var, value="json_out").pack(anchor=tk.W)
            
            # Einrückung
            indent_frame = ttk.Frame(options_frame)
            indent_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(indent_frame, text="JSON-Einrückung:").pack(side=tk.LEFT)
            indent_var = tk.IntVar(value=2)
            indent_spinbox = ttk.Spinbox(indent_frame, from_=0, to=8, width=5, 
                                        textvariable=indent_var)
            indent_spinbox.pack(side=tk.LEFT, padx=(10, 0))
            
            # Konvertierungs-Button
            convert_frame = ttk.Frame(main_frame)
            convert_frame.pack(fill=tk.X)
            
            def perform_conversion():
                current_tab = notebook.index(notebook.select())
                yaml_files = []
                
                if current_tab == 0:  # Einzelne Dateien
                    yaml_files = [selected_files_listbox.get(i) 
                                 for i in range(selected_files_listbox.size())]
                    if not yaml_files:
                        messagebox.showwarning("Warnung", "Keine Dateien ausgewählt!")
                        return
                
                elif current_tab == 1:  # Ordner
                    selections = folders_listbox.curselection()
                    if not selections:
                        messagebox.showwarning("Warnung", "Keine Ordner ausgewählt!")
                        return
                    
                    for i in selections:
                        folder_text = folders_listbox.get(i)
                        folder_name = folder_text.split(" (")[0]
                        folder_path = self.assistant.marker_dir.parent / folder_name
                        if folder_path.exists():
                            yaml_files.extend(folder_path.glob("*.yaml"))
                            yaml_files.extend(folder_path.glob("*.yml"))
                
                if yaml_files:
                    output_same_folder = output_var.get() == "same"
                    indent = indent_var.get()
                    self._perform_conversion(yaml_files, dialog, output_same_folder, indent)
            
            ttk.Button(convert_frame, text="🚀 Konvertierung starten", 
                      command=perform_conversion).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(convert_frame, text="❌ Abbrechen", 
                      command=dialog.destroy).pack(side=tk.RIGHT)
            
            # Status-Label
            self.conversion_status = ttk.Label(convert_frame, text="", font=('Arial', 9))
            self.conversion_status.pack(side=tk.LEFT)
            
            self.update_status("✅ YAML → JSON Konverter geöffnet")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Konverters:\n{str(e)}")
    
    def _perform_conversion(self, yaml_files, dialog, output_same_folder=True, indent=2):
        """Führt die YAML zu JSON Konvertierung durch"""
        try:
            # Progress-Dialog
            progress_dialog = tk.Toplevel(dialog)
            progress_dialog.title("🔄 Konvertierung läuft...")
            progress_dialog.geometry("500x300")
            progress_dialog.transient(dialog)
            progress_dialog.grab_set()
            
            progress_frame = ttk.Frame(progress_dialog, padding="20")
            progress_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(progress_frame, text="Konvertiere YAML-Dateien...", 
                     font=('Arial', 12, 'bold')).pack(pady=(0, 20))
            
            # Progress Bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, 
                                         maximum=len(yaml_files))
            progress_bar.pack(fill=tk.X, pady=(0, 10))
            
            # Status Text
            status_text = scrolledtext.ScrolledText(progress_frame, height=10, width=60)
            status_text.pack(fill=tk.BOTH, expand=True)
            
            # Konvertierung durchführen
            results = self.assistant.convert_yaml_to_json(yaml_files, output_same_folder, indent)
            
            # Zeige Ergebnisse
            progress_dialog.destroy()
            
            # Ergebnis-Dialog
            result_dialog = tk.Toplevel(dialog)
            result_dialog.title("✅ Konvertierung abgeschlossen")
            result_dialog.geometry("600x500")
            result_dialog.transient(dialog)
            result_dialog.grab_set()
            
            result_frame = ttk.Frame(result_dialog, padding="20")
            result_frame.pack(fill=tk.BOTH, expand=True)
            
            # Zusammenfassung
            summary_text = f"""
🎉 Konvertierung abgeschlossen!

📊 Statistik:
• Dateien gesamt: {results['total']}
• Erfolgreich konvertiert: {results['success']} ✅
• Fehler: {results['failed']} ❌
"""
            
            ttk.Label(result_frame, text=summary_text, 
                     font=('Arial', 11), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
            
            # Details
            if results['converted']:
                ttk.Label(result_frame, text="✅ Erfolgreich konvertierte Dateien:", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W)
                
                success_text = scrolledtext.ScrolledText(result_frame, height=10, width=70)
                success_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
                
                for item in results['converted']:
                    success_text.insert(tk.END, f"• {Path(item['yaml_file']).name} → {Path(item['json_file']).name}\n")
                
                success_text.config(state='disabled')
            
            if results['errors']:
                ttk.Label(result_frame, text="❌ Fehler:", 
                         font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(10, 0))
                
                error_text = scrolledtext.ScrolledText(result_frame, height=5, width=70)
                error_text.pack(fill=tk.BOTH, pady=(5, 10))
                
                for error in results['errors']:
                    error_text.insert(tk.END, f"• {Path(error['file']).name}: {error['error']}\n")
                
                error_text.config(state='disabled')
            
            # Buttons
            button_frame = ttk.Frame(result_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            def open_output_folder():
                if results['converted']:
                    # Öffne den Ordner der ersten konvertierten Datei
                    first_json = Path(results['converted'][0]['json_file'])
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', str(first_json.parent)])
                    elif platform.system() == 'Windows':
                        subprocess.run(['explorer', str(first_json.parent)])
                    else:  # Linux
                        subprocess.run(['xdg-open', str(first_json.parent)])
            
            if results['converted']:
                ttk.Button(button_frame, text="📁 Ausgabeordner öffnen", 
                          command=open_output_folder).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(button_frame, text="✅ OK", 
                      command=lambda: [result_dialog.destroy(), dialog.destroy()]).pack(side=tk.RIGHT)
            
            # Update Status
            self.update_status(f"✅ {results['success']} YAML-Dateien erfolgreich zu JSON konvertiert")
            
            # Chat-Nachricht
            self.add_chat_message("🤖 Assistant", 
                                f"YAML → JSON Konvertierung abgeschlossen!\n\n"
                                f"📊 Ergebnis:\n"
                                f"• {results['success']} Dateien erfolgreich konvertiert\n"
                                f"• {results['failed']} Fehler\n\n"
                                f"Die JSON-Dateien wurden {'im selben Ordner' if output_same_folder else 'im json_out Ordner'} gespeichert.")
            
        except Exception as e:
            if 'progress_dialog' in locals():
                progress_dialog.destroy()
            
            self.update_status(f"❌ Fehler bei der Konvertierung: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler bei der Konvertierung:\n{str(e)}")
    
    def auto_repair_markers(self):
        """Führt automatische Marker-Reparatur durch"""
        try:
            self.update_status("🔧 Starte Auto-Repair für Marker...")
            
            # Importiere das repair_markers Modul
            import subprocess
            import sys
            from pathlib import Path
            
            # Erstelle Progress-Dialog
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("🔧 Auto-Repair Markers")
            progress_dialog.geometry("500x300")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            
            main_frame = ttk.Frame(progress_dialog, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Auto-Repair für Marker-YAMLs", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Status-Text
            status_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
            status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Führe repair_markers.py als Subprocess aus
            repair_script = Path(__file__).parent / "repair_markers.py"
            
            def run_repair():
                try:
                    # Zeige Info
                    status_text.insert(tk.END, "🔧 Starte Marker-Reparatur...\n")
                    status_text.insert(tk.END, f"📁 Skript: {repair_script}\n\n")
                    status_text.update()
                    
                    # Führe Skript aus
                    result = subprocess.run(
                        [sys.executable, str(repair_script), "--verbose"],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 Minuten Timeout
                    )
                    
                    # Zeige Ausgabe - sichere GUI-Updates
                    try:
                        if result.stdout:
                            status_text.insert(tk.END, "📤 AUSGABE:\n")
                            status_text.insert(tk.END, result.stdout)
                            status_text.insert(tk.END, "\n")
                        
                        if result.stderr:
                            status_text.insert(tk.END, "⚠️ WARNUNGEN:\n")
                            status_text.insert(tk.END, result.stderr)
                            status_text.insert(tk.END, "\n")
                    except tk.TclError:
                        # GUI bereits geschlossen
                        return
                    
                    try:
                        if result.returncode == 0:
                            status_text.insert(tk.END, "\n✅ Auto-Repair erfolgreich abgeschlossen!")
                            self.update_status("✅ Auto-Repair erfolgreich abgeschlossen")
                            
                            # Refresh marker list
                            self.refresh_marker_list()
                            
                            # Chat-Nachricht
                            self.add_chat_message("🤖 Assistant", 
                                                "✅ Auto-Repair abgeschlossen!\n\n"
                                                "Alle Marker-YAML-Dateien wurden automatisch repariert:\n"
                                                "• Feld-Umbenennungen durchgeführt\n"
                                                "• Datentypen normalisiert\n"
                                                "• Mindestbeispiele hinzugefügt\n"
                                                "• UPPER_SNAKE_CASE angewendet\n\n"
                                                "Die Marker-Liste wurde aktualisiert.")
                        else:
                            status_text.insert(tk.END, f"\n❌ Fehler bei Auto-Repair (Exit-Code: {result.returncode})")
                            self.update_status(f"❌ Auto-Repair fehlgeschlagen")
                    except tk.TclError:
                        # GUI bereits geschlossen
                        return
                        
                except subprocess.TimeoutExpired:
                    try:
                        status_text.insert(tk.END, "\n⏰ Timeout: Prozess wurde abgebrochen")
                        self.update_status("⏰ Auto-Repair Timeout")
                    except tk.TclError:
                        pass
                except Exception as e:
                    try:
                        status_text.insert(tk.END, f"\n❌ Unerwarteter Fehler: {e}")
                        self.update_status(f"❌ Auto-Repair Fehler: {e}")
                    except tk.TclError:
                        pass
                finally:
                    # Sichere GUI-Aktualisierung - prüfe ob Widget noch existiert
                    try:
                        if status_text.winfo_exists():
                            status_text.see(tk.END)
                    except tk.TclError:
                        # GUI bereits geschlossen - ignoriere den Fehler
                        pass
            
            # Starte Reparatur in Thread
            import threading
            threading.Thread(target=run_repair, daemon=True).start()
            
            # Schließen-Button
            ttk.Button(main_frame, text="✅ Schließen", 
                      command=progress_dialog.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            self.update_status(f"❌ Fehler beim Starten von Auto-Repair: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Starten von Auto-Repair:\n{str(e)}")
    
    def refresh_detectors(self):
        """Aktualisiert das Detector-Schema mit neuen Python-Modulen"""
        try:
            self.update_status("🔄 Aktualisiere Detector-Schema...")
            
            # Importiere das update_detectors Modul
            import subprocess
            import sys
            from pathlib import Path
            
            # Erstelle Progress-Dialog
            progress_dialog = tk.Toplevel(self.root)
            progress_dialog.title("🔄 Refresh Detectors")
            progress_dialog.geometry("500x300")
            progress_dialog.transient(self.root)
            progress_dialog.grab_set()
            
            main_frame = ttk.Frame(progress_dialog, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Detector-Schema Aktualisierung", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # Status-Text
            status_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
            status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Führe update_detectors.py als Subprocess aus
            update_script = Path(__file__).parent / "update_detectors.py"
            
            def run_update():
                try:
                    # Zeige Info
                    status_text.insert(tk.END, "🔄 Starte Detector-Update...\n")
                    status_text.insert(tk.END, f"📁 Skript: {update_script}\n\n")
                    status_text.update()
                    
                    # Führe Skript aus
                    result = subprocess.run(
                        [sys.executable, str(update_script), "--verbose"],
                        capture_output=True,
                        text=True,
                        timeout=120  # 2 Minuten Timeout
                    )
                    
                    # Zeige Ausgabe
                    if result.stdout:
                        status_text.insert(tk.END, "📤 AUSGABE:\n")
                        status_text.insert(tk.END, result.stdout)
                        status_text.insert(tk.END, "\n")
                    
                    if result.stderr:
                        status_text.insert(tk.END, "⚠️ WARNUNGEN:\n")
                        status_text.insert(tk.END, result.stderr)
                        status_text.insert(tk.END, "\n")
                    
                    if result.returncode == 0:
                        status_text.insert(tk.END, "\n✅ Detector-Update erfolgreich abgeschlossen!")
                        self.update_status("✅ Detector-Schema aktualisiert")
                        
                        # Chat-Nachricht
                        self.add_chat_message("🤖 Assistant", 
                                            "✅ Detector-Schema aktualisiert!\n\n"
                                            "Neue Python-Detector-Module wurden automatisch erkannt und registriert:\n"
                                            "• Neue Detector-Klassen gefunden\n"
                                            "• Schema-Einträge erstellt\n"
                                            "• Module-Pfade konfiguriert\n\n"
                                            "Das DETECT_default_marker_schema.yaml wurde aktualisiert.")
                    else:
                        status_text.insert(tk.END, f"\n❌ Fehler bei Detector-Update (Exit-Code: {result.returncode})")
                        self.update_status(f"❌ Detector-Update fehlgeschlagen")
                        
                except subprocess.TimeoutExpired:
                    status_text.insert(tk.END, "\n⏰ Timeout: Prozess wurde abgebrochen")
                    self.update_status("⏰ Detector-Update Timeout")
                except Exception as e:
                    status_text.insert(tk.END, f"\n❌ Unerwarteter Fehler: {e}")
                    self.update_status(f"❌ Detector-Update Fehler: {e}")
                finally:
                    try:
                        if status_text.winfo_exists():
                            status_text.see(tk.END)
                    except tk.TclError:
                        pass
            
            # Starte Update in Thread
            import threading
            threading.Thread(target=run_update, daemon=True).start()
            
            # Schließen-Button
            ttk.Button(main_frame, text="✅ Schließen", 
                      command=progress_dialog.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            self.update_status(f"❌ Fehler beim Starten von Detector-Update: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Starten von Detector-Update:\n{str(e)}")
    
    def open_schema_creator(self):
        """Öffnet den Wizard zur Erstellung eines neuen Analyse-Schemas."""
        try:
            # Übergebe die assistant-Instanz an das neue Fenster
            creator_window = SchemaCreatorWindow(self.root, self.assistant)
            creator_window.grab_set()  # Macht das Fenster modal
            self.update_status("📈 Analyse-Schema-Creator geöffnet.")
            self.add_chat_message("🤖 Assistant", "Öffne den Wizard zur Erstellung eines neuen Analyse-Schemas.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte den Schema-Creator nicht öffnen:\n{e}")
            self.update_status(f"❌ Fehler beim Öffnen des Schema-Creators: {e}")

    def load_analysis_schemas(self):
        """Lädt verfügbare Analyse-Schemata aus dem Ordner."""
        try:
            schemas_path = Path("analysis_schemas")
            if schemas_path.exists():
                schemas = ["(Standard-Analyse)"] + [f.name for f in schemas_path.glob("*_schema.json")]
                self.schema_combo['values'] = schemas
                self.schema_combo.set(schemas[0])
            else:
                self.schema_combo['values'] = ["(Keine Schemata gefunden)"]
                self.schema_combo.set("(Keine Schemata gefunden)")
        except Exception as e:
            self.update_status(f"❌ Fehler beim Laden der Schemata: {e}")

    def run_schema_analysis(self):
        """Führt eine Analyse mit dem ausgewählten Schema durch."""
        selected_schema = self.schema_var.get()
        text_to_analyze = self.chat_entry.get(1.0, tk.END).strip()

        if not text_to_analyze:
            messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie einen Text in das Chat-Feld ein, der analysiert werden soll.")
            return

        if not selected_schema or selected_schema in ["(Keine Schemata gefunden)", "Kein Schema ausgewählt"]:
            messagebox.showwarning("Auswahl fehlt", "Bitte wählen Sie ein gültiges Analyse-Schema aus.")
            return

        try:
            if selected_schema == "(Standard-Analyse)":
                # Führe hier die Standard-Analyse mit dem originalen MarkerMatcher aus, falls gewünscht
                # Für diese Demo verwenden wir V2 ohne Schema-Config
                matcher = MarkerMatcherV2()
                analysis_title = "Standard-Analyse Ergebnis"
            else:
                # Lade das ausgewählte Schema
                schema_path = Path("analysis_schemas") / selected_schema
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_config = json.load(f)
                
                # Erstelle den V2 Matcher mit der Schema-Konfiguration
                matcher = MarkerMatcherV2(schema_config=schema_config)
                analysis_title = f"Analyse-Ergebnis mit Schema: {selected_schema}"

            # Führe die Analyse durch
            result = matcher.analyze_text(text_to_analyze)
            
            # Zeige das Ergebnis an
            result_text = f"Analyse für: '{text_to_analyze[:50]}...'\n\n"
            result_text += f"Risk-Level: {result.risk_level.upper()} (Score: {result.total_risk_score})\n"
            result_text += f"------------------------------------------\n"
            result_text += f"Gefundene Marker ({len(result.gefundene_marker)}):\n"
            for match in result.gefundene_marker:
                result_text += f"- {match.marker_name} (Gewichteter Score: {match.risk_score:.2f})\n"
            result_text += f"------------------------------------------\n"
            result_text += f"Zusammenfassung:\n{result.summary}"

            self.add_chat_message("📈 Analyse-Ergebnis", result_text)
            self.update_status(f"✅ Schema-Analyse abgeschlossen. Risk-Level: {result.risk_level.upper()}")

        except Exception as e:
            messagebox.showerror("Analyse-Fehler", f"Ein Fehler ist während der Analyse aufgetreten:\n{e}")
            self.update_status("❌ Fehler bei der Schema-Analyse.")
            
    def run(self):
        self.root.mainloop()

def main():
    app = FRAUSARGUI()
    app.run()

if __name__ == "__main__":
    main()
