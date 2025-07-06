#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Start-Skript für FRAUSAR GUI
============================
Startet die FRAUSAR Marker Management GUI
"""

import sys
import os
from pathlib import Path

# Stelle sicher, dass das aktuelle Verzeichnis im Python-Pfad ist
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🤖 Starte FRAUSAR Marker Management GUI...")
print("=" * 60)
print("📁 Arbeitsverzeichnis:", os.getcwd())
print("📍 Marker-Quelle: ../ALL_SEMANTIC_MARKER_TXT/")
print("=" * 60)

# Prüfe ob die Marker-Quelle existiert
marker_path = Path("../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01")
if marker_path.exists():
    print(f"✅ Marker-Quelle gefunden: {marker_path.resolve()}")
    
    # Zähle Marker
    txt_files = list(marker_path.glob("*.txt"))
    py_files = list(marker_path.glob("*.py"))
    print(f"📊 Gefunden: {len(txt_files)} TXT-Dateien, {len(py_files)} PY-Dateien")
else:
    print(f"⚠️  Warnung: Marker-Quelle nicht gefunden: {marker_path}")
    print("   Die GUI wird trotzdem gestartet...")

print()

# Importiere und starte die GUI
try:
    from frausar_gui import main
    main()
except ImportError as e:
    print(f"❌ Fehler beim Import: {e}")
    print("Stelle sicher, dass frausar_gui.py vorhanden ist!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Fehler beim Starten der GUI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 