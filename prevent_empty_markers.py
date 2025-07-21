#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prevent Empty Markers - Verhindert Erstellung inhaltsloser Marker
================================================================
Erweitert das Repair-System um Validierung vor der Marker-Erstellung
"""

import yaml
from datetime import datetime
from pathlib import Path

def validate_marker_before_save(marker_data):
    """Validiert Marker vor dem Speichern"""
    
    # Kritische Felder prüfen
    marker_name = marker_data.get("marker_name")
    description = marker_data.get("description", marker_data.get("beschreibung", ""))
    examples = marker_data.get("examples", [])
    
    # 1. marker_name darf nicht null/leer sein
    if not marker_name or marker_name == "null" or str(marker_name).strip() == "":
        return False, "marker_name ist null oder leer"
    
    # 2. Beschreibung muss vorhanden sein
    if not description or str(description).strip() == "":
        return False, "Beschreibung ist leer"
    
    # 3. Echte Beispiele erforderlich (nicht nur AUTO_GENERATED)
    if isinstance(examples, list):
        real_examples = [ex for ex in examples if not str(ex).startswith("AUTO_GENERATED_EXAMPLE")]
        if len(real_examples) == 0:
            return False, "Keine echten Beispiele vorhanden"
    
    return True, "Marker ist valide"

def enhanced_repair_marker(marker_data):
    """Verbesserte Repair-Funktion die keine leeren Marker erstellt"""
    
    # Erst validieren
    is_valid, reason = validate_marker_before_save(marker_data)
    
    if not is_valid:
        print(f"⚠️ Marker wird NICHT gespeichert: {reason}")
        return None
    
    # Bestehende Repair-Logik...
    # (hier würde die normale Repair-Logik stehen)
    
    return marker_data

def patch_frausar_gui():
    """Patcht die FRAUSAR GUI um Validierung hinzuzufügen"""
    
    patch_code = '''
# PATCH für frausar_gui.py
# Füge diese Validierung vor dem Speichern hinzu:

def validate_before_save(self, marker_data):
    """Validiert Marker vor dem Speichern"""
    
    marker_name = marker_data.get("marker_name")
    description = marker_data.get("description", marker_data.get("beschreibung", ""))
    
    if not marker_name or marker_name == "null" or str(marker_name).strip() == "":
        messagebox.showerror("Validierung fehlgeschlagen", 
                           "marker_name darf nicht leer sein!")
        return False
    
    if not description or str(description).strip() == "":
        messagebox.showerror("Validierung fehlgeschlagen", 
                           "Beschreibung darf nicht leer sein!")
        return False
    
    return True

# In der save_marker Funktion vor dem Speichern einfügen:
if not self.validate_before_save(marker_data):
    return  # Speichern abbrechen
'''
    
    print("📋 Patch-Code für FRAUSAR GUI:")
    print(patch_code)

if __name__ == "__main__":
    print("🛡️ **EMPTY MARKER PREVENTION TOOL**")
    print("=" * 50)
    
    # Teste die Validierung
    test_empty_marker = {
        "marker_name": None,
        "beschreibung": "",
        "examples": ["AUTO_GENERATED_EXAMPLE_1"]
    }
    
    test_valid_marker = {
        "marker_name": "TEST_MARKER", 
        "beschreibung": "Eine echte Beschreibung",
        "examples": ["Echtes Beispiel 1", "Echtes Beispiel 2"]
    }
    
    print("🧪 Teste Validierung...")
    
    is_valid, reason = validate_marker_before_save(test_empty_marker)
    print(f"❌ Leerer Marker: {is_valid} - {reason}")
    
    is_valid, reason = validate_marker_before_save(test_valid_marker)
    print(f"✅ Valider Marker: {is_valid} - {reason}")
    
    print("\n💡 Empfehlung:")
    print("1. Füge die validate_before_save Funktion zu frausar_gui.py hinzu")
    print("2. Rufe sie vor jedem Speichern auf")
    print("3. Verhindere das Speichern bei Validierungsfehlern")
    
    patch_frausar_gui() 