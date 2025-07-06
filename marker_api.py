#!/usr/bin/env python3
"""
Marker API - REST-API für den Marker-basierten Textanalyse-Service
Bietet Endpoints für Einzeltext- und Batch-Analyse
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from typing import Dict, Any, List
from datetime import datetime
import json
import os
import sys

# Importiere den Marker Matcher
from marker_matcher import MarkerMatcher, AnalysisResult

# Flask App initialisieren
app = Flask(__name__)
CORS(app)  # Enable CORS für Frontend-Integration

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globale Matcher-Instanz
matcher = None


def initialize_matcher():
    """Initialisiert den Marker Matcher"""
    global matcher
    try:
        matcher = MarkerMatcher()
        logger.info("Marker Matcher erfolgreich initialisiert")
    except Exception as e:
        logger.error(f"Fehler beim Initialisieren des Matchers: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'markers_loaded': len(matcher.markers) if matcher else 0
    })


@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analysiert einen einzelnen Text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Kein Text zum Analysieren gefunden',
                'status': 'error'
            }), 400
        
        text = data['text']
        
        # Optional: Konfiguration
        config = data.get('config', {})
        
        # Analysiere Text
        result = matcher.analyze_text(text)
        
        # Konvertiere zu JSON-kompatiblem Format
        response = result.to_dict()
        response['status'] = 'success'
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Fehler bei der Analyse: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/analyze_batch', methods=['POST'])
def analyze_batch():
    """Analysiert mehrere Texte gleichzeitig"""
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'error': 'Keine Texte zum Analysieren gefunden',
                'status': 'error'
            }), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({
                'error': 'texts muss eine Liste sein',
                'status': 'error'
            }), 400
        
        # Analysiere alle Texte
        results = []
        for i, text in enumerate(texts):
            try:
                result = matcher.analyze_text(text)
                result_dict = result.to_dict()
                result_dict['index'] = i
                results.append(result_dict)
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'status': 'error'
                })
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total_analyzed': len(results)
        })
        
    except Exception as e:
        logger.error(f"Fehler bei der Batch-Analyse: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/markers', methods=['GET'])
def get_markers():
    """Gibt alle verfügbaren Marker zurück"""
    try:
        markers_list = []
        
        for marker_name, marker_data in matcher.markers.items():
            markers_list.append({
                'name': marker_name,
                'beschreibung': marker_data.get('beschreibung', ''),
                'kategorie': marker_data.get('kategorie', 'UNCATEGORIZED'),
                'tags': marker_data.get('tags', []),
                'risk_score': marker_data.get('risk_score', 1),
                'beispiele_count': len(marker_data.get('beispiele', []))
            })
        
        # Sortiere nach Namen
        markers_list.sort(key=lambda x: x['name'])
        
        return jsonify({
            'status': 'success',
            'markers': markers_list,
            'total': len(markers_list)
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Marker: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/marker/<marker_name>', methods=['GET'])
def get_marker_details(marker_name):
    """Gibt Details zu einem spezifischen Marker zurück"""
    try:
        marker_name = marker_name.upper()
        
        if marker_name not in matcher.markers:
            return jsonify({
                'error': f'Marker {marker_name} nicht gefunden',
                'status': 'error'
            }), 404
        
        marker_data = matcher.markers[marker_name]
        
        return jsonify({
            'status': 'success',
            'marker': marker_data
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Marker-Details: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


@app.route('/stats', methods=['GET'])
def get_statistics():
    """Gibt Statistiken über das Marker-System zurück"""
    try:
        # Sammle Statistiken
        categories = {}
        total_examples = 0
        markers_with_detectors = 0
        
        for marker_data in matcher.markers.values():
            # Kategorien zählen
            cat = marker_data.get('kategorie', 'UNCATEGORIZED')
            categories[cat] = categories.get(cat, 0) + 1
            
            # Beispiele zählen
            total_examples += len(marker_data.get('beispiele', []))
            
            # Detektoren zählen
            if marker_data.get('semantics_detector'):
                markers_with_detectors += 1
        
        return jsonify({
            'status': 'success',
            'statistics': {
                'total_markers': len(matcher.markers),
                'total_examples': total_examples,
                'average_examples_per_marker': round(total_examples / len(matcher.markers), 2) if matcher.markers else 0,
                'categories': categories,
                'markers_with_semantic_detectors': markers_with_detectors
            }
        })
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Statistiken: {e}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500


# Beispiel-HTML für die API-Dokumentation
@app.route('/', methods=['GET'])
def index():
    """Zeigt eine einfache API-Dokumentation"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Marker API - Dokumentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { color: #fff; padding: 2px 8px; border-radius: 3px; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            code { background: #e8e8e8; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🔍 Marker API - Semantisch-psychologischer Textanalyse-Service</h1>
        
        <h2>Verfügbare Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/health</code>
            <p>Health Check - Prüft ob der Service läuft</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/analyze</code>
            <p>Analysiert einen einzelnen Text</p>
            <pre>Body: { "text": "Zu analysierender Text..." }</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/analyze_batch</code>
            <p>Analysiert mehrere Texte gleichzeitig</p>
            <pre>Body: { "texts": ["Text 1", "Text 2", ...] }</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/markers</code>
            <p>Listet alle verfügbaren Marker auf</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/marker/{marker_name}</code>
            <p>Zeigt Details zu einem spezifischen Marker</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/stats</code>
            <p>Zeigt Statistiken über das Marker-System</p>
        </div>
        
        <h2>Risk-Level Farbcodierung:</h2>
        <ul>
            <li>🟢 <strong>Grün:</strong> Kein oder nur unkritischer Marker</li>
            <li>🟡 <strong>Gelb:</strong> 1-2 moderate Marker, erste Drift erkennbar</li>
            <li>🟠 <strong>Blinkend:</strong> 3+ Marker oder ein Hochrisiko-Marker</li>
            <li>🔴 <strong>Rot:</strong> Hochrisiko-Kombination, massive Manipulation</li>
        </ul>
    </body>
    </html>
    """
    return html


if __name__ == '__main__':
    # Initialisiere Matcher
    initialize_matcher()
    
    # Starte Server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 