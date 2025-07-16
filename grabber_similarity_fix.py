#!/usr/bin/env python3
"""
Grabber Similarity Fix - Phase 3
Verbessert die Grabber-Similarity-Berechnung mit semantischen Embeddings
"""

import yaml
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
import logging
from typing import List, Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedGrabberSimilarity:
    """
    Verbesserte Grabber-Similarity-Berechnung mit semantischen Embeddings
    """
    
    def __init__(self, model_name: str = 'distiluse-base-multilingual-cased'):
        self.model = SentenceTransformer(model_name)
        self.semantic_grabbers = {}
        self.embeddings_cache = {}
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
                self.semantic_grabbers = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(self.semantic_grabbers)} semantic grabbers")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Grabber Library: {e}")
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Berechnet Embedding für Text mit Caching
        """
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        embedding = self.model.encode(text, convert_to_tensor=False)
        self.embeddings_cache[text] = embedding
        return embedding
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Berechnet semantische Ähnlichkeit zwischen zwei Texten
        """
        try:
            embedding1 = self.get_text_embedding(text1)
            embedding2 = self.get_text_embedding(text2)
            
            # Cosine Similarity
            similarity = util.cos_sim(embedding1, embedding2).item()
            return max(0.0, min(1.0, similarity))  # Clamp zwischen 0 und 1
        except Exception as e:
            logger.error(f"Fehler bei Similarity-Berechnung: {e}")
            return 0.0
    
    def calculate_examples_similarity(self, examples1: List[str], examples2: List[str]) -> float:
        """
        Berechnet Ähnlichkeit zwischen zwei Listen von Beispielen
        """
        if not examples1 or not examples2:
            return 0.0
        
        # Berechne alle paarweisen Ähnlichkeiten
        similarities = []
        
        for ex1 in examples1[:5]:  # Limitiere für Performance
            for ex2 in examples2[:5]:
                sim = self.calculate_semantic_similarity(ex1, ex2)
                similarities.append(sim)
        
        if not similarities:
            return 0.0
        
        # Verwende durchschnittliche Ähnlichkeit
        avg_similarity = np.mean(similarities)
        
        # Bonus für hohe Maximalwerte (beste Übereinstimmung)
        max_similarity = np.max(similarities)
        
        # Gewichtete Kombination: 70% Durchschnitt, 30% Maximum
        final_similarity = 0.7 * avg_similarity + 0.3 * max_similarity
        
        return final_similarity
    
    def find_similar_grabber(self, examples: List[str], threshold: float = 0.6) -> Tuple[Optional[str], float]:
        """
        Findet ähnlichen Grabber basierend auf Beispielen (verbesserte Version)
        """
        if not examples:
            return None, 0.0
        
        best_match = None
        best_score = 0.0
        
        for grabber_id, grabber_data in self.semantic_grabbers.items():
            # Unterstütze sowohl 'patterns' als auch 'examples'
            grabber_examples = grabber_data.get('patterns', grabber_data.get('examples', []))
            
            if not grabber_examples:
                continue
            
            # Berechne semantische Ähnlichkeit
            similarity = self.calculate_examples_similarity(examples, grabber_examples)
            
            if similarity > best_score:
                best_score = similarity
                best_match = grabber_id
        
        if best_score >= threshold:
            return best_match, best_score
        
        return None, best_score
    
    def analyze_all_grabber_similarities(self, threshold: float = 0.75) -> List[Dict]:
        """
        Analysiert Ähnlichkeiten zwischen allen Grabbern
        """
        grabber_ids = list(self.semantic_grabbers.keys())
        similarities = []
        
        for i, id1 in enumerate(grabber_ids):
            for id2 in grabber_ids[i+1:]:
                examples1 = self.semantic_grabbers[id1].get('patterns', 
                           self.semantic_grabbers[id1].get('examples', []))
                examples2 = self.semantic_grabbers[id2].get('patterns',
                           self.semantic_grabbers[id2].get('examples', []))
                
                if examples1 and examples2:
                    similarity = self.calculate_examples_similarity(examples1, examples2)
                    
                    if similarity >= threshold:
                        similarities.append({
                            'grabber1': id1,
                            'grabber2': id2,
                            'similarity': similarity,
                            'recommendation': 'merge' if similarity > 0.85 else 'review'
                        })
        
        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)
    
    def test_similarity_improvements(self) -> Dict:
        """
        Testet die Verbesserungen der Similarity-Berechnung
        """
        test_cases = [
            # Test 1: Identische Texte
            ("Ich bin traurig", "Ich bin traurig", "identical"),
            
            # Test 2: Semantisch ähnlich
            ("Ich bin traurig", "Ich fühle mich schlecht", "similar"),
            
            # Test 3: Verwandt aber unterschiedlich
            ("Ich bin traurig", "Ich bin wütend", "related"),
            
            # Test 4: Völlig unterschiedlich
            ("Ich bin traurig", "Das Auto ist rot", "different"),
            
            # Test 5: Synonyme
            ("Ich bin glücklich", "Ich bin fröhlich", "synonyms")
        ]
        
        results = {}
        
        for text1, text2, category in test_cases:
            old_similarity = self._old_similarity_method(text1, text2)
            new_similarity = self.calculate_semantic_similarity(text1, text2)
            
            results[category] = {
                'text1': text1,
                'text2': text2,
                'old_similarity': old_similarity,
                'new_similarity': new_similarity,
                'improvement': new_similarity - old_similarity
            }
        
        return results
    
    def _old_similarity_method(self, text1: str, text2: str) -> float:
        """
        Alte Similarity-Methode mit difflib für Vergleich
        """
        import difflib
        return difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def generate_fix_report(self) -> str:
        """
        Generiert einen Report über die Similarity-Verbesserungen
        """
        # Teste Verbesserungen
        test_results = self.test_similarity_improvements()
        
        # Analysiere Grabber-Ähnlichkeiten
        grabber_similarities = self.analyze_all_grabber_similarities()
        
        report = f"""
# Grabber Similarity Fix Report - Phase 3

## Problem
Die ursprüngliche Similarity-Berechnung verwendete `difflib.SequenceMatcher`, 
was zu unrealistisch niedrigen Werten (<50%) führte, da nur Zeichenähnlichkeit 
gemessen wurde, nicht semantische Ähnlichkeit.

## Lösung
Implementierung von semantischen Embeddings mit SentenceTransformer:
- Modell: distiluse-base-multilingual-cased
- Cosine Similarity zwischen Embeddings
- Gewichtete Kombination aus Durchschnitt und Maximum

## Test-Ergebnisse

### Verbesserungen der Similarity-Werte:
"""
        
        for category, result in test_results.items():
            report += f"""
**{category.upper()}:**
- Text 1: "{result['text1']}"
- Text 2: "{result['text2']}"
- Alt (difflib): {result['old_similarity']:.3f}
- Neu (semantic): {result['new_similarity']:.3f}
- Verbesserung: {result['improvement']:+.3f}
"""
        
        report += f"""
## Grabber-Ähnlichkeiten (Threshold: 0.75)
Gefunden: {len(grabber_similarities)} ähnliche Grabber-Paare

"""
        
        for sim in grabber_similarities[:10]:  # Top 10
            report += f"""
- **{sim['grabber1']}** ↔ **{sim['grabber2']}**
  - Ähnlichkeit: {sim['similarity']:.3f}
  - Empfehlung: {sim['recommendation']}
"""
        
        report += f"""
## Neue Schwellwerte (Empfehlung)
- **Sehr ähnlich (Merge):** ≥ 0.85
- **Ähnlich (Verwenden):** ≥ 0.70
- **Unterschiedlich (Neu):** < 0.70

## Implementierung
Die verbesserte Similarity-Berechnung kann in die FRAUSAR GUI integriert werden,
indem die `_calculate_similarity` Methode ersetzt wird.
"""
        
        return report

def main():
    """
    Hauptfunktion
    """
    print("🔧 Grabber Similarity Fix - Phase 3")
    print("=" * 50)
    
    # Initialisiere verbesserte Similarity
    similarity_fixer = ImprovedGrabberSimilarity()
    
    # Generiere Report
    report = similarity_fixer.generate_fix_report()
    
    # Speichere Report
    with open("grabber_similarity_fix_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✅ Similarity-Analyse abgeschlossen!")
    print("📊 Report gespeichert: grabber_similarity_fix_report.md")

if __name__ == "__main__":
    main() 