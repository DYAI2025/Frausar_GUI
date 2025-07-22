Bausteine, die zusammen ein Analyse-Schema ergeben
Ebene	Rolle	Typische Dateien / Klassen	Kernausschnitt
1. Marker-Quellen	Fachliche Einheiten (Atomic → Meta) samt Metadaten & Gewichtung	YAML/JSON/TXT in markers/ (z. B. 2107_1400marker_unified_for_gpt.yaml)	jedes Marker-Objekt trägt u. a. id, level, optionale scoring.weight
2. Loader-Schicht	Liest Marker aus allen Formaten, normalisiert & cached sie in ein Python-Dict	config_loader.py → MarkerLoader.load_all_markers() lädt YAML, JSON, TXT und merged sie config_loader	
3. Detektor-Module	Algorithmen, die Marker oder komplexe Muster in Texten erkennen	Auto-registrierte DETECT_*.py Klassen in DETECT_default_marker_schema.yaml DETECT_default_marker_s…	
4. Matcher / Scoring	Verknüpft Treffer mit Risiko-Logik & Level-Aggregation	marker_matcher.py – Risk-Schwellen & Gesamtscore marker_matcher	
5. Schema-Template	JSON-Gerüst, das definiert welche Marker-Gruppen, Drift-Achsen, Metriken & Outputs später befüllt werden	Beispiel beziehungsanalyse_schema.json (Gruppen‐Blöcke ab Zeile 17) beziehungsanalyse_schema	
6. Schema-Loader / API	Bietet Lese-Methoden für UI, Pipeline, Export	schema_loader.py → get_included_marker_names() etc. schema_loader	
7. Validierung / QA	Prüft Level-Regeln, Pflichtfelder, Zyklusfreiheit	marker_analyzer.py → analyze_marker_level() & validate_marker_structure() marker_analyzer	

Ergebnis: Erst wenn Marker-Set (1) plus Detektoren (3) plus ein passendes JSON-Gerüst (5) durch Loader (2 & 6) in die Pipeline fließen und die QA-Checks (7) grün sind, spricht man von einem spezifischen Analyse-Schema.

Logik für die halb-automatische Schema-Erstellung
Domänen-Ziel definieren
Welche Dynamik will ich messen? → wähle/erstelle passendes JSON-Template (wie beziehungsanalyse_schema.json).

Marker-Subset ableiten
Strategien

Tag-/Folder-Filter in MarkerLoader (z. B. nur Flirtation-Marker laden).

SemanticGrabber-Library: semantische Suche nach Beispielsätzen.

Recursive Marker Generator für LLM-gestützte Neumarker SYSTEM_PROMPT - recursi… & Rekursive_marker-genera….

Auto-Detektor-Skeletons erzeugen
Für jedes neue Marker-Cluster ein DETECT_*.py anlegen (Generator-Klasse in detect_creator.py, registriert im Detector-Schema).

Gewichte & Schwellen festlegen

scoring.weight pro Marker (fachliche Bedeutung).

globale Risk-Thresholds in marker_matcher.py anpassen.

Schema-JSON bauen
Ein einfaches Script (siehe Loader-Workflow-Beispiel Guide_for_YAML_Marker-H…)

füllt die Marker-Listen in den Blöcken atomic_markers, cluster_markers, … mit count: 0.

kopiert Standard-Abschnitte (Drift-Achsen, Outputs) aus einer Vorlage.

CI-Validierung

yaml_syntax_checker.py für reine Syntax.

marker_analyzer.py für Struktur- & Level-Checks.

optionale LLM-Self-Test via Prompt.

Publish & Versionieren
Bestehender Pipeline-Runner (PIPELINE.py o. Ä.) lädt:
MarkerLoader → MarkerMatcher → Scoring → exportiert Ergebnisse gem. outputs.visualization/export_format.

Kurzform-“Rezept”
text
Kopieren
Bearbeiten
1. choose_domain()         # Analyse-Typ & Vorlage
2. select_markers()        # Loader-Filter + Grabber + LLM-Generator
3. generate_detectors()    # detect_creator.create()
4. tune_scoring()          # weight + thresholds
5. build_schema_json()     # compile_template()
6. run_ci_checks()         # yaml_checker + marker_analyzer
7. deploy_schema()         # commit & pipeline
Mit diesem Bauplan lassen sich neue Analyse-Schemata in wenigen Minuten aus vorhandenen Bausteinen halb-automatisch erzeugen – skalierbar, versionierbar und CI-geprüft.