#!/usr/bin/env python3
"""
Connection Status Fix - Phase 3
Diagnostiziert und repariert das Connection-Status-Problem
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStatusFixer:
    """
    Diagnostiziert und repariert Connection-Status-Probleme
    """
    
    def __init__(self, markers_directory: str = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"):
        self.markers_directory = Path(markers_directory)
        self.semantic_grabber_file = self.markers_directory / "SemanticGrabberLibrary" / "semantic_grabber_library.yaml"
        self.markers = {}
        self.semantic_grabbers = {}
        self.load_data()
    
    def load_data(self):
        """
        Lädt alle Marker und Semantic Grabber
        """
        # Lade Marker
        self.load_all_markers()
        
        # Lade Semantic Grabbers
        self.load_semantic_grabbers()
        
        logger.info(f"Loaded {len(self.markers)} markers and {len(self.semantic_grabbers)} semantic grabbers")
    
    def load_all_markers(self):
        """
        Lädt alle Marker aus dem Verzeichnis
        """
        for file_path in self.markers_directory.glob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                
                if content:
                    marker_name = file_path.stem
                    self.markers[marker_name] = {
                        'file_path': file_path,
                        'content': content
                    }
            except Exception as e:
                logger.warning(f"Could not load marker {file_path}: {e}")
    
    def load_semantic_grabbers(self):
        """
        Lädt die Semantic Grabber Library
        """
        if not self.semantic_grabber_file.exists():
            logger.warning(f"Semantic Grabber Library not found: {self.semantic_grabber_file}")
            return
        
        try:
            with open(self.semantic_grabber_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Extrahiere Grabber aus der Struktur
            if 'semantic_grabbers' in data:
                self.semantic_grabbers = data['semantic_grabbers']
            else:
                self.semantic_grabbers = data
                
        except Exception as e:
            logger.error(f"Error loading semantic grabbers: {e}")
    
    def analyze_connections(self) -> Dict:
        """
        Analysiert die Verbindungen zwischen Markern und Grabbern
        """
        analysis = {
            'total_markers': len(self.markers),
            'total_grabbers': len(self.semantic_grabbers),
            'connected_markers': 0,
            'unconnected_markers': 0,
            'orphaned_grabbers': 0,
            'connection_details': {},
            'problems': []
        }
        
        # Analysiere Marker-Verbindungen
        grabber_usage = set()
        
        for marker_name, marker_info in self.markers.items():
            content = marker_info['content']
            
            # Suche nach Grabber-Referenzen
            grabber_id = self.find_grabber_reference(content)
            
            if grabber_id:
                analysis['connected_markers'] += 1
                grabber_usage.add(grabber_id)
                
                # Prüfe ob Grabber existiert
                if grabber_id not in self.semantic_grabbers:
                    analysis['problems'].append({
                        'type': 'broken_reference',
                        'marker': marker_name,
                        'grabber_id': grabber_id,
                        'description': f"Marker {marker_name} referenziert nicht-existenten Grabber {grabber_id}"
                    })
                
                analysis['connection_details'][marker_name] = {
                    'grabber_id': grabber_id,
                    'status': 'connected' if grabber_id in self.semantic_grabbers else 'broken'
                }
            else:
                analysis['unconnected_markers'] += 1
                analysis['connection_details'][marker_name] = {
                    'grabber_id': None,
                    'status': 'not_connected'
                }
        
        # Finde verwaiste Grabber
        for grabber_id in self.semantic_grabbers:
            if grabber_id not in grabber_usage:
                analysis['orphaned_grabbers'] += 1
                analysis['problems'].append({
                    'type': 'orphaned_grabber',
                    'grabber_id': grabber_id,
                    'description': f"Grabber {grabber_id} wird von keinem Marker verwendet"
                })
        
        return analysis
    
    def find_grabber_reference(self, content: Dict) -> str:
        """
        Findet Grabber-Referenzen in Marker-Content
        """
        # Verschiedene mögliche Felder für Grabber-Referenzen
        grabber_fields = [
            'semantic_grabber_id',
            'semantische_grabber_id',
            'grabber_id',
            'semantic_grab_id'
        ]
        
        # Suche in verschiedenen Strukturen
        for field in grabber_fields:
            if field in content:
                return content[field]
        
        # Suche in nested structures
        if 'marker' in content and isinstance(content['marker'], dict):
            for field in grabber_fields:
                if field in content['marker']:
                    return content['marker'][field]
        
        # Suche in semantic_grab structure
        if 'semantic_grab' in content:
            grab_data = content['semantic_grab']
            if isinstance(grab_data, dict) and 'id' in grab_data:
                return grab_data['id']
        
        return None
    
    def fix_broken_connections(self) -> Dict:
        """
        Repariert defekte Verbindungen
        """
        analysis = self.analyze_connections()
        fix_results = {
            'fixed_connections': 0,
            'created_grabbers': 0,
            'errors': []
        }
        
        for problem in analysis['problems']:
            if problem['type'] == 'broken_reference':
                # Versuche Grabber zu erstellen oder Referenz zu reparieren
                marker_name = problem['marker']
                broken_grabber_id = problem['grabber_id']
                
                # Erstelle neuen Grabber basierend auf Marker-Beispielen
                marker_content = self.markers[marker_name]['content']
                examples = self.extract_examples(marker_content)
                
                if examples:
                    new_grabber = {
                        'beschreibung': f"Automatisch erstellt für {marker_name}",
                        'patterns': examples[:10],  # Limitiere auf 10 Patterns
                        'created_from': marker_name,
                        'created_at': '2025-07-13T23:59:59',
                        'auto_generated': True
                    }
                    
                    self.semantic_grabbers[broken_grabber_id] = new_grabber
                    fix_results['created_grabbers'] += 1
                    logger.info(f"Created grabber {broken_grabber_id} for {marker_name}")
        
        # Speichere aktualisierte Grabber Library
        if fix_results['created_grabbers'] > 0:
            self.save_semantic_grabbers()
        
        return fix_results
    
    def extract_examples(self, content: Dict) -> List[str]:
        """
        Extrahiert Beispiele aus Marker-Content
        """
        examples = []
        
        # Verschiedene mögliche Felder für Beispiele
        example_fields = ['beispiele', 'examples', 'patterns']
        
        for field in example_fields:
            if field in content and isinstance(content[field], list):
                examples.extend(content[field])
        
        # Suche in nested structures
        if 'marker' in content and isinstance(content['marker'], dict):
            for field in example_fields:
                if field in content['marker'] and isinstance(content['marker'][field], list):
                    examples.extend(content['marker'][field])
        
        return [ex for ex in examples if isinstance(ex, str) and ex.strip()]
    
    def save_semantic_grabbers(self):
        """
        Speichert die aktualisierte Semantic Grabber Library
        """
        try:
            # Erstelle Backup
            backup_file = self.semantic_grabber_file.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if self.semantic_grabber_file.exists():
                backup_file.write_text(self.semantic_grabber_file.read_text(encoding='utf-8'), encoding='utf-8')
            
            # Speichere aktualisierte Daten
            data = {
                'marker_name': 'semantic_grabber_library',
                'semantic_grabbers': self.semantic_grabbers
            }
            
            with open(self.semantic_grabber_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            logger.info(f"Saved updated semantic grabber library to {self.semantic_grabber_file}")
            
        except Exception as e:
            logger.error(f"Error saving semantic grabbers: {e}")
    
    def generate_connection_report(self) -> str:
        """
        Generiert einen umfassenden Connection-Report
        """
        analysis = self.analyze_connections()
        
        report = f"""
# Connection Status Analysis Report - Phase 3

## 📊 Übersicht

### Statistiken:
- **Gesamte Marker:** {analysis['total_markers']}
- **Gesamte Grabber:** {analysis['total_grabbers']}
- **Verbundene Marker:** {analysis['connected_markers']} ({analysis['connected_markers']/analysis['total_markers']*100:.1f}%)
- **Nicht verbundene Marker:** {analysis['unconnected_markers']} ({analysis['unconnected_markers']/analysis['total_markers']*100:.1f}%)
- **Verwaiste Grabber:** {analysis['orphaned_grabbers']}

## 🔍 Probleme gefunden: {len(analysis['problems'])}

### Defekte Referenzen:
"""
        
        broken_refs = [p for p in analysis['problems'] if p['type'] == 'broken_reference']
        if broken_refs:
            for problem in broken_refs:
                report += f"- **{problem['marker']}** → `{problem['grabber_id']}` (nicht existent)\n"
        else:
            report += "- Keine defekten Referenzen gefunden ✅\n"
        
        report += f"""
### Verwaiste Grabber:
"""
        
        orphaned = [p for p in analysis['problems'] if p['type'] == 'orphaned_grabber']
        if orphaned:
            for problem in orphaned:
                report += f"- **{problem['grabber_id']}** (nicht verwendet)\n"
        else:
            report += "- Keine verwaisten Grabber gefunden ✅\n"
        
        report += f"""
## 📋 Verbindungsdetails

### Verbundene Marker:
"""
        
        connected = {k: v for k, v in analysis['connection_details'].items() if v['status'] == 'connected'}
        for marker, details in list(connected.items())[:10]:  # Zeige ersten 10
            report += f"- **{marker}** → `{details['grabber_id']}` ✅\n"
        
        if len(connected) > 10:
            report += f"- ... und {len(connected) - 10} weitere\n"
        
        report += f"""
### Nicht verbundene Marker:
"""
        
        not_connected = {k: v for k, v in analysis['connection_details'].items() if v['status'] == 'not_connected'}
        for marker in list(not_connected.keys())[:10]:  # Zeige ersten 10
            report += f"- **{marker}** ❌\n"
        
        if len(not_connected) > 10:
            report += f"- ... und {len(not_connected) - 10} weitere\n"
        
        report += f"""
## 🔧 Lösungsvorschläge

### Für nicht verbundene Marker:
1. **Automatische Grabber-Erstellung:** Erstelle Grabber basierend auf Marker-Beispielen
2. **Manuelle Zuordnung:** Weise existierende Grabber zu ähnlichen Markern zu
3. **Grabber-Merge:** Kombiniere ähnliche Marker zu einem Grabber

### Für verwaiste Grabber:
1. **Zuordnung prüfen:** Finde passende Marker für ungenutzte Grabber
2. **Grabber-Bereinigung:** Entferne ungenutzte Grabber
3. **Dokumentation:** Dokumentiere Zweck ungenutzter Grabber

## 📋 Nächste Schritte

1. **Sofort:** Führe `fix_broken_connections()` aus
2. **Kurz:** Überprüfe und teste reparierte Verbindungen
3. **Mittel:** Implementiere Connection-Status-Anzeige in GUI
4. **Lang:** Automatisiere Connection-Monitoring

---

**Status:** {"⚠️ Probleme gefunden" if analysis['problems'] else "✅ Alle Verbindungen OK"}
"""
        
        return report

def main():
    """
    Hauptfunktion
    """
    print("🔧 Connection Status Fix - Phase 3")
    print("=" * 50)
    
    # Initialisiere Fixer
    fixer = ConnectionStatusFixer()
    
    # Analysiere Verbindungen
    analysis = fixer.analyze_connections()
    
    print(f"📊 Analysiert: {analysis['total_markers']} Marker, {analysis['total_grabbers']} Grabber")
    print(f"✅ Verbunden: {analysis['connected_markers']}")
    print(f"❌ Nicht verbunden: {analysis['unconnected_markers']}")
    print(f"🔍 Probleme: {len(analysis['problems'])}")
    
    # Repariere defekte Verbindungen
    if analysis['problems']:
        print("\n🔧 Repariere defekte Verbindungen...")
        fix_results = fixer.fix_broken_connections()
        print(f"✅ Erstellt: {fix_results['created_grabbers']} neue Grabber")
    
    # Generiere Report
    report = fixer.generate_connection_report()
    
    # Speichere Report
    with open("connection_status_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n✅ Connection-Status-Analyse abgeschlossen!")
    print("📊 Report gespeichert: connection_status_report.md")

if __name__ == "__main__":
    from datetime import datetime
    main() 