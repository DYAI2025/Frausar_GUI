#!/usr/bin/env python3
"""
DateTime Fix Tool
Repariert datetime-Objekte in YAML-Dateien für JSON-Kompatibilität
"""

import yaml
import os
import json
from datetime import datetime

def fix_datetime_objects():
    """Repariert datetime-Objekte in problematischen YAML-Dateien"""
    
    problem_files = [
        "-_ID_MARKER.yaml",
        "MARKER_MARKER.yaml", 
        "SELF_DISCLOSURE_DRIFT_AXES_MARKER.yaml",
        "STYLE_SYNC_MARKER.yaml"
    ]
    
    directory = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"
    
    print("🔧 Repariere datetime-Objekte in YAML-Dateien...")
    print("=" * 60)
    
    for filename in problem_files:
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  {filename} nicht gefunden")
            continue
            
        print(f"\n🔧 Bearbeite {filename}...")
        
        try:
            # Backup erstellen
            backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Backup erstellt")
            
            # YAML laden
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Datetime-Objekte zu Strings konvertieren
            data = convert_datetime_to_string(data)
            
            # Zurück speichern
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
            
            # Validierung
            with open(filepath, 'r', encoding='utf-8') as f:
                test_data = yaml.safe_load(f)
            
            json.dumps(test_data, ensure_ascii=False)
            
            print(f"   ✅ Erfolgreich repariert und validiert")
            
        except Exception as e:
            print(f"   ❌ Fehler: {e}")

def convert_datetime_to_string(obj):
    """Konvertiert datetime-Objekte rekursiv zu ISO-Strings"""
    
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_string(item) for item in obj]
    else:
        return obj

def verify_json_compatibility():
    """Überprüft JSON-Kompatibilität aller YAML-Dateien"""
    
    directory = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"
    yaml_files = [f for f in os.listdir(directory) if f.endswith('.yaml')]
    
    print("\n🧪 ÜBERPRÜFE JSON-KOMPATIBILITÄT")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for filename in sorted(yaml_files):
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            json.dumps(yaml_data, ensure_ascii=False)
            success_count += 1
            
        except Exception as e:
            print(f"❌ {filename}: {str(e)}")
            error_count += 1
    
    print(f"\n✅ JSON-kompatibel: {success_count}/{len(yaml_files)} Dateien")
    print(f"❌ Probleme: {error_count}")
    
    return error_count == 0

if __name__ == "__main__":
    print("🚀 DateTime Fix Tool")
    print("=" * 60)
    
    # Datetime-Objekte reparieren
    fix_datetime_objects()
    
    # JSON-Kompatibilität überprüfen
    if verify_json_compatibility():
        print("\n🎉 Alle YAML-Dateien sind jetzt JSON-kompatibel!")
    else:
        print("\n⚠️  Es gibt noch JSON-Kompatibilitätsprobleme.") 