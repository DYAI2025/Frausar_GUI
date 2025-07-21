# 🤖 FRAUSAR One-Click Starter

## 🚀 Einfacher Start per Doppelklick

Die FRAUSAR GUI kann jetzt mit einem einzigen Doppelklick gestartet werden - **komplett automatisch** mit Installation aller Dependencies!

## 📋 Verfügbare Startoptionen

### 🖥️ **Für alle Betriebssysteme**
**Datei:** `start_frausar_oneclick.py`
- **Verwendung:** Doppelklick auf die Datei
- **Features:** Grafische Benutzeroberfläche mit Progress-Anzeige
- **Funktionen:**
  - ✅ Automatische Pip-Installation
  - ✅ Dependency-Check
  - ✅ FRAUSAR-Setup
  - ✅ GUI-Start
  - ✅ Status-Log mit Zeitstempel

### 🍎 **Speziell für macOS**
**Datei:** `start_frausar.command`
- **Verwendung:** Doppelklick auf die Datei
- **Features:** Terminal-basiert, automatisch ausführbar
- **Vorteile:** Keine zusätzlichen Berechtigungen nötig

### 🪟 **Speziell für Windows**
**Datei:** `start_frausar.bat`
- **Verwendung:** Doppelklick auf die Datei
- **Features:** Kommandozeilen-basiert
- **Vorteile:** Unicode-Unterstützung für Emojis

## 🎯 Wie funktioniert es?

### **Schritt 1: Dependency-Check**
- Prüft automatisch ob alle Python-Packages installiert sind
- Zeigt Status für jedes Package an

### **Schritt 2: Automatische Installation**
- Führt `pip install -r requirements.txt` aus
- Fallback auf Essential-Packages falls requirements.txt fehlt
- Timeout-Schutz (10 Minuten maximum)

### **Schritt 3: FRAUSAR Setup**
- Führt `frausar_setup.py` aus falls vorhanden
- Konfiguriert alle notwendigen Einstellungen

### **Schritt 4: GUI-Start**
- Startet `frausar_gui.py` in separatem Prozess
- Schließt den Starter automatisch nach 3 Sekunden

## 🛠️ Manuelle Verwendung

Falls Sie den One-Click-Starter nicht per Doppelklick ausführen können:

```bash
# Terminal/Kommandozeile
cd Marker_assist_bot
python3 start_frausar_oneclick.py
```

## ⚡ Schnellstart (GUI bereits installiert)

Wenn FRAUSAR bereits funktioniert und Sie nur die GUI starten möchten:

1. **Doppelklick** auf eine der Startdateien
2. **Klick** auf "📋 Nur GUI starten"
3. **Fertig!** - GUI startet sofort

## 🔧 Problembehandlung

### **Python nicht gefunden**
- Installieren Sie Python 3.8+ von [python.org](https://python.org)
- Stellen Sie sicher, dass Python im PATH ist

### **Permission denied (macOS)**
```bash
chmod +x start_frausar.command
```

### **Antivirus-Warnung (Windows)**
- Fügen Sie das Verzeichnis zur Ausnahmeliste hinzu
- Die .bat-Datei ist sicher und führt nur Python-Code aus

### **Installation schlägt fehl**
1. **Internetverbindung** prüfen
2. **Administrator-Rechte** verwenden falls nötig
3. **Manueller Pip-Update:** `python -m pip install --upgrade pip`

## 📊 Was wird installiert?

**Essential Packages:**
- PyYAML (YAML-Verarbeitung)
- tkinter (GUI-Framework)
- pathlib (Pfad-Handling)
- requests (HTTP-Requests)
- numpy (Numerische Operationen)

**Plus alle Packages aus:** `requirements.txt`

## 🎉 Erfolgsmeldung

Nach erfolgreichem Setup sehen Sie:
```
✅ FRAUSAR erfolgreich gestartet!
🎉 Sie können dieses Fenster jetzt schließen
```

Die FRAUSAR GUI öffnet sich automatisch und ist einsatzbereit!

## 🔄 Updates

Um FRAUSAR zu aktualisieren:
1. **Neue Dateien** in das Verzeichnis kopieren
2. **One-Click-Starter** erneut ausführen
3. **Dependencies** werden automatisch aktualisiert

---

**💡 Tipp:** Erstellen Sie eine Desktop-Verknüpfung zur gewünschten Startdatei für noch einfacheren Zugriff! 