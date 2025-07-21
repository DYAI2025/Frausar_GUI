#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup Empty Markers - Bereinigung inhaltsloser Auto-Marker
============================================================
Findet und entfernt automatisch generierte, aber inhaltslose Marker
"""

import os
import yaml
import re
from pathlib import Path
from datetime import datetime
import argparse

class EmptyMarkerCleaner:
    def __init__(self, marker_directory=".", dry_run=True):
        self.marker_directory = Path(marker_directory)
        self.dry_run = dry_run
        self.found_empty_markers = []
        
    def is_empty_marker(self, marker_data):
        """Prüft ob ein Marker leer/inhaltslos ist"""
        # Kriteria für leeren Marker:
        
        # 1. marker_name ist null oder leer
        marker_name = marker_data.get("marker_name")
        if not marker_name or marker_name == "null" or str(marker_name).strip() == "":
            return True, "marker_name ist null/leer"
            
        # 2. Beschreibung ist leer
        description = marker_data.get("description", marker_data.get("beschreibung", ""))
        if not description or str(description).strip() == "":
            return True, "Beschreibung ist leer"
            
        # 3. Nur AUTO_GENERATED Beispiele
        examples = marker_data.get("examples", [])
        if isinstance(examples, list):
            auto_examples = [ex for ex in examples if str(ex).startswith("AUTO_GENERATED_EXAMPLE")]
            if len(auto_examples) == len(examples) and len(examples) > 0:
                return True, "Nur AUTO_GENERATED Beispiele"
                
        # 4. AUTO_SEM ID mit created_by FRAUSAR_GUI_v2 UND leerem Inhalt
        grabber_id = marker_data.get("semantic_grabber_id", "")
        metadata = marker_data.get("metadata", {})
        created_by = metadata.get("created_by", "")
        
        if (grabber_id.startswith("AUTO_SEM_") and 
            created_by == "FRAUSAR_GUI_v2" and
            (not description or str(description).strip() == "")):
            return True, "AUTO_SEM Marker ohne Inhalt von FRAUSAR_GUI_v2"
            
        return False, ""
        
    def scan_directory(self):
        """Scannt Verzeichnis nach YAML-Dateien und prüft auf leere Marker"""
        yaml_files = list(self.marker_directory.rglob("*.yaml"))
        yaml_files.extend(list(self.marker_directory.rglob("*.yml")))
        
        print(f"🔍 Scanne {len(yaml_files)} YAML-Dateien in {self.marker_directory}")
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    marker_data = yaml.safe_load(f)
                    
                if not isinstance(marker_data, dict):
                    continue
                    
                is_empty, reason = self.is_empty_marker(marker_data)
                
                if is_empty:
                    self.found_empty_markers.append({
                        'file': yaml_file,
                        'reason': reason,
                        'marker_data': marker_data
                    })
                    
            except Exception as e:
                print(f"⚠️ Fehler beim Lesen von {yaml_file}: {e}")
                
    def print_report(self):
        """Druckt Report über gefundene leere Marker"""
        print(f"\n📊 **CLEANUP REPORT**")
        print(f"={'=' * 50}")
        
        if not self.found_empty_markers:
            print("✅ Keine leeren Marker gefunden!")
            return
            
        print(f"❌ **{len(self.found_empty_markers)} leere Marker gefunden:**\n")
        
        for i, marker in enumerate(self.found_empty_markers, 1):
            file_path = marker['file']
            reason = marker['reason']
            data = marker['marker_data']
            
            print(f"**{i}. {file_path.name}**")
            print(f"   📁 Pfad: {file_path}")
            print(f"   🔍 Grund: {reason}")
            print(f"   📝 marker_name: {data.get('marker_name', 'N/A')}")
            print(f"   📄 beschreibung: '{data.get('description', data.get('beschreibung', ''))}'")
            print(f"   🔢 grabber_id: {data.get('semantic_grabber_id', 'N/A')}")
            
            # Zeige Metadaten
            metadata = data.get('metadata', {})
            if metadata:
                print(f"   📅 created_at: {metadata.get('created_at', 'N/A')}")
                print(f"   👤 created_by: {metadata.get('created_by', 'N/A')}")
                
            print()
            
    def cleanup_empty_markers(self):
        """Löscht die gefundenen leeren Marker"""
        if not self.found_empty_markers:
            print("✅ Nichts zu bereinigen!")
            return 0
            
        if self.dry_run:
            print(f"🧪 **DRY RUN MODE** - Keine Dateien werden gelöscht!")
            print(f"Würde {len(self.found_empty_markers)} Dateien löschen.")
            return 0
            
        print(f"🗑️ Lösche {len(self.found_empty_markers)} leere Marker...")
        
        deleted_count = 0
        for marker in self.found_empty_markers:
            try:
                file_path = marker['file']
                file_path.unlink()
                print(f"🗑️ Gelöscht: {file_path.name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Fehler beim Löschen von {file_path}: {e}")
                
        print(f"✅ {deleted_count} leere Marker erfolgreich gelöscht!")
        return deleted_count
        
    def create_backup(self):
        """Erstellt Backup der zu löschenden Dateien"""
        if not self.found_empty_markers:
            return None
            
        backup_dir = Path(f"empty_markers_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(exist_ok=True)
        
        print(f"💾 Erstelle Backup in: {backup_dir}")
        
        for marker in self.found_empty_markers:
            try:
                source_file = marker['file']
                backup_file = backup_dir / source_file.name
                
                # Kopiere Datei
                import shutil
                shutil.copy2(source_file, backup_file)
                
            except Exception as e:
                print(f"⚠️ Backup-Fehler für {source_file}: {e}")
                
        return backup_dir

def main():
    parser = argparse.ArgumentParser(description="Cleanup Empty Auto-Generated Markers")
    parser.add_argument("directory", nargs="?", default=".", 
                       help="Verzeichnis zum Scannen (Standard: aktuelles Verzeichnis)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Nur anzeigen, nicht löschen (Standard: True)")
    parser.add_argument("--execute", action="store_true",
                       help="Tatsächlich löschen (überschreibt --dry-run)")
    parser.add_argument("--backup", action="store_true",
                       help="Backup erstellen vor dem Löschen")
    
    args = parser.parse_args()
    
    # Wenn --execute gesetzt ist, überschreibe dry_run
    dry_run = not args.execute
    
    print("🧹 **EMPTY MARKER CLEANUP TOOL**")
    print("=" * 40)
    print(f"📁 Verzeichnis: {args.directory}")
    print(f"🧪 Dry Run: {'Ja' if dry_run else 'Nein'}")
    print()
    
    # Cleaner erstellen
    cleaner = EmptyMarkerCleaner(args.directory, dry_run=dry_run)
    
    # Scannen
    cleaner.scan_directory()
    
    # Report
    cleaner.print_report()
    
    if cleaner.found_empty_markers:
        # Backup erstellen falls gewünscht
        if args.backup:
            backup_dir = cleaner.create_backup()
            if backup_dir:
                print(f"💾 Backup erstellt: {backup_dir}")
                
        # Bereinigen
        deleted = cleaner.cleanup_empty_markers()
        
        if dry_run and cleaner.found_empty_markers:
            print("\n💡 **Zum tatsächlichen Löschen:**")
            print(f"python {__file__} {args.directory} --execute")
            print(f"python {__file__} {args.directory} --execute --backup  # Mit Backup")

if __name__ == "__main__":
    main() 