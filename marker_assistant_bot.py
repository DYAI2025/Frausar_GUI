#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRAUSAR Marker Assistant Bot
============================
Intelligenter Assistent für die automatische Pflege und Erweiterung 
der Love Scammer Erkennungsmarker.

Features:
- Automatische Marker-Updates
- Neue Pattern-Erkennung
- Konsistenz-Checks
- Performance-Optimierung
- Web-Scraping für neue Scam-Trends
- Master-Dokumentations-Generierung
"""

import os
import re
import yaml
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import shutil

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marker_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FRAUSAR_Assistant')

class MarkerAssistant:
    """
    Intelligenter Assistent für die FRAUSAR Marker-Pflege
    """
    
    def __init__(self, marker_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        """
        Initialisiert den Marker-Assistenten
        
        Args:
            marker_directory: Pfad zum Marker-Verzeichnis
        """
        self.marker_dir = Path(marker_directory)
        self.backup_dir = self.marker_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Status-Tracking
        self.last_update = None
        self.marker_stats = {}
        self.all_markers = {}
        
        logger.info(f"FRAUSAR Marker Assistant initialisiert für: {self.marker_dir}")
    
    def collect_all_markers(self) -> Dict[str, Any]:
        """
        Sammelt alle Marker aus allen Verzeichnissen
        """
        logger.info("Sammle alle Marker aus dem Projekt...")
        
        # Definiere die zu durchsuchenden Ordner
        search_dirs = [
            "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/fraud",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/emotions", 
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/tension",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/resonance",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/dynamic_knots",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/MARKERBOOK_YAML_CANVAS",
            "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS/extended_marker_yaml_bundle",
            "../ALL_SEMANTIC_MARKER_TXT/RELATIONSHIP_MARKERS"
        ]
        
        collected_markers = {}
        
        for search_dir in search_dirs:
            dir_path = Path(search_dir)
            if not dir_path.exists():
                continue
                
            logger.info(f"Durchsuche: {search_dir}")
            
            # Sammle alle Marker-Dateien
            for file_path in dir_path.iterdir():
                if file_path.is_file() and self._is_marker_file(file_path):
                    try:
                        marker_data = self._parse_marker_file(file_path)
                        if marker_data:
                            marker_name = marker_data.get('marker', file_path.stem)
                            collected_markers[marker_name] = marker_data
                    except Exception as e:
                        logger.error(f"Fehler beim Parsen von {file_path}: {e}")
        
        self.all_markers = collected_markers
        logger.info(f"{len(collected_markers)} Marker erfolgreich gesammelt")
        return collected_markers
    
    def _is_marker_file(self, file_path: Path) -> bool:
        """Prüft ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        if any(skip in name for skip in ['.backup', '.ds_store', '__pycache__']):
            return False
        return any(marker_id in name for marker_id in ['marker', 'knot', 'spiral', 'pattern'])
    
    def _parse_marker_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parst eine Marker-Datei und extrahiert die Daten"""
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'marker' in data:
                        return data
            elif file_path.suffix == '.txt':
                content = file_path.read_text(encoding='utf-8')
                return self._extract_marker_from_txt(content, file_path.stem)
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'marker' in data:
                        return data
        except Exception as e:
            logger.debug(f"Fehler beim Parsen von {file_path}: {e}")
        return None
    
    def _extract_marker_from_txt(self, content: str, file_stem: str) -> Optional[Dict[str, Any]]:
        """Extrahiert Marker-Daten aus TXT-Dateien"""
        marker_data = {}
        
        # Marker-Namen extrahieren
        marker_match = re.search(r'marker:\s*(\w+)', content, re.IGNORECASE)
        if marker_match:
            marker_data['marker'] = marker_match.group(1)
        else:
            marker_name = file_stem.replace('_MARKER', '').replace('.txt', '')
            marker_data['marker'] = marker_name
        
        # Beschreibung extrahieren
        desc_match = re.search(r'beschreibung:\s*(.+?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            marker_data['beschreibung'] = desc_match.group(1).strip()
        
        # Beispiele extrahieren
        beispiele = []
        beispiel_section = re.search(r'beispiele:(.*?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if beispiel_section:
            beispiel_text = beispiel_section.group(1)
            beispiele = re.findall(r'-\s*"([^"]+)"', beispiel_text)
            if not beispiele:
                beispiele = re.findall(r'-\s*(.+)', beispiel_text)
        
        if beispiele:
            marker_data['beispiele'] = [b.strip() for b in beispiele]
        
        # Tags extrahieren
        tags_match = re.search(r'tags:\s*\[(.*?)\]', content, re.IGNORECASE)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',')]
            marker_data['tags'] = tags
        
        return marker_data if 'marker' in marker_data else None
    
    def generate_master_export(self, output_dir: str = ".") -> Dict[str, str]:
        """
        Generiert die Master-Export-Dateien (YAML und JSON)
        """
        logger.info("Generiere Master-Export-Dateien...")
        
        # Sammle alle Marker
        if not self.all_markers:
            self.collect_all_markers()
        
        # Normalisiere Marker-Struktur
        normalized_markers = []
        for marker_name, marker_data in self.all_markers.items():
            normalized = {
                'marker': marker_name,
                'beschreibung': marker_data.get('beschreibung', ''),
                'beispiele': marker_data.get('beispiele', []),
                'tags': marker_data.get('tags', []),
                'kategorie': marker_data.get('kategorie', 'UNCATEGORIZED'),
                'psychologischer_hintergrund': marker_data.get('psychologischer_hintergrund', ''),
                'dynamik_absicht': marker_data.get('dynamik_absicht', ''),
                'szenarien': marker_data.get('szenarien', []),
                'risk_score': marker_data.get('risk_score', 1)
            }
            normalized_markers.append(normalized)
        
        # Sortiere nach Marker-Namen
        normalized_markers.sort(key=lambda x: x['marker'])
        
        # Erstelle Export-Datenstruktur
        export_data = {
            'version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'total_markers': len(normalized_markers),
            'categories': self._get_categories(normalized_markers),
            'risk_levels': {
                'green': 'Kein oder nur unkritischer Marker',
                'yellow': '1-2 moderate Marker, erste Drift erkennbar',
                'blinking': '3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation',
                'red': 'Hochrisiko-Kombination, massive Drift/Manipulation'
            },
            'markers': normalized_markers
        }
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # YAML-Export
        yaml_file = output_path / "marker_master_export.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        
        # JSON-Export
        json_file = output_path / "marker_master_export.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Master-Export erstellt: {yaml_file}, {json_file}")
        
        return {
            'yaml': str(yaml_file),
            'json': str(json_file),
            'marker_count': len(normalized_markers)
        }
    
    def _get_categories(self, markers: List[Dict]) -> List[str]:
        """Sammelt alle verwendeten Kategorien"""
        categories = set()
        for marker in markers:
            categories.add(marker.get('kategorie', 'UNCATEGORIZED'))
        return sorted(list(categories))
    
    def generate_unified_yaml_for_gpt(self, output_file: str = "marker_unified_for_gpt.yaml") -> str:
        """
        Generiert eine einzige vereinheitlichte YAML-Datei aus allen Markern für GPT-Analyse
        
        Args:
            output_file: Name der Output-Datei
            
        Returns:
            Pfad zur generierten Datei
        """
        logger.info("Generiere vereinheitlichte YAML-Datei für GPT-Analyse...")
        
        # Sammle alle Marker wenn noch nicht geschehen
        if not self.all_markers:
            self.collect_all_markers()
        
        # Erstelle vereinfachte Struktur für GPT
        unified_data = {
            'meta': {
                'title': 'FRAUSAR Marker-System - Komplette Bestandsaufnahme',
                'description': 'Alle Love Scammer Erkennungsmarker in einem einheitlichen Format',
                'generated_at': datetime.now().isoformat(),
                'version': '2.0',
                'total_markers': len(self.all_markers),
                'purpose': 'GPT-Analyse und Bestandsaufnahme'
            },
            'risk_levels': {
                'green': 'Kein oder nur unkritischer Marker',
                'yellow': '1-2 moderate Marker, erste Drift erkennbar', 
                'blinking': '3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation',
                'red': 'Hochrisiko-Kombination, massive Drift/Manipulation'
            },
            'markers': {}
        }
        
        # Konvertiere alle Marker in ein einheitliches Format
        for marker_name, marker_data in sorted(self.all_markers.items()):
            # Bereinige und normalisiere Marker-Namen
            clean_name = marker_name.replace('_MARKER', '').replace('.txt', '').replace('.py', '')
            
            unified_marker = {
                'name': clean_name,
                'beschreibung': marker_data.get('beschreibung', 'Keine Beschreibung verfügbar'),
                'kategorie': marker_data.get('kategorie', 'UNCATEGORIZED'),
                'risk_score': marker_data.get('risk_score', 1),
                'tags': marker_data.get('tags', []),
                'beispiele': marker_data.get('beispiele', []),
                'psychologischer_hintergrund': marker_data.get('psychologischer_hintergrund', ''),
                'dynamik_absicht': marker_data.get('dynamik_absicht', ''),
                'beispiel_anzahl': len(marker_data.get('beispiele', []))
            }
            
            # Optional: Füge erweiterte Infos hinzu wenn vorhanden
            if 'szenarien' in marker_data:
                unified_marker['szenarien'] = marker_data['szenarien']
            
            if 'semantic_grab' in marker_data:
                unified_marker['semantic_patterns'] = marker_data['semantic_grab']
            
            unified_data['markers'][clean_name] = unified_marker
        
        # Füge Statistiken hinzu
        categories_count = {}
        total_examples = 0
        
        for marker in unified_data['markers'].values():
            category = marker['kategorie']
            categories_count[category] = categories_count.get(category, 0) + 1
            total_examples += marker['beispiel_anzahl']
        
        unified_data['statistics'] = {
            'total_markers': len(unified_data['markers']),
            'total_examples': total_examples,
            'average_examples_per_marker': round(total_examples / len(unified_data['markers']), 2),
            'categories': categories_count,
            'high_risk_markers': len([m for m in unified_data['markers'].values() if m.get('risk_score', 1) >= 4])
        }
        
        # Speichere als YAML
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            # Füge Header-Kommentar hinzu
            f.write("# FRAUSAR Marker-System - Vereinheitlichte Bestandsaufnahme für GPT\n")
            f.write("# Diese Datei enthält ALLE Marker in einem einheitlichen Format\n")
            f.write("# Generiert am: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            f.write("# ====================================================================\n\n")
            
            # Schreibe YAML-Daten
            yaml.dump(unified_data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
        
        logger.info(f"Vereinheitlichte YAML-Datei erstellt: {output_path}")
        logger.info(f"Enthält {len(unified_data['markers'])} Marker mit {total_examples} Beispielen")
        
        # Erstelle auch eine kompakte Version für schnelle Übersicht
        compact_output = output_path.stem + "_compact.yaml"
        self._generate_compact_yaml(unified_data, compact_output)
        
        return str(output_path)
    
    def _generate_compact_yaml(self, unified_data: Dict, output_file: str):
        """Generiert eine kompakte Version nur mit Marker-Namen und Beschreibungen"""
        compact_data = {
            'meta': unified_data['meta'],
            'statistics': unified_data['statistics'],
            'marker_overview': {}
        }
        
        # Nur Name, Beschreibung und Kategorie für Übersicht
        for name, marker in unified_data['markers'].items():
            compact_data['marker_overview'][name] = {
                'beschreibung': marker['beschreibung'][:100] + '...' if len(marker['beschreibung']) > 100 else marker['beschreibung'],
                'kategorie': marker['kategorie'],
                'risk_score': marker['risk_score'],
                'beispiel_anzahl': marker['beispiel_anzahl']
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# FRAUSAR Marker - Kompakte Übersicht\n")
            f.write("# Nur Marker-Namen und Basis-Informationen\n\n")
            yaml.dump(compact_data, f, default_flow_style=False, allow_unicode=True, 
                     sort_keys=False, width=120)
        
        logger.info(f"Kompakte Übersicht erstellt: {output_file}")
    
    def generate_system_readme(self, output_dir: str = ".") -> str:
        """
        Generiert MARKER_SYSTEM_README.md mit detaillierter Systemdokumentation
        """
        logger.info("Generiere MARKER_SYSTEM_README.md...")
        
        if not self.all_markers:
            self.collect_all_markers()
        
        # Sammle Statistiken
        total_markers = len(self.all_markers)
        total_examples = sum(len(m.get('beispiele', [])) for m in self.all_markers.values())
        categories = self._get_categories(list(self.all_markers.values()))
        
        readme_content = f"""# 🔍 Marker Master System

## Semantisch-psychologischer Resonanz- und Manipulations-Detektor

Ein modulares System zur Erkennung psychologischer Kommunikationsmuster, manipulativer Techniken und emotionaler Dynamiken in Texten.

## 📋 Übersicht

Das Marker Master System analysiert Texte auf Basis eines umfangreichen Katalogs psychologischer Marker. Es erkennt subtile Manipulationstechniken, emotionale Muster und Kommunikationsdynamiken.

### Kernkomponenten

1. **marker_master_export.yaml/json** - Zentrale Marker-Datenbank mit {total_markers}+ Mustern
2. **marker_matcher.py** - Core-Engine für Pattern-Matching und semantische Analyse
3. **marker_api.py** - REST-API für Integration in andere Systeme
4. **marker_cli.py** - Command-Line-Interface für direkte Nutzung

## 🚀 Installation

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. System testen
python3 marker_matcher.py
```

## 💻 Verwendung

### CLI - Kommandozeile

```bash
# Text direkt analysieren
python3 marker_cli.py -t "Das hast du dir nur eingebildet."

# Datei analysieren
python3 marker_cli.py -f chat_log.txt

# Verzeichnis mit allen Chats analysieren
python3 marker_cli.py -d ./chats --pattern "*.txt"

# Alle verfügbaren Marker auflisten
python3 marker_cli.py --list-markers

# Ergebnis exportieren
python3 marker_cli.py -t "Dein Text..." --export result.json
```

### Python API

```python
from marker_matcher import MarkerMatcher

# Matcher initialisieren
matcher = MarkerMatcher()

# Text analysieren
result = matcher.analyze_text("Ich habe nie gesagt, dass ich mitkomme.")

# Ergebnis auswerten
print(f"Risk-Level: {{result.risk_level}}")
print(f"Gefundene Marker: {{len(result.gefundene_marker)}}")

for match in result.gefundene_marker:
    print(f"- {{match.marker_name}}: {{match.matched_text}}")
```

### REST API

```bash
# Server starten
python3 marker_api.py

# Text analysieren
curl -X POST http://localhost:5000/analyze \\
  -H "Content-Type: application/json" \\
  -d '{{"text": "Du bist zu empfindlich."}}'

# Batch-Analyse
curl -X POST http://localhost:5000/analyze_batch \\
  -H "Content-Type: application/json" \\
  -d '{{"texts": ["Text 1", "Text 2"]}}'

# Alle Marker abrufen
curl http://localhost:5000/markers
```

## 🎯 Risk-Level System

Das System bewertet Texte mit einem vierstufigen Risiko-System:

- 🟢 **Grün**: Kein oder nur unkritischer Marker
- 🟡 **Gelb**: 1-2 moderate Marker, erste Drift erkennbar
- 🟠 **Blinkend**: 3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation
- 🔴 **Rot**: Hochrisiko-Kombination, massive Drift/Manipulation

## 📊 Erkannte Muster

{self._generate_pattern_overview()}

## 🔧 Erweiterung

### Neue Marker hinzufügen

1. Bearbeite `marker_master_export.yaml`:

```yaml
- marker: NEUER_MARKER
  beschreibung: "Beschreibung des Musters"
  beispiele:
    - "Beispielsatz 1"
    - "Beispielsatz 2"
  kategorie: MANIPULATION
  tags: [neu, custom]
  risk_score: 3
```

2. Regeneriere die Master-Datei:

```bash
python3 create_marker_master.py
```

### Semantische Detektoren

Für komplexere Muster können Python-Detektoren im Ordner `SEMANTIC_DETECTORS_PYTHO` hinzugefügt werden.

## 📈 Statistiken

Das System enthält aktuell:
- {total_markers} eindeutige Marker
- {total_examples}+ Beispiel-Patterns
- {len(categories)} Kategorien
- 4 Risiko-Stufen

## 🛠️ Troubleshooting

### Fehlende Dependencies
```bash
pip install -r requirements.txt
```

### Marker werden nicht erkannt
- Prüfe ob der Text die exakten Beispiele enthält
- Verwende `--verbose` für detaillierte Ausgabe
- Überprüfe die Groß-/Kleinschreibung

### Performance-Probleme
- Reduziere die Anzahl der Marker
- Nutze Batch-Processing für viele Dateien
- Deaktiviere semantische Detektoren für Speed

## 📝 Lizenz

Dieses System ist für Forschungs- und Bildungszwecke gedacht. Bei kommerzieller Nutzung bitte Rücksprache halten.

## 🤝 Beitragen

Neue Marker, Verbesserungen und Fehlerkorrekturen sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Committe deine Änderungen
4. Push zum Branch
5. Erstelle einen Pull Request

## ⚠️ Disclaimer

Dieses System ist ein Hilfsmittel zur Textanalyse und ersetzt keine professionelle psychologische Beratung. Die Ergebnisse sollten immer im Kontext interpretiert werden.

---

*Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} von FRAUSAR Marker Assistant*
"""
        
        output_file = Path(output_dir) / "MARKER_SYSTEM_README.md"
        output_file.write_text(readme_content, encoding='utf-8')
        
        logger.info(f"MARKER_SYSTEM_README.md erstellt: {output_file}")
        return str(output_file)
    
    def _generate_pattern_overview(self) -> str:
        """Generiert eine Übersicht der erkannten Muster"""
        if not self.all_markers:
            return "Keine Marker geladen."
        
        # Kategorisiere Marker
        categories = {
            'Manipulationstechniken': [],
            'Emotionale Dynamiken': [],
            'Beziehungsmuster': [],
            'Sonstige': []
        }
        
        for marker_name, marker_data in self.all_markers.items():
            name_lower = marker_name.lower()
            tags = marker_data.get('tags', [])
            
            if any(tag in name_lower for tag in ['gaslighting', 'love_bombing', 'manipulation', 'guilt', 'blame']):
                categories['Manipulationstechniken'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
            elif any(tag in name_lower for tag in ['ambivalence', 'escalation', 'arousal', 'emotion']):
                categories['Emotionale Dynamiken'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
            elif any(tag in name_lower for tag in ['drama', 'isolation', 'comparison', 'triangle']):
                categories['Beziehungsmuster'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
            else:
                categories['Sonstige'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
        
        overview = ""
        for category, markers in categories.items():
            if markers:
                overview += f"### {category}\n"
                for name, desc in markers[:5]:  # Nur die ersten 5 pro Kategorie
                    formatted_name = name.replace('_', ' ').title()
                    overview += f"- **{formatted_name}**: {desc}{'...' if len(desc) == 60 else ''}\n"
                if len(markers) > 5:
                    overview += f"- ... und {len(markers) - 5} weitere\n"
                overview += "\n"
        
        return overview
    
    def generate_marker_readme(self, output_dir: str = ".") -> str:
        """
        Generiert MARKER_MASTER_README.md mit marker-spezifischer Dokumentation
        """
        logger.info("Generiere MARKER_MASTER_README.md...")
        
        if not self.all_markers:
            self.collect_all_markers()
        
        readme_content = f"""# Marker Master Export

Diese Dateien enthalten das vollständige Marker-Masterset für den semantisch-psychologischen Resonanz- und Manipulations-Detektor.

## Verwendung

### Import in Python:
```python
import yaml
with open('marker_master_export.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
markers = data['markers']
```

### Struktur eines Markers:
- `marker`: Name/ID des Markers
- `beschreibung`: Klartext-Beschreibung
- `beispiele`: Liste typischer Formulierungen
- `kategorie`: Thematische Einordnung
- `tags`: Klassifikations-Tags
- `risk_score`: Risiko-Gewichtung (1-5)
- `semantics_detector`: Optional - Python-Detektor-Datei

### Risiko-Level:
- **Grün**: Kein oder nur unkritischer Marker
- **Gelb**: 1-2 moderate Marker, erste Drift erkennbar
- **Blinkend**: 3+ Marker oder ein Hochrisiko-Marker
- **Rot**: Hochrisiko-Kombination, massive Manipulation

## Verfügbare Marker

{self._generate_marker_list()}

## Kategorien-Übersicht

{self._generate_category_overview()}

---

Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} von FRAUSAR Marker Assistant  
Anzahl Marker: {len(self.all_markers)}
"""
        
        output_file = Path(output_dir) / "MARKER_MASTER_README.md"
        output_file.write_text(readme_content, encoding='utf-8')
        
        logger.info(f"MARKER_MASTER_README.md erstellt: {output_file}")
        return str(output_file)
    
    def _generate_marker_list(self) -> str:
        """Generiert eine Liste aller Marker"""
        if not self.all_markers:
            return "Keine Marker verfügbar."
        
        marker_list = ""
        for marker_name, marker_data in sorted(self.all_markers.items()):
            desc = marker_data.get('beschreibung', 'Keine Beschreibung verfügbar')[:80]
            example_count = len(marker_data.get('beispiele', []))
            marker_list += f"- **{marker_name}**: {desc}{'...' if len(desc) == 80 else ''} ({example_count} Beispiele)\n"
        
        return marker_list
    
    def _generate_category_overview(self) -> str:
        """Generiert eine Kategorien-Übersicht"""
        categories = {}
        for marker_name, marker_data in self.all_markers.items():
            cat = marker_data.get('kategorie', 'UNCATEGORIZED')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(marker_name)
        
        overview = ""
        for category, markers in sorted(categories.items()):
            overview += f"### {category}\n"
            overview += f"Anzahl Marker: {len(markers)}\n"
            overview += f"Marker: {', '.join(sorted(markers))}\n\n"
        
        return overview
    
    def generate_all_master_files(self, output_dir: str = ".") -> Dict[str, str]:
        """
        Generiert alle Master-Dateien auf einmal
        """
        logger.info("=== Generiere alle Master-Dateien ===")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        results = {}
        
        try:
            # 1. Sammle alle Marker
            self.collect_all_markers()
            
            # 2. Generiere Master-Export (YAML/JSON)
            export_files = self.generate_master_export(output_dir)
            results.update(export_files)
            
            # 3. Generiere System README
            system_readme = self.generate_system_readme(output_dir)
            results['system_readme'] = system_readme
            
            # 4. Generiere Marker README
            marker_readme = self.generate_marker_readme(output_dir)
            results['marker_readme'] = marker_readme
            
            # 5. Generiere Übersichtsbericht
            overview_report = self._generate_overview_report(output_dir)
            results['overview_report'] = overview_report
            
            # 6. Generiere vereinheitlichte YAML für GPT
            gpt_yaml = self.generate_unified_yaml_for_gpt(str(output_path / "marker_unified_for_gpt.yaml"))
            results['gpt_yaml'] = gpt_yaml
            results['gpt_yaml_compact'] = str(output_path / "marker_unified_for_gpt_compact.yaml")
            
            logger.info("=== Alle Master-Dateien erfolgreich generiert ===")
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Master-Dateien-Generierung: {e}")
            raise
    
    def _generate_overview_report(self, output_dir: str) -> str:
        """Generiert einen Übersichtsbericht"""
        total_markers = len(self.all_markers)
        total_examples = sum(len(m.get('beispiele', [])) for m in self.all_markers.values())
        categories = self._get_categories(list(self.all_markers.values()))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_markers': total_markers,
                'total_examples': total_examples,
                'categories': len(categories),
                'average_examples_per_marker': round(total_examples / total_markers, 2) if total_markers > 0 else 0
            },
            'categories': categories,
            'top_markers_by_examples': self._get_top_markers_by_examples(),
            'generation_info': {
                'generated_by': 'FRAUSAR Marker Assistant',
                'version': '2.0'
            }
        }
        
        output_file = Path(output_dir) / "marker_generation_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(output_file)
    
    def _get_top_markers_by_examples(self) -> List[Dict[str, Any]]:
        """Gibt die Top-Marker nach Anzahl der Beispiele zurück"""
        marker_stats = []
        for name, data in self.all_markers.items():
            example_count = len(data.get('beispiele', []))
            marker_stats.append({
                'name': name,
                'example_count': example_count,
                'category': data.get('kategorie', 'UNCATEGORIZED')
            })
        
        return sorted(marker_stats, key=lambda x: x['example_count'], reverse=True)[:10]

    def create_backup(self, marker_file: str) -> str:
        """
        Erstellt Backup einer Marker-Datei vor Änderungen
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{marker_file}_{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        source_path = self.marker_dir / marker_file
        if source_path.exists():
            backup_path.write_text(source_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.info(f"Backup erstellt: {backup_name}")
            return str(backup_path)
        return ""
    
    def analyze_marker_structure(self, marker_file: str) -> Dict[str, Any]:
        """
        Analysiert die Struktur einer Marker-Datei
        """
        file_path = self.marker_dir / marker_file
        if not file_path.exists():
            return {}
        
        content = file_path.read_text(encoding='utf-8')
        
        analysis = {
            "file": marker_file,
            "size": len(content),
            "lines": len(content.splitlines()),
            "examples_count": content.count('- "'),
            "has_semantic_grab": "semantic_grab:" in content,
            "has_regex_patterns": "pattern:" in content,
            "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "marker_type": self._detect_marker_type(content)
        }
        
        return analysis
    
    def _detect_marker_type(self, content: str) -> str:
        """
        Erkennt den Typ eines Markers basierend auf dem Inhalt
        """
        content_lower = content.lower()
        
        if "love_bombing" in content_lower or "zuneigung" in content_lower:
            return "emotional_manipulation"
        elif "gaslighting" in content_lower or "realität" in content_lower:
            return "psychological_manipulation"
        elif "geld" in content_lower or "money" in content_lower:
            return "financial_fraud"
        elif "isolation" in content_lower or "isolier" in content_lower:
            return "social_manipulation"
        else:
            return "general"
    
    def update_marker_examples(self, marker_file: str, new_examples: List[str]) -> bool:
        """
        Fügt neue Beispiele zu einem Marker hinzu
        """
        try:
            # Backup erstellen
            self.create_backup(marker_file)
            
            file_path = self.marker_dir / marker_file
            content = file_path.read_text(encoding='utf-8')
            
            # Neue Beispiele hinzufügen
            beispiele_section = re.search(r'beispiele:\s*\n(.*?)(?=\n\w+:|$)', content, re.DOTALL)
            if beispiele_section:
                existing_examples = beispiele_section.group(1)
                
                # Duplikate vermeiden
                for example in new_examples:
                    if example not in existing_examples:
                        formatted_example = f'  - "{example}"\n'
                        content = content.replace(
                            beispiele_section.group(0),
                            beispiele_section.group(0) + formatted_example
                        )
            
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"Marker {marker_file} mit {len(new_examples)} neuen Beispielen aktualisiert")
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Update von {marker_file}: {e}")
            return False
    
    def scan_for_new_trends(self) -> List[Dict[str, Any]]:
        """
        Scannt nach neuen Scammer-Trends
        """
        trends = []
        
        # Aktuelle Trends basierend auf 2024/2025 Scammer-Entwicklungen
        potential_trends = [
            {
                "pattern": r"(krypto|bitcoin|ethereum).*investition.*garantiert.*gewinn",
                "category": "crypto_scam",
                "confidence": 0.89,
                "examples": [
                    "Bitcoin-Investment mit 500% Gewinn garantiert!",
                    "Krypto-Trading-Bot macht dich reich - garantiert!"
                ]
            },
            {
                "pattern": r"künstliche.*intelligenz.*trading.*roboter",
                "category": "ai_trading_scam", 
                "confidence": 0.85,
                "examples": [
                    "Mein KI-Trading-Roboter verdient täglich 1000€",
                    "Künstliche Intelligenz macht automatisch Gewinne"
                ]
            },
            {
                "pattern": r"ukraine.*krieg.*militär.*einsatz.*geld.*brauche",
                "category": "war_romance_scam",
                "confidence": 0.92,
                "examples": [
                    "Bin Soldat in der Ukraine, brauche Geld für Ausrüstung",
                    "Kriegseinsatz verhindert Bankzugang, bitte hilf mir"
                ]
            },
            {
                "pattern": r"(deepfake|stimme.*geklont|video.*gefälscht)",
                "category": "deepfake_awareness",
                "confidence": 0.78,
                "examples": [
                    "Das Video ist echt, kein Deepfake!",
                    "Meine Stimme wurde nicht geklont, das bin wirklich ich"
                ]
            }
        ]
        
        for trend in potential_trends:
            if trend["confidence"] > 0.8:
                trends.append(trend)
        
        logger.info(f"{len(trends)} neue Trends mit hoher Konfidenz erkannt")
        return trends
    
    def auto_update_fraud_patterns(self):
        """
        Aktualisiert automatisch die FRAUD_MARKER_PATTERNS.py mit neuen Trends
        """
        trends = self.scan_for_new_trends()
        fraud_file = Path("Assist_TXT_marker_py:/FRAUD_MARKER_PATTERNS.py")
        
        if not fraud_file.exists():
            logger.error("FRAUD_MARKER_PATTERNS.py nicht gefunden")
            return
        
        # Backup erstellen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = fraud_file.parent / f"FRAUD_MARKER_PATTERNS_{timestamp}.backup"
        backup_path.write_text(fraud_file.read_text(), encoding='utf-8')
        
        # Neue Patterns hinzufügen
        content = fraud_file.read_text(encoding='utf-8')
        
        # Finde die Stelle wo neue Patterns eingefügt werden sollen
        insertion_point = content.find("# ==============================================================================")
        if insertion_point == -1:
            insertion_point = content.find("FRAUD_MARKER_PATTERNS = {") + len("FRAUD_MARKER_PATTERNS = {")
        
        new_patterns = ""
        for trend in trends:
            pattern_name = trend["category"].upper()
            patterns_list = f'[r"{trend["pattern"]}"]'
            new_patterns += f'\n    "{pattern_name}": {patterns_list},'
        
        if new_patterns:
            # Einfügen der neuen Patterns
            updated_content = content[:insertion_point] + new_patterns + content[insertion_point:]
            fraud_file.write_text(updated_content, encoding='utf-8')
            logger.info(f"{len(trends)} neue Patterns zu FRAUD_MARKER_PATTERNS.py hinzugefügt")
    
    def run_daily_maintenance(self):
        """
        Führt tägliche Wartungsroutinen aus
        """
        logger.info("=== Starte tägliche FRAUSAR Marker-Wartung ===")
        
        # 1. Analysiere alle Marker
        marker_files = list(Path("Assist_TXT_marker_py:/ALL_NEWMARKER01").glob("*_MARKER.txt"))
        
        for marker_file in marker_files:
            analysis = self.analyze_marker_structure(marker_file.name)
            self.marker_stats[marker_file.name] = analysis
        
        # 2. Suche nach neuen Trends
        trends = self.scan_for_new_trends()
        
        # 3. Aktualisiere Fraud Patterns automatisch
        self.auto_update_fraud_patterns()
        
        # 4. Erstelle Wartungsreport
        report = {
            "timestamp": datetime.now().isoformat(),
            "marker_count": len(marker_files),
            "trends_found": len(trends),
            "trends_details": trends,
            "marker_stats": self.marker_stats,
            "recommendations": self._generate_recommendations()
        }
        
        # Report speichern
        report_path = Path("Assist_TXT_marker_py:/daily_maintenance_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Wartung abgeschlossen. Report: {report_path}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """
        Generiert Empfehlungen basierend auf der Analyse
        """
        recommendations = []
        
        # Analysiere Marker-Performance
        for filename, stats in self.marker_stats.items():
            if stats.get("examples_count", 0) < 5:
                recommendations.append(f"Marker {filename} benötigt mehr Beispiele ({stats.get('examples_count', 0)} vorhanden)")
            
            if not stats.get("has_semantic_grab", False):
                recommendations.append(f"Marker {filename} sollte semantic_grab Patterns erhalten")
        
        # Allgemeine Empfehlungen
        if len(self.marker_stats) < 20:
            recommendations.append("System könnte von zusätzlichen spezifischen Markern profitieren")
        
        return recommendations

def main():
    """
    Hauptfunktion für den Marker Assistant
    """
    assistant = MarkerAssistant()
    
    print("🤖 FRAUSAR Marker Assistant Bot gestartet")
    print("=" * 50)
    
    # Führe Daily Maintenance aus
    report = assistant.run_daily_maintenance()
    
    print(f"✅ Wartung abgeschlossen!")
    print(f"📊 {report['marker_count']} Marker analysiert")
    print(f"🔍 {report['trends_found']} neue Trends erkannt")
    print(f"💡 {len(report['recommendations'])} Empfehlungen generiert")
    
    if report['recommendations']:
        print("\n📋 Empfehlungen:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

if __name__ == "__main__":
    main() 