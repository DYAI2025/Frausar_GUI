#!/usr/bin/env python3
"""
YAML Syntax Repair Tool
Repariert spezifische YAML-Syntaxfehler in Marker-Dateien
"""

import yaml
import os
import json
from datetime import datetime

def repair_stellvertreterkonflikt_marker():
    """Repariert die spezifischen Probleme in M_STELLVERTRETERKONFLIKT_MARKER.yaml"""
    
    file_path = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/M_STELLVERTRETERKONFLIKT_MARKER.yaml"
    
    print("🔧 Repariere M_STELLVERTRETERKONFLIKT_MARKER.yaml...")
    
    # Backup erstellen
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup erstellt: {backup_path}")
        
        # Korrekte Struktur aufbauen
        marker_data = {
            "id": "M_STELLVERTRETERKONFLIKT",
            "name": "Stellvertreterkonflikt",
            "level": 2,
            "category": "dynamics",
            "cluster": ["conflict_avoidance", "hidden_motivation"],
            "meta_marker": ["MM_INDIREKTER_KONFLIKT"],
            "status": "review",
            "author": "ben_2025",
            "created_at": "2025-07-14",
            "lang": "de",
            "description": """Marker für indirekte, verschobene Konfliktführung: Die eigentliche emotionale Motivation (z.B. Eifersucht, Neid, Angst, Verletztheit) bleibt unausgesprochen. Die Diskussion wird auf ein Nebenthema verlagert (Prinzipien, Sicherheit, Ordnung, Budget, Kompetenz), um ohne Offenlegung eigener Verletzlichkeit Kontrolle, Vorteil oder moralische Überlegenheit zu beanspruchen.""",
            "pattern": [
                "Plötzliche Sorge um rationale, organisatorische oder moralische Details, während im Hintergrund ein anderes Gefühl steht.",
                "Diskussionen, die auf der Sachebene bleiben, obwohl der wahre Grund emotional ist.",
                "Begründungen, die moralisch, vernünftig oder fürsorglich klingen, aber dem Anderen das Handeln erschweren oder Schuld zuweisen.",
                "Scheinbar selbstlose Bedenken, die faktisch Kontrolle, Überlegenheit oder Vorteil sichern."
            ],
            "rules": [
                {
                    "type": "negation",
                    "description": "Keine direkte Benennung der eigentlichen Emotion (Eifersucht, Angst, Neid, Unsicherheit)."
                },
                {
                    "type": "co_occurrence",
                    "condition": "emotionale Spannung, die sich im Verhalten/Timing zeigt"
                },
                {
                    "type": "role_inversion",
                    "description": "Vorteil, Kontrolle oder Überlegenheit werden durch den Vorwand beansprucht."
                }
            ],
            "tags": ["konflikt", "indirekt", "stellvertreter", "beziehung", "hidden_agenda"],
            "semantic_grabber_id": "AUTO_SEM_20250714_6E57",
            "scoring": {
                "weight": 1.3,
                "impact": "mid"
            },
            "examples": [
                {
                    "title": "Finanzen als Vorwand",
                    "text": "B möchte verreisen. A: \"Schatz, hast du gesehen, wie viel wir diesen Monat schon ausgegeben haben? Deine Reise… ich weiß nicht, ob das so klug ist.\"",
                    "hidden_motivation": "Eifersucht auf Zeit ohne A"
                },
                {
                    "title": "Kompetenz in Frage gestellt",
                    "text": "Team-Meeting, Kollege A zu B: \"Bevor wir uns später Ärger einhandeln: Hast du alle Zahlen geprüft? Letztes Mal gab's da eine Lücke. Ich kann da nachher drüber schauen.\"",
                    "hidden_motivation": "Neid, Angst vor Statusverlust"
                },
                {
                    "title": "Unordnung als Streitpunkt",
                    "text": "A fühlt sich vernachlässigt, B beschäftigt sich mit neuem Hobby. \"So ein Chaos überall – ich kann hier gar nicht mehr entspannen. Musst du immer alles liegen lassen?\"",
                    "hidden_motivation": "Verletztheit, Wunsch nach mehr Aufmerksamkeit"
                },
                {
                    "title": "Prinzipien als Totschlagargument",
                    "text": "B schlägt vor, Freunde zu besuchen. A: \"Nein, zu denen geh ich nicht. Ich bin strikt gegen Rauchen in geschlossenen Räumen, das weißt du. Da bin ich konsequent.\"",
                    "hidden_motivation": "Vermeidung einer Person aus Eifersucht/Misstrauen"
                },
                {
                    "title": "Sicherheit als Begründung",
                    "text": "B will ein sportliches Fahrrad kaufen. A: \"Hast du mal die Unfallzahlen gesehen? Ich find das echt gefährlich. Ein normales Bike wär sicherer.\"",
                    "hidden_motivation": "Neid, Angst vor weniger Einfluss"
                },
                {
                    "title": "Wohlergehen vorschieben",
                    "text": "B möchte abends ausgehen. A: \"Ich glaub ehrlich, du solltest mal mehr auf deinen Schlaf achten – dauernd unterwegs ist doch nicht gesund.\"",
                    "hidden_motivation": "Angst, den Partner zu verlieren; Wunsch nach Kontrolle"
                },
                {
                    "title": "Zeitmanagement/Selbstfürsorge als Vorwand",
                    "text": "Kollegin B schlägt gemeinsames Projekt vor. A: \"Ich habe gelernt, Grenzen zu setzen und muss gerade an mein eigenes Wohl denken. Vielleicht passt das einfach nicht mehr zu meiner Work-Life-Balance.\"",
                    "hidden_motivation": "Missgunst, Angst vor Überflügeltwerden"
                },
                {
                    "title": "\"Fürsorglicher\" Kontaktabbruch",
                    "text": "Nach Streit, A zu B: \"Ich glaube, es ist besser, wenn wir uns eine Weile nicht sehen. Du brauchst Raum, und ich will dich da nicht einengen.\"",
                    "hidden_motivation": "Selbstschutz, aber auch Strafe/Kontrolle durch Rückzug"
                }
            ],
            "metadata": {
                "created_at": "2025-07-14T00:42:25.155399",
                "created_by": "FRAUSAR_GUI_v2",
                "version": "1.0",
                "tags": ["neu_erstellt", "needs_review"],
                "repaired_at": datetime.now().isoformat(),
                "repaired_by": "yaml_syntax_repair_tool"
            }
        }
        
        # Als YAML speichern
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(marker_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2)
        
        print("✅ YAML-Datei erfolgreich repariert!")
        
        # Validierung
        with open(file_path, 'r', encoding='utf-8') as f:
            validated_data = yaml.safe_load(f)
        
        print("✅ YAML-Syntax validiert - keine Fehler!")
        print(f"📊 Marker ID: {validated_data['id']}")
        print(f"📊 Anzahl Beispiele: {len(validated_data['examples'])}")
        print(f"📊 Semantic Grabber ID: {validated_data['semantic_grabber_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei der Reparatur: {e}")
        return False

def test_yaml_to_json_conversion():
    """Testet die YAML zu JSON Konvertierung nach der Reparatur"""
    
    file_path = "../ALL_SEMANTIC_MARKER_TXT/ALL_NEWMARKER01/M_STELLVERTRETERKONFLIKT_MARKER.yaml"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        json_output = json.dumps(yaml_data, indent=2, ensure_ascii=False)
        
        print("🧪 YAML zu JSON Konvertierung erfolgreich!")
        print(f"📏 JSON Größe: {len(json_output)} Zeichen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei YAML zu JSON Konvertierung: {e}")
        return False

if __name__ == "__main__":
    print("🚀 YAML Syntax Repair Tool")
    print("=" * 50)
    
    # Reparatur durchführen
    if repair_stellvertreterkonflikt_marker():
        print("\n" + "=" * 50)
        print("🧪 Teste YAML zu JSON Konvertierung...")
        test_yaml_to_json_conversion()
    else:
        print("❌ Reparatur fehlgeschlagen!") 