#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DETECT.py Creator - Robuste Erstellung von Detector-Modulen
===========================================================
Separate Logik für die Erstellung von DETECT.py Dateien mit:
- Template-basierte Generierung
- Schema-Integration
- Automatische Namensgenerierung
- Funktionale Struktur nach DETECT-Standard
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

class DetectCreator:
    """Klasse für die robuste Erstellung von DETECT.py Dateien"""
    
    def __init__(self, base_directory=None, schema_path=None):
        self.base_directory = Path(base_directory) if base_directory else Path("../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/_python")
        self.schema_path = Path(schema_path) if schema_path else Path("DETECT_default_marker_schema.yaml")
        
        # Erstelle Verzeichnis falls nicht vorhanden
        self.base_directory.mkdir(parents=True, exist_ok=True)
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def create_detect_module(self, 
                           module_name: str,
                           description: str,
                           patterns: List[str],
                           semantic_grabber_id: Optional[str] = None,
                           detection_threshold: int = 2) -> Tuple[bool, str, Dict]:
        """
        Erstellt ein neues DETECT.py Modul
        
        Args:
            module_name: Name des Moduls (wird automatisch formatiert)
            description: Beschreibung der Funktion
            patterns: Liste von Erkennungsmustern
            semantic_grabber_id: Optional - Semantic Grabber ID
            detection_threshold: Mindestanzahl Komponenten für Erkennung
            
        Returns:
            Tuple[success, file_path, metadata]
        """
        try:
            # Formatiere Modulnamen nach DETECT-Standard
            formatted_name = self._format_module_name(module_name)
            
            # Generiere Dateiinhalt
            file_content = self._generate_detect_template(
                formatted_name, description, patterns, semantic_grabber_id, detection_threshold
            )
            
            # Speichere Datei
            file_path = self.base_directory / f"{formatted_name}.py"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            # Erstelle Metadaten
            metadata = {
                'module_name': formatted_name,
                'file_path': str(file_path),
                'description': description,
                'patterns_count': len(patterns),
                'created_at': datetime.now().isoformat(),
                'semantic_grabber_id': semantic_grabber_id
            }
            
            # Aktualisiere Schema
            schema_updated = self._update_schema(metadata)
            
            self.logger.info(f"DETECT.py Modul erfolgreich erstellt: {file_path}")
            return True, str(file_path), metadata
            
        except Exception as e:
            self.logger.error(f"Fehler bei DETECT.py Erstellung: {e}")
            return False, str(e), {}
    
    def _format_module_name(self, name: str) -> str:
        """Formatiert Modulnamen nach DETECT-Standard"""
        # Entferne Sonderzeichen und normalisiere
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name.upper())
        
        # Entferne doppelte Unterstriche
        cleaned = re.sub(r'_+', '_', cleaned)
        
        # Stelle sicher dass es mit DETECT beginnt
        if not cleaned.startswith('DETECT_'):
            cleaned = f"DETECT_{cleaned}"
        
        # Entferne trailing Underscores
        cleaned = cleaned.rstrip('_')
        
        return cleaned
    
    def _generate_detect_template(self, 
                                module_name: str, 
                                description: str,
                                patterns: List[str],
                                semantic_grabber_id: Optional[str],
                                threshold: int) -> str:
        """Generiert DETECT.py Template nach vorhandenem Standard"""
        
        # Extrahiere Funktionsname aus Modulname
        function_name = module_name.lower().replace('detect_', '')
        
        # Generiere Komponenten-Dictionary
        components_dict = self._generate_components_dict(patterns)
        
        template = f'''import re

# ==============================================================================
# DEFINITION DER SEMANTISCHEN KOMPONENTEN
# Diese "Zutaten" machen das {description} aus.
# ==============================================================================

{module_name}_COMPONENTS = {components_dict}

# ==============================================================================
# ANALYSEFUNKTION
# ==============================================================================

def detect_{function_name}(text: str) -> dict:
    """
    Analysiert einen Text semantisch auf "{description}".

    Die Funktion prüft, ob mehrere Komponenten des Markers im Text vorkommen,
    um eine hohe Treffsicherheit zu gewährleisten.

    Args:
        text: Der zu analysierende Text (z.B. eine Chat-Nachricht, eine Aussage).

    Returns:
        Ein Dictionary mit dem Analyseergebnis.
    """
    found_components = set()
    
    # Durchsuche den Text nach jeder Komponente
    for component_name, patterns in {module_name}_COMPONENTS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                found_components.add(component_name)
                break  # Ein Treffer pro Komponente reicht

    score = len(found_components)
    is_detected = score >= {threshold}  # Marker wird als erkannt gewertet, wenn mind. {threshold} Komponenten zutreffen

    analysis = {{
        "marker_id": "{module_name}",
        "is_detected": is_detected,
        "confidence_score": score / len({module_name}_COMPONENTS) if {module_name}_COMPONENTS else 0,
        "found_components": list(found_components),
        "semantic_grabber_id": "{semantic_grabber_id or 'AUTO_GENERATED'}"
    }}

    if is_detected:
        explanation = "Die Aussage enthält mehrere Signale für {description.lower()}. "
        analysis["explanation"] = explanation

    return analysis

# ==============================================================================
# DEMONSTRATION / ANWENDUNGSBEISPIEL
# ==============================================================================

if __name__ == "__main__":
    
    test_cases = [
        # Testfälle werden hier automatisch generiert basierend auf den Patterns
{self._generate_test_cases(patterns)}
    ]

    print("--- Semantische Analyse auf {description} ---\\n")

    for i, text in enumerate(test_cases):
        result = detect_{function_name}(text)
        print(f"Testfall #{{i+1}}: \\"{{text}}\\"")
        if result["is_detected"]:
            print(f"  ▶️ Marker erkannt: JA")
            print(f"  ▶️ Erklärung: {{result.get('explanation', 'N/A')}}")
            print(f"  ▶️ Gefundene Komponenten: {{result['found_components']}}")
        else:
            print(f"  ▶️ Marker erkannt: NEIN (Nur {{len(result['found_components'])}}/{threshold} Komponenten gefunden)")
        print("-" * 50)

# ==============================================================================
# METADATA FÜR AUTOMATISCHE INTEGRATION
# ==============================================================================

DETECTOR_METADATA = {{
    "module_name": "{module_name}",
    "function_name": "detect_{function_name}",
    "description": "{description}",
    "semantic_grabber_id": "{semantic_grabber_id or 'AUTO_GENERATED'}",
    "created_at": "{datetime.now().isoformat()}",
    "detection_threshold": {threshold},
    "components_count": {len(patterns)}
}}
'''
        return template
    
    def _generate_components_dict(self, patterns: List[str]) -> str:
        """Generiert Komponenten-Dictionary aus Pattern-Liste"""
        if not patterns:
            return '{\n    "BASE_COMPONENT": [\n        r"\\\\b(pattern)\\\\b"\n    ]\n}'
        
        components = {}
        
        # Gruppiere Patterns intelligently - ALLE Patterns verwenden
        for i, pattern in enumerate(patterns[:10]):  # Max 10 Komponenten
            # Erstelle semantischen Komponentennamen
            component_name = self._generate_component_name(pattern, i)
            
            # Vermeide doppelte Komponentennamen
            original_name = component_name
            counter = 1
            while component_name in components:
                component_name = f"{original_name}_{counter}"
                counter += 1
            
            # Konvertiere zu Regex-Pattern
            regex_pattern = self._pattern_to_regex(pattern)
            
            components[component_name] = [regex_pattern]
        
        # Formatiere als Python-Dictionary-String
        dict_str = "{\n"
        for name, pattern_list in components.items():
            dict_str += f'    "{name}": [\n'
            for pattern in pattern_list:
                dict_str += f'        r"{pattern}",\n'
            dict_str += "    ],\n"
        dict_str += "}"
        
        return dict_str
    
    def _generate_component_name(self, pattern: str, index: int) -> str:
        """Generiert semantischen Komponentennamen aus Pattern"""
        # Extrahiere Schlüsselwörter
        keywords = re.findall(r'\b\w{3,}\b', pattern.lower())
        
        if keywords:
            # Nehme erstes relevantes Keyword
            main_keyword = keywords[0].upper()
            return f"{main_keyword}_COMPONENT"
        else:
            return f"COMPONENT_{index + 1}"
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """Konvertiert einfachen Pattern zu Regex"""
        # Für Template-String: Verwende nur ein Level Escaping
        # re.escape macht bereits das nötige Escaping für Regex
        escaped = re.escape(pattern)
        
        # Verwende Wortgrenzen für Text-Patterns die mit Buchstaben beginnen/enden
        if re.match(r'^[a-zA-Z].*[a-zA-Z]$', pattern.strip()):
            # Template-String braucht nur \b nicht \\b
            return f"\\b{escaped}\\b"
        else:
            return escaped
    
    def _generate_test_cases(self, patterns: List[str]) -> str:
        """Generiert Testfälle basierend auf Patterns"""
        test_cases = []
        
        # Erstelle Beispiele aus Patterns
        for pattern in patterns[:3]:  # Erste 3 Patterns als Basis
            test_cases.append(f'        "{pattern}",')
        
        # Füge negative Testfälle hinzu
        test_cases.append('        "Normaler Text ohne relevante Marker.",')
        test_cases.append('        "Positive eindeutige Aussage.",')
        
        return '\n'.join(test_cases)
    
    def _update_schema(self, metadata: Dict) -> bool:
        """Aktualisiert das DETECT Schema mit dem neuen Modul"""
        try:
            # Lade existierendes Schema
            schema = self._load_schema()
            
            # Füge neues Modul hinzu
            # Bereinige den file_path für das Schema
            try:
                relative_path = str(Path(metadata['file_path']).relative_to(Path.cwd()))
            except ValueError:
                # Fallback: Verwende absoluten Pfad ohne Umwandlung
                relative_path = metadata['file_path']
            
            module_entry = {
                "module": metadata['module_name'].lower(),
                "class": metadata['module_name'],
                "file_path": relative_path,
                "description": metadata['description'],
                "last_updated": metadata['created_at'],
                "auto_generated": True
            }
            
            schema['application_schema']['detectors'][metadata['module_name'].lower()] = module_entry
            
            # Aktualisiere Meta-Informationen
            schema['meta']['last_updated'] = datetime.now().isoformat()
            schema['meta']['total_detectors'] = len(schema['application_schema']['detectors'])
            
            # Speichere Schema
            with open(self.schema_path, 'w', encoding='utf-8') as f:
                yaml.dump(schema, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Schema erfolgreich aktualisiert: {self.schema_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Schema-Update: {e}")
            return False
    
    def _load_schema(self) -> Dict:
        """Lädt das existierende Schema oder erstellt ein neues"""
        if self.schema_path.exists():
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.logger.warning(f"Fehler beim Laden des Schemas: {e}")
        
        # Fallback: Erstelle neues Schema
        return {
            "meta": {
                "title": "FRAUSAR Detector Schema",
                "version": "1.0",
                "description": "Automatisch generiertes Schema für Detector-Module",
                "created_at": datetime.now().isoformat(),
                "auto_generated": True,
                "last_updated": datetime.now().isoformat(),
                "total_detectors": 0
            },
            "application_schema": {
                "detectors": {}
            }
        }
    
    def list_existing_detectors(self) -> List[Dict]:
        """Listet alle existierenden DETECT.py Module auf"""
        detectors = []
        
        for py_file in self.base_directory.glob("DETECT_*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extrahiere Metadaten
                metadata_match = re.search(r'DETECTOR_METADATA\s*=\s*\{([^}]+)\}', content, re.DOTALL)
                if metadata_match:
                    # Parse Metadaten (vereinfacht)
                    detectors.append({
                        'file': py_file.name,
                        'path': str(py_file),
                        'has_metadata': True
                    })
                else:
                    detectors.append({
                        'file': py_file.name,
                        'path': str(py_file),
                        'has_metadata': False
                    })
                    
            except Exception as e:
                self.logger.error(f"Fehler beim Lesen von {py_file}: {e}")
        
        return detectors
    
    def validate_detector(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validiert ein DETECT.py Modul"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Prüfe erforderliche Komponenten
            required_elements = [
                r'def detect_\w+\(',
                r'_COMPONENTS\s*=',
                r'DETECTOR_METADATA\s*=',
                r'if __name__ == "__main__":'
            ]
            
            for element in required_elements:
                if not re.search(element, content):
                    errors.append(f"Missing required element: {element}")
            
            # Prüfe Syntax
            try:
                compile(content, file_path, 'exec')
            except SyntaxError as e:
                errors.append(f"Syntax error: {e}")
            
        except Exception as e:
            errors.append(f"File read error: {e}")
        
        return len(errors) == 0, errors

# ==============================================================================
# HILFS-FUNKTIONEN FÜR GUI INTEGRATION
# ==============================================================================

def create_detect_from_dialog_data(name: str, description: str, examples: List[str], 
                                  semantic_grabber_id: Optional[str] = None) -> Tuple[bool, str, Dict]:
    """
    Wrapper-Funktion für GUI-Integration
    
    Args:
        name: Modulname
        description: Beschreibung
        examples: Liste von Beispiel-Patterns
        semantic_grabber_id: Optional Grabber ID
        
    Returns:
        Tuple[success, message, metadata]
    """
    creator = DetectCreator()
    
    success, result, metadata = creator.create_detect_module(
        module_name=name,
        description=description,
        patterns=examples,
        semantic_grabber_id=semantic_grabber_id
    )
    
    if success:
        return True, f"DETECT.py Modul erfolgreich erstellt: {result}", metadata
    else:
        return False, f"Fehler bei der Erstellung: {result}", {}

# ==============================================================================
# DEMO UND TESTS
# ==============================================================================

if __name__ == "__main__":
    # Demo der Funktionalität
    creator = DetectCreator()
    
    print("🔍 DETECT.py Creator - Demo")
    print("=" * 40)
    
    # Beispiel-Erstellung
    success, file_path, metadata = creator.create_detect_module(
        module_name="EXAMPLE_BEHAVIOR",
        description="Beispielhafte Verhaltenserkennung",
        patterns=[
            "vielleicht später",
            "schauen wir mal",
            "bin nicht sicher"
        ],
        semantic_grabber_id="EXAMPLE_SEM_001"
    )
    
    if success:
        print(f"✅ Demo erfolgreich: {file_path}")
        print(f"📊 Metadaten: {metadata}")
    else:
        print(f"❌ Demo fehlgeschlagen: {file_path}") 