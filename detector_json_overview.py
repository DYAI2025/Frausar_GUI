#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector & JSON Overview - Übersichtsfunktionen für DETECT.py und JSON-Dateien
=============================================================================
Erweitert die FRAUSAR GUI um strukturierte Auflistungen
"""

import os
import json
import ast
import re
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class DetectorOverview:
    def __init__(self, base_directory="."):
        self.base_directory = Path(base_directory)
        
    def scan_detect_files(self):
        """Scannt nach DETECT.py Dateien und extrahiert Informationen"""
        detect_files = []
        
        # Suche rekursiv nach DETECT*.py Dateien
        for py_file in self.base_directory.rglob("*DETECT*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                detector_info = self.extract_detector_info(py_file, content)
                if detector_info:
                    detect_files.append(detector_info)
                    
            except Exception as e:
                print(f"Fehler beim Lesen von {py_file}: {e}")
                
        return sorted(detect_files, key=lambda x: x['name'])
        
    def extract_detector_info(self, file_path, content):
        """Extrahiert Informationen aus einer DETECT.py Datei"""
        try:
            # Parse als AST
            tree = ast.parse(content)
            
            info = {
                'file': file_path,
                'name': file_path.stem,
                'path': str(file_path.relative_to(self.base_directory)),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                'classes': [],
                'functions': [],
                'imports': [],
                'docstring': '',
                'semantic_grabber_id': None,
                'description': ''
            }
            
            # Extrahiere Docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant)):
                info['docstring'] = tree.body[0].value.value
                
            # Durchsuche AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info['classes'].append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    info['functions'].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        info['imports'].append(f"{module}.{alias.name}")
                        
            # Suche nach semantic_grabber_id in Kommentaren/Strings
            grabber_match = re.search(r'semantic_grabber_id[:\s]+([A-Z0-9_]+)', content)
            if grabber_match:
                info['semantic_grabber_id'] = grabber_match.group(1)
                
            # Suche nach Beschreibung
            desc_match = re.search(r'"""([^"]+)"""', content, re.DOTALL)
            if desc_match:
                info['description'] = desc_match.group(1).strip()[:200] + "..."
                
            return info
            
        except Exception as e:
            print(f"AST Parse Fehler für {file_path}: {e}")
            return None
            
    def generate_detect_overview(self, output_file="detect_overview.md"):
        """Generiert Markdown-Übersicht aller DETECT.py Dateien"""
        detect_files = self.scan_detect_files()
        
        if not detect_files:
            return "Keine DETECT.py Dateien gefunden."
            
        content = f"""# 🔍 DETECT.py Detektoren Übersicht

**Generiert am:** {datetime.now().strftime("%d.%m.%Y um %H:%M:%S")}
**Anzahl Detektoren:** {len(detect_files)}

---

"""
        
        for i, detector in enumerate(detect_files, 1):
            content += f"""## {i}. {detector['name']}

**📁 Pfad:** `{detector['path']}`
**📊 Größe:** {detector['size']:,} Bytes
**📅 Letzte Änderung:** {detector['modified'].strftime("%d.%m.%Y %H:%M")}
**🔢 Semantic Grabber ID:** {detector['semantic_grabber_id'] or 'Nicht gefunden'}

### 📝 Beschreibung
{detector['description'] or 'Keine Beschreibung verfügbar'}

### 🏗️ Struktur
- **Klassen:** {len(detector['classes'])} ({', '.join(detector['classes'][:3])}{'...' if len(detector['classes']) > 3 else ''})
- **Funktionen:** {len(detector['functions'])} ({', '.join(detector['functions'][:3])}{'...' if len(detector['functions']) > 3 else ''})
- **Imports:** {len(detector['imports'])} Module

### 🔧 Hauptfunktionen
"""
            
            # Zeige wichtigste Funktionen
            main_functions = [f for f in detector['functions'] if any(keyword in f.lower() 
                            for keyword in ['detect', 'analyze', 'process', 'match', 'find'])]
            if main_functions:
                for func in main_functions[:5]:
                    content += f"- `{func}()`\n"
            else:
                content += "- Keine Hauptfunktionen identifiziert\n"
                
            content += "\n---\n\n"
            
        # Statistiken
        total_classes = sum(len(d['classes']) for d in detect_files)
        total_functions = sum(len(d['functions']) for d in detect_files)
        total_size = sum(d['size'] for d in detect_files)
        
        content += f"""## 📊 Statistiken

- **Gesamtanzahl Detektoren:** {len(detect_files)}
- **Gesamtanzahl Klassen:** {total_classes}
- **Gesamtanzahl Funktionen:** {total_functions}
- **Gesamtgröße:** {total_size:,} Bytes ({total_size/1024:.1f} KB)
- **Durchschnittliche Dateigröße:** {total_size/len(detect_files):.0f} Bytes

## 🏷️ Semantic Grabber IDs

"""
        
        # Zeige alle Grabber IDs
        grabber_ids = [d['semantic_grabber_id'] for d in detect_files if d['semantic_grabber_id']]
        if grabber_ids:
            for gid in sorted(set(grabber_ids)):
                content += f"- `{gid}`\n"
        else:
            content += "- Keine Semantic Grabber IDs gefunden\n"
            
        # Speichere Datei
        output_path = self.base_directory / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(output_path)

class JSONOverview:
    def __init__(self, base_directory="."):
        self.base_directory = Path(base_directory)
        
    def scan_json_files(self):
        """Scannt nach JSON-Dateien und extrahiert Strukturinformationen"""
        json_files = []
        
        # Suche rekursiv nach JSON-Dateien
        for json_file in self.base_directory.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    data = json.loads(content)
                
                json_info = self.extract_json_info(json_file, data)
                if json_info:
                    json_files.append(json_info)
                    
            except Exception as e:
                print(f"Fehler beim Lesen von {json_file}: {e}")
                
        return sorted(json_files, key=lambda x: x['name'])
        
    def extract_json_info(self, file_path, data):
        """Extrahiert Informationen aus einer JSON-Datei"""
        try:
            info = {
                'file': file_path,
                'name': file_path.stem,
                'path': str(file_path.relative_to(self.base_directory)),
                'size': file_path.stat().st_size,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                'structure_type': type(data).__name__,
                'keys': [],
                'item_count': 0,
                'max_depth': 0,
                'semantic_grabber_ids': [],
                'marker_names': []
            }
            
            # Analysiere Struktur
            if isinstance(data, dict):
                info['keys'] = list(data.keys())
                info['item_count'] = len(data)
                info['max_depth'] = self.calculate_depth(data)
                
                # Suche nach semantischen Mustern
                self.find_semantic_patterns(data, info)
                
            elif isinstance(data, list):
                info['item_count'] = len(data)
                if data:
                    if isinstance(data[0], dict):
                        info['keys'] = list(data[0].keys()) if data[0] else []
                        info['max_depth'] = max(self.calculate_depth(item) for item in data if isinstance(item, dict))
                        
                        # Suche in allen Listenelementen
                        for item in data:
                            if isinstance(item, dict):
                                self.find_semantic_patterns(item, info)
                                
            return info
            
        except Exception as e:
            print(f"JSON-Analyse Fehler für {file_path}: {e}")
            return None
            
    def calculate_depth(self, obj, current_depth=0):
        """Berechnet die maximale Verschachtelungstiefe"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self.calculate_depth(value, current_depth + 1) for value in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self.calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
            
    def find_semantic_patterns(self, data, info):
        """Sucht nach semantischen Mustern in JSON-Daten"""
        def search_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    # Suche nach semantic_grabber_id
                    if 'semantic_grabber_id' in key.lower():
                        if value and value not in info['semantic_grabber_ids']:
                            info['semantic_grabber_ids'].append(str(value))
                    
                    # Suche nach marker_name
                    if 'marker_name' in key.lower() or 'name' in key.lower():
                        if value and value not in info['marker_names']:
                            info['marker_names'].append(str(value))
                    
                    # Rekursive Suche
                    search_recursive(value)
                    
            elif isinstance(obj, list):
                for item in obj:
                    search_recursive(item)
        
        search_recursive(data)
        
    def generate_json_overview(self, output_file="json_overview.md"):
        """Generiert Markdown-Übersicht aller JSON-Dateien"""
        json_files = self.scan_json_files()
        
        if not json_files:
            return "Keine JSON-Dateien gefunden."
            
        content = f"""# 📋 JSON-Dateien Übersicht

**Generiert am:** {datetime.now().strftime("%d.%m.%Y um %H:%M:%S")}
**Anzahl JSON-Dateien:** {len(json_files)}

---

"""
        
        for i, json_info in enumerate(json_files, 1):
            content += f"""## {i}. {json_info['name']}.json

**📁 Pfad:** `{json_info['path']}`
**📊 Größe:** {json_info['size']:,} Bytes
**📅 Letzte Änderung:** {json_info['modified'].strftime("%d.%m.%Y %H:%M")}
**🏗️ Typ:** {json_info['structure_type']}
**📏 Verschachtelungstiefe:** {json_info['max_depth']}
**📦 Anzahl Elemente:** {json_info['item_count']}

### 🔑 Hauptschlüssel
"""
            
            # Zeige Hauptschlüssel
            if json_info['keys']:
                for key in json_info['keys'][:10]:  # Max 10 Keys
                    content += f"- `{key}`\n"
                if len(json_info['keys']) > 10:
                    content += f"- ... und {len(json_info['keys']) - 10} weitere\n"
            else:
                content += "- Keine Schlüssel (Array oder einfacher Wert)\n"
                
            # Semantic Grabber IDs
            if json_info['semantic_grabber_ids']:
                content += "\n### 🏷️ Semantic Grabber IDs\n"
                for gid in json_info['semantic_grabber_ids'][:5]:
                    content += f"- `{gid}`\n"
                    
            # Marker Names
            if json_info['marker_names']:
                content += "\n### 📛 Marker Names\n"
                for name in json_info['marker_names'][:5]:
                    content += f"- `{name}`\n"
                    
            content += "\n---\n\n"
            
        # Statistiken
        total_size = sum(j['size'] for j in json_files)
        total_items = sum(j['item_count'] for j in json_files)
        max_depth = max(j['max_depth'] for j in json_files) if json_files else 0
        
        content += f"""## 📊 Statistiken

- **Gesamtanzahl JSON-Dateien:** {len(json_files)}
- **Gesamtgröße:** {total_size:,} Bytes ({total_size/1024:.1f} KB)
- **Gesamtanzahl Elemente:** {total_items:,}
- **Maximale Verschachtelungstiefe:** {max_depth}
- **Durchschnittliche Dateigröße:** {total_size/len(json_files):.0f} Bytes

## 🏷️ Alle Semantic Grabber IDs

"""
        
        # Sammle alle Grabber IDs
        all_grabber_ids = set()
        for j in json_files:
            all_grabber_ids.update(j['semantic_grabber_ids'])
            
        if all_grabber_ids:
            for gid in sorted(all_grabber_ids):
                content += f"- `{gid}`\n"
        else:
            content += "- Keine Semantic Grabber IDs gefunden\n"
            
        # Speichere Datei
        output_path = self.base_directory / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(output_path)

def create_overview_gui_extension(parent_frame, base_directory="."):
    """Erstellt GUI-Extension für Detector und JSON Übersichten"""
    
    detector_overview = DetectorOverview(base_directory)
    json_overview = JSONOverview(base_directory)
    
    # Frame für die neuen Buttons
    overview_frame = ttk.LabelFrame(parent_frame, text="📊 Übersichten & Listen")
    overview_frame.pack(fill=tk.X, padx=5, pady=5)
    
    button_frame = ttk.Frame(overview_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def generate_detect_overview():
        """Handler für DETECT.py Übersicht"""
        try:
            output_file = detector_overview.generate_detect_overview()
            messagebox.showinfo("Erfolg", f"DETECT.py Übersicht generiert:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei DETECT.py Übersicht:\n{e}")
            
    def generate_json_overview():
        """Handler für JSON Übersicht"""
        try:
            output_file = json_overview.generate_json_overview()
            messagebox.showinfo("Erfolg", f"JSON Übersicht generiert:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei JSON Übersicht:\n{e}")
            
    def show_detect_quick_view():
        """Zeigt schnelle DETECT.py Übersicht"""
        detect_files = detector_overview.scan_detect_files()
        
        # Neues Fenster
        window = tk.Toplevel()
        window.title("🔍 DETECT.py Schnellübersicht")
        window.geometry("800x600")
        
        # Text-Widget
        text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inhalt
        content = f"🔍 DETECT.py DATEIEN ({len(detect_files)} gefunden)\n"
        content += "=" * 50 + "\n\n"
        
        for i, detector in enumerate(detect_files, 1):
            content += f"{i}. {detector['name']}\n"
            content += f"   📁 {detector['path']}\n"
            content += f"   🔢 {detector['semantic_grabber_id'] or 'Keine ID'}\n"
            content += f"   🏗️ {len(detector['classes'])} Klassen, {len(detector['functions'])} Funktionen\n\n"
            
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
        
    def show_json_quick_view():
        """Zeigt schnelle JSON Übersicht"""
        json_files = json_overview.scan_json_files()
        
        # Neues Fenster
        window = tk.Toplevel()
        window.title("📋 JSON Schnellübersicht")
        window.geometry("800x600")
        
        # Text-Widget
        text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inhalt
        content = f"📋 JSON DATEIEN ({len(json_files)} gefunden)\n"
        content += "=" * 50 + "\n\n"
        
        for i, json_info in enumerate(json_files, 1):
            content += f"{i}. {json_info['name']}.json\n"
            content += f"   📁 {json_info['path']}\n"
            content += f"   🏗️ {json_info['structure_type']}, {json_info['item_count']} Elemente\n"
            if json_info['semantic_grabber_ids']:
                content += f"   🏷️ IDs: {', '.join(json_info['semantic_grabber_ids'][:3])}\n"
            content += "\n"
            
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
    
    # Buttons erstellen
    ttk.Button(button_frame, text="🔍 DETECT.py Übersicht", 
               command=generate_detect_overview).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="📋 JSON Übersicht", 
               command=generate_json_overview).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="🔍 DETECT.py Schnellansicht", 
               command=show_detect_quick_view).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(button_frame, text="📋 JSON Schnellansicht", 
               command=show_json_quick_view).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    # Test der Funktionen
    print("🔍 **DETECTOR & JSON OVERVIEW TEST**")
    print("=" * 40)
    
    detector_overview = DetectorOverview(".")
    json_overview = JSONOverview(".")
    
    print("📊 Scanne DETECT.py Dateien...")
    detect_files = detector_overview.scan_detect_files()
    print(f"✅ {len(detect_files)} DETECT.py Dateien gefunden")
    
    print("📊 Scanne JSON Dateien...")
    json_files = json_overview.scan_json_files()
    print(f"✅ {len(json_files)} JSON Dateien gefunden")
    
    if detect_files or json_files:
        print("\n💾 Generiere Übersichtsdateien...")
        if detect_files:
            detect_output = detector_overview.generate_detect_overview()
            print(f"🔍 DETECT.py Übersicht: {detect_output}")
            
        if json_files:
            json_output = json_overview.generate_json_overview()
            print(f"📋 JSON Übersicht: {json_output}")
    else:
        print("ℹ️ Keine DETECT.py oder JSON Dateien zum Analysieren gefunden.") 