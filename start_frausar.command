#!/bin/bash

# FRAUSAR One-Click Starter für macOS
# Doppelklick-fähiges Script

echo "🤖 FRAUSAR One-Click Starter"
echo "=========================="

# Wechsle ins Skript-Verzeichnis
cd "$(dirname "$0")"

echo "📁 Arbeitsverzeichnis: $(pwd)"

# Prüfe verschiedene Python-Pfade
if [ -x "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3" ]; then
    echo "✅ Python3 gefunden: $(/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 --version)"
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 start_frausar_oneclick.py
elif command -v python3 &> /dev/null; then
    echo "✅ Python3 gefunden: $(python3 --version)"
    python3 start_frausar_oneclick.py
elif command -v python &> /dev/null; then
    echo "✅ Python gefunden: $(python --version)"
    python start_frausar_oneclick.py
else
    echo "❌ Python nicht gefunden!"
    echo "Bitte installieren Sie Python3 von https://python.org"
    echo "Oder prüfen Sie, ob Python im PATH ist:"
    echo "  export PATH=\"/Library/Frameworks/Python.framework/Versions/3.13/bin:\$PATH\""
    echo ""
    read -p "Drücken Sie Enter um zu beenden..."
    exit 1
fi

echo ""
echo "🎉 FRAUSAR Setup abgeschlossen!"
read -p "Drücken Sie Enter um dieses Fenster zu schließen..." 