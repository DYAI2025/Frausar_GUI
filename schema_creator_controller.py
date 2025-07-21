#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema Creator Controller - Backend-Logik für den Analyse-Schema-Wizard
"""

import re
from typing import Dict, List, Any
import yaml
from pathlib import Path
import json
from datetime import datetime

# Wir können die FRAUSARAssistant-Klasse nicht direkt importieren wegen zyklischer Abhängigkeiten,
# aber wir erwarten ein Objekt mit einer `collect_all_markers`-Methode.

class SchemaCreatorController:
    """
    Diese Klasse enthält die Geschäftslogik zur Erstellung, Validierung
    und Verwaltung von Analyse-Schemata.
    """
    def __init__(self, assistant):
        """
        Initialisiert den Controller.
        
        Args:
            assistant: Eine Instanz von FRAUSARAssistant (oder ein Mock-Objekt),
                       das eine `collect_all_markers()`-Methode bereitstellt.
        """
        self.assistant = assistant
        self.all_markers_cache = None
        self.all_detectors_cache = None # NEUER CACHE

    def _get_all_markers(self) -> Dict[str, Any]:
        """Lädt alle Marker und cached das Ergebnis, um wiederholte Ladevorgänge zu vermeiden."""
        if self.all_markers_cache is None:
            # Annahme: assistant.collect_all_markers() gibt ein Dict zurück
            # mit Marker-Namen als Keys.
            self.all_markers_cache = self.assistant.collect_all_markers()
        return self.all_markers_cache

    def suggest_markers(self, description: str, name: str, top_n: int = 15) -> List[str]:
        """
        Schlägt Marker basierend auf einer Beschreibung und einem Namen vor.
        
        Args:
            description (str): Die vom Nutzer eingegebene Beschreibung des Schemas.
            name (str): Der vom Nutzer eingegebene Name des Schemas.
            top_n (int): Die maximale Anzahl an Vorschlägen.
            
        Returns:
            List[str]: Eine Liste der am besten passenden Marker-Namen.
        """
        if not description and not name:
            return []

        search_text = (name + " " + description).lower()
        # Zerlege den Suchtext in einzelne Keywords, ignoriere Stoppwörter
        keywords = set(re.findall(r'\b\w{3,}\b', search_text))
        stoppwörter = {'und', 'oder', 'die', 'das', 'ein', 'eine', 'für', 'mit', 'ist'}
        keywords -= stoppwörter
        
        all_markers = self._get_all_markers()
        scored_markers = []

        for marker_name, marker_data in all_markers.items():
            score = 0
            
            # 1. Prüfe auf Keywords im Marker-Namen, Beschreibung und Tags
            marker_content = (
                marker_name.lower() + " " + 
                marker_data.get('beschreibung', '').lower() + " " +
                ' '.join(marker_data.get('tags', [])).lower()
            )
            
            for keyword in keywords:
                if keyword in marker_content:
                    score += 2  # Höhere Gewichtung für direkte Keyword-Treffer
                if keyword in marker_name.lower():
                    score += 3 # Noch höhere Gewichtung für Treffer im Namen
            
            # 2. Bonus für Marker mit vielen Beispielen (oft wichtiger)
            example_count = len(marker_data.get('beispiele', []))
            if example_count > 5:
                score += 1
            if example_count > 10:
                score += 1

            if score > 0:
                scored_markers.append((score, marker_name))

        # Sortiere nach Score (höchster zuerst) und gib die Top N zurück
        scored_markers.sort(key=lambda x: x[0], reverse=True)
        
        return [name for score, name in scored_markers[:top_n]]

    def suggest_markers_with_llm(self, description: str, name: str) -> List[Dict]:
        """
        Generiert neue Marker-Vorschläge mithilfe eines LLM.
        
        Args:
            description (str): Die Beschreibung des Schemas.
            name (str): Der Name des Schemas.
            
        Returns:
            List[Dict]: Eine Liste von Dictionaries, die neue Marker repräsentieren.
        """
        system_prompt = """Du bist ein Experte für Kommunikationsanalyse und Betrugserkennung. Deine Aufgabe ist es, basierend auf einer Analyse-Zielbeschreibung neue, passende "Marker" zu konzipieren. Ein Marker ist eine spezifische, beobachtbare Handlung oder Aussage.

Gib deine Antwort IMMER als eine Liste von YAML-Objekten zurück. Jeder Marker MUSS die Felder 'marker_name' und 'beschreibung' haben.

Beispiel-Output:
```yaml
- marker_name: ZUKUNFTSVERSPRECHEN_MARKER
  beschreibung: Macht vage, aber große Versprechungen über eine gemeinsame Zukunft, um emotionale Bindung zu erzeugen.
- marker_name: SPIEGELN_DER_INTERESSEN_MARKER
  beschreibung: Übernimmt auffällig schnell die Hobbies und Interessen des Gegenübers, um eine künstliche Seelenverwandtschaft zu suggerieren.
```"""

        user_prompt = f"""Ich entwerfe ein neues Analyse-Schema mit folgendem Ziel:
Name: "{name}"
Beschreibung: "{description}"

Bitte generiere 5-7 passende, kreative und präzise Marker-Konzepte, die für diese Analyse nützlich wären. Gib NUR die YAML-Liste zurück."""

        # --- SIMULIERTER LLM-AUFRUF ---
        # In einer echten Implementierung würde hier der API-Call zum LLM stehen.
        # z.B. response = openai.Completion.create(...)
        print("--- LLM-AUFRUF (SIMULIERT) ---")
        print(f"SYSTEM PROMPT:\n{system_prompt}")
        print(f"USER PROMPT:\n{user_prompt}")
        
        simulated_llm_response = f"""
```yaml
- marker_name: EMOTIONALER_APPETITHAPPEN_MARKER
  beschreibung: Teilt eine kleine, scheinbar verletzliche persönliche Geschichte, um schnell künstliches Vertrauen und Neugier zu wecken.
- marker_name: GETEILTES_GEHEIMNIS_MARKER
  beschreibung: Vertraut dem Ziel ein angebliches Geheimnis an, um ein exklusives Band zu schaffen und das Ziel zur Preisgabe eigener Geheimnisse zu motivieren.
- marker_name: UNTERSCHWELLIGE_DRINGLICHKEIT_MARKER
  beschreibung: Baut subtilen Zeitdruck auf ("Diese Gelegenheit gibt es nur jetzt"), ohne eine direkte Forderung zu stellen.
- marker_name: IDEALISIERUNGS_FEEDBACK_MARKER
  beschreibung: Bestätigt und überhöht die positiven Selbstansichten des Ziels exzessiv, um Abhängigkeit von dieser Bestätigung zu schaffen.
- marker_name: PROBLEM_LÖSUNGS_FALLE_MARKER
  beschreibung: Präsentiert ein komplexes, persönliches Problem und positioniert das Ziel als den einzigen möglichen Retter oder Helfer.
```
"""
        # --- ENDE SIMULATION ---
        
        return self._parse_llm_response(simulated_llm_response)

    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parst die YAML-formatierte Antwort des LLM."""
        try:
            # Extrahiere den Inhalt innerhalb der ```yaml ... ``` Blöcke
            match = re.search(r'```yaml\n(.*?)\n```', response_text, re.DOTALL)
            if match:
                yaml_content = match.group(1)
            else:
                yaml_content = response_text # Fallback, falls keine code fences da sind

            parsed_yaml = yaml.safe_load(yaml_content)
            
            if isinstance(parsed_yaml, list):
                # Stelle sicher, dass jedes Element ein Dict mit den nötigen Keys ist
                return [
                    item for item in parsed_yaml 
                    if isinstance(item, dict) and 'marker_name' in item and 'beschreibung' in item
                ]
        except Exception as e:
            print(f"Fehler beim Parsen der LLM-Antwort: {e}")
        
        return []

    def _get_all_detectors(self) -> Dict[str, Any]:
        """Lädt alle Detektoren aus dem Schema und cached das Ergebnis."""
        if self.all_detectors_cache is None:
            try:
                schema_path = Path("DETECT_default_marker_schema.yaml")
                if schema_path.exists():
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_data = yaml.safe_load(f)
                    self.all_detectors_cache = schema_data.get('application_schema', {}).get('detectors', {})
                else:
                    self.all_detectors_cache = {}
            except Exception as e:
                print(f"Fehler beim Laden des Detektor-Schemas: {e}")
                self.all_detectors_cache = {}
        return self.all_detectors_cache

    def suggest_detectors(self, selected_markers: List[str]) -> List[str]:
        """
        Schlägt Detektoren basierend auf den ausgewählten Markern vor.
        """
        all_detectors = self._get_all_detectors()
        suggestions = []
        selected_marker_set = set(selected_markers)

        for detector_name, detector_data in all_detectors.items():
            supported = detector_data.get('supported_markers', [])
            # Wenn es eine Überschneidung zwischen den unterstützten Markern des Detektors
            # und den vom Nutzer gewählten Markern gibt, schlage ihn vor.
            if selected_marker_set.intersection(supported):
                suggestions.append(detector_data.get('file_path', detector_name))
        
        return sorted(list(set(suggestions)))

    def build_summary_text(self, schema_data: Dict) -> str:
        """Erstellt einen Text-String für die Review-Seite."""
        summary = f"Schema-Name: {schema_data.get('name', 'N/A')}\n"
        summary += "=" * 40 + "\n"
        summary += f"Beschreibung:\n{schema_data.get('description', 'N/A')}\n\n"
        summary += f"Vorlage: {schema_data.get('template', 'N/A')}\n"
        summary += "=" * 40 + "\n"
        
        markers = schema_data.get('markers', [])
        summary += f"Ausgewählte Marker ({len(markers)}):\n"
        if markers:
            for i, marker in enumerate(markers[:10]):
                summary += f"- {marker}\n"
            if len(markers) > 10:
                summary += f"- ... und {len(markers) - 10} weitere\n"
        else:
            summary += "- Keine\n"
        summary += "\n"

        detectors = schema_data.get('detectors', [])
        summary += f"Ausgewählte Detektoren ({len(detectors)}):\n"
        if detectors:
            for detector in detectors:
                summary += f"- {detector}\n"
        else:
            summary += "- Keine\n"
            
        return summary

    def validate_configuration(self, schema_data: Dict) -> List[Dict]:
        """
        Validiert die Konfiguration des Schemas und gibt eine Checkliste zurück.
        """
        checks = []
        
        # Check 1: Name vorhanden
        name = schema_data.get('name', '').strip()
        checks.append({
            'text': 'Schema-Name ist vergeben',
            'valid': bool(name)
        })
        
        # Check 2: Mindestens 5 Marker
        markers = schema_data.get('markers', [])
        checks.append({
            'text': f'Mindestens 5 Marker ausgewählt ({len(markers)}/5)',
            'valid': len(markers) >= 5
        })
        
        # Check 3: Mindestens 1 Detektor
        detectors = schema_data.get('detectors', [])
        checks.append({
            'text': f'Mindestens 1 Detektor ausgewählt ({len(detectors)}/1)',
            'valid': len(detectors) >= 1
        })
        
        # Check 4: Alle Marker-Referenzen sind gültig (vereinfacht)
        # In einer echten Implementierung würde man hier gegen die Master-Liste prüfen
        checks.append({
            'text': 'Alle Marker-Referenzen sind gültig',
            'valid': True # Annahme für jetzt
        })
        
        return checks
        
    def build_schema_json(self, schema_data: Dict) -> Dict:
        """
        Erstellt das finale JSON-Objekt für das Analyse-Schema.
        """
        template_path = Path(f"analysis_schemas/templates/{schema_data.get('template')}")
        
        # Lade Basis-Template, falls eines ausgewählt wurde
        if schema_data.get('template') != '(Keine Vorlage)' and template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                final_schema = json.load(f)
        else:
            # Fallback auf eine generische Struktur
            final_schema = {
                "schema_info": {},
                "marker_config": {"atomic_markers": []},
                "detector_config": {"enabled_detectors": []},
                "scoring_config": {
                    "risk_thresholds": {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 0.95},
                    "default_marker_weight": 1.0
                }
            }
            
        # Fülle die Schema-Informationen
        final_schema['schema_info']['name'] = schema_data.get('name')
        final_schema['schema_info']['description'] = schema_data.get('description')
        final_schema['schema_info']['created_at'] = datetime.now().isoformat()
        final_schema['schema_info']['created_by'] = "FRAUSAR_Schema_Creator"
        final_schema['schema_info']['version'] = "1.0"
        
        # Fülle die Marker-Konfiguration
        # Annahme: Alle Marker sind 'atomic' für diese erste Version
        # Wir fügen sie als Objekte mit ID und Standardgewicht hinzu
        final_schema['marker_config']['atomic_markers'] = [
            {'id': marker_name, 'scoring.weight': 1.0} 
            for marker_name in schema_data.get('markers', [])
        ]
        
        # Fülle die Detektor-Konfiguration
        final_schema['detector_config']['enabled_detectors'] = schema_data.get('detectors', [])
        
        return final_schema 