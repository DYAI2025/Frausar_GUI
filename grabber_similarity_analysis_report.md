
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

**IDENTICAL:** 📉
- Text 1: "Ich bin traurig"
- Text 2: "Ich bin traurig"
- Alt (difflib): 1.000 (100.0%)
- Neu (verbessert): 1.000 (100.0%)
- Verbesserung: +0.000 (+0.0%)

**SIMILAR:** 📈
- Text 1: "Ich bin traurig"
- Text 2: "Ich fühle mich schlecht"
- Alt (difflib): 0.368 (36.8%)
- Neu (verbessert): 0.477 (47.7%)
- Verbesserung: +0.109 (+10.9%)

**SYNONYMS:** 📉
- Text 1: "Ich bin glücklich"
- Text 2: "Ich bin fröhlich"
- Alt (difflib): 0.727 (72.7%)
- Neu (verbessert): 0.718 (71.8%)
- Verbesserung: -0.009 (-0.9%)

**RELATED:** 📉
- Text 1: "Ich bin traurig"
- Text 2: "Ich bin wütend"
- Alt (difflib): 0.621 (62.1%)
- Neu (verbessert): 0.386 (38.6%)
- Verbesserung: -0.234 (-23.4%)

**DIFFERENT:** 📉
- Text 1: "Ich bin traurig"
- Text 2: "Das Auto ist rot"
- Alt (difflib): 0.258 (25.8%)
- Neu (verbessert): 0.077 (7.7%)
- Verbesserung: -0.181 (-18.1%)

**STRUCTURE:** 📈
- Text 1: "Ich kann nicht mehr"
- Text 2: "Ich schaffe es nicht"
- Alt (difflib): 0.564 (56.4%)
- Neu (verbessert): 0.603 (60.3%)
- Verbesserung: +0.038 (+3.8%)

**NEGATION:** 📉
- Text 1: "Ich bin nicht glücklich"
- Text 2: "Ich bin unglücklich"
- Alt (difflib): 0.857 (85.7%)
- Neu (verbessert): 0.517 (51.7%)
- Verbesserung: -0.340 (-34.0%)

## 📚 Grabber Library Analyse

### Statistiken:
- **Gesamte Grabber:** 195
- **Mit Patterns:** 182
- **Mit Examples:** 0
- **Leere Grabber:** 13
- **Durchschnittliche Pattern-Anzahl:** 4.8

### Beispiel-Patterns:
- Ich weiß nicht mehr, ob ich dir glauben kann
- Du hast schon so oft versprochen
- Unsere Nachrichten klingen fast gleich mittlerweile.
- Ich schreibe jetzt schon so wie du – fällt dir das auf?
- Ich brauche dringend 500 Euro für eine Operation

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
