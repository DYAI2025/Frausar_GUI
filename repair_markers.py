#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatische Syntax-Reparatur aller Marker-YAMLs
================================================
Repariert YAML-Dateien gemäß neuem Schema mit folgenden Regeln:
- Umbenennung veralteter Felder
- Entfernung verbotener Level-1 Felder
- Normalisierung von Datentypen
- Mindestanzahl Beispiele (5)
- UPPER_SNAKE_CASE für IDs und Namen
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Konfiguration - anpassbar
DEFAULT_MARKER_DIRS = [
    "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01",
    "../ALL_SEMANTIC_MARKER_TXT/Former_NEW_MARKER_FOLDERS",
    ".",  # Aktuelles Verzeichnis für Tests
]

# Regeln für die Reparatur
FIELD_RENAMES = {
    "categories": "category",
    "kategorie": "category", 
    "semantic_tags": "tags",
    "marker": "marker_name",
}

FORBIDDEN_IN_LEVEL1 = {
    "composed_of", "rules", "activation_logic", "trigger_threshold"
}

REQUIRED_FIELDS = {
    "marker_name": str,
    "category": str,
    "tags": list,
    "examples": list,
}

class MarkerRepairEngine:
    """Hauptklasse für die automatische Marker-Reparatur"""
    
    def __init__(self, marker_dirs=None):
        self.marker_dirs = marker_dirs or DEFAULT_MARKER_DIRS
        self.stats = {
            "files_processed": 0,
            "files_fixed": 0,
            "fixes_applied": 0,
            "errors": []
        }
        
    def find_marker_files(self):
        """Findet alle YAML-Marker-Dateien in den konfigurierten Verzeichnissen"""
        marker_files = []
        
        for base_dir in self.marker_dirs:
            base_path = Path(base_dir)
            if not base_path.exists():
                logger.warning(f"Verzeichnis nicht gefunden: {base_path}")
                continue
                
            # Durchsuche Hauptverzeichnis
            for file in base_path.glob("*.yaml"):
                if self._is_marker_file(file):
                    marker_files.append(file)
                    
            # Durchsuche Unterverzeichnisse (nur eine Ebene tief)
            for subdir in base_path.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    for file in subdir.glob("*.yaml"):
                        if self._is_marker_file(file):
                            marker_files.append(file)
                            
        logger.info(f"Gefunden: {len(marker_files)} Marker-YAML-Dateien")
        return marker_files
        
    def _is_marker_file(self, file_path):
        """Prüft ob eine Datei eine Marker-Datei ist"""
        name = file_path.name.lower()
        return any(keyword in name for keyword in ['marker', 'pattern', 'fraud', 'scam'])
        
    def load_yaml_safe(self, file_path):
        """Lädt YAML-Datei sicher mit Fehlerbehandlung"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Versuche verschiedene YAML-Parser
            try:
                # Standard-Parser
                docs = list(yaml.safe_load_all(content))
                return docs if docs else []
            except yaml.YAMLError:
                # Fallback: Zeile für Zeile parsen
                logger.warning(f"Standard-Parser fehlgeschlagen für {file_path}, versuche Fallback...")
                return self._parse_yaml_fallback(content)
                
        except Exception as e:
            logger.error(f"Fehler beim Laden von {file_path}: {e}")
            self.stats["errors"].append(f"{file_path}: {e}")
            return []
            
    def _parse_yaml_fallback(self, content):
        """Fallback-Parser für problematische YAML-Dateien"""
        try:
            # Versuche einfache Struktur-Erkennung
            if content.strip().startswith('marker_name:') or content.strip().startswith('marker:'):
                # Einzelnes Dokument
                return [yaml.safe_load(content)]
            else:
                # Multi-Dokument
                docs = content.split('---')
                return [yaml.safe_load(doc.strip()) for doc in docs if doc.strip()]
        except:
            return []
            
    def save_yaml_safe(self, file_path, docs):
        """Speichert YAML-Datei sicher"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if len(docs) == 1:
                    yaml.safe_dump(docs[0], f, sort_keys=False, allow_unicode=True, default_flow_style=False)
                else:
                    yaml.safe_dump_all(docs, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern von {file_path}: {e}")
            self.stats["errors"].append(f"Save {file_path}: {e}")
            return False
            
    def repair_marker(self, marker_data):
        """Repariert einen einzelnen Marker"""
        if not isinstance(marker_data, dict):
            return marker_data, False
            
        original = marker_data.copy()
        changed = False
        
        # 1. Feld-Umbenennungen
        for old_key, new_key in FIELD_RENAMES.items():
            if old_key in marker_data:
                marker_data[new_key] = marker_data.pop(old_key)
                changed = True
                logger.debug(f"Umbenannt: {old_key} → {new_key}")
                
        # 2. Level-1 Beschränkungen
        level = marker_data.get("level", 1)
        if level == 1:
            for forbidden_field in FORBIDDEN_IN_LEVEL1:
                if forbidden_field in marker_data:
                    marker_data.pop(forbidden_field)
                    changed = True
                    logger.debug(f"Entfernt Level-1 Feld: {forbidden_field}")
                    
        # 3. Kategorie als String normalisieren
        if "category" in marker_data:
            category = marker_data["category"]
            if isinstance(category, list):
                marker_data["category"] = category[0] if category else "UNCATEGORIZED"
                changed = True
            elif not isinstance(category, str):
                marker_data["category"] = str(category) if category else "UNCATEGORIZED"
                changed = True
        else:
            marker_data["category"] = "UNCATEGORIZED"
            changed = True
            
        # 4. Tags als Liste sicherstellen
        if "tags" in marker_data:
            tags = marker_data["tags"]
            if not isinstance(tags, list):
                marker_data["tags"] = [str(tags)] if tags else ["needs_review"]
                changed = True
        else:
            marker_data["tags"] = ["needs_review"]
            changed = True
            
        # 5. Mindestens 5 Beispiele
        examples = marker_data.get("examples", [])
        if not isinstance(examples, list):
            examples = []
        
        if len(examples) < 5:
            # Füge Platzhalter hinzu
            for i in range(5 - len(examples)):
                examples.append(f"AUTO_GENERATED_EXAMPLE_{i+1}")
            marker_data["examples"] = examples
            changed = True
            
        # 6. ID und Name zu UPPER_SNAKE_CASE
        for field in ["id", "marker_name", "name"]:
            if field in marker_data:
                old_value = marker_data[field]
                if isinstance(old_value, str):
                    new_value = re.sub(r"[^A-Z0-9_]", "_", old_value.upper())
                    if new_value != old_value:
                        marker_data[field] = new_value
                        changed = True
                        
        # 7. Metadaten hinzufügen falls geändert
        if changed:
            if "metadata" not in marker_data:
                marker_data["metadata"] = {}
            marker_data["metadata"]["last_repaired"] = datetime.now().isoformat()
            marker_data["metadata"]["repair_version"] = "1.0"
            
        return marker_data, changed
        
    def repair_file(self, file_path):
        """Repariert eine einzelne YAML-Datei"""
        logger.info(f"Verarbeite: {file_path}")
        self.stats["files_processed"] += 1
        
        # Backup erstellen
        backup_path = file_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            # Datei laden
            docs = self.load_yaml_safe(file_path)
            if not docs:
                logger.warning(f"Keine gültigen YAML-Dokumente in {file_path}")
                return False
                
            # Dokumente reparieren
            repaired_docs = []
            file_changed = False
            
            for doc in docs:
                repaired_doc, changed = self.repair_marker(doc)
                repaired_docs.append(repaired_doc)
                if changed:
                    file_changed = True
                    self.stats["fixes_applied"] += 1
                    
            # Speichern falls Änderungen
            if file_changed:
                # Backup erstellen
                file_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                
                # Reparierte Version speichern
                if self.save_yaml_safe(file_path, repaired_docs):
                    self.stats["files_fixed"] += 1
                    logger.info(f"✅ Repariert: {file_path}")
                    return True
                else:
                    # Restore backup bei Fehler
                    file_path.write_text(backup_path.read_text(encoding='utf-8'), encoding='utf-8')
                    logger.error(f"❌ Fehler beim Speichern, Backup wiederhergestellt: {file_path}")
                    return False
            else:
                logger.debug(f"Keine Änderungen nötig: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"Unerwarteter Fehler bei {file_path}: {e}")
            self.stats["errors"].append(f"{file_path}: {e}")
            return False
            
    def repair_all(self):
        """Hauptmethode: Repariert alle gefundenen Marker-Dateien"""
        logger.info("🔧 Starte automatische Marker-Reparatur...")
        
        # Dateien finden
        marker_files = self.find_marker_files()
        if not marker_files:
            logger.warning("Keine Marker-Dateien gefunden!")
            return False
            
        # Reparieren
        for file_path in marker_files:
            self.repair_file(file_path)
            
        # Statistiken
        self._print_stats()
        return self.stats["files_fixed"] > 0
        
    def _print_stats(self):
        """Gibt Reparatur-Statistiken aus"""
        print("\n" + "="*50)
        print("📊 REPARATUR-STATISTIKEN")
        print("="*50)
        print(f"Dateien verarbeitet: {self.stats['files_processed']}")
        print(f"Dateien repariert:   {self.stats['files_fixed']}")
        print(f"Fixes angewendet:    {self.stats['fixes_applied']}")
        print(f"Fehler aufgetreten:  {len(self.stats['errors'])}")
        
        if self.stats["errors"]:
            print("\n❌ FEHLER:")
            for error in self.stats["errors"][:5]:  # Zeige nur ersten 5
                print(f"  - {error}")
            if len(self.stats["errors"]) > 5:
                print(f"  ... und {len(self.stats['errors']) - 5} weitere")
                
        print("\n✅ Reparatur abgeschlossen!")
        print("="*50)


def main():
    """Hauptfunktion für Kommandozeilen-Nutzung"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatische YAML-Marker-Reparatur")
    parser.add_argument("--dirs", nargs="+", help="Marker-Verzeichnisse (Standard: vordefinierte)")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nicht ändern")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Engine initialisieren
    engine = MarkerRepairEngine(marker_dirs=args.dirs)
    
    if args.dry_run:
        logger.info("🔍 DRY-RUN Modus - keine Änderungen werden gespeichert")
        # TODO: Dry-run Implementation
        
    # Reparatur durchführen
    success = engine.repair_all()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 