#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generiert eine vereinheitlichte YAML-Datei für GPT-Analyse
"""

from marker_assistant_bot import MarkerAssistant
from pathlib import Path
import sys

def main():
    print("🤖 FRAUSAR Marker GPT-YAML Generator")
    print("=" * 60)
    
    # Initialisiere MarkerAssistant
    print("📋 Initialisiere Marker Assistant...")
    assistant = MarkerAssistant()
    
    # Generiere die vereinheitlichte YAML
    print("\n🔄 Generiere vereinheitlichte YAML-Datei für GPT...")
    
    try:
        # Generiere die Datei
        output_file = assistant.generate_unified_yaml_for_gpt()
        
        # Zeige Ergebnis
        print(f"\n✅ Erfolgreich generiert!")
        print(f"📄 Hauptdatei: {output_file}")
        print(f"📄 Kompakte Version: {Path(output_file).stem}_compact.yaml")
        
        # Zeige Datei-Info
        file_size = Path(output_file).stat().st_size / 1024  # KB
        print(f"\n📊 Dateigröße: {file_size:.1f} KB")
        
        # Zeige erste Zeilen der Datei
        print("\n📋 Vorschau der generierten Datei:")
        print("-" * 60)
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
            for line in lines:
                print(line.rstrip())
        print("-" * 60)
        
        print(f"\n💡 Die Datei kann jetzt an GPT übergeben werden für:")
        print("   • Bestandsaufnahme aller Marker")
        print("   • Analyse der Marker-Struktur")
        print("   • Identifikation von Lücken")
        print("   • Verbesserungsvorschläge")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Generieren: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 