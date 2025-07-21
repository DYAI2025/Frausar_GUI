#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatische Detector-Schema Updates
===================================
Findet neue *.py-Detector-Module und trägt sie ins DETECT-Schema ein.
Automatisiert die Integration neuer Detector-Python-Skripte.
"""

import os
import ast
import yaml
import json
from pathlib import Path
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfiguration - anpassbare Pfade
DEFAULT_SCHEMA_PATH = "DETECT_default_marker_schema.yaml"
DEFAULT_DETECTOR_DIRS = [
    "detectors",
    "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/_python",
    "../ALL_SEMANTIC_MARKER_TXT/SEMANTIC_DETECTORS_PYTHO",
    ".",  # Aktuelles Verzeichnis für Tests
]

# Fallback-Schema wenn Datei nicht existiert
FALLBACK_SCHEMA = {
    "meta": {
        "title": "FRAUSAR Detector Schema",
        "version": "1.0",
        "description": "Automatisch generiertes Schema für Detector-Module",
        "created_at": datetime.now().isoformat(),
        "auto_generated": True
    },
    "application_schema": {
        "detectors": {}
    }
}

class DetectorUpdater:
    """Hauptklasse für die automatische Detector-Schema-Aktualisierung"""
    
    def __init__(self, schema_path=None, detector_dirs=None):
        self.schema_path = Path(schema_path or DEFAULT_SCHEMA_PATH)
        self.detector_dirs = detector_dirs or DEFAULT_DETECTOR_DIRS
        self.stats = {
            "modules_found": 0,
            "modules_added": 0,
            "modules_updated": 0,
            "errors": []
        }
        
    def find_detector_modules(self):
        """Findet alle Python-Detector-Module in den konfigurierten Verzeichnissen"""
        detector_modules = {}
        
        for base_dir in self.detector_dirs:
            base_path = Path(base_dir)
            if not base_path.exists():
                logger.warning(f"Verzeichnis nicht gefunden: {base_path}")
                continue
                
            logger.info(f"Durchsuche: {base_path}")
            
            # Durchsuche Verzeichnis nach Python-Dateien
            for py_file in base_path.glob("*.py"):
                if self._is_detector_file(py_file):
                    try:
                        detector_classes = self._extract_detector_classes(py_file)
                        if detector_classes:
                            module_name = py_file.stem
                            detector_modules[module_name] = {
                                "file_path": py_file,
                                "classes": detector_classes,
                                "module_path": self._get_module_path(py_file, base_path)
                            }
                            self.stats["modules_found"] += 1
                            logger.debug(f"Gefunden: {module_name} mit {len(detector_classes)} Detector-Klassen")
                    except Exception as e:
                        logger.error(f"Fehler beim Verarbeiten von {py_file}: {e}")
                        self.stats["errors"].append(f"{py_file}: {e}")
                        
        logger.info(f"Insgesamt {len(detector_modules)} Detector-Module gefunden")
        return detector_modules
        
    def _is_detector_file(self, file_path):
        """Prüft ob eine Python-Datei ein Detector-Modul ist"""
        name = file_path.name.lower()
        
        # Ausschließen von Standard-Dateien
        if name.startswith('_') or name in ['setup.py', 'test.py', '__init__.py']:
            return False
            
        # Muss Python-Datei sein und Detector-Keywords enthalten
        return (name.endswith('.py') and 
                any(keyword in name for keyword in ['detector', 'detect', 'marker', 'semantic']))
                
    def _extract_detector_classes(self, py_file):
        """Extrahiert alle Detector-Klassen aus einer Python-Datei"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse Python AST
            tree = ast.parse(content, filename=str(py_file))
            
            detector_classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    # Prüfe ob es sich um eine Detector-Klasse handelt
                    if (class_name.endswith('Detector') or 
                        'detector' in class_name.lower() or
                        self._has_detector_methods(node)):
                        detector_classes.append({
                            "name": class_name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node) or ""
                        })
                        
            return detector_classes
            
        except Exception as e:
            logger.error(f"Fehler beim Parsen von {py_file}: {e}")
            return []
            
    def _has_detector_methods(self, class_node):
        """Prüft ob eine Klasse typische Detector-Methoden hat"""
        method_names = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_names.append(item.name.lower())
                
        detector_methods = ['detect', 'analyze', 'scan', 'match', 'process']
        return any(method in ' '.join(method_names) for method in detector_methods)
        
    def _get_module_path(self, py_file, base_path):
        """Erstellt den relativen Modul-Pfad für den Import"""
        try:
            relative_path = py_file.relative_to(base_path)
            module_parts = list(relative_path.parts[:-1])  # Ohne .py Extension
            module_parts.append(relative_path.stem)
            return '.'.join(module_parts) if module_parts else relative_path.stem
        except ValueError:
            # Fallback für absolute Pfade
            return py_file.stem
            
    def load_schema(self):
        """Lädt das bestehende Detector-Schema oder erstellt ein neues"""
        if self.schema_path.exists():
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    schema = yaml.safe_load(f)
                logger.info(f"Schema geladen: {self.schema_path}")
                return schema
            except Exception as e:
                logger.error(f"Fehler beim Laden des Schemas: {e}")
                logger.info("Verwende Fallback-Schema")
                return FALLBACK_SCHEMA.copy()
        else:
            logger.info("Schema-Datei nicht gefunden, erstelle neue")
            return FALLBACK_SCHEMA.copy()
            
    def save_schema(self, schema):
        """Speichert das aktualisierte Schema"""
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            self.schema_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.schema_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(schema, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
            logger.info(f"Schema gespeichert: {self.schema_path}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Schemas: {e}")
            self.stats["errors"].append(f"Save schema: {e}")
            return False
            
    def update_schema_with_detectors(self, schema, detector_modules):
        """Aktualisiert das Schema mit den gefundenen Detector-Modulen"""
        # Stelle sicher, dass die Struktur existiert
        if "application_schema" not in schema:
            schema["application_schema"] = {}
        if "detectors" not in schema["application_schema"]:
            schema["application_schema"]["detectors"] = {}
            
        detectors_config = schema["application_schema"]["detectors"]
        
        for module_name, module_info in detector_modules.items():
            # Wähle die beste Detector-Klasse (erste oder die mit "Detector" im Namen)
            best_class = None
            for cls in module_info["classes"]:
                if cls["name"].endswith("Detector"):
                    best_class = cls
                    break
            if not best_class and module_info["classes"]:
                best_class = module_info["classes"][0]
                
            if best_class:
                # Prüfe ob bereits vorhanden
                if module_name in detectors_config:
                    old_config = detectors_config[module_name]
                    logger.info(f"Aktualisiere bestehenden Detector: {module_name}")
                    self.stats["modules_updated"] += 1
                else:
                    logger.info(f"Neuer Detector hinzugefügt: {module_name}")
                    self.stats["modules_added"] += 1
                    
                # Konfiguration erstellen/aktualisieren
                detector_config = {
                    "module": module_info["module_path"],
                    "class": best_class["name"],
                    "file_path": str(module_info["file_path"]),
                    "description": best_class["docstring"][:100] + "..." if len(best_class["docstring"]) > 100 else best_class["docstring"],
                    "last_updated": datetime.now().isoformat(),
                    "auto_generated": True
                }
                
                # Zusätzliche Klassen als Alternative speichern
                if len(module_info["classes"]) > 1:
                    detector_config["alternative_classes"] = [
                        cls["name"] for cls in module_info["classes"] if cls != best_class
                    ]
                    
                detectors_config[module_name] = detector_config
                
        # Schema-Metadaten aktualisieren
        if "meta" not in schema:
            schema["meta"] = {}
        schema["meta"]["last_updated"] = datetime.now().isoformat()
        schema["meta"]["total_detectors"] = len(detectors_config)
        
        return schema
        
    def update_all(self):
        """Hauptmethode: Aktualisiert das gesamte Detector-Schema"""
        logger.info("🔄 Starte automatische Detector-Schema-Aktualisierung...")
        
        # Detector-Module finden
        detector_modules = self.find_detector_modules()
        if not detector_modules:
            logger.warning("Keine Detector-Module gefunden!")
            return False
            
        # Schema laden
        schema = self.load_schema()
        
        # Schema aktualisieren
        updated_schema = self.update_schema_with_detectors(schema, detector_modules)
        
        # Schema speichern
        if self.save_schema(updated_schema):
            self._print_stats()
            return True
        else:
            return False
            
    def _print_stats(self):
        """Gibt Aktualisierungs-Statistiken aus"""
        print("\n" + "="*50)
        print("📊 DETECTOR-UPDATE STATISTIKEN")
        print("="*50)
        print(f"Module gefunden:     {self.stats['modules_found']}")
        print(f"Module hinzugefügt:  {self.stats['modules_added']}")
        print(f"Module aktualisiert: {self.stats['modules_updated']}")
        print(f"Fehler aufgetreten:  {len(self.stats['errors'])}")
        
        if self.stats["errors"]:
            print("\n❌ FEHLER:")
            for error in self.stats["errors"][:5]:  # Zeige nur ersten 5
                print(f"  - {error}")
            if len(self.stats["errors"]) > 5:
                print(f"  ... und {len(self.stats['errors']) - 5} weitere")
                
        print(f"\n✅ Schema aktualisiert: {self.schema_path}")
        print("="*50)
        
    def validate_schema(self):
        """Validiert das aktuelle Schema"""
        try:
            schema = self.load_schema()
            
            # Grundstruktur prüfen
            required_keys = ["application_schema"]
            for key in required_keys:
                if key not in schema:
                    logger.error(f"Fehlender Schlüssel im Schema: {key}")
                    return False
                    
            # Detector-Konfigurationen prüfen
            detectors = schema.get("application_schema", {}).get("detectors", {})
            for name, config in detectors.items():
                if not isinstance(config, dict):
                    logger.error(f"Ungültige Detector-Konfiguration: {name}")
                    continue
                    
                required_detector_keys = ["module", "class"]
                for key in required_detector_keys:
                    if key not in config:
                        logger.warning(f"Fehlender Schlüssel in Detector {name}: {key}")
                        
            logger.info(f"Schema-Validierung erfolgreich: {len(detectors)} Detectors")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei Schema-Validierung: {e}")
            return False


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatische Detector-Schema-Aktualisierung")
    parser.add_argument("--schema", help=f"Schema-Datei (Standard: {DEFAULT_SCHEMA_PATH})")
    parser.add_argument("--dirs", nargs="+", help="Detector-Verzeichnisse (Standard: vordefinierte)")
    parser.add_argument("--validate", action="store_true", help="Nur Schema validieren")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Updater initialisieren
    updater = DetectorUpdater(schema_path=args.schema, detector_dirs=args.dirs)
    
    if args.validate:
        # Nur validieren
        success = updater.validate_schema()
        return 0 if success else 1
    else:
        # Aktualisierung durchführen
        success = updater.update_all()
        return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 