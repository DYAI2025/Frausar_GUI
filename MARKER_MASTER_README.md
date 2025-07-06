# Marker Master Export

Diese Dateien enthalten das vollständige Marker-Masterset für den semantisch-psychologischen Resonanz- und Manipulations-Detektor.

## Verwendung

### Import in Python:
```python
import yaml
with open('marker_master_export.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)
    
markers = data['markers']
```

### Struktur eines Markers:
- `marker`: Name/ID des Markers
- `beschreibung`: Klartext-Beschreibung
- `beispiele`: Liste typischer Formulierungen
- `kategorie`: Thematische Einordnung
- `tags`: Klassifikations-Tags
- `risk_score`: Risiko-Gewichtung (1-5)
- `semantics_detector`: Optional - Python-Detektor-Datei

### Risiko-Level:
- **Grün**: Kein oder nur unkritischer Marker
- **Gelb**: 1-2 moderate Marker, erste Drift erkennbar
- **Blinkend**: 3+ Marker oder ein Hochrisiko-Marker
- **Rot**: Hochrisiko-Kombination, massive Manipulation

## Verfügbare Marker

- **AI_BOTS_SEMANTIC_DETECT**: >
  beschreibung: >
  # -*- coding: utf-8 -*-

# ###############################... (0 Beispiele)
- **AI_BOT_SCAM_MARKER**: >
  beschreibung: >
  Erkennt sprachliche Muster, typische Phrasen und Begriffe ... (34 Beispiele)
- **AI_BOT_SEMANTIC_DETECT**: >
  # -*- coding: utf-8 -*-

# #################################################... (75 Beispiele)
- **AMBIVALENCE**: Keine Beschreibung verfügbar (0 Beispiele)
- **ARCHETYPAL_PATTERNS**: '' (0 Beispiele)
- **AROUSAL**: Keine Beschreibung verfügbar (0 Beispiele)
- **Ambivalence**: Keine Beschreibung verfügbar (0 Beispiele)
- **BLAME_SHIFT_MARKER**: Die Technik, die Verantwortung für eigene Fehler, negative Gefühle oder Beziehun... (20 Beispiele)
- **COMPARISON_GHOST_MARKER**: Subtiler oder offener Vergleich einer aktuellen Situation mit Ex-Partnern, einem... (20 Beispiele)
- **CONNECTION**: Keine Beschreibung verfügbar (0 Beispiele)
- **DEEPENING_BY_QUESTIONING_MARKER**: >
  semantic_marker = {
    "marker": "DEEPENING_BY_QUESTIONING",
    "beschreib... (563 Beispiele)
- **DRAMA_TRIANGLE_MARKER**: >
  Typische Rollenrotationen nach dem Dramadreieck: Verfolger, Opfer, Retter – ... (86 Beispiele)
- **EMOTIONAL_BEHAVIORALS**: '' (0 Beispiele)
- **EMOTIONAL_VALENCES**: '' (0 Beispiele)
- **ESCALATION**: Keine Beschreibung verfügbar (0 Beispiele)
- **FLUCTUATION**: Keine Beschreibung verfügbar (0 Beispiele)
- **FRIENDLY_FLIRTING_DETECT**: >
  "beschreibung": (
            "Erkennt kommunikative Muster von freundlich-s... (28 Beispiele)
- **FRIENDLY_FLIRTING_MARKER**: >
  Neue umfangreiche Beispieldaten für die bestehenden Marker
updated_markers =... (19 Beispiele)
- **Family**: Keine Beschreibung verfügbar (0 Beispiele)
- **GASLIGHTING_MARKER**: >
  Kommunikation, die das Gegenüber gezielt an seiner Wahrnehmung, Erinnerung o... (19 Beispiele)
- **GUILT_TRIPPING_MARKER**: >
  Aussagen, die gezielt Schuldgefühle erzeugen oder verstärken, meist durch su... (46 Beispiele)
- **GUILT_TRIPPING_SEMANTIC_DETECT**: >
  # -*- coding: utf-8 -*-

# #################################################... (28 Beispiele)
- **INTEGRATION**: Keine Beschreibung verfügbar (0 Beispiele)
- **ISOLATION_MARKER**: >
  Kommunikation, die aktiv oder subtil soziale Kontakte, Familie oder Freunde ... (77 Beispiele)
- **LIE_CONCEALMENT_MARKER**: >
  Indikatoren für Lügen, Ausflüchte oder bewusste Verheimlichung. Erkennbar an... (5 Beispiele)
- **LOVE_BOMBING**: >
  Übertriebene, überschnelle Zuneigung und Aufmerksamkeit, oft mit starken Ver... (38 Beispiele)
- **META_COMMUNICATIONS**: '' (0 Beispiele)
- **OFFENSIVE_FLIRTING_MARKER**: >
  eschreibung: >

Erkennt kommunikative Muster von offensivem, teils grenzüber... (12 Beispiele)
- **PERMANENT_POSTPONE_MARKER**: Das wiederholte und oft vage Aufschieben von wichtigen Entscheidungen, klärenden... (20 Beispiele)
- **PLAYING_VICTIM_MARKER**: >
  Das bewusste oder unbewusste Einnehmen der Opferrolle, um Mitleid, Entlastun... (74 Beispiele)
- **PROJECTIVE_IDENTIFICATION_MARKER**: >
  Eigene, oft unbewusste Gefühle, Schwächen oder Eigenschaften werden dem Gege... (20 Beispiele)
- **Pseudo**: Keine Beschreibung verfügbar (0 Beispiele)
- **RELATIONSHIP_AUTHENTICITY_MARKER_MARKER**: >
  beschreibung: >
    Erkennt, ob im Gesprächsverlauf Hinweise darauf bestehen... (12 Beispiele)
- **RESONACE_MATCHING_DETECTOR**: >
  Semantic detection of too good to be true matching. (6 Beispiele)
- **RESONANZ_MATCHING_MARKER_MARKER**: >
  beschreibung: >
    Erkennt eine auffallend hohe Übereinstimmung oder perfek... (27 Beispiele)
- **Reactive**: Keine Beschreibung verfügbar (0 Beispiele)
- **SCAMMER_BEHAVIOUR_DETECT**: >
  Erkennt manipulative Verhaltensmuster aus Romance-Scam-Situationen. 
  Die M... (56 Beispiele)
- **SCAMMER_DETECTIO**: >
  beschreibung: >
  Erkennt manipulative Verhaltensmuster aus Romance-Scam-Sit... (20 Beispiele)
- **SCAMMER_SEMANTIC_BEHAVIOUR**: >
  beschreibung: >
  Erkennt manipulative Verhaltensmuster aus Romance-Scam-Sit... (58 Beispiele)
- **SELF_SABOTAGE_LOOP_MARKER**: Ein Verhaltens- oder Kommunikationsmuster, bei dem eine Person aktiv oder passiv... (20 Beispiele)
- **SEMANTIC_BEHAVIOR_MARKER**: Erkennt manipulative Verhaltensmuster aus Romance-Scam-Situationen.  Die Marker ... (0 Beispiele)
- **SILENT_TREATMENT_MARKER**: >
  Kommunikationsverweigerung, Mauern oder Ignorieren des Gegenübers als passiv... (15 Beispiele)
- **SIMU_IMITATION_STRATEGIES**: >
  Um das Verhalten eines Love Scammers möglichst realistisch zu imitieren, mus... (33 Beispiele)
- **SIMU_LAVE_SCAM_SEMANTIC**: >
  YAML-Struktur fürs semantische Verhalten von SIMULATRO KI bei der Simulation... (13 Beispiele)
- **SIMU_LOVE_SCAM_HUMAN01**: >
  Was bräuchte diese semantische Erkennung?
Statt "Ich liebe dich" einfach nur... (31 Beispiele)
- **SIMU_LOVE_SCAM_PSYCHO_DISTRACT**: >
  Intensiver Beziehungsaufbau, um beim Opfer ein Trauma-Bonding zu erzeugen, u... (72 Beispiele)
- **SOCIAL_BORDERLINES_MARKER_MIX_MARKER**: >
  A mixture of markers to identify social closeness and allowingness of steppi... (22 Beispiele)
- **SOCIAL_INTERACTION**: >
  "beschreibung": (
            "Erkennt kommunikative Muster von freundlich-s... (30 Beispiele)
- **SOCIAL_RESONANCE_DETECTOR**: >
  Semantic greb pattern (2 Beispiele)
- **SPIRAL_DYNAMICS_LEVELS**: '' (0 Beispiele)
- **SUBTLE_TERRITORIAL_MARKER**: Verdecktes oder offenes Abstecken von persönlichen Grenzen und Revieren durch Re... (20 Beispiele)
- **TERMINATION**: Keine Beschreibung verfügbar (0 Beispiele)
- **TOMS_Erweiterte_Marker**: Keine Beschreibung verfügbar (0 Beispiele)
- **UNCERTAINTY**: Keine Beschreibung verfügbar (0 Beispiele)
- **WEBCAM_EXCUSE_MARKER**: >
  beschreibung: >
  Erkennt typische Ausreden, mit denen eine Videoverbindung ... (48 Beispiele)
- **abbruchmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **ambivalenzmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **beispiele**: '' (0 Beispiele)
- **daten**: Keine Beschreibung verfügbar (0 Beispiele)
- **erregungsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **eskalationsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **integrationsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **kommunikationsmarker_ident**: Keine Beschreibung verfügbar (0 Beispiele)
- **marker_rollen_rotation**: Keine Beschreibung verfügbar (0 Beispiele)
- **marker_set_beziehung**: 'Enthält Marker rund um emotionale Dynamiken in Beziehungen: Manipulation,
    R... (0 Beispiele)
- **marker_set_bindungsmuster**: Marker zur Erkennung von Bindungsstrategien in zwischenmenschlichen
    Beziehun... (0 Beispiele)
- **meta_marker_definitions**: >
      Ein manipulatives Muster, das emotionale Schuld erzeugt, indem es Selbst... (0 Beispiele)
- **neue_marker_beziehung**: Keine Beschreibung verfügbar (0 Beispiele)
- **o3_text_markers**: Keine Beschreibung verfügbar (0 Beispiele)
- **schwankenmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **sentinelMarkerMatcher**: Keine Beschreibung verfügbar (0 Beispiele)
- **spiral_analysis**: Keine Beschreibung verfügbar (0 Beispiele)
- **streitmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **unklarheitsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **verbindungsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **versöhnungsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **verstandnismarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **vorwurfsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **widerspruchsmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **wutmarker**: Keine Beschreibung verfügbar (0 Beispiele)
- **zweifelmarker**: Keine Beschreibung verfügbar (0 Beispiele)


## Kategorien-Übersicht

### UNCATEGORIZED
Anzahl Marker: 81
Marker: AI_BOTS_SEMANTIC_DETECT, AI_BOT_SCAM_MARKER, AI_BOT_SEMANTIC_DETECT, AMBIVALENCE, ARCHETYPAL_PATTERNS, AROUSAL, Ambivalence, BLAME_SHIFT_MARKER, COMPARISON_GHOST_MARKER, CONNECTION, DEEPENING_BY_QUESTIONING_MARKER, DRAMA_TRIANGLE_MARKER, EMOTIONAL_BEHAVIORALS, EMOTIONAL_VALENCES, ESCALATION, FLUCTUATION, FRIENDLY_FLIRTING_DETECT, FRIENDLY_FLIRTING_MARKER, Family, GASLIGHTING_MARKER, GUILT_TRIPPING_MARKER, GUILT_TRIPPING_SEMANTIC_DETECT, INTEGRATION, ISOLATION_MARKER, LIE_CONCEALMENT_MARKER, LOVE_BOMBING, META_COMMUNICATIONS, OFFENSIVE_FLIRTING_MARKER, PERMANENT_POSTPONE_MARKER, PLAYING_VICTIM_MARKER, PROJECTIVE_IDENTIFICATION_MARKER, Pseudo, RELATIONSHIP_AUTHENTICITY_MARKER_MARKER, RESONACE_MATCHING_DETECTOR, RESONANZ_MATCHING_MARKER_MARKER, Reactive, SCAMMER_BEHAVIOUR_DETECT, SCAMMER_DETECTIO, SCAMMER_SEMANTIC_BEHAVIOUR, SELF_SABOTAGE_LOOP_MARKER, SEMANTIC_BEHAVIOR_MARKER, SILENT_TREATMENT_MARKER, SIMU_IMITATION_STRATEGIES, SIMU_LAVE_SCAM_SEMANTIC, SIMU_LOVE_SCAM_HUMAN01, SIMU_LOVE_SCAM_PSYCHO_DISTRACT, SOCIAL_BORDERLINES_MARKER_MIX_MARKER, SOCIAL_INTERACTION, SOCIAL_RESONANCE_DETECTOR, SPIRAL_DYNAMICS_LEVELS, SUBTLE_TERRITORIAL_MARKER, TERMINATION, TOMS_Erweiterte_Marker, UNCERTAINTY, WEBCAM_EXCUSE_MARKER, abbruchmarker, ambivalenzmarker, beispiele, daten, erregungsmarker, eskalationsmarker, integrationsmarker, kommunikationsmarker_ident, marker_rollen_rotation, marker_set_beziehung, marker_set_bindungsmuster, meta_marker_definitions, neue_marker_beziehung, o3_text_markers, schwankenmarker, sentinelMarkerMatcher, spiral_analysis, streitmarker, unklarheitsmarker, verbindungsmarker, versöhnungsmarker, verstandnismarker, vorwurfsmarker, widerspruchsmarker, wutmarker, zweifelmarker



---

Generiert am: 2025-07-01 13:19:02 von FRAUSAR Marker Assistant  
Anzahl Marker: 81
