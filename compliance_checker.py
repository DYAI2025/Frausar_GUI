#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Compliance Checker für Semantic Marker Framework
Überprüft ob alle Marker und Grabber den Projekt-Regeln entsprechen
"""

import yaml
import re
from pathlib import Path
from datetime import datetime

class ComplianceChecker:
    def __init__(self):
        self.rules_path = Path("semantic_marker_rules.yaml")
        self.grabber_library_path = Path("semantic_grabber_library.yaml")
        self.marker_dir = Path("../ALL_SEMANTIC_MARKER_TXT")
        self.violations = []
        self.warnings = []
        self.stats = {
            'total_markers': 0,
            'compliant_markers': 0,
            'total_grabbers': 0,
            'compliant_grabbers': 0
        }
    
    def load_rules(self):
        """Lädt die Projekt-Regeln"""
        if self.rules_path.exists():
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            self.violations.append("❌ semantic_marker_rules.yaml nicht gefunden!")
            return None
    
    def check_marker_naming(self, marker_name):
        """Prüft ob Marker-Name den Konventionen entspricht"""
        # Regel: ALL_CAPS + _MARKER
        pattern = r'^[A-Z][A-Z_]+_MARKER$'
        if not re.match(pattern, marker_name):
            return False, f"Marker-Name '{marker_name}' entspricht nicht dem Format ALL_CAPS_MARKER"
        return True, ""
    
    def check_grabber_naming(self, grabber_id):
        """Prüft ob Grabber-ID den Konventionen entspricht"""
        # Regel: ALL_CAPS + _SEM oder AUTO_SEM_<datum>_<nummer>
        pattern1 = r'^[A-Z][A-Z_]+_SEM$'
        pattern2 = r'^AUTO_SEM_\d{8}_[A-Z0-9]{4}$'
        
        if not (re.match(pattern1, grabber_id) or re.match(pattern2, grabber_id)):
            return False, f"Grabber-ID '{grabber_id}' entspricht nicht dem Format *_SEM oder AUTO_SEM_*"
        return True, ""
    
    def check_marker_structure(self, marker_data, filename):
        """Prüft ob Marker alle erforderlichen Felder hat"""
        required_fields = ['marker_name', 'beschreibung', 'beispiele', 'semantische_grabber_id']
        missing_fields = []
        
        for field in required_fields:
            if field not in marker_data or not marker_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Fehlende Pflichtfelder in {filename}: {', '.join(missing_fields)}"
        
        # Prüfe ob beispiele eine Liste ist
        if not isinstance(marker_data.get('beispiele', []), list):
            return False, f"'beispiele' muss eine Liste sein in {filename}"
        
        # Prüfe ob mindestens ein Beispiel vorhanden
        if len(marker_data.get('beispiele', [])) == 0:
            self.warnings.append(f"⚠️  Keine Beispiele in {filename}")
        
        return True, ""
    
    def check_grabber_structure(self, grabber_id, grabber_data):
        """Prüft ob Grabber alle erforderlichen Felder hat"""
        required_fields = ['beschreibung', 'patterns']
        missing_fields = []
        
        for field in required_fields:
            if field not in grabber_data or not grabber_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Fehlende Pflichtfelder in Grabber {grabber_id}: {', '.join(missing_fields)}"
        
        # Prüfe ob patterns eine Liste ist
        if not isinstance(grabber_data.get('patterns', []), list):
            return False, f"'patterns' muss eine Liste sein in Grabber {grabber_id}"
        
        return True, ""
    
    def check_grabber_references(self, markers, grabbers):
        """Prüft ob alle Marker-Grabber-Referenzen gültig sind"""
        used_grabbers = set()
        orphaned_references = []
        
        for marker_file, marker_data in markers.items():
            grabber_id = marker_data.get('semantische_grabber_id')
            if grabber_id:
                used_grabbers.add(grabber_id)
                if grabber_id not in grabbers:
                    orphaned_references.append(f"{marker_file} → {grabber_id}")
        
        # Finde ungenutzte Grabber
        unused_grabbers = set(grabbers.keys()) - used_grabbers
        
        if orphaned_references:
            self.violations.append(f"❌ Verwaiste Grabber-Referenzen: {', '.join(orphaned_references)}")
        
        if unused_grabbers:
            self.warnings.append(f"⚠️  Ungenutzte Grabber: {', '.join(unused_grabbers)}")
    
    def scan_markers(self):
        """Scannt alle Marker-Dateien"""
        markers = {}
        
        # Scanne YAML-Dateien
        for yaml_file in self.marker_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        markers[yaml_file.name] = data
                        self.stats['total_markers'] += 1
            except Exception as e:
                self.warnings.append(f"⚠️  Fehler beim Lesen von {yaml_file.name}: {str(e)}")
        
        # Scanne TXT-Dateien (Legacy-Format)
        for txt_file in self.marker_dir.rglob("*_MARKER.txt"):
            self.warnings.append(f"⚠️  Legacy TXT-Format gefunden: {txt_file.name} - sollte zu YAML konvertiert werden")
            self.stats['total_markers'] += 1
        
        return markers
    
    def scan_grabbers(self):
        """Lädt alle Grabber aus der Library"""
        if not self.grabber_library_path.exists():
            self.violations.append("❌ semantic_grabber_library.yaml nicht gefunden!")
            return {}
        
        try:
            with open(self.grabber_library_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                grabbers = data.get('semantic_grabbers', {})
                self.stats['total_grabbers'] = len(grabbers)
                return grabbers
        except Exception as e:
            self.violations.append(f"❌ Fehler beim Laden der Grabber-Library: {str(e)}")
            return {}
    
    def run_compliance_check(self):
        """Führt vollständigen Compliance-Check durch"""
        print("🔍 Starte Compliance-Check für Semantic Marker Framework...")
        print("=" * 60)
        
        # Lade Regeln
        rules = self.load_rules()
        if not rules:
            print("❌ Konnte Regeln nicht laden!")
            return
        
        # Scanne Marker und Grabber
        markers = self.scan_markers()
        grabbers = self.scan_grabbers()
        
        print(f"\n📊 Gefunden: {len(markers)} Marker, {len(grabbers)} Grabber")
        
        # Prüfe Marker
        print("\n🔍 Prüfe Marker-Compliance...")
        for marker_file, marker_data in markers.items():
            marker_name = marker_data.get('marker_name', marker_file.replace('.yaml', ''))
            
            # Naming Convention
            valid, msg = self.check_marker_naming(marker_name)
            if not valid:
                self.violations.append(f"❌ {msg}")
            else:
                self.stats['compliant_markers'] += 1
            
            # Struktur
            valid, msg = self.check_marker_structure(marker_data, marker_file)
            if not valid:
                self.violations.append(f"❌ {msg}")
        
        # Prüfe Grabber
        print("\n🔍 Prüfe Grabber-Compliance...")
        for grabber_id, grabber_data in grabbers.items():
            # Naming Convention
            valid, msg = self.check_grabber_naming(grabber_id)
            if not valid:
                self.violations.append(f"❌ {msg}")
            else:
                self.stats['compliant_grabbers'] += 1
            
            # Struktur
            valid, msg = self.check_grabber_structure(grabber_id, grabber_data)
            if not valid:
                self.violations.append(f"❌ {msg}")
        
        # Prüfe Referenzen
        print("\n🔍 Prüfe Grabber-Referenzen...")
        self.check_grabber_references(markers, grabbers)
        
        # Report
        self.generate_report()
    
    def generate_report(self):
        """Generiert Compliance-Report"""
        print("\n" + "=" * 60)
        print("📋 COMPLIANCE REPORT")
        print("=" * 60)
        
        # Statistiken
        print(f"\n📊 Statistiken:")
        print(f"   Marker gesamt: {self.stats['total_markers']}")
        print(f"   Marker compliant: {self.stats['compliant_markers']}")
        print(f"   Grabber gesamt: {self.stats['total_grabbers']}")
        print(f"   Grabber compliant: {self.stats['compliant_grabbers']}")
        
        # Violations
        if self.violations:
            print(f"\n❌ Regelverletzungen ({len(self.violations)}):")
            for v in self.violations[:10]:  # Zeige max 10
                print(f"   {v}")
            if len(self.violations) > 10:
                print(f"   ... und {len(self.violations) - 10} weitere")
        else:
            print("\n✅ Keine Regelverletzungen gefunden!")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnungen ({len(self.warnings)}):")
            for w in self.warnings[:10]:  # Zeige max 10
                print(f"   {w}")
            if len(self.warnings) > 10:
                print(f"   ... und {len(self.warnings) - 10} weitere")
        
        # Empfehlungen
        print("\n💡 Empfehlungen:")
        if self.stats['total_markers'] > self.stats['compliant_markers']:
            print("   - Konvertiere alle Marker zu YAML-Format")
            print("   - Stelle sicher dass alle Marker eine semantische_grabber_id haben")
        
        if any("Legacy TXT-Format" in w for w in self.warnings):
            print("   - Migriere TXT-Dateien zu YAML-Format")
        
        print("\n✅ Compliance-Check abgeschlossen!")
        
        # Speichere Report
        report_file = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("SEMANTIC MARKER FRAMEWORK - COMPLIANCE REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generiert: {datetime.now().isoformat()}\n\n")
            f.write(f"Violations: {len(self.violations)}\n")
            for v in self.violations:
                f.write(f"  {v}\n")
            f.write(f"\nWarnings: {len(self.warnings)}\n")
            for w in self.warnings:
                f.write(f"  {w}\n")
        
        print(f"\n📄 Report gespeichert: {report_file}")

if __name__ == "__main__":
    checker = ComplianceChecker()
    checker.run_compliance_check() 