import re

def detect_emo_contrast_drift(text: str):
    """
    Detects the S_EMO_CONTRAST_DRIFT marker by finding sentences
    with a clear pivot from a positive/certain state to a negative/uncertain one.
    """
    certainty = r"(ich weiß|i know|ich bin (mir )?sicher|i am sure|normalerweise|eigentlich|usually|grundsätzlich)"
    uncertainty = r"(weiß (ich )?nicht|i don't know|unsicher|not sure|keine Ahnung|habe Angst|feel scared)"
    contrast = r"\b(aber|jedoch|andererseits|but|however)\b"
    
    # Pattern: [Certainty Phrase] , [Contrast Conjunction] , [Uncertainty Phrase]
    pattern_full = re.compile(f"({certainty}).*({contrast}).*({uncertainty})", re.IGNORECASE)

    # Pattern for positive vs. negative adjectives
    pos_adj = r"\b(stark|glücklich|gut|unabhängig|strong|happy|good|independent)\b"
    neg_adj = r"\b(schwach|verletzt|klein|ängstlich|weak|hurt|small|afraid)\b"
    pattern_adjectives = re.compile(f"({pos_adj}).*({contrast}).*({neg_adj})", re.IGNORECASE)

    matches = []
    if re.search(pattern_full, text):
        matches.append({"marker": "S_EMO_CONTRAST_DRIFT", "rule": "certainty_uncertainty_pivot", "snippet": re.search(pattern_full, text).group(0)})
    if re.search(pattern_adjectives, text):
        matches.append({"marker": "S_EMO_CONTRAST_DRIFT", "rule": "adjective_contrast", "snippet": re.search(pattern_adjectives, text).group(0)})
        
    return matches if matches else None

# Example Usage:
text1 = "I usually know what I want, but in this situation, I don't know."
text2 = "Einerseits fühle ich mich stark, aber andererseits bin ich auch sehr verletzlich."
print(f"Analysis for text1: {detect_emo_contrast_drift(text1)}")
print(f"Analysis for text2: {detect_emo_contrast_drift(text2)}")