#!/usr/bin/env python3
"""
Marker Matcher V2 - Schema-gesteuerter Resonanz- und Manipulations-Detektor
Analysiert Texte basierend auf einem dynamischen Analyse-Schema.
"""

import yaml
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import logging
from datetime import datetime
from collections import defaultdict

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MarkerMatch:
    """Repräsentiert einen gefundenen Marker-Treffer"""
    marker_name: str
    marker_beschreibung: str
    matched_text: str
    position: Tuple[int, int]  # (start, end)
    confidence_score: float = 1.0
    kontext: str = ""
    pattern_type: str = "exact"  # exact, fuzzy, semantic
    tags: List[str] = field(default_factory=list)
    risk_score: int = 1


@dataclass
class AnalysisResult:
    """Ergebnis der Marker-Analyse"""
    text: str
    timestamp: str
    gefundene_marker: List[MarkerMatch]
    risk_level: str
    risk_level_color: str
    total_risk_score: int
    categories_found: Dict[str, int]
    summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Ergebnis in ein Dictionary"""
        return {
            'timestamp': self.timestamp,
            'text_preview': self.text[:100] + '...' if len(self.text) > 100 else self.text,
            'gefundene_marker': [
                {
                    'marker': m.marker_name,
                    'beschreibung': m.marker_beschreibung,
                    'matched_text': m.matched_text,
                    'position': m.position,
                    'confidence': m.confidence_score,
                    'tags': m.tags
                } for m in self.gefundene_marker
            ],
            'risk_level': self.risk_level,
            'risk_level_color': self.risk_level_color,
            'total_risk_score': self.total_risk_score,
            'categories': self.categories_found,
            'summary': self.summary
        }


class MarkerMatcherV2:
    """Hauptklasse für schema-gesteuerte, Marker-basierte Textanalyse"""

    def __init__(self, marker_file: str = "marker_master_export.yaml", schema_config: Optional[Dict] = None):
        """
        Initialisiert den Matcher mit Marker-Daten und optional einem Analyse-Schema.
        
        Args:
            marker_file (str): Pfad zur Master-Marker-Datei.
            schema_config (Optional[Dict]): Ein Analyse-Schema, das die Analyse steuert.
        """
        self.master_markers = {}
        self.schema_config = schema_config
        self.active_markers = {}
        self.risk_thresholds = {}

        # Lade alle verfügbaren Marker
        self._load_master_markers(marker_file)

        # Konfiguriere den Matcher basierend auf dem Schema oder den Standards
        if self.schema_config:
            self._apply_schema_config(self.schema_config)
        else:
            self._apply_default_config()

    def _load_master_markers(self, marker_file: str):
        """Lädt die komplette Marker-Bibliothek aus der YAML-Datei"""
        try:
            with open(marker_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            for marker in data.get('markers', []):
                self.master_markers[marker['marker']] = marker
            logger.info(f"{len(self.master_markers)} Master-Marker geladen.")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Master-Marker-Datei: {e}")
            raise

    def _apply_schema_config(self, schema_config: Dict):
        """Konfiguriert den Matcher basierend auf einem geladenen Schema."""
        logger.info(f"Wende Analyse-Schema an: {schema_config.get('schema_info', {}).get('name')}")
        
        # Lade Marker, die im Schema definiert sind
        schema_markers = []
        for marker_list in schema_config.get('marker_config', {}).values():
            schema_markers.extend([m.get('id') for m in marker_list if 'id' in m])

        self.active_markers = {}
        for marker_id in set(schema_markers):
            if marker_id in self.master_markers:
                # Füge schema-spezifische Gewichtung hinzu
                marker_data = self.master_markers[marker_id].copy()
                for m_conf in schema_config.get('marker_config', {}).values():
                    for item in m_conf:
                        if item.get('id') == marker_id:
                            marker_data['schema_weight'] = item.get('scoring.weight', 1.0)
                
                self.active_markers[marker_id] = marker_data

        # Lade Risiko-Schwellenwerte aus dem Schema
        self.risk_thresholds = schema_config.get('scoring_config', {}).get('risk_thresholds', self._get_default_thresholds())
        logger.info(f"{len(self.active_markers)} aktive Marker und spezifische Risiko-Schwellenwerte aus Schema geladen.")
        
    def _apply_default_config(self):
        """Lädt die Standardkonfiguration, wenn kein Schema vorhanden ist."""
        logger.info("Kein Schema gefunden. Verwende Standardkonfiguration.")
        self.active_markers = self.master_markers
        self.risk_thresholds = self._get_default_thresholds()

    def _get_default_thresholds(self) -> Dict:
        """Gibt die Standard-Risiko-Schwellenwerte zurück."""
        return {
            'green': (0, 1),
            'yellow': (2, 5),
            'blinking': (6, 10),
            'red': (11, float('inf'))
        }

    def analyze_text(self, text: str) -> AnalysisResult:
        """Analysiert einen Text basierend auf den aktiven Markern und der Konfiguration."""
        logger.debug(f"Analysiere Text mit {len(text)} Zeichen unter Verwendung von {len(self.active_markers)} aktiven Markern.")
        
        matches = []
        categories_count = defaultdict(int)
        total_risk_score = 0
        
        for marker_name, marker_data in self.active_markers.items():
            marker_matches = self._find_marker_in_text(text, marker_data)
            
            for match in marker_matches:
                # Wende schema-spezifische Gewichtung an, falls vorhanden
                schema_weight = marker_data.get('schema_weight', 1.0)
                match.risk_score *= schema_weight
                
                matches.append(match)
                categories_count[marker_data.get('kategorie', 'UNCATEGORIZED')] += 1
                total_risk_score += match.risk_score
        
        risk_level, risk_color = self._calculate_risk_level(total_risk_score, len(matches))
        summary = self._generate_summary(matches, risk_level)
        
        return AnalysisResult(
            text=text,
            timestamp=datetime.now().isoformat(),
            gefundene_marker=matches,
            risk_level=risk_level,
            risk_level_color=risk_color,
            total_risk_score=total_risk_score,
            categories_found=dict(categories_count),
            summary=summary
        )

    def _find_marker_in_text(self, text: str, marker_data: Dict[str, Any]) -> List[MarkerMatch]:
        """Sucht nach einem spezifischen Marker im Text"""
        matches = []
        
        # Suche nach Beispielen
        for beispiel in marker_data.get('beispiele', []):
            if not beispiel:  # Überspringe leere Beispiele
                continue
                
            # Normalisiere für besseres Matching
            beispiel_normalized = beispiel.lower().strip()
            text_lower = text.lower()
            
            # Exakte Suche
            if beispiel_normalized in text_lower:
                start = text_lower.find(beispiel_normalized)
                end = start + len(beispiel_normalized)
                
                match = MarkerMatch(
                    marker_name=marker_data['marker'],
                    marker_beschreibung=marker_data.get('beschreibung', ''),
                    matched_text=text[start:end],
                    position=(start, end),
                    confidence_score=1.0,
                    kontext=self._extract_context(text, start, end),
                    pattern_type='exact',
                    tags=marker_data.get('tags', []),
                    risk_score=marker_data.get('risk_score', 1)
                )
                matches.append(match)
            
            # Fuzzy-Matching für teilweise Übereinstimmungen
            elif self._fuzzy_match(beispiel_normalized, text_lower):
                # Vereinfachtes Fuzzy-Matching
                words = beispiel_normalized.split()
                if len(words) > 2 and sum(1 for w in words if w in text_lower) >= len(words) * 0.7:
                    match = MarkerMatch(
                        marker_name=marker_data['marker'],
                        marker_beschreibung=marker_data.get('beschreibung', ''),
                        matched_text=beispiel[:50] + '...',
                        position=(0, 0),
                        confidence_score=0.7,
                        pattern_type='fuzzy',
                        tags=marker_data.get('tags', []),
                        risk_score=marker_data.get('risk_score', 1)
                    )
                    matches.append(match)
        
        # Semantische Patterns (falls vorhanden)
        if 'semantic_patterns' in marker_data:
            semantic_matches = self._apply_semantic_patterns(text, marker_data)
            matches.extend(semantic_matches)
        
        return matches
    
    def _fuzzy_match(self, pattern: str, text: str) -> bool:
        """Einfaches Fuzzy-Matching"""
        # Sehr vereinfachte Version - kann erweitert werden
        words = pattern.split()
        return len(words) > 2 and sum(1 for w in words if w in text) >= len(words) * 0.6
    
    def _apply_semantic_patterns(self, text: str, marker_data: Dict[str, Any]) -> List[MarkerMatch]:
        """Wendet semantische Patterns an (falls definiert)"""
        matches = []
        semantic_data = marker_data.get('semantic_patterns', {})
        
        if 'patterns' in semantic_data:
            for pattern_rule in semantic_data['patterns']:
                if 'pattern' in pattern_rule:
                    try:
                        # Kompiliere Regex-Pattern
                        regex = re.compile(pattern_rule['pattern'], re.IGNORECASE)
                        
                        for match in regex.finditer(text):
                            marker_match = MarkerMatch(
                                marker_name=marker_data['marker'],
                                marker_beschreibung=marker_data.get('beschreibung', ''),
                                matched_text=match.group(0),
                                position=(match.start(), match.end()),
                                confidence_score=0.9,
                                kontext=self._extract_context(text, match.start(), match.end()),
                                pattern_type='semantic',
                                tags=marker_data.get('tags', []),
                                risk_score=marker_data.get('risk_score', 1)
                            )
                            matches.append(marker_match)
                    except Exception as e:
                        logger.debug(f"Fehler bei Regex-Pattern: {e}")
        
        return matches
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Extrahiert Kontext um einen Match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        
        context = text[context_start:context_end]
        
        # Markiere den gefundenen Text
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."
            
        return context
    
    def _calculate_risk_level(self, total_score: int, marker_count: int) -> Tuple[str, str]:
        """Berechnet das Risiko-Level basierend auf Score und Anzahl"""
        # Berücksichtige sowohl Score als auch Anzahl
        adjusted_score = total_score + (marker_count * 0.5)
        
        for level, (min_score, max_score) in self.risk_thresholds.items():
            if min_score <= adjusted_score <= max_score:
                return level, self._get_color_for_level(level)
        
        # Fallback falls kein Level passt (z.B. bei sehr hohem Score)
        if adjusted_score > self.risk_thresholds.get('red', (11, 0))[0]:
             return 'red', self._get_color_for_level('red')

        return 'undefined', '#808080'
    
    def _get_color_for_level(self, level: str) -> str:
        """Gibt die Farbe für ein Risk-Level zurück"""
        colors = {
            'green': '#00FF00',
            'yellow': '#FFFF00',
            'blinking': '#FFA500',  # Orange für "blinkend"
            'red': '#FF0000'
        }
        return colors.get(level, '#808080')
    
    def _generate_summary(self, matches: List[MarkerMatch], risk_level: str) -> str:
        """Generiert eine Zusammenfassung der Analyse"""
        if not matches:
            return "Keine kritischen Marker gefunden. Die Kommunikation erscheint neutral."
        
        # Zähle Marker-Typen
        marker_types = defaultdict(int)
        for match in matches:
            marker_types[match.marker_name] += 1
        
        # Top 3 Marker
        top_markers = sorted(marker_types.items(), key=lambda x: x[1], reverse=True)[:3]
        
        summary = f"Risiko-Level: {risk_level.upper()}\n"
        summary += f"Gefundene Marker: {len(matches)}\n"
        summary += f"Häufigste Muster: "
        summary += ", ".join([f"{name} ({count}x)" for name, count in top_markers])
        
        # Füge spezifische Warnungen hinzu
        if risk_level in ['blinking', 'red']:
            summary += "\n⚠️ WARNUNG: Deutliche Anzeichen für manipulative Kommunikation erkannt!"
        
        return summary
    
    def analyze_batch(self, texts: List[str]) -> List[AnalysisResult]:
        """Analysiert mehrere Texte"""
        results = []
        for text in texts:
            results.append(self.analyze_text(text))
        return results


def main_v2_demo():
    """Demo-Funktion für MarkerMatcherV2"""
    # 1. Lade ein Beispiel-Schema
    schema_path = Path(__file__).parent.parent / 'analysis_schemas/templates/template_generic_analysis.json'
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            # Beispiel-Schema anpassen, um Marker zu inkludieren
            schema = json.load(f)
            schema['marker_config']['atomic_markers'] = [
                {'id': 'GASLIGHTING_MARKER', 'scoring.weight': 2.0},
                {'id': 'LOVE_BOMBING_MARKER', 'scoring.weight': 1.5}
            ]
            schema['scoring_config']['risk_thresholds'] = {
                 'green': (0, 1), 'yellow': (2, 6), 'blinking': (7, 12), 'red': (13, float('inf'))
            }
            print(f"Lade Demo-Schema: {schema['schema_info']['name']}")
    except FileNotFoundError:
        print(f"Demo-Schema nicht gefunden unter {schema_path}. Führe ohne Schema aus.")
        schema = None
    
    # 2. Erstelle Matcher mit dem Schema
    matcher = MarkerMatcherV2(schema_config=schema)
    
    # 3. Test-Texte
    test_texts = [
        "Das hast du dir nur eingebildet. Ich habe nie gesagt, dass ich mitkomme.",
        "Ich liebe dich über alles! Du bist meine Seelenverwandte. Niemand versteht mich so wie du.",
        "Ich bin hin- und hergerissen zwischen Bleiben und Gehen – ich weiß nicht mehr weiter.",
        "Hey, wie geht's dir? Schönes Wetter heute, nicht wahr?",
        "Du bist zu empfindlich. Das war doch nur ein Scherz. Du übertreibst mal wieder."
    ]
    
    print("\nMARKER MATCHER V2 - DEMO")
    print("="*60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nText {i}: {text[:50]}...")
        result = matcher.analyze_text(text)
        
        print(f"Risk-Level: {result.risk_level} ({result.risk_level_color})")
        print(f"Total Risk Score: {result.total_risk_score}")
        print(f"Gefundene Marker: {len(result.gefundene_marker)}")
        
        for match in result.gefundene_marker:
            print(f"  - {match.marker_name} (Gewichteter Score: {match.risk_score})")
        
        print(f"\nZusammenfassung:\n{result.summary}")
        print("-"*60)


if __name__ == "__main__":
    main_v2_demo() 