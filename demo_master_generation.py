#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo: Master-Dokumentations-Generierung
=======================================
Demonstriert die neue "Ein-Klick" Master-Generierung des FRAUSAR Marker Assistant.

Dieses Skript zeigt, wie aus allen vorhandenen Markern automatisch:
- marker_master_export.yaml/json (Zentrale Marker-Datenbank)
- MARKER_SYSTEM_README.md (Detaillierte Systemdokumentation)  
- MARKER_MASTER_README.md (Marker-spezifische Dokumentation)
generiert werden können.
"""

import os
import time
from pathlib import Path
from marker_assistant_bot import MarkerAssistant

def demo_master_generation():
    """Führt eine vollständige Demo der Master-Generierung durch"""
    
    print("🤖 FRAUSAR Marker Assistant - Master-Generierung Demo")
    print("=" * 60)
    print()
    
    # Schritt 1: MarkerAssistant initialisieren
    print("📋 Schritt 1: Initialisiere Marker Assistant...")
    assistant = MarkerAssistant()
    time.sleep(1)
    
    # Schritt 2: Marker sammeln (Vorschau)
    print("🔍 Schritt 2: Sammle alle Marker aus dem Projekt...")
    markers = assistant.collect_all_markers()
    
    print(f"   ✅ {len(markers)} Marker erfolgreich gesammelt!")
    
    # Zeige einige Beispiele
    print("   📑 Beispiel-Marker:")
    for i, (name, data) in enumerate(list(markers.items())[:5]):
        example_count = len(data.get('beispiele', []))
        print(f"      • {name}: {example_count} Beispiele")
    
    if len(markers) > 5:
        print(f"      ... und {len(markers) - 5} weitere")
    print()
    
    # Schritt 3: Master-Dateien generieren
    print("🚀 Schritt 3: Generiere alle Master-Dateien...")
    output_dir = "demo_output"
    Path(output_dir).mkdir(exist_ok=True)
    
    results = assistant.generate_all_master_files(output_dir)
    
    print("   ✅ Generierung abgeschlossen!")
    print()
    
    # Schritt 4: Ergebnisse anzeigen
    print("📄 Schritt 4: Generierte Dateien:")
    print("=" * 40)
    
    for key, file_path in results.items():
        if isinstance(file_path, str) and Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            size_str = format_file_size(file_size)
            
            print(f"   📄 {Path(file_path).name}")
            print(f"      Pfad: {file_path}")
            print(f"      Größe: {size_str}")
            print()
    
    # Schritt 5: Statistiken
    print("📊 Schritt 5: Marker-Statistiken:")
    print("=" * 40)
    
    total_examples = sum(len(m.get('beispiele', [])) for m in markers.values())
    categories = set(m.get('kategorie', 'UNCATEGORIZED') for m in markers.values())
    
    print(f"   • Marker insgesamt: {len(markers)}")
    print(f"   • Beispiele insgesamt: {total_examples}")
    print(f"   • Durchschnitt/Marker: {total_examples/len(markers):.1f} Beispiele")
    print(f"   • Kategorien: {len(categories)}")
    print()
    
    # Top-Marker nach Beispielen
    top_markers = sorted(
        [(name, len(data.get('beispiele', []))) for name, data in markers.items()],
        key=lambda x: x[1], reverse=True
    )[:5]
    
    print("   🏆 Top Marker (nach Beispielen):")
    for name, count in top_markers:
        print(f"      • {name}: {count} Beispiele")
    print()
    
    # Schritt 6: Demo der Verwendung
    print("💡 Schritt 6: Verwendung der generierten Dateien:")
    print("=" * 50)
    
    demo_usage(output_dir)
    
    print("✨ Demo abgeschlossen!")
    print(f"📁 Alle Dateien wurden in '{output_dir}' gespeichert.")
    print()
    print("🚀 Die Master-Dateien können jetzt für folgende Zwecke verwendet werden:")
    print("   • Integration in andere Systeme")
    print("   • API-Entwicklung")
    print("   • Dokumentation")
    print("   • Backup und Versionierung")

def demo_usage(output_dir):
    """Demonstriert die Verwendung der generierten Dateien"""
    
    yaml_file = Path(output_dir) / "marker_master_export.yaml"
    json_file = Path(output_dir) / "marker_master_export.json"
    
    print("   📚 Import-Beispiele:")
    print()
    
    # YAML Import Demo
    if yaml_file.exists():
        print("   🔸 YAML Import:")
        print("   ```python")
        print("   import yaml")
        print(f"   with open('{yaml_file}', 'r', encoding='utf-8') as f:")
        print("       data = yaml.safe_load(f)")
        print("   markers = data['markers']")
        print("   ```")
        print()
    
    # JSON Import Demo  
    if json_file.exists():
        print("   🔸 JSON Import:")
        print("   ```python")
        print("   import json")
        print(f"   with open('{json_file}', 'r', encoding='utf-8') as f:")
        print("       data = json.load(f)")
        print("   markers = data['markers']")
        print("   ```")
        print()
    
    # CLI Demo
    print("   🔸 CLI Verwendung:")
    print("   ```bash")
    print("   # Text analysieren")
    print("   python3 marker_cli.py -t \"Das hast du dir nur eingebildet.\"")
    print("   ")
    print("   # API starten")
    print("   python3 marker_api.py")
    print("   ```")
    print()

def format_file_size(size_bytes):
    """Formatiert Dateigröße"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def interactive_demo():
    """Interaktive Demo mit Benutzer-Eingabe"""
    
    print("\n" + "="*60)
    print("🎮 INTERAKTIVE DEMO")
    print("="*60)
    
    while True:
        print("\nWas möchten Sie tun?")
        print("1. 🚀 Master-Dateien generieren")
        print("2. 📊 Marker-Statistiken anzeigen")
        print("3. 📄 Datei-Inhalt anzeigen")
        print("4. 🏃 Demo beenden")
        
        choice = input("\nIhre Wahl (1-4): ").strip()
        
        if choice == "1":
            output_dir = input("Output-Verzeichnis (Enter für 'demo_output'): ").strip()
            if not output_dir:
                output_dir = "demo_output"
            
            assistant = MarkerAssistant()
            results = assistant.generate_all_master_files(output_dir)
            
            print(f"\n✅ {len(results)} Dateien generiert in: {output_dir}")
            
        elif choice == "2":
            assistant = MarkerAssistant()
            markers = assistant.collect_all_markers()
            
            print(f"\n📊 STATISTIKEN:")
            print(f"   Marker: {len(markers)}")
            total_examples = sum(len(m.get('beispiele', [])) for m in markers.values())
            print(f"   Beispiele: {total_examples}")
            print(f"   Durchschnitt: {total_examples/len(markers):.1f} Beispiele/Marker")
            
        elif choice == "3":
            files = list(Path("demo_output").glob("*.md")) if Path("demo_output").exists() else []
            if not files:
                print("❌ Keine README-Dateien gefunden. Bitte erst Master-Dateien generieren.")
                continue
                
            print("\nVerfügbare Dateien:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {file.name}")
            
            try:
                file_choice = int(input("Datei-Nummer: ")) - 1
                if 0 <= file_choice < len(files):
                    content = files[file_choice].read_text(encoding='utf-8')
                    print(f"\n📄 {files[file_choice].name}:")
                    print("-" * 40)
                    print(content[:500] + "..." if len(content) > 500 else content)
            except (ValueError, IndexError):
                print("❌ Ungültige Auswahl")
                
        elif choice == "4":
            print("👋 Demo beendet!")
            break
        else:
            print("❌ Ungültige Auswahl. Bitte 1-4 eingeben.")

def main():
    """Hauptfunktion"""
    try:
        # Automatische Demo
        demo_master_generation()
        
        # Frage nach interaktiver Demo
        response = input("\n🎮 Möchten Sie die interaktive Demo starten? (j/n): ").strip().lower()
        if response in ['j', 'ja', 'y', 'yes']:
            interactive_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo abgebrochen!")
    except Exception as e:
        print(f"\n❌ Fehler in der Demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 