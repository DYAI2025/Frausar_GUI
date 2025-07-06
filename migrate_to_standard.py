#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migration Tool für Semantic Marker Framework
Konvertiert bestehende Marker ins Projekt-Standard-Format
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
import shutil

class MarkerMigrator:
    def __init__(self):
        self.marker_dir = Path("../ALL_SEMANTIC_MARKER_TXT")
        self.backup_dir = Path("migration_backup")
        self.grabber_library_path = Path("semantic_grabber_library.yaml")
        self.migrated_count = 0
        self.failed_count = 0
        self.semantic_grabbers = self._load_grabbers()
    
    def _load_grabbers(self):
        """Lädt existierende Grabber"""
        if self.grabber_library_path.exists():
            with open(self.grabber_library_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('semantic_grabbers', {})
        return {}
    
    def _save_grabbers(self):
        """Speichert Grabber-Library"""
        data = {'semantic_grabbers': self.semantic_grabbers}
        with open(self.grabber_library_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def _generate_grabber_id(self, marker_name):
        """Generiert Grabber-ID nach Standard"""
        from uuid import uuid4
        date_str = datetime.now().strftime('%Y%m%d')
        unique_num = str(uuid4())[:4].upper()
        return f"AUTO_SEM_{date_str}_{unique_num}"
    
    def _parse_txt_marker(self, content, filename):
        """Parst TXT-Marker und extrahiert Daten"""
        marker_data = {
            'marker_name': filename.replace('.txt', '').upper(),
            'beschreibung': '',
            'beispiele': [],
            'semantische_grabber_id': None
        }
        
        # Extrahiere Beschreibung
        desc_match = re.search(r'beschreibung:\s*(.+?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if desc_match:
            marker_data['beschreibung'] = desc_match.group(1).strip().replace('\n', ' ')
        
        # Extrahiere Beispiele
        beispiele_match = re.search(r'beispiele:(.*?)(?=\n\w+:|$)', content, re.IGNORECASE | re.DOTALL)
        if beispiele_match:
            beispiele_text = beispiele_match.group(1)
            beispiele = re.findall(r'-\s*"([^"]+)"', beispiele_text)
            marker_data['beispiele'] = beispiele
        
        # Suche existierende Grabber-ID
        grabber_match = re.search(r'semantische_grabber_id:\s*(\S+)', content, re.IGNORECASE)
        if grabber_match:
            marker_data['semantische_grabber_id'] = grabber_match.group(1)
        
        return marker_data
    
    def _create_or_find_grabber(self, marker_name, beispiele, beschreibung):
        """Erstellt neuen Grabber oder findet passenden"""
        # Vereinfachte Ähnlichkeitssuche
        for grabber_id, grabber_data in self.semantic_grabbers.items():
            # Prüfe ob Beispiele ähnlich sind
            grabber_patterns = grabber_data.get('patterns', [])
            if grabber_patterns and beispiele:
                # Einfacher Check: Gibt es gemeinsame Wörter?
                marker_words = ' '.join(beispiele).lower().split()
                grabber_words = ' '.join(grabber_patterns).lower().split()
                common_words = set(marker_words) & set(grabber_words)
                
                if len(common_words) > min(len(marker_words), len(grabber_words)) * 0.5:
                    return grabber_id
        
        # Kein passender gefunden - erstelle neuen
        new_id = self._generate_grabber_id(marker_name)
        self.semantic_grabbers[new_id] = {
            'beschreibung': beschreibung or f"Automatisch migriert aus {marker_name}",
            'patterns': beispiele[:10],  # Max 10 Patterns
            'created_from': marker_name,
            'created_at': datetime.now().isoformat(),
            'migration': True
        }
        
        return new_id
    
    def migrate_txt_to_yaml(self, txt_file):
        """Migriert eine TXT-Datei zu YAML"""
        try:
            # Lese TXT-Content
            content = txt_file.read_text(encoding='utf-8')
            
            # Parse Marker-Daten
            marker_data = self._parse_txt_marker(content, txt_file.stem)
            
            # Stelle sicher dass Marker-Name konform ist
            if not marker_data['marker_name'].endswith('_MARKER'):
                marker_data['marker_name'] += '_MARKER'
            
            # Erstelle/finde Grabber wenn nötig
            if not marker_data['semantische_grabber_id']:
                marker_data['semantische_grabber_id'] = self._create_or_find_grabber(
                    marker_data['marker_name'],
                    marker_data['beispiele'],
                    marker_data['beschreibung']
                )
            
            # Erstelle YAML-Struktur
            yaml_content = f"""# {marker_data['marker_name']} - Semantic Marker
# Automatisch migriert von {txt_file.name}
marker_name: {marker_data['marker_name']}
beschreibung: >
  {marker_data['beschreibung']}
beispiele:
"""
            
            for beispiel in marker_data['beispiele']:
                yaml_content += f'  - "{beispiel}"\n'
            
            yaml_content += f"""
semantische_grabber_id: {marker_data['semantische_grabber_id']}

metadata:
  migrated_from: {txt_file.name}
  migrated_at: {datetime.now().isoformat()}
  original_format: txt
  version: 1.0
  tags: [migrated, needs_review]
"""
            
            # Speichere als YAML
            yaml_file = txt_file.with_suffix('.yaml')
            yaml_file.write_text(yaml_content, encoding='utf-8')
            
            # Backup Original
            backup_path = self.backup_dir / txt_file.name
            shutil.copy2(txt_file, backup_path)
            
            # Lösche Original
            txt_file.unlink()
            
            print(f"✅ Migriert: {txt_file.name} → {yaml_file.name}")
            self.migrated_count += 1
            return True
            
        except Exception as e:
            print(f"❌ Fehler bei {txt_file.name}: {str(e)}")
            self.failed_count += 1
            return False
    
    def run_migration(self):
        """Führt die Migration durch"""
        print("🚀 Starte Migration zum Semantic Marker Framework Standard...")
        print("=" * 60)
        
        # Erstelle Backup-Verzeichnis
        self.backup_dir.mkdir(exist_ok=True)
        
        # Finde alle TXT-Marker
        txt_files = list(self.marker_dir.rglob("*_MARKER.txt"))
        
        if not txt_files:
            print("✅ Keine TXT-Dateien zum Migrieren gefunden!")
            return
        
        print(f"\n📊 Gefunden: {len(txt_files)} TXT-Marker zum Migrieren")
        
        # Bestätigung
        response = input("\n⚠️  Möchten Sie fortfahren? Die Originaldateien werden gesichert. (j/n): ")
        if response.lower() != 'j':
            print("❌ Migration abgebrochen.")
            return
        
        print("\n🔄 Starte Migration...")
        
        # Migriere alle Dateien
        for txt_file in txt_files:
            self.migrate_txt_to_yaml(txt_file)
        
        # Speichere aktualisierte Grabber-Library
        if self.semantic_grabbers:
            self._save_grabbers()
            print(f"\n💾 Grabber-Library aktualisiert: {len(self.semantic_grabbers)} Grabber")
        
        # Abschlussbericht
        print("\n" + "=" * 60)
        print("📋 MIGRATION ABGESCHLOSSEN")
        print("=" * 60)
        print(f"✅ Erfolgreich migriert: {self.migrated_count}")
        print(f"❌ Fehlgeschlagen: {self.failed_count}")
        print(f"📁 Backups gespeichert in: {self.backup_dir}")
        
        if self.migrated_count > 0:
            print("\n💡 Nächste Schritte:")
            print("   1. Führen Sie compliance_checker.py aus")
            print("   2. Überprüfen Sie die migrierten YAML-Dateien")
            print("   3. Passen Sie ggf. Beschreibungen und Grabber an")

class GrabberOptimizer:
    """Optimiert bestehende Grabber nach dem Standard"""
    
    def __init__(self):
        self.grabber_library_path = Path("semantic_grabber_library.yaml")
        self.semantic_grabbers = self._load_grabbers()
    
    def _load_grabbers(self):
        """Lädt Grabber-Library"""
        if self.grabber_library_path.exists():
            with open(self.grabber_library_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('semantic_grabbers', {})
        return {}
    
    def _save_grabbers(self):
        """Speichert Grabber-Library"""
        data = {'semantic_grabbers': self.semantic_grabbers}
        with open(self.grabber_library_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def fix_grabber_ids(self):
        """Korrigiert Grabber-IDs nach Standard"""
        fixed_count = 0
        new_grabbers = {}
        
        for old_id, grabber_data in self.semantic_grabbers.items():
            # Prüfe ob ID konform ist
            if not (old_id.endswith('_SEM') or re.match(r'^AUTO_SEM_\d{8}_[A-Z0-9]{4}$', old_id)):
                # Generiere neue konforme ID
                if old_id.startswith('AUTO_'):
                    new_id = self._generate_auto_id()
                else:
                    # Versuche sinnvollen Namen zu extrahieren
                    clean_name = re.sub(r'[^A-Z_]', '', old_id.upper())
                    if not clean_name:
                        clean_name = "MIGRATED"
                    new_id = f"{clean_name}_SEM"
                
                print(f"🔄 Korrigiere: {old_id} → {new_id}")
                new_grabbers[new_id] = grabber_data
                fixed_count += 1
            else:
                new_grabbers[old_id] = grabber_data
        
        self.semantic_grabbers = new_grabbers
        
        if fixed_count > 0:
            self._save_grabbers()
            print(f"\n✅ {fixed_count} Grabber-IDs korrigiert")
        else:
            print("\n✅ Alle Grabber-IDs sind bereits konform")
    
    def _generate_auto_id(self):
        """Generiert AUTO_SEM ID"""
        from uuid import uuid4
        date_str = datetime.now().strftime('%Y%m%d')
        unique_num = str(uuid4())[:4].upper()
        return f"AUTO_SEM_{date_str}_{unique_num}"

def main():
    """Hauptfunktion"""
    print("🛠️  SEMANTIC MARKER FRAMEWORK - MIGRATION TOOL")
    print("=" * 60)
    print("\nWas möchten Sie tun?")
    print("1. TXT-Marker zu YAML migrieren")
    print("2. Grabber-IDs korrigieren")
    print("3. Beides")
    
    choice = input("\nIhre Wahl (1-3): ")
    
    if choice in ['1', '3']:
        migrator = MarkerMigrator()
        migrator.run_migration()
    
    if choice in ['2', '3']:
        print("\n" + "=" * 60)
        optimizer = GrabberOptimizer()
        optimizer.fix_grabber_ids()
    
    print("\n✅ Fertig!")

if __name__ == "__main__":
    main() 