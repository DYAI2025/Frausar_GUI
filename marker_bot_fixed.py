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
    
    def __init__(self, marker_directory: str = "/Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT"):
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
        
        # Prüfe ob das Verzeichnis existiert
        if not self.marker_dir.exists():
            logger.error(f"Marker-Verzeichnis nicht gefunden: {self.marker_dir}")
            raise FileNotFoundError(f"Verzeichnis {self.marker_dir} existiert nicht!")
    
    def collect_all_markers(self) -> Dict[str, Any]:
        """
        Sammelt alle Marker aus allen Verzeichnissen
        """
        logger.info("Sammle alle Marker aus dem Projekt...")
        
        collected_markers = {}
        
        # Durchsuche das Hauptverzeichnis und alle Unterverzeichnisse
        def scan_directory(directory: Path, prefix: str = ""):
            if not directory.exists():
                return
                
            logger.info(f"Durchsuche: {directory}")
            
            # Sammle alle Dateien im aktuellen Verzeichnis
            for file_path in directory.iterdir():
                if file_path.is_file() and self._is_marker_file(file_path):
                    try:
                        marker_data = self._parse_marker_file(file_path)
                        if marker_data:
                            marker_name = marker_data.get('marker', file_path.stem)
                            # Füge Pfad-Info hinzu
                            marker_data['source_file'] = str(file_path)
                            marker_data['source_directory'] = str(directory)
                            collected_markers[marker_name] = marker_data
                    except Exception as e:
                        logger.error(f"Fehler beim Parsen von {file_path}: {e}")
                
                # Rekursiv in Unterverzeichnisse
                elif file_path.is_dir() and not file_path.name.startswith('.'):
                    scan_directory(file_path, f"{prefix}{file_path.name}/")
        
        # Starte Scan vom Hauptverzeichnis
        scan_directory(self.marker_dir)
        
        self.all_markers = collected_markers
        logger.info(f"{len(collected_markers)} Marker erfolgreich gesammelt")
        
        # Debug-Ausgabe der gefundenen Dateien
        for marker_name, marker_data in collected_markers.items():
            logger.debug(f"Gefunden: {marker_name} in {marker_data.get('source_file', 'Unbekannt')}")
        
        return collected_markers
    
    def _is_marker_file(self, file_path: Path) -> bool:
        """Prüft ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        
        # Überspringe System-Dateien
        if any(skip in name for skip in ['.backup', '.ds_store', '__pycache__', '.git']):
            return False
        
        # Erweiterte Marker-Erkennung
        marker_indicators = [
            'marker', 'knot', 'spiral', 'pattern', 'detector', 
            'semantic', 'gaslighting', 'love_bombing', 'manipulation',
            'scam', 'fraud', 'drift'
        ]
        
        # Prüfe Dateiname und Erweiterung
        return (any(indicator in name for indicator in marker_indicators) and 
                file_path.suffix in ['.txt', '.yaml', '.yml', '.json', '.py'])
    
    def _parse_marker_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parst eine Marker-Datei und extrahiert die Daten"""
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict):
                        # Wenn kein 'marker' Feld vorhanden, verwende Dateiname
                        if 'marker' not in data:
                            data['marker'] = file_path.stem
                        return data
            
            elif file_path.suffix == '.txt':
                content = file_path.read_text(encoding='utf-8')
                return self._extract_marker_from_txt(content, file_path.stem)
            
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'marker' not in data:
                            data['marker'] = file_path.stem
                        return data
            
            elif file_path.suffix == '.py':
                # Einfache Python-Datei-Parsing für Marker-Definitionen
                content = file_path.read_text(encoding='utf-8')
                return self._extract_marker_from_python(content, file_path.stem)
                
        except Exception as e:
            logger.debug(f"Fehler beim Parsen von {file_path}: {e}")
        return None
    
    def _extract_marker_from_python(self, content: str, file_stem: str) -> Optional[Dict[str, Any]]:
        """Extrahiert Marker-Daten aus Python-Dateien"""
        marker_data = {}
        
        # Suche nach Marker-Definitionen in Python-Kommentaren oder Strings
        marker_patterns = [
            r'MARKER_NAME\s*=\s*["\']([^"\']+)["\']',
            r'marker["\']?\s*:\s*["\']([^"\']+)["\']',
            r'# MARKER:\s*(\w+)'
        ]
        
        for pattern in marker_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                marker_data['marker'] = match.group(1)
                break
        
        if not marker_data.get('marker'):
            marker_data['marker'] = file_stem.replace('_MARKER', '').replace('.py', '')
        
        # Suche nach Beschreibung in Docstrings oder Kommentaren
        desc_patterns = [
            r'"""([^"]+)"""',
            r"'''([^']+)'''",
            r'# BESCHREIBUNG:\s*(.+)',
            r'DESCRIPTION\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 10:  # Nur sinnvolle Beschreibungen
                    marker_data['beschreibung'] = desc[:200]  # Begrenzen auf 200 Zeichen
                    break
        
        # Extrahiere Patterns/Regex
        pattern_matches = re.findall(r'r["\']([^"\']+)["\']', content)
        if pattern_matches:
            marker_data['patterns'] = pattern_matches[:5]  # Max 5 Patterns
        
        marker_data['kategorie'] = 'PYTHON_DETECTOR'
        marker_data['tags'] = ['python', 'semantic', 'detector']
        
        return marker_data
    
    def _extract_marker_from_txt(self, content: str, file_stem: str) -> Optional[Dict[str, Any]]:
        """Extrahiert Marker-Daten aus TXT-Dateien"""
        marker_data = {}
        
        # Marker-Namen extrahieren (mehrere Varianten)
        marker_patterns = [
            r'marker:\s*(\w+)',
            r'MARKER:\s*(\w+)',
            r'name:\s*(\w+)',
            r'# MARKER:\s*(\w+)'
        ]
        
        for pattern in marker_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                marker_data['marker'] = match.group(1)
                break
        
        if not marker_data.get('marker'):
            # Fallback: Verwende Dateiname
            marker_name = file_stem.replace('_MARKER', '').replace('.txt', '')
            marker_data['marker'] = marker_name
        
        # Beschreibung extrahieren (erweiterte Patterns)
        desc_patterns = [
            r'beschreibung:\s*(.+?)(?=\n\w+:|$)',
            r'description:\s*(.+?)(?=\n\w+:|$)',
            r'# BESCHREIBUNG:\s*(.+?)(?=\n|$)',
            r'"""([^"]+)"""'
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 5:
                    marker_data['beschreibung'] = desc
                    break
        
        # Beispiele extrahieren (erweiterte Patterns)
        beispiele = []
        
        # Verschiedene Beispiel-Formate erkennen
        beispiel_patterns = [
            r'beispiele:(.*?)(?=\n\w+:|$)',
            r'examples:(.*?)(?=\n\w+:|$)',
            r'# BEISPIELE:(.*?)(?=\n\w+:|$)'
        ]
        
        for pattern in beispiel_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                beispiel_text = match.group(1)
                
                # Extrahiere Beispiele in verschiedenen Formaten
                beispiel_formats = [
                    r'-\s*"([^"]+)"',  # - "Beispiel"
                    r'-\s*([^-\n]+)',  # - Beispiel ohne Anführungszeichen
                    r'•\s*([^•\n]+)',  # • Beispiel
                    r'\*\s*([^*\n]+)'  # * Beispiel
                ]
                
                for beispiel_format in beispiel_formats:
                    found = re.findall(beispiel_format, beispiel_text)
                    if found:
                        beispiele.extend([b.strip() for b in found if len(b.strip()) > 3])
                        break
        
        if beispiele:
            marker_data['beispiele'] = beispiele
        
        # Tags extrahieren
        tags_patterns = [
            r'tags:\s*\[(.*?)\]',
            r'tags:\s*(.+?)(?=\n|$)',
            r'# TAGS:\s*(.+?)(?=\n|$)'
        ]
        
        for pattern in tags_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                tags_text = match.group(1)
                tags = [t.strip(' "\'') for t in re.split(r'[,\s]+', tags_text) if t.strip()]
                if tags:
                    marker_data['tags'] = tags
                    break
        
        # Kategorie ableiten
        if not marker_data.get('kategorie'):
            marker_data['kategorie'] = self._detect_category_from_content(content, marker_data.get('marker', ''))
        
        return marker_data if 'marker' in marker_data else None
    
    def _detect_category_from_content(self, content: str, marker_name: str) -> str:
        """Erkennt die Kategorie basierend auf Inhalt und Marker-Namen"""
        content_lower = content.lower()
        name_lower = marker_name.lower()
        
        # Kategorisierungs-Regeln
        categories = {
            'GASLIGHTING': ['gaslighting', 'realität', 'wahrnehmung', 'einbildung', 'verrückt'],
            'LOVE_BOMBING': ['love_bombing', 'zuneigung', 'überwältigen', 'intensive', 'geschenke'],
            'FINANCIAL_FRAUD': ['geld', 'money', 'invest', 'bitcoin', 'krypto', 'notfall', 'schulden'],
            'ISOLATION': ['isolation', 'isolier', 'freunde', 'familie', 'kontakt', 'allein'],
            'GUILT_TRIPPING': ['schuld', 'guilt', 'verantwortung', 'enttäuscht', 'verletzt'],
            'MANIPULATION': ['manipulation', 'kontroll', 'macht', 'dominanz', 'unterwerfung'],
            'EMOTIONAL_ABUSE': ['emotional', 'gefühl', 'emotion', 'psycho', 'mental'],
            'DECEPTION': ['lüge', 'täuschung', 'betrug', 'fake', 'falsch', 'scam']
        }
        
        # Prüfe Content und Marker-Name
        combined_text = content_lower + " " + name_lower
        
        for category, keywords in categories.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return 'UNCATEGORIZED'
    
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
                'risk_score': marker_data.get('risk_score', 1),
                'source_file': marker_data.get('source_file', ''),
                'patterns': marker_data.get('patterns', [])
            }
            normalized_markers.append(normalized)
        
        # Sortiere nach Marker-Namen
        normalized_markers.sort(key=lambda x: x['marker'])
        
        # Erstelle Export-Datenstruktur
        export_data = {
            'version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'total_markers': len(normalized_markers),
            'source_directory': str(self.marker_dir),
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
pip install pyyaml requests

# 2. System testen
python3 marker_assistant_bot_fixed.py
```

## 💻 Verwendung

### Bot starten

```bash
# Bot mit Standard-Pfad starten
python3 marker_assistant_bot_fixed.py

# Bot mit eigenem Pfad starten
python3 -c "
from marker_assistant_bot_fixed import MarkerAssistant
assistant = MarkerAssistant('/Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT')
report = assistant.run_daily_maintenance()
print(f'✅ {report[\"marker_count\"]} Marker analysiert')
"
```

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
from marker_assistant_bot_fixed import MarkerAssistant

# Marker-Assistant initialisieren
assistant = MarkerAssistant('/Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT')

# Alle Marker sammeln
markers = assistant.collect_all_markers()
print(f"Gefundene Marker: {len(markers)}")

# Master-Export generieren
export_files = assistant.generate_master_export()
print(f"Export erstellt: {export_files}")

# Daily Maintenance ausführen
report = assistant.run_daily_maintenance()
```

## 🎯 Risk-Level System

Das System bewertet Texte mit einem vierstufigen Risiko-System:

- 🟢 **Grün**: Kein oder nur unkritischer Marker
- 🟡 **Gelb**: 1-2 moderate Marker, erste Drift erkennbar
- 🟠 **Blinkend**: 3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation
- 🔴 **Rot**: Hochrisiko-Kombination, massive Drift/Manipulation

## 📊 Erkannte Muster

{self._generate_pattern_overview()}

## 🔧 Bot-Funktionen

### Hauptfunktionen des Bots:

1. **collect_all_markers()** - Scannt alle Verzeichnisse nach Marker-Dateien
2. **generate_master_export()** - Erstellt YAML/JSON Master-Dateien
3. **generate_system_readme()** - Generiert diese Dokumentation
4. **run_daily_maintenance()** - Führt automatische Wartung durch
5. **scan_for_new_trends()** - Erkennt neue Scammer-Trends

### Unterstützte Dateiformate:

- **.txt** - Textdateien mit Marker-Definitionen
- **.yaml/.yml** - YAML-formatierte Marker
- **.json** - JSON-formatierte Marker
- **.py** - Python-Dateien mit Detector-Code

## 📈 Statistiken

Das System enthält aktuell:
- {total_markers} eindeutige Marker
- {total_examples}+ Beispiel-Patterns
- {len(categories)} Kategorien
- 4 Risiko-Stufen
- Quelle: {self.marker_dir}

## 🛠️ Troubleshooting

### Bot startet nicht
```bash
# Prüfe ob der Pfad existiert
ls -la /Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT

# Installiere fehlende Dependencies
pip install pyyaml requests pathlib
```

### Keine Marker gefunden
```bash
# Debug-Modus aktivieren
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from marker_assistant_bot_fixed import MarkerAssistant
assistant = MarkerAssistant('/Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT')
markers = assistant.collect_all_markers()
"
```

### Pfad-Probleme
```bash
# Aktuellen Pfad anzeigen
pwd

# Marker-Verzeichnis prüfen
find /Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT -name "*marker*" -type f
```

## 📝 Lizenz

Dieses System ist für Forschungs- und Bildungszwecke gedacht. Bei kommerzieller Nutzung bitte Rücksprache halten.

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
            kategorie = marker_data.get('kategorie', '').lower()
            
            if any(tag in name_lower or tag in kategorie for tag in ['gaslighting', 'love_bombing', 'manipulation', 'guilt', 'blame']):
                categories['Manipulationstechniken'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
            elif any(tag in name_lower or tag in kategorie for tag in ['ambivalence', 'escalation', 'arousal', 'emotion']):
                categories['Emotionale Dynamiken'].append((marker_name, marker_data.get('beschreibung', '')[:60]))
            elif any(tag in name_lower or tag in kategorie for tag in ['drama', 'isolation', 'comparison', 'triangle']):
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
    
    def run_daily_maintenance(self):
        """
        Führt tägliche Wartungsroutinen aus
        """
        logger.info("=== Starte tägliche FRAUSAR Marker-Wartung ===")
        
        try:
            # 1. Sammle alle Marker
            markers = self.collect_all_markers()
            logger.info(f"✅ {len(markers)} Marker gesammelt")
            
            # 2. Generiere Master-Export
            export_files = self.generate_master_export()
            logger.info(f"✅ Master-Export erstellt: {export_files.get('marker_count', 0)} Marker")
            
            # 3. Generiere Dokumentation
            readme_file = self.generate_system_readme()
            logger.info(f"✅ Dokumentation erstellt: {readme_file}")
            
            # 4. Erstelle Wartungsreport
            report = {
                "timestamp": datetime.now().isoformat(),
                "marker_count": len(markers),
                "source_directory": str(self.marker_dir),
                "export_files": export_files,
                "readme_file": readme_file,
                "categories": self._get_categories(list(markers.values())),
                "recommendations": self._generate_recommendations(markers)
            }
            
            # Report speichern
            report_path = Path("daily_maintenance_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Wartung abgeschlossen. Report: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Fehler bei der Wartung: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "marker_count": 0
            }
    
    def _generate_recommendations(self, markers: Dict[str, Any]) -> List[str]:
        """
        Generiert Empfehlungen basierend auf der Analyse
        """
        recommendations = []
        
        # Analysiere Marker-Performance
        total_examples = 0
        markers_without_examples = 0
        
        for marker_name, marker_data in markers.items():
            examples = marker_data.get('beispiele', [])
            total_examples += len(examples)
            
            if len(examples) < 3:
                markers_without_examples += 1
                recommendations.append(f"Marker '{marker_name}' benötigt mehr Beispiele ({len(examples)} vorhanden)")
        
        # Allgemeine Empfehlungen
        if len(markers) < 10:
            recommendations.append("System könnte von zusätzlichen spezifischen Markern profitieren")
        
        if markers_without_examples > len(markers) * 0.3:
            recommendations.append(f"Viele Marker haben zu wenige Beispiele ({markers_without_examples}/{len(markers)})")
        
        avg_examples = total_examples / len(markers) if markers else 0
        if avg_examples < 2:
            recommendations.append(f"Durchschnittlich nur {avg_examples:.1f} Beispiele pro Marker - sollte mindestens 3 sein")
        
        return recommendations

def main():
    """
    Hauptfunktion für den Marker Assistant
    """
    print("🤖 FRAUSAR Marker Assistant Bot gestartet")
    print("=" * 50)
    
    try:
        # Bot mit dem korrekten Pfad initialisieren
        assistant = MarkerAssistant("/Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT")
        
        print(f"📁 Suche Marker in: {assistant.marker_dir}")
        
        # Prüfe ob Verzeichnis existiert
        if not assistant.marker_dir.exists():
            print(f"❌ Fehler: Verzeichnis {assistant.marker_dir} nicht gefunden!")
            print("Verfügbare Optionen:")
            print("1. Erstelle das Verzeichnis")
            print("2. Ändere den Pfad in der main() Funktion")
            return
        
        # Führe Daily Maintenance aus
        print("🔄 Starte Wartung...")
        report = assistant.run_daily_maintenance()
        
        if "error" in report:
            print(f"❌ Fehler: {report['error']}")
        else:
            print(f"✅ Wartung abgeschlossen!")
            print(f"📊 {report['marker_count']} Marker analysiert")
            print(f"💡 {len(report.get('recommendations', []))} Empfehlungen generiert")
            
            if report.get('recommendations'):
                print("\n📋 Empfehlungen:")
                for i, rec in enumerate(report['recommendations'], 1):
                    print(f"  {i}. {rec}")
            
            print(f"\n📄 Generierte Dateien:")
            export_files = report.get('export_files', {})
            if export_files.get('yaml'):
                print(f"  - {export_files['yaml']}")
            if export_files.get('json'):
                print(f"  - {export_files['json']}")
            if report.get('readme_file'):
                print(f"  - {report['readme_file']}")
            print(f"  - daily_maintenance_report.json")
        
    except FileNotFoundError as e:
        print(f"❌ Verzeichnis-Fehler: {e}")
        print("\n🔧 Problemlösung:")
        print("1. Prüfe ob der Pfad korrekt ist:")
        print("   ls -la /Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT")
        print("2. Erstelle das Verzeichnis falls es nicht existiert:")
        print("   mkdir -p /Users/benjaminpoersch/claudeALL_SEMANTIC_MARKER_TXT")
        print("3. Oder passe den Pfad in der main() Funktion an")
        
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        print("Aktiviere Debug-Modus für mehr Informationen:")
        print("python3 -c \"import logging; logging.basicConfig(level=logging.DEBUG); exec(open('marker_assistant_bot_fixed.py').read())\"")

if __name__ == "__main__":
    main()