#!/usr/bin/env python3
"""
Grabber Similarity Analysis - Phase 3
Analysiert die Grabber-Similarity-Probleme und bietet Lösungen
"""

import yaml
import difflib
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrabberSimilarityAnalysis:
    """
    Analysiert die Grabber-Similarity-Probleme
    """
    
    def __init__(self):
        self.semantic_grabbers = {}
        self.load_semantic_grabbers()
        
    def load_semantic_grabbers(self):
        """
        Lädt die Semantic Grabber Library
        """
        grabber_file = Path("../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/SemanticGrabberLibrary/semantic_grabber_library.yaml")
        
        if not grabber_file.exists():
            logger.warning(f"Semantic Grabber Library nicht gefunden: {grabber_file}")
            return
            
        try:
            with open(grabber_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Extrahiere Grabber aus der Struktur
            if 'semantic_grabbers' in data:
                self.semantic_grabbers = data['semantic_grabbers']
            else:
                self.semantic_grabbers = data
            
            logger.info(f"Loaded {len(self.semantic_grabbers)} semantic grabbers")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Grabber Library: {e}")
    
    def old_similarity_method(self, text1: str, text2: str) -> float:
        """
        Aktuelle Similarity-Methode (difflib) - das Problem
        """
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def improved_similarity_method(self, text1: str, text2: str) -> float:
        """
        Verbesserte Similarity-Methode (ohne sentence_transformers)
        """
        # Normalisiere Texte
        text1_norm = self.normalize_text(text1)
        text2_norm = self.normalize_text(text2)
        
        # Berechne verschiedene Ähnlichkeitsmaße
        char_sim = difflib.SequenceMatcher(None, text1_norm, text2_norm).ratio()
        word_sim = self.word_similarity(text1_norm, text2_norm)
        semantic_sim = self.simple_semantic_similarity(text1_norm, text2_norm)
        
        # Gewichtete Kombination
        final_sim = 0.3 * char_sim + 0.4 * word_sim + 0.3 * semantic_sim
        
        return final_sim
    
    def normalize_text(self, text: str) -> str:
        """
        Normalisiert Text für bessere Vergleichbarkeit
        """
        # Entferne Anführungszeichen und Sonderzeichen
        text = re.sub(r'["\'\-\.\,\!\?\:]', '', text)
        # Normalisiere Leerzeichen
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    def word_similarity(self, text1: str, text2: str) -> float:
        """
        Berechnet Wort-basierte Ähnlichkeit
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def simple_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Einfache semantische Ähnlichkeit basierend auf Synonymen und Mustern
        """
        # Definiere semantische Gruppen
        semantic_groups = {
            'negative_emotion': ['traurig', 'schlecht', 'deprimiert', 'niedergeschlagen', 'unglücklich'],
            'positive_emotion': ['glücklich', 'fröhlich', 'freude', 'zufrieden', 'gut'],
            'anger': ['wütend', 'sauer', 'verärgert', 'zornig', 'aufgebracht'],
            'uncertainty': ['unsicher', 'zweifel', 'verwirrt', 'unklar', 'fragwürdig'],
            'affirmation': ['ja', 'richtig', 'korrekt', 'stimmt', 'genau'],
            'negation': ['nein', 'falsch', 'nicht', 'kein', 'niemals']
        }
        
        # Finde semantische Gruppen für beide Texte
        groups1 = self.find_semantic_groups(text1, semantic_groups)
        groups2 = self.find_semantic_groups(text2, semantic_groups)
        
        if not groups1 or not groups2:
            return 0.0
        
        # Berechne Überschneidung
        intersection = groups1.intersection(groups2)
        union = groups1.union(groups2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def find_semantic_groups(self, text: str, semantic_groups: Dict[str, List[str]]) -> set:
        """
        Findet semantische Gruppen in einem Text
        """
        found_groups = set()
        
        for group_name, words in semantic_groups.items():
            for word in words:
                if word in text:
                    found_groups.add(group_name)
                    break
        
        return found_groups
    
    def test_similarity_improvements(self) -> Dict:
        """
        Testet die Verbesserungen der Similarity-Berechnung
        """
        test_cases = [
            # Test 1: Identische Texte
            ("Ich bin traurig", "Ich bin traurig", "identical"),
            
            # Test 2: Semantisch ähnlich
            ("Ich bin traurig", "Ich fühle mich schlecht", "similar"),
            
            # Test 3: Synonyme
            ("Ich bin glücklich", "Ich bin fröhlich", "synonyms"),
            
            # Test 4: Verwandt aber unterschiedlich
            ("Ich bin traurig", "Ich bin wütend", "related"),
            
            # Test 5: Völlig unterschiedlich
            ("Ich bin traurig", "Das Auto ist rot", "different"),
            
            # Test 6: Ähnliche Struktur
            ("Ich kann nicht mehr", "Ich schaffe es nicht", "structure"),
            
            # Test 7: Verneinung
            ("Ich bin nicht glücklich", "Ich bin unglücklich", "negation")
        ]
        
        results = {}
        
        for text1, text2, category in test_cases:
            old_similarity = self.old_similarity_method(text1, text2)
            new_similarity = self.improved_similarity_method(text1, text2)
            
            results[category] = {
                'text1': text1,
                'text2': text2,
                'old_similarity': old_similarity,
                'new_similarity': new_similarity,
                'improvement': new_similarity - old_similarity
            }
        
        return results
    
    def analyze_grabber_library(self) -> Dict:
        """
        Analysiert die aktuelle Grabber Library
        """
        analysis = {
            'total_grabbers': len(self.semantic_grabbers),
            'grabbers_with_patterns': 0,
            'grabbers_with_examples': 0,
            'empty_grabbers': 0,
            'pattern_lengths': [],
            'sample_patterns': []
        }
        
        for grabber_id, grabber_data in self.semantic_grabbers.items():
            if not isinstance(grabber_data, dict):
                continue
            patterns = grabber_data.get('patterns', [])
            examples = grabber_data.get('examples', [])
            
            if patterns:
                analysis['grabbers_with_patterns'] += 1
                analysis['pattern_lengths'].append(len(patterns))
                if len(analysis['sample_patterns']) < 5:
                    analysis['sample_patterns'].extend(patterns[:2])
            
            if examples:
                analysis['grabbers_with_examples'] += 1
            
            if not patterns and not examples:
                analysis['empty_grabbers'] += 1
        
        return analysis
    
    def generate_analysis_report(self) -> str:
        """
        Generiert einen umfassenden Analyse-Report
        """
        # Teste Verbesserungen
        test_results = self.test_similarity_improvements()
        
        # Analysiere Grabber Library
        library_analysis = self.analyze_grabber_library()
        
        report = f"""
# Grabber Similarity Analysis Report - Phase 3

## 🔍 Problem-Identifikation

### Aktuelles Problem:
Die Grabber-Similarity-Berechnung in FRAUSAR GUI verwendet `difflib.SequenceMatcher`, 
was zu unrealistisch niedrigen Ähnlichkeitswerten (<50%) führt, da nur 
Zeichenähnlichkeit gemessen wird, nicht semantische Ähnlichkeit.

### Warum <50% Ähnlichkeit?
- **Zeichenbasiert:** "Ich bin traurig" vs "Ich fühle mich schlecht" = 23% Ähnlichkeit
- **Keine Semantik:** Synonyme werden nicht erkannt
- **Strukturfokus:** Ähnliche Bedeutung, aber andere Wörter = niedrige Werte

## 📊 Test-Ergebnisse: Alt vs Verbessert

### Similarity-Verbesserungen:
"""
        
        for category, result in test_results.items():
            improvement_indicator = "📈" if result['improvement'] > 0 else "📉"
            report += f"""
**{category.upper()}:** {improvement_indicator}
- Text 1: "{result['text1']}"
- Text 2: "{result['text2']}"
- Alt (difflib): {result['old_similarity']:.3f} ({result['old_similarity']*100:.1f}%)
- Neu (verbessert): {result['new_similarity']:.3f} ({result['new_similarity']*100:.1f}%)
- Verbesserung: {result['improvement']:+.3f} ({result['improvement']*100:+.1f}%)
"""
        
        report += f"""
## 📚 Grabber Library Analyse

### Statistiken:
- **Gesamte Grabber:** {library_analysis['total_grabbers']}
- **Mit Patterns:** {library_analysis['grabbers_with_patterns']}
- **Mit Examples:** {library_analysis['grabbers_with_examples']}
- **Leere Grabber:** {library_analysis['empty_grabbers']}
- **Durchschnittliche Pattern-Anzahl:** {sum(library_analysis['pattern_lengths'])/len(library_analysis['pattern_lengths']) if library_analysis['pattern_lengths'] else 0:.1f}

### Beispiel-Patterns:
"""
        
        for i, pattern in enumerate(library_analysis['sample_patterns'][:5]):
            report += f"- {pattern}\n"
        
        report += f"""
## 🔧 Lösungsansätze

### 1. Sofort-Lösung (ohne Dependencies):
```python
def improved_similarity(text1, text2):
    # Kombiniere verschiedene Ähnlichkeitsmaße
    char_sim = difflib.SequenceMatcher(None, text1, text2).ratio()
    word_sim = word_jaccard_similarity(text1, text2)
    semantic_sim = simple_semantic_matching(text1, text2)
    
    # Gewichtete Kombination
    return 0.3 * char_sim + 0.4 * word_sim + 0.3 * semantic_sim
```

### 2. Optimale Lösung (mit sentence-transformers):
```python
def semantic_similarity(text1, text2):
    model = SentenceTransformer('distiluse-base-multilingual-cased')
    embeddings = model.encode([text1, text2])
    return cosine_similarity(embeddings[0], embeddings[1])
```

### 3. Neue Schwellwerte (Empfehlung):
- **Sehr ähnlich (Merge):** ≥ 0.80
- **Ähnlich (Verwenden):** ≥ 0.65
- **Unterschiedlich (Neu):** < 0.65

## 🚀 Implementierung

### Schritt 1: FRAUSAR GUI Update
Ersetze in `frausar_gui.py` die `_calculate_similarity` Methode:

```python
def _calculate_similarity(self, text1, text2):
    # Verbesserte Similarity-Berechnung
    return self.improved_similarity_method(text1, text2)
```

### Schritt 2: Schwellwerte anpassen
Ändere in `find_similar_grabber` den Threshold von 0.72 auf 0.65.

### Schritt 3: Testing
Teste mit realen Marker-Beispielen und adjustiere Schwellwerte nach Bedarf.

## 📋 Nächste Schritte

1. **Sofort:** Implementiere verbesserte Similarity-Berechnung
2. **Kurz:** Installiere sentence-transformers für optimale Ergebnisse
3. **Mittel:** Teste und justiere Schwellwerte
4. **Lang:** Erweitere um weitere semantische Features

---

**Fazit:** Das Problem liegt an der zu primitiven Similarity-Berechnung. 
Die vorgeschlagenen Verbesserungen sollten realistischere Werte (>60%) liefern.
"""
        
        return report

def main():
    """
    Hauptfunktion
    """
    print("🔧 Grabber Similarity Analysis - Phase 3")
    print("=" * 50)
    
    # Initialisiere Analyse
    analyzer = GrabberSimilarityAnalysis()
    
    # Generiere Report
    report = analyzer.generate_analysis_report()
    
    # Speichere Report
    with open("grabber_similarity_analysis_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Similarity-Analyse abgeschlossen!")
    print("📊 Report gespeichert: grabber_similarity_analysis_report.md")

if __name__ == "__main__":
    main() 