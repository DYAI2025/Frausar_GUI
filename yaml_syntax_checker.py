#!/usr/bin/env python3
"""
YAML Syntax Checker
Überprüft alle YAML-Dateien im Marker-Verzeichnis auf Syntaxfehler
"""

import yaml
import os
import json
from datetime import datetime

def check_all_yaml_files():
    """Überprüft alle YAML-Dateien auf Syntaxfehler"""
    
    directory = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"
    
    print("🔍 Überprüfe alle YAML-Dateien auf Syntaxfehler...")
    print("=" * 60)
    
    yaml_files = [f for f in os.listdir(directory) if f.endswith('.yaml')]
    
    valid_files = []
    error_files = []
    
    for filename in sorted(yaml_files):
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Test JSON Konvertierung
            json.dumps(yaml_data, ensure_ascii=False)
            
            print(f"✅ {filename}")
            valid_files.append(filename)
            
        except yaml.YAMLError as e:
            print(f"❌ {filename}: YAML Syntax Error")
            print(f"   └─ {str(e)}")
            error_files.append((filename, str(e)))
            
        except Exception as e:
            print(f"⚠️  {filename}: Anderer Fehler")
            print(f"   └─ {str(e)}")
            error_files.append((filename, str(e)))
    
    print("\n" + "=" * 60)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 60)
    print(f"✅ Gültige YAML-Dateien: {len(valid_files)}")
    print(f"❌ Fehlerhafte YAML-Dateien: {len(error_files)}")
    print(f"📁 Gesamt: {len(yaml_files)}")
    
    if error_files:
        print("\n🔧 FEHLERHAFTE DATEIEN:")
        for filename, error in error_files:
            print(f"   • {filename}")
            print(f"     └─ {error[:100]}...")
    
    return valid_files, error_files

def test_yaml_to_json_conversion():
    """Testet YAML zu JSON Konvertierung für alle Dateien"""
    
    directory = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01"
    yaml_files = [f for f in os.listdir(directory) if f.endswith('.yaml')]
    
    print("\n🧪 TESTE YAML ZU JSON KONVERTIERUNG")
    print("=" * 60)
    
    success_count = 0
    
    for filename in sorted(yaml_files):
        filepath = os.path.join(directory, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            json_output = json.dumps(yaml_data, indent=2, ensure_ascii=False)
            success_count += 1
            
        except Exception as e:
            print(f"❌ {filename}: {str(e)}")
    
    print(f"✅ Erfolgreich konvertiert: {success_count}/{len(yaml_files)} Dateien")
    
    return success_count == len(yaml_files)

if __name__ == "__main__":
    print("🚀 YAML Syntax Checker")
    print("=" * 60)
    
    # Alle YAML-Dateien überprüfen
    valid_files, error_files = check_all_yaml_files()
    
    # YAML zu JSON Test
    if test_yaml_to_json_conversion():
        print("\n🎉 Alle YAML-Dateien sind syntaktisch korrekt!")
    else:
        print("\n⚠️  Es gibt noch Probleme mit einigen YAML-Dateien.") 