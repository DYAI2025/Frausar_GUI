# 🎭 Emotionale Dynamikdetektion - Iterationsplan

**Projektname:** EmotionDynamics Integration für FRAUSAR  
**Erstellt am:** 21.07.2025  
**Version:** 1.0  

---

## 📋 **ÜBERBLICK**

### **Zielsetzung:**
Implementierung zeitlich sensitiver Emotionserkennung pro Sprecher zur Verfeinerung der Markerresonanz und Auffindung subtiler Dynamiken im Verlauf.

### **Integrationsebene:**
- **Ort:** `detectors/emotion_dynamics_detector.py`
- **Format:** Python-Modul im Stil bestehender Detektoren (DETECT_[NAME].py)
- **Integration:** Vollständige Einbindung in bestehendes FRAUSAR-Schema

---

## 🎯 **DETAILLIERTER ITERATIONSPLAN**

### **PHASE 1: Foundation & Setup** ⏱️ 2-3 Stunden

#### **Task 1.1: Umgebungsanalyse und Dependencies** (30 min)
- ✅ **Analysiert:** Aktuelle DETECT.py Struktur verstanden
- ✅ **Evaluiert:** Bestehende Marker-Integration-Patterns
- 🔄 **TODO:** EmotionDynamics/uedLib.py Requirements prüfen
- 🔄 **TODO:** NRC VAD/EmoLex Verfügbarkeit validieren

#### **Task 1.2: Verzeichnisstruktur erstellen** (15 min)
```
detectors/
├── emotion_dynamics_detector.py      # Hauptdetektor
├── emotion_utils/                    # Hilfsfunktionen
│   ├── __init__.py
│   ├── vad_calculator.py             # VAD-Berechnungen
│   ├── movement_metrics.py           # Slope, Variance, etc.
│   └── emotion_models.py             # Datenmodelle
└── tests/
    └── test_emotion_dynamics.py      # Unit Tests
```

#### **Task 1.3: Basis-Dependencies installieren** (30 min)
- NRC VAD Lexicon vorbereiten
- SentenceTransformers (falls nötig)
- NumPy, SciPy für mathematische Berechnungen
- Requirements.txt erweitern

#### **Task 1.4: Template-Erstellung** (45 min)
- DETECT_EMOTION_DYNAMICS.py Grundstruktur
- BaseDetector-Klasse als Vorlage verwenden
- Schema-Integration vorbereiten

---

### **PHASE 2: Core Emotion Engine** ⏱️ 4-5 Stunden

#### **Task 2.1: VAD-Berechnungsmodul** (2 Stunden)
```python
# emotion_utils/vad_calculator.py

class VADCalculator:
    def __init__(self, nrc_vad_path):
        self.load_nrc_vad_lexicon(nrc_vad_path)
    
    def calculate_text_vad(self, text: str) -> Dict[str, float]:
        """Berechnet Valenz, Erregung, Dominanz für Text"""
        # Tokenization + NRC VAD Lookup
        # Gewichteter Durchschnitt
        return {"valence": 0.0, "arousal": 0.0, "dominance": 0.0}
    
    def calculate_speaker_vad_sequence(self, messages: List[Dict]) -> List[Dict]:
        """VAD-Zeitreihe pro Sprecher"""
        pass
```

#### **Task 2.2: Bewegungsmetriken-Modul** (1.5 Stunden)
```python
# emotion_utils/movement_metrics.py

def calculate_slope(values: List[float], timestamps: List[datetime]) -> float:
    """Linear regression slope über Zeitachse"""
    
def calculate_variance(values: List[float]) -> float:
    """Emotionale Volatilität"""
    
def calculate_displacement(start_val: float, end_val: float) -> float:
    """Gesamtverschiebung"""
    
def calculate_volatility(values: List[float], window_size: int = 3) -> float:
    """Rolling-window Volatilität"""
```

#### **Task 2.3: Datenmodelle definieren** (30 min)
```python
# emotion_utils/emotion_models.py

@dataclass
class EmotionPoint:
    timestamp: datetime
    speaker: str
    valence: float
    arousal: float
    dominance: float
    text: str
    
@dataclass
class EmotionDynamics:
    speaker: str
    window_start: datetime
    window_end: datetime
    valence_slope: float
    arousal_slope: float
    dominance_slope: float
    volatility: float
    displacement: float
    marker_triggered: Optional[str] = None
```

#### **Task 2.4: Testing Foundation** (1 Stunde)
- Unit Tests für VAD-Berechnungen
- Mock-Daten für Testing
- Baseline-Performance-Tests

---

### **PHASE 3: Detector Implementation** ⏱️ 3-4 Stunden

#### **Task 3.1: DETECT_EMOTION_DYNAMICS Klasse** (2 Stunden)
```python
# detectors/emotion_dynamics_detector.py

import re
from typing import Dict, List
from datetime import datetime, timedelta
from .emotion_utils.vad_calculator import VADCalculator
from .emotion_utils.movement_metrics import *

DETECT_EMOTION_DYNAMICS_COMPONENTS = {
    "EMO_SLOPE_UP": ["steigender Emotionstrend"],
    "EMO_SLOPE_DOWN": ["fallender Emotionstrend"], 
    "EMO_VOLATILE": ["emotionale Volatilität"],
    "EMO_CONTRAST_DRIFT": ["emotionaler Kontrastwechsel"]
}

def detect_emotion_dynamics(conversation_chunk: List[Dict], 
                           window_minutes: int = 30,
                           min_messages: int = 5) -> Dict:
    """
    Hauptdetektor für emotionale Dynamiken
    
    Args:
        conversation_chunk: Liste von Nachrichten mit ts, speaker, text, markers
        window_minutes: Zeitfenster in Minuten
        min_messages: Mindestanzahl Nachrichten pro Sprecher
    
    Returns:
        Dict mit erkannten emotionalen Markern
    """
    
    results = {
        "is_detected": False,
        "emotion_markers": [],
        "speaker_dynamics": {},
        "confidence_score": 0.0
    }
    
    # Gruppiere nach Sprecher
    speaker_messages = group_by_speaker(conversation_chunk)
    
    for speaker, messages in speaker_messages.items():
        if len(messages) < min_messages:
            continue
            
        # VAD-Sequenz berechnen
        vad_sequence = calculate_vad_sequence(messages)
        
        # Bewegungsmetriken
        dynamics = analyze_emotion_movement(vad_sequence, window_minutes)
        
        # Trigger-Logik
        triggered_markers = check_trigger_conditions(dynamics)
        
        if triggered_markers:
            results["is_detected"] = True
            results["emotion_markers"].extend(triggered_markers)
            results["speaker_dynamics"][speaker] = dynamics
    
    return results

# Trigger-Schwellwerte
SLOPE_THRESHOLD = 0.15
VOLATILITY_THRESHOLD = 0.5
CONTRAST_THRESHOLD = 1.2

def check_trigger_conditions(dynamics: EmotionDynamics) -> List[str]:
    """Prüft welche emotionalen Marker ausgelöst werden"""
    markers = []
    
    # Steigender Trend
    if dynamics.valence_slope > SLOPE_THRESHOLD:
        markers.append("EMO_SLOPE_UP")
    
    # Fallender Trend  
    if dynamics.valence_slope < -SLOPE_THRESHOLD:
        markers.append("EMO_SLOPE_DOWN")
        
    # Hohe Volatilität
    if dynamics.volatility > VOLATILITY_THRESHOLD:
        markers.append("EMO_VOLATILE_WINDOW")
        
    # Kontrastwechsel
    if abs(dynamics.displacement) > CONTRAST_THRESHOLD:
        markers.append("EMO_CONTRAST_DRIFT")
    
    return markers
```

#### **Task 3.2: Integration in Marker-System** (1 Stunde)
- Schema-Update für neue Emotion-Marker
- Integration in DETECT_default_marker_schema.yaml
- Verbindung zu bestehenden Markern

#### **Task 3.3: Rollierende Anwendung** (1 Stunde)
- Zeitbasierte Trigger (alle X Minuten/Nachrichten)
- Integration in marker_matcher Pipeline
- Kompatibilität mit bestehenden Detektoren

---

### **PHASE 4: Advanced Features & Integration** ⏱️ 2-3 Stunden

#### **Task 4.1: Marker-Kombinationen** (1 Stunden)
```python
# Integration mit bestehenden Markern
EMOTION_MARKER_COMBINATIONS = {
    "C_ADAPTIVE_POLARIZATION + EMO_VOLATILE": "EMOTIONAL_CHAOS_PATTERN",
    "MM_MEANING_CRISIS + EMO_SLOPE_DOWN": "DEEPENING_DEPRESSION_RISK", 
    "C_INNER_EMPTINESS + EMO_MEAN_LOW": "CHRONIC_LOW_MOOD_PATTERN"
}

def detect_combined_patterns(emotion_results: Dict, 
                           existing_markers: List[str]) -> List[str]:
    """Erkennt Kombinationsmuster zwischen Emotion und bestehenden Markern"""
    pass
```

#### **Task 4.2: Konfigurationssystem** (30 min)
```yaml
# emotion_dynamics_config.yaml
emotion_detection:
  window_minutes: 30
  min_messages_per_speaker: 5
  triggers:
    slope_threshold: 0.15
    volatility_threshold: 0.5
    contrast_threshold: 1.2
  
marker_combinations:
  enabled: true
  priority_combinations:
    - ["C_ADAPTIVE_POLARIZATION", "EMO_VOLATILE"]
    - ["MM_MEANING_CRISIS", "EMO_SLOPE_DOWN"]
```

#### **Task 4.3: Performance-Optimierung** (30 min)
- Caching für VAD-Berechnungen
- Efficient sliding-window implementation
- Memory management für große Conversations

#### **Task 4.4: Driftachsen-Integration** (30 min)
- Verbindung zu driftachsen_kompakt.yaml
- Emotionale Dichte für Risiko-Drift-Muster
- Kalibrierung von Risk-Levels (green/yellow/blinking/red)

---

### **PHASE 5: Testing & Documentation** ⏱️ 2-3 Stunden

#### **Task 5.1: Comprehensive Testing** (1.5 Stunden)
```python
# tests/test_emotion_dynamics.py

def test_vad_calculation():
    """Teste VAD-Berechnung mit bekannten Werten"""
    
def test_slope_detection():
    """Teste Trend-Erkennung"""
    
def test_volatility_measurement():
    """Teste Volatilitäts-Berechnung"""
    
def test_full_emotion_detection():
    """End-to-End Test mit simulierten Gesprächen"""
    
def test_marker_integration():
    """Teste Integration in bestehende Marker-Pipeline"""
```

#### **Task 5.2: Dokumentation** (1 Stunden)
- API-Dokumentation
- Konfigurations-Guide
- Beispiel-Anwendungen
- Performance-Benchmarks

#### **Task 5.3: GUI-Integration** (30 min)
- Button für Emotion-Dynamics-Analyse
- Visualisierung von Emotional-Trends
- Konfiguration über GUI

---

## 🔧 **VALIDIERUNG UND QUALITÄTSSICHERUNG**

### **Effizienz-Kriterien:**
✅ **Modularität:** Separate Utils, klare Interfaces  
✅ **Performance:** O(n) für VAD-Berechnung, O(n log n) für Sliding-Window  
✅ **Skalierbarkeit:** Unterstützt beliebige Gesprächslängen  
✅ **Integration:** Nahtlos in bestehendes FRAUSAR-System  

### **Nachhaltigkeit-Kriterien:**
✅ **Konfigurierbar:** Schwellwerte und Fenster anpassbar  
✅ **Erweiterbar:** Neue Emotion-Metriken einfach hinzufügbar  
✅ **Testbar:** Umfassende Unit-Test-Coverage  
✅ **Dokumentiert:** Vollständige API- und User-Dokumentation  

---

## 📊 **ERWARTETE OUTPUTS**

### **Neue Marker-Klassen:**
- `EMO_SLOPE_UP` / `EMO_SLOPE_DOWN`
- `EMO_VOLATILE_WINDOW`  
- `EMO_MEAN_LOW`
- `EMO_CONTRAST_DRIFT`

### **MarkerPacket Format:**
```json
{
  "speaker": "B",
  "marker": "EMO_SLOPE_UP", 
  "score": 0.76,
  "window": "2025-07-21T10:00:00 → 2025-07-21T10:30:00",
  "details": {
    "valence_slope": 0.32,
    "arousal_slope": 0.18, 
    "dominance_slope": 0.05,
    "volatility": 0.45,
    "displacement": 0.67
  }
}
```

### **Integration Points:**
- ✅ DETECT_default_marker_schema.yaml
- ✅ frausar_gui.py (neuer Button)
- ✅ marker_matcher.py (Pipeline-Integration)
- ✅ Bestehende Marker-Kombinationen

---

## ⏰ **ZEITSCHÄTZUNG**

| Phase | Dauer | Kritischer Pfad |
|-------|--------|------------------|
| Phase 1 | 2-3h | VAD-Setup |
| Phase 2 | 4-5h | Core-Engine |
| Phase 3 | 3-4h | Detector-Implementierung |
| Phase 4 | 2-3h | Advanced-Features |
| Phase 5 | 2-3h | Testing & Docs |
| **TOTAL** | **13-18h** | **2-3 Arbeitstage** |

---

## 🚀 **NÄCHSTE SCHRITTE**

1. **Plan-Validierung**: Review und Approval des Plans ✅
2. **Phase 1 Start**: Umgebung und Dependencies setup 
3. **Iterative Entwicklung**: Kleine Schritte mit kontinuierlichem Testing
4. **Integration Testing**: Nahtlose Einbindung in FRAUSAR
5. **Produktive Nutzung**: Rollout für Live-Marker-Detection

**Ready to begin implementation!** 🎯 