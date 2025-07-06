#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Start-Skript für FRAUSAR Marker Assistant GUI
"""

import sys
import os
from pathlib import Path

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importiere und starte die GUI
try:
    from marker_assistant_gui import main
    
    print("🤖 Starte FRAUSAR Marker Assistant GUI...")
    print("=" * 50)
    print("📁 Arbeitsverzeichnis:", os.getcwd())
    print("📍 Marker-Quelle: ../ALL_SEMANTIC_MARKER_TXT/")
    print("=" * 50)
    print()
    
    main()
    
except ImportError as e:
    print(f"❌ Fehler beim Import: {e}")
    print("Stelle sicher, dass alle benötigten Dateien vorhanden sind:")
    print("- marker_assistant_bot.py")
    print("- marker_assistant_gui.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Fehler beim Starten der GUI: {e}")
    sys.exit(1) 