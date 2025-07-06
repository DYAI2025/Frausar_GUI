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

class FRAUSARAssistant:
    def __init__(self, marker_directory="../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.marker_dir = Path(marker_directory)
        self.pending_changes = []
        self.semantic_grabber_library_path = Path("semantic_grabber_library.yaml")
        self.semantic_grabbers = self._load_semantic_grabbers()
        self.embeddings_cache = {}
    
    def get_marker_list(self):
        """Lädt alle Marker aus Hauptordner und Unterordnern"""
        markers = []
        if not self.marker_dir.exists():
            return markers
        
        # Hauptordner scannen
        for file in self.marker_dir.glob("*.txt"):
            if any(keyword in file.name.lower() for keyword in ['marker', 'fraud', 'pattern']):
                markers.append(f"📄 {file.name}")
        
        for file in self.marker_dir.glob("*.py"):
            if 'marker' in file.name.lower() or 'pattern' in file.name.lower():
                markers.append(f"🐍 {file.name}")
        
        # Unterordner scannen
        marker_folders = [
            "Former_NEW_MARKER_FOLDERS/fraud",
            "Former_NEW_MARKER_FOLDERS/emotions", 
            "Former_NEW_MARKER_FOLDERS/resonance",
            "Former_NEW_MARKER_FOLDERS/dynamic_knots",
            "Former_NEW_MARKER_FOLDERS/tension",
            "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS",
            "Former_NEW_MARKER_FOLDERS/extended_marker_yaml_bundle"
        ]
        
        # Die Unterordner sind direkt im ALL_SEMANTIC_MARKER_TXT Ordner
        for folder in marker_folders:
            folder_path = self.marker_dir.parent / folder
            if folder_path.exists():
                folder_name = folder.split('/')[-1]
                
                # Text-Marker
                for file in folder_path.glob("*.txt"):
                    markers.append(f"📁 {folder_name}/{file.name}")
                
                # Python-Skripte
                for file in folder_path.glob("*.py"):
                    markers.append(f"🐍 {folder_name}/{file.name}")
                
                # JSON/YAML Dateien
                for file in folder_path.glob("*.json"):
                    markers.append(f"📊 {folder_name}/{file.name}")
                
                for file in folder_path.glob("*.yaml"):
                    markers.append(f"📊 {folder_name}/{file.name}")
                
                for file in folder_path.glob("*.yml"):
                    markers.append(f"📊 {folder_name}/{file.name}")
        
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
            parts = clean_name.split('/')
            folder_name = parts[0]
            file_name = parts[1]
            file_path = self.marker_dir.parent / f"Former_NEW_MARKER_FOLDERS/{folder_name}" / file_name
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
        parent_dir = self.marker_dir.parent
        subfolders = ["Former_NEW_MARKER_FOLDERS/fraud", "Former_NEW_MARKER_FOLDERS/emotions",
                     "Former_NEW_MARKER_FOLDERS/tension", "Former_NEW_MARKER_FOLDERS/resonance",
                     "Former_NEW_MARKER_FOLDERS/dynamic_knots", "Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS"]
        
        for folder in subfolders:
            folder_path = parent_dir / folder
            if folder_path.exists():
                for file in folder_path.iterdir():
                    if file.is_file() and self._is_marker_file(file):
                        try:
                            content = file.read_text(encoding='utf-8')
                            marker_data = self._parse_marker_content(content, file.name)
                            if marker_data:
                                markers[marker_data['name']] = marker_data
                        except:
                            pass  # Ignoriere Dateien die nicht gelesen werden können
        
        return markers
    
    def _is_marker_file(self, file_path):
        """Prüft ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        return any(ext in name for ext in ['.txt', '.yaml', '.yml', '.json']) and \
               any(keyword in name for keyword in ['marker', 'pattern', 'knot', 'spiral'])
    
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
                return data.get('semantic_grabbers', {})
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
            grabber_examples = grabber_data.get('patterns', [])
            
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
                'patterns': examples[:10],  # Maximal 10 Beispiele
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
        
        # Sammle alle Patterns
        all_patterns = []
        descriptions = []
        
        for gid in grabber_ids:
            if gid in self.semantic_grabbers:
                grabber = self.semantic_grabbers[gid]
                all_patterns.extend(grabber.get('patterns', []))
                descriptions.append(grabber.get('beschreibung', ''))
        
        # Entferne Duplikate
        unique_patterns = list(dict.fromkeys(all_patterns))
        
        # Erstelle neuen Grabber
        merged_id = new_name or f"MERGED_{grabber_ids[0]}"
        self.semantic_grabbers[merged_id] = {
            'beschreibung': f"Vereint aus: {', '.join(descriptions[:3])}",
            'patterns': unique_patterns[:20],  # Maximal 20
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
                examples1 = self.semantic_grabbers[id1].get('patterns', [])
                examples2 = self.semantic_grabbers[id2].get('patterns', [])
                
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

class FRAUSARGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 FRAUSAR Marker Assistant")
        self.root.geometry("1200x800")
        
        self.assistant = FRAUSARAssistant()
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
        
        # Hauptbereich mit 3 Spalten
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte - Marker-Liste
        left_frame = ttk.LabelFrame(content_frame, text="📋 Marker-Liste", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
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
        
        self.marker_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.marker_listbox.pack(fill=tk.BOTH, expand=True)
        self.marker_listbox.bind('<<ListboxSelect>>', self.on_marker_select)
        
        marker_buttons = ttk.Frame(left_frame)
        marker_buttons.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(marker_buttons, text="🔄 Aktualisieren", 
                  command=self.refresh_marker_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(marker_buttons, text="➕ Neu", 
                  command=self.create_new_marker_dialog).pack(side=tk.LEFT)
        
        # Mittlere Spalte - Chat & Marker-Viewer
        middle_frame = ttk.LabelFrame(content_frame, text="💬 Chat & Marker-Viewer", padding="5")
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Notebook für Chat und Marker-Inhalt
        self.middle_notebook = ttk.Notebook(middle_frame)
        self.middle_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Chat-Tab
        chat_tab = ttk.Frame(self.middle_notebook)
        self.middle_notebook.add(chat_tab, text="💬 Chat")
        
        self.chat_display = scrolledtext.ScrolledText(chat_tab, height=20, state='disabled')
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
        
        # Chat-Eingabe (unten)
        chat_input_frame = ttk.Frame(middle_frame)
        chat_input_frame.pack(fill=tk.X)
        
        self.chat_entry = tk.Text(chat_input_frame, height=4)
        self.chat_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.chat_entry.bind('<Control-Return>', self.send_chat_message)
        
        send_button_frame = ttk.Frame(chat_input_frame)
        send_button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(send_button_frame, text="📤 Senden", 
                  command=self.send_chat_message).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(send_button_frame, text="📁 Als Datei", 
                  command=self.create_file_from_chat).pack(fill=tk.X)
        
        # Rechte Spalte - Status & Genehmigungen
        right_frame = ttk.LabelFrame(content_frame, text="💡 Vorschläge & Status", padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(5, 0))
        
        self.status_text = scrolledtext.ScrolledText(right_frame, width=35, height=20)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        approval_frame = ttk.Frame(right_frame)
        approval_frame.pack(fill=tk.X)
        
        ttk.Button(approval_frame, text="✅ Genehmigen", 
                  command=self.approve_suggestions).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="❌ Ablehnen", 
                  command=self.reject_suggestions).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="📝 Beispiele hinzufügen", 
                  command=self.add_examples_dialog).pack(fill=tk.X, pady=(0, 2))
        
        # Neue Analyse-Buttons
        ttk.Label(approval_frame, text="Analysen:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        ttk.Button(approval_frame, text="🤖 GPT-YAML generieren", 
                  command=self.generate_gpt_yaml).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="📊 Struktur analysieren", 
                  command=self.analyze_structure).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="🔍 Lücken identifizieren", 
                  command=self.identify_gaps).pack(fill=tk.X, pady=(0, 2))
        
        # Semantic Grabber Buttons
        ttk.Label(approval_frame, text="Semantic Grabber:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        ttk.Button(approval_frame, text="🧲 Grabber analysieren", 
                  command=self.analyze_grabbers).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="🔄 Grabber optimieren", 
                  command=self.optimize_grabbers).pack(fill=tk.X, pady=(0, 2))
        ttk.Button(approval_frame, text="📄 Grabber Library öffnen", 
                  command=self.open_grabber_library).pack(fill=tk.X)
        
        # Initialisierung
        self.refresh_marker_list()
        # Zähle alle verfügbaren Marker
        total_markers = len(self.assistant.get_marker_list())
        
        self.add_chat_message("🤖 FRAUSAR Assistant", 
                             f"Hallo! Ich bin bereit, deine {total_markers} Marker zu verwalten.\n\n"
                             "📋 Verfügbare Marker-Typen:\n"
                             "📄 Text-Marker (.txt)\n"
                             "🐍 Python-Skripte (.py)\n"
                             "📊 JSON/YAML Dateien\n"
                             "📁 Unterordner-Marker\n\n"
                             "💻 Was du tun kannst:\n"
                             "• Marker aus der Liste auswählen\n"
                             "• Neue Beispiele zu allen Formaten hinzufügen\n"
                             "• Neue Marker erstellen\n"
                             "• Python-Skripte für semantische Erkennung bearbeiten\n"
                             "• Mit mir chatten für Hilfe\n\n"
                             "🔒 Sicherheit: Alle Änderungen müssen von dir genehmigt werden!\n"
                             "💾 Automatische Backups für alle Dateitypen!")
    
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
        
        ttk.Radiobutton(folder_frame, text="🤖 Automatisch wählen", variable=folder_var, value="AUTO").pack(anchor=tk.W)
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
                        parsed.get('is_python', False)
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
                        self._create_single_marker(parsed['name'], parsed['description'], parsed['examples'])
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
            if isinstance(data, dict):
                # Prüfe ob es das Standard-Format ist mit 'marker' als Key
                if 'marker' in data:
                    # Standard-Format: marker: NAME
                    result = {
                        'name': data.get('marker', 'UNKNOWN_MARKER'),
                        'description': data.get('beschreibung', '').strip(),
                        'examples': data.get('beispiele', []),
                        'semantic_grabber_id': data.get('semantische_grabber_id', None)
                    }
                else:
                    # Alternatives Format: NAME als Key
                    marker_name = list(data.keys())[0]
                    marker_data = data[marker_name]
                    
                    result = {
                        'name': marker_name,
                        'description': marker_data.get('beschreibung', '').strip(),
                        'examples': marker_data.get('beispiele', []),
                        'semantic_grabber_id': marker_data.get('semantische_grabber_id', None)
                    }
                
                # Wenn kein Grabber angegeben, versuche einen zu finden/erstellen
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
            return {
                'name': marker_name,
                'description': description,
                'examples': examples
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
            'is_python': True
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
        marker_pattern = re.compile(r'^[\s-]*marker:\s*\w+', re.MULTILINE)
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
    
    def _create_single_marker(self, name, description, examples, semantic_grabber_id=None, is_python=False):
        """Erstellt einen einzelnen Marker mit Semantic Grabber Support nach Projekt-Standard"""
        # Stelle sicher dass der Name den Konventionen entspricht
        name = name.upper().replace(' ', '_')
        if not name.endswith("_MARKER"):
            name = f"{name}_MARKER"
        
        # Entscheide Dateierweiterung basierend auf Typ
        file_extension = ".py" if is_python else ".yaml"  # Projekt-Standard: YAML für Marker
        filename = name + file_extension
        
        if is_python:
            # Python Template
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
                details_text.insert(tk.END, f"   Patterns: {len(grabber.get('patterns', []))}\n")
                
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
        """Optimiert Semantic Grabbers durch Merge-Vorschläge"""
        try:
            self.update_status("🔄 Optimiere Semantic Grabbers...")
            
            overlaps = self.assistant.analyze_grabber_overlaps(threshold=0.85)
            
            if not overlaps:
                messagebox.showinfo("Info", "Keine Optimierungen notwendig!\nAlle Grabber sind ausreichend unterschiedlich.")
                return
            
            # Dialog für Merge-Vorschläge
            dialog = tk.Toplevel(self.root)
            dialog.title("🔄 Grabber Optimierung")
            dialog.geometry("600x400")
            dialog.transient(self.root)
            dialog.grab_set()
            
            frame = ttk.Frame(dialog, padding="15")
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Grabber Merge-Vorschläge", 
                     font=('Arial', 12, 'bold')).pack(pady=(0, 10))
            
            # Checkboxen für Merge-Auswahl
            merge_vars = []
            
            for i, overlap in enumerate(overlaps):
                if overlap['recommendation'] == 'merge':
                    var = tk.BooleanVar(value=True)
                    merge_vars.append((var, overlap))
                    
                    check_frame = ttk.Frame(frame)
                    check_frame.pack(fill=tk.X, pady=2)
                    
                    ttk.Checkbutton(check_frame, variable=var).pack(side=tk.LEFT)
                    ttk.Label(check_frame, 
                             text=f"{overlap['grabber1']} + {overlap['grabber2']} ({overlap['similarity']:.0%} ähnlich)").pack(side=tk.LEFT)
            
            # Buttons
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            def perform_merges():
                merged_count = 0
                for var, overlap in merge_vars:
                    if var.get():
                        success = self.assistant.merge_grabbers([overlap['grabber1'], overlap['grabber2']])
                        if success:
                            merged_count += 1
                
                if merged_count > 0:
                    messagebox.showinfo("Erfolg", f"{merged_count} Grabber-Paare erfolgreich vereint!")
                    self.update_status(f"✅ {merged_count} Grabber optimiert")
                
                dialog.destroy()
            
            ttk.Button(button_frame, text="🔄 Ausgewählte vereinen", command=perform_merges).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
            
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
grabbers:
  GRABBER_NAME_SEM:
    beschreibung: "Beschreibung des Grabbers"
    patterns:
      - "Beispiel-Pattern 1"
      - "Beispiel-Pattern 2"
    """
            ttk.Label(help_frame, text=help_text, font=('Consolas', 9)).pack(anchor=tk.W)
            
            self.update_status(f"📄 Grabber Library geöffnet: {library_path}")
            
        except Exception as e:
            self.update_status(f"❌ Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Konnte Grabber Library nicht öffnen:\n{str(e)}")
    
    def run(self):
        self.root.mainloop()

def main():
    app = FRAUSARGUI()
    app.run()

if __name__ == "__main__":
    main()
