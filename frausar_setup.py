#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRAUSAR Setup & Konfiguration
=============================
Einrichtung des automatischen Marker-Assistenten für das FRAUSAR-System
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_frausar_system():
    """
    Richtet das FRAUSAR-System ein
    """
    print("🚀 FRAUSAR-System Setup wird gestartet...")
    print("=" * 50)
    
    # 1. Überprüfe Python-Version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ erforderlich!")
        return False
    
    print("✅ Python-Version OK")
    
    # 2. Installiere benötigte Packages
    required_packages = [
        'PyYAML',
        'requests',
        'pathlib',
        'spacy'
    ]
    
    print("📦 Installiere benötigte Pakete...")
    for package in required_packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installiert")
        except subprocess.CalledProcessError:
            print(f"⚠️ {package} Installation fehlgeschlagen")
    
    # 3. Lade spaCy-Modell
    print("🧠 Lade deutsches spaCy-Modell...")
    try:
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'de_core_news_lg'], 
                     check=True, capture_output=True)
        print("✅ spaCy-Modell installiert")
    except subprocess.CalledProcessError:
        print("⚠️ spaCy-Modell Installation fehlgeschlagen")
    
    # 4. Erstelle Cron-Job für automatische Ausführung
    create_cron_job()
    
    # 5. Erstelle Konfigurationsdatei
    create_config_file()
    
    print("\n🎉 FRAUSAR-System erfolgreich eingerichtet!")
    print("📋 Nächste Schritte:")
    print("   1. Führe 'python marker_assistant_bot.py' aus")
    print("   2. Der Bot läuft automatisch täglich um 02:00 Uhr")
    print("   3. Logs werden in 'marker_assistant.log' gespeichert")
    
    return True

def create_cron_job():
    """
    Erstellt einen Cron-Job für die automatische Ausführung
    """
    cron_entry = f"0 2 * * * cd {os.getcwd()} && python3 marker_assistant_bot.py"
    
    # Cron-Job Datei erstellen
    cron_file = Path("frausar_cron.txt")
    cron_file.write_text(cron_entry)
    
    print(f"📅 Cron-Job erstellt: {cron_file}")
    print("   Führe aus: crontab frausar_cron.txt")

def create_config_file():
    """
    Erstellt Konfigurationsdatei
    """
    config = {
        "marker_directory": "Assist_TXT_marker_py:/ALL_NEWMARKER01",
        "backup_retention_days": 30,
        "trend_confidence_threshold": 0.8,
        "auto_update_enabled": True,
        "log_level": "INFO"
    }
    
    import json
    config_file = Path("frausar_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"⚙️ Konfiguration erstellt: {config_file}")

if __name__ == "__main__":
    setup_frausar_system() 