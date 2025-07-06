#!/usr/bin/env python3
"""
Marker Master Export Generator
Konsolidiert alle Marker aus verschiedenen Quellen in eine Master-YAML-Datei
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarkerCollector:
    """Sammelt und konsolidiert Marker aus verschiedenen Quellen"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.markers = {}
        self.semantic_detectors = {}
        self.duplicate_count = 0
        
    def collect_all_markers(self) -> Dict[str, Any]:
        """Hauptmethode: Sammelt alle Marker aus verschiedenen Quellen"""
        logger.info("Starte Marker-Sammlung...")
        
        # Definiere die zu durchsuchenden Ordner
        search_dirs = [
            "Assist_TXT_marker_py:/ALL_NEWMARKER01",
            "Assist_TXT_marker_py: 2/ALL_NEWMARKER01",
            "Assist_TXT_marker_py: 2/MARKERBOOK_YAML_CANVAS",
            "Assist_TXT_marker_py: 2/tension",
            "Assist_TXT_marker_py: 2/resonance",
            "Assist_TXT_marker_py: 3/ALL_NEWMARKER01",
            "Assist_TXT_marker_py: 3/MARKERBOOK_YAML_CANVAS",
            "Assist_TXT_marker_py: 3/tension",
            "Assist_TXT_marker_py: 3/resonance",
            "Assist_YAML_marker_py: 4",
            "Assist_YAML_marker_py: 4/MARKERBOOK_YAML_CANVAS",
            "Assist_YAML_marker_py: 4/tension",
            "Assist_YAML_marker_py: 4/resonance",
        ]
        
        # Sammle Marker aus jedem Verzeichnis
        for dir_path in search_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists():
                logger.info(f"Durchsuche: {dir_path}")
                self._process_directory(full_path)
            else:
                logger.warning(f"Verzeichnis nicht gefunden: {dir_path}")
        
        # Sammle semantische Detektoren
        self._collect_semantic_detectors()
        
        # Verknüpfe Marker mit Detektoren
        self._link_detectors_to_markers()
        
        logger.info(f"Sammlung abgeschlossen. {len(self.markers)} eindeutige Marker gefunden.")
        logger.info(f"{self.duplicate_count} Duplikate übersprungen.")
        
        return self.markers 

    def _process_directory(self, directory: Path):
        """Verarbeitet alle Marker-Dateien in einem Verzeichnis"""
        for file_path in directory.iterdir():
            if file_path.is_file() and self._is_marker_file(file_path):
                try:
                    self._process_file(file_path)
                except Exception as e:
                    logger.error(f"Fehler beim Verarbeiten von {file_path}: {e}")
    
    def _is_marker_file(self, file_path: Path) -> bool:
        """Prüft, ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        # Überspringe Backup-Dateien und System-Dateien
        if any(skip in name for skip in ['.backup', '.ds_store', '__pycache__']):
            return False
        # Akzeptiere Marker-Dateien
        return any(marker_id in name for marker_id in ['marker', 'knot', 'spiral', 'pattern'])
    
    def _process_file(self, file_path: Path):
        """Verarbeitet eine einzelne Marker-Datei"""
        logger.debug(f"Verarbeite: {file_path.name}")
        
        if file_path.suffix == '.yaml' or file_path.suffix == '.yml':
            self._process_yaml_file(file_path)
        elif file_path.suffix == '.txt':
            self._process_txt_file(file_path)
        elif file_path.suffix == '.json':
            self._process_json_file(file_path)
    
    def _process_yaml_file(self, file_path: Path):
        """Verarbeitet YAML-Dateien"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if isinstance(data, dict):
                # Prüfe ob es ein einzelner Marker ist
                if 'marker' in data:
                    self._add_marker(data)
                # Oder eine Liste von Markern
                elif any(key.lower().endswith('marker') for key in data.keys()):
                    for key, value in data.items():
                        if isinstance(value, list):
                            for item in value:
                                self._add_marker_from_list_format(key, item)
        except Exception as e:
            logger.error(f"Fehler beim Parsen von YAML {file_path}: {e}")
    
    def _process_txt_file(self, file_path: Path):
        """Verarbeitet TXT-Dateien mit Marker-Definitionen"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Versuche strukturierte Marker zu extrahieren
            marker_data = self._extract_marker_from_txt(content, file_path.stem)
            if marker_data:
                self._add_marker(marker_data)
        except Exception as e:
            logger.error(f"Fehler beim Lesen von {file_path}: {e}")
    
    def _process_json_file(self, file_path: Path):
        """Verarbeitet JSON-Dateien"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                if 'marker' in data:
                    self._add_marker(data)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'marker' in item:
                            self._add_marker(item)
        except Exception as e:
            logger.error(f"Fehler beim Parsen von JSON {file_path}: {e}")

    def _extract_marker_from_txt(self, content: str, file_stem: str) -> Optional[Dict[str, Any]]:
        """Extrahiert Marker-Daten aus TXT-Dateien"""
        marker_data = {}
        
        # Versuche Marker-Namen zu extrahieren
        marker_match = re.search(r'marker:\s*(\w+)', content, re.IGNORECASE)
        if marker_match:
            marker_data['marker'] = marker_match.group(1)
        else:
            # Verwende Dateinamen als Marker-Namen
            marker_name = file_stem.replace('_MARKER', '').replace('.txt', '')
            marker_data['marker'] = marker_name
        
        # Extrahiere Beschreibung
        desc_match = re.search(r'beschreibung:\s*(.+?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            marker_data['beschreibung'] = desc_match.group(1).strip()
        
        # Extrahiere Beispiele
        beispiele = []
        beispiel_section = re.search(r'beispiele:(.*?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if beispiel_section:
            beispiel_text = beispiel_section.group(1)
            # Finde alle Zeilen mit - am Anfang
            beispiele = re.findall(r'-\s*"([^"]+)"', beispiel_text)
            if not beispiele:
                # Alternative: Zeilen mit Aufzählungszeichen
                beispiele = re.findall(r'-\s*(.+)', beispiel_text)
        
        if beispiele:
            marker_data['beispiele'] = [b.strip() for b in beispiele]
        
        # Extrahiere Tags
        tags_match = re.search(r'tags:\s*\[(.*?)\]', content, re.IGNORECASE)
        if tags_match:
            tags = [t.strip() for t in tags_match.group(1).split(',')]
            marker_data['tags'] = tags
        
        return marker_data if 'marker' in marker_data else None
    
    def _add_marker(self, marker_data: Dict[str, Any]):
        """Fügt einen Marker zur Sammlung hinzu"""
        marker_name = marker_data.get('marker', '').upper()
        
        if not marker_name:
            return
        
        # Prüfe auf Duplikate
        if marker_name in self.markers:
            self.duplicate_count += 1
            # Merge Daten wenn nötig
            existing = self.markers[marker_name]
            # Füge neue Beispiele hinzu
            if 'beispiele' in marker_data:
                existing_examples = set(existing.get('beispiele', []))
                new_examples = set(marker_data.get('beispiele', []))
                existing['beispiele'] = list(existing_examples | new_examples)
            # Merge Tags
            if 'tags' in marker_data:
                existing_tags = set(existing.get('tags', []))
                new_tags = set(marker_data.get('tags', []))
                existing['tags'] = list(existing_tags | new_tags)
        else:
            # Normalisiere Marker-Struktur
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
            
            # Füge semantische Detektor-Info hinzu, falls vorhanden
            if 'semantic_grab' in marker_data:
                normalized['semantic_patterns'] = marker_data['semantic_grab']
            
            self.markers[marker_name] = normalized
    
    def _add_marker_from_list_format(self, key: str, item: Dict[str, Any]):
        """Fügt Marker aus Listen-Format hinzu (z.B. Ambivalenzmarker)"""
        if isinstance(item, dict) and 'input' in item:
            marker_name = key.upper()
            if marker_name not in self.markers:
                self.markers[marker_name] = {
                    'marker': marker_name,
                    'beschreibung': f'Automatisch generiert aus {key}',
                    'beispiele': [],
                    'tags': [key],
                    'kategorie': 'PATTERN',
                    'risk_score': 1
                }
            
            # Füge Beispiel hinzu
            if 'input' in item:
                self.markers[marker_name]['beispiele'].append(item['input'])
    
    def _collect_semantic_detectors(self):
        """Sammelt alle Python-Detektoren"""
        detector_dirs = [
            "Assist_TXT_marker_py: 2/SEMANTIC_DETECTORS_PYTHO",
            "Assist_TXT_marker_py: 3/SEMANTIC_DETECTORS_PYTHO"
        ]
        
        for dir_path in detector_dirs:
            full_path = self.base_path / dir_path
            if full_path.exists():
                for file_path in full_path.glob("*.py"):
                    if file_path.stem not in ['__init__', 'setup_py']:
                        self.semantic_detectors[file_path.stem.upper()] = file_path.name
    
    def _link_detectors_to_markers(self):
        """Verknüpft Detektoren mit passenden Markern"""
        for marker_name, marker_data in self.markers.items():
            # Suche nach passendem Detektor
            for detector_name, detector_file in self.semantic_detectors.items():
                if detector_name in marker_name or marker_name in detector_name:
                    marker_data['semantics_detector'] = detector_file
                    break 

    def export_to_yaml(self, output_file: str = "marker_master_export.yaml"):
        """Exportiert alle Marker in eine YAML-Datei"""
        # Konvertiere Marker-Dictionary in Liste für bessere Lesbarkeit
        marker_list = list(self.markers.values())
        
        # Sortiere nach Marker-Namen
        marker_list.sort(key=lambda x: x['marker'])
        
        # Füge Metadaten hinzu
        export_data = {
            'version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'total_markers': len(marker_list),
            'categories': self._get_categories(),
            'risk_levels': {
                'green': 'Kein oder nur unkritischer Marker',
                'yellow': '1-2 moderate Marker, erste Drift erkennbar',
                'blinking': '3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation',
                'red': 'Hochrisiko-Kombination, massive Drift/Manipulation'
            },
            'markers': marker_list
        }
        
        # Schreibe YAML-Datei
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, 
                     default_flow_style=False, 
                     allow_unicode=True,
                     sort_keys=False,
                     width=120)
        
        logger.info(f"YAML-Export erstellt: {output_file}")
        return output_file
    
    def export_to_json(self, output_file: str = "marker_master_export.json"):
        """Exportiert alle Marker in eine JSON-Datei"""
        # Konvertiere Marker-Dictionary in Liste
        marker_list = list(self.markers.values())
        
        # Sortiere nach Marker-Namen
        marker_list.sort(key=lambda x: x['marker'])
        
        # Füge Metadaten hinzu
        export_data = {
            'version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'total_markers': len(marker_list),
            'categories': self._get_categories(),
            'risk_levels': {
                'green': 'Kein oder nur unkritischer Marker',
                'yellow': '1-2 moderate Marker, erste Drift erkennbar',
                'blinking': '3+ Marker oder ein Hochrisiko-Marker, klare Drift/Manipulation',
                'red': 'Hochrisiko-Kombination, massive Drift/Manipulation'
            },
            'markers': marker_list
        }
        
        # Schreibe JSON-Datei
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, 
                     ensure_ascii=False, 
                     indent=2)
        
        logger.info(f"JSON-Export erstellt: {output_file}")
        return output_file
    
    def _get_categories(self) -> List[str]:
        """Sammelt alle verwendeten Kategorien"""
        categories = set()
        for marker in self.markers.values():
            categories.add(marker.get('kategorie', 'UNCATEGORIZED'))
        return sorted(list(categories))
    
    def generate_report(self):
        """Generiert einen Bericht über die gesammelten Marker"""
        print("\n" + "="*60)
        print("MARKER MASTER EXPORT - BERICHT")
        print("="*60)
        print(f"\nGesammelte Marker: {len(self.markers)}")
        print(f"Duplikate übersprungen: {self.duplicate_count}")
        print(f"Semantische Detektoren gefunden: {len(self.semantic_detectors)}")
        
        # Kategorien-Übersicht
        categories = {}
        for marker in self.markers.values():
            cat = marker.get('kategorie', 'UNCATEGORIZED')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nKategorien:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} Marker")
        
        # Marker mit Detektoren
        markers_with_detectors = sum(1 for m in self.markers.values() if 'semantics_detector' in m)
        print(f"\nMarker mit semantischen Detektoren: {markers_with_detectors}")
        
        # Top 10 Marker nach Anzahl der Beispiele
        sorted_by_examples = sorted(
            self.markers.items(), 
            key=lambda x: len(x[1].get('beispiele', [])), 
            reverse=True
        )[:10]
        
        print("\nTop 10 Marker nach Anzahl der Beispiele:")
        for name, data in sorted_by_examples:
            print(f"  - {name}: {len(data.get('beispiele', []))} Beispiele")


def main():
    """Hauptfunktion"""
    print("Marker Master Export Generator")
    print("==============================\n")
    
    # Erstelle Collector-Instanz
    collector = MarkerCollector()
    
    # Sammle alle Marker
    markers = collector.collect_all_markers()
    
    if not markers:
        logger.error("Keine Marker gefunden!")
        return
    
    # Generiere Bericht
    collector.generate_report()
    
    # Exportiere in beide Formate
    yaml_file = collector.export_to_yaml()
    json_file = collector.export_to_json()
    
    print(f"\nExport abgeschlossen:")
    print(f"  - YAML: {yaml_file}")
    print(f"  - JSON: {json_file}")
    
    # Erstelle README für die Verwendung
    readme_content = """# Marker Master Export

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

Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open("MARKER_MASTER_README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("  - README: MARKER_MASTER_README.md")


if __name__ == "__main__":
    main() 