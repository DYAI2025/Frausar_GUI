#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRAUSAR One-Click Starter
=========================
Doppelklick-fähiger Starter für FRAUSAR GUI
- Automatische Pip-Installation aller Dependencies
- Setup-Prozess
- GUI-Start

Einfach per Doppelklick ausführen!
"""

import sys
import subprocess
import os
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

class FRAUSAROneClickStarter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 FRAUSAR One-Click Starter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variablen
        self.installation_complete = False
        self.setup_complete = False
        
        self.setup_gui()
        
    def setup_gui(self):
        # Hauptframe
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="🤖 FRAUSAR Marker Management", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="One-Click Setup & Start", 
                                 font=('Arial', 12), bg='#f0f0f0', fg='#7f8c8d')
        subtitle_label.pack()
        
        # Status-Bereich
        status_frame = tk.LabelFrame(main_frame, text="📋 Setup Status", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15, 
                                                    font=('Consolas', 10), wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Button-Bereich
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X)
        
        self.start_button = tk.Button(button_frame, text="🚀 FRAUSAR Setup & Start", 
                                     font=('Arial', 14, 'bold'), bg='#3498db', fg='white',
                                     command=self.start_setup_process, 
                                     padx=20, pady=10, relief=tk.RAISED, bd=3)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.gui_only_button = tk.Button(button_frame, text="📋 Nur GUI starten", 
                                        font=('Arial', 12), bg='#95a5a6', fg='white',
                                        command=self.start_gui_only, 
                                        padx=15, pady=8, relief=tk.RAISED, bd=2)
        self.gui_only_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.exit_button = tk.Button(button_frame, text="❌ Beenden", 
                                    font=('Arial', 12), bg='#e74c3c', fg='white',
                                    command=self.root.quit, 
                                    padx=15, pady=8, relief=tk.RAISED, bd=2)
        self.exit_button.pack(side=tk.RIGHT)
        
        # Initial-Nachricht
        self.log_message("🤖 FRAUSAR One-Click Starter bereit!")
        self.log_message("📋 Klicken Sie auf 'FRAUSAR Setup & Start' für vollständige Installation")
        self.log_message("⚡ Oder 'Nur GUI starten' wenn bereits installiert\n")
        
    def log_message(self, message, level="INFO"):
        """Fügt Nachricht zum Status-Log hinzu"""
        timestamp = time.strftime("%H:%M:%S")
        if level == "ERROR":
            formatted_message = f"[{timestamp}] ❌ {message}\n"
        elif level == "SUCCESS":
            formatted_message = f"[{timestamp}] ✅ {message}\n"
        elif level == "WARN":
            formatted_message = f"[{timestamp}] ⚠️ {message}\n"
        else:
            formatted_message = f"[{timestamp}] ℹ️ {message}\n"
            
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update()
        
    def disable_buttons(self):
        """Deaktiviert alle Buttons während des Setups"""
        self.start_button.config(state=tk.DISABLED, bg='#bdc3c7')
        self.gui_only_button.config(state=tk.DISABLED, bg='#bdc3c7')
        
    def enable_buttons(self):
        """Aktiviert alle Buttons nach dem Setup"""
        self.start_button.config(state=tk.NORMAL, bg='#3498db')
        self.gui_only_button.config(state=tk.NORMAL, bg='#95a5a6')
        
    def run_command(self, command, description, timeout=300):
        """Führt Kommando aus und loggt Ergebnis"""
        try:
            self.log_message(f"🔄 {description}...")
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            if result.returncode == 0:
                self.log_message(f"{description} erfolgreich", "SUCCESS")
                if result.stdout.strip():
                    self.log_message(f"📤 Ausgabe: {result.stdout.strip()[:100]}...")
                return True
            else:
                self.log_message(f"{description} fehlgeschlagen (Exit-Code: {result.returncode})", "ERROR")
                if result.stderr.strip():
                    self.log_message(f"📤 Fehler: {result.stderr.strip()[:200]}...", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message(f"{description} - Timeout nach {timeout}s", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"{description} - Unerwarteter Fehler: {str(e)}", "ERROR")
            return False
            
    def check_dependencies(self):
        """Prüft ob notwendige Dependencies installiert sind"""
        self.log_message("🔍 Prüfe Dependencies...")
        
        required_packages = ['tkinter', 'yaml', 'pathlib']
        missing_packages = []
        
        for package in required_packages:
            try:
                if package == 'tkinter':
                    import tkinter
                elif package == 'yaml':
                    import yaml
                elif package == 'pathlib':
                    from pathlib import Path
                self.log_message(f"✅ {package} verfügbar")
            except ImportError:
                missing_packages.append(package)
                self.log_message(f"❌ {package} fehlt", "WARN")
                
        return len(missing_packages) == 0
        
    def install_dependencies(self):
        """Installiert notwendige Python-Packages"""
        self.log_message("📦 Installiere Dependencies...")
        
        # Requirements-Datei prüfen
        requirements_file = Path(__file__).parent / "requirements.txt"
        if requirements_file.exists():
            cmd = f"{sys.executable} -m pip install -r requirements.txt --upgrade"
            return self.run_command(cmd, "Pip-Installation aus requirements.txt", timeout=600)
        else:
            # Fallback: Einzelne Packages
            essential_packages = [
                "PyYAML", "pathlib2", "tkinter", "requests", "numpy"
            ]
            
            success = True
            for package in essential_packages:
                cmd = f"{sys.executable} -m pip install {package} --upgrade"
                if not self.run_command(cmd, f"Installation von {package}", timeout=120):
                    success = False
                    
            return success
            
    def run_setup(self):
        """Führt FRAUSAR-Setup aus falls vorhanden"""
        setup_file = Path(__file__).parent / "frausar_setup.py"
        if setup_file.exists():
            cmd = f"{sys.executable} frausar_setup.py"
            return self.run_command(cmd, "FRAUSAR Setup-Prozess", timeout=300)
        else:
            self.log_message("⚠️ frausar_setup.py nicht gefunden - übersprungen", "WARN")
            return True
            
    def start_frausar_gui(self):
        """Startet die FRAUSAR GUI"""
        gui_file = Path(__file__).parent / "frausar_gui.py"
        if gui_file.exists():
            self.log_message("🚀 Starte FRAUSAR GUI...")
            
            try:
                # GUI in separatem Prozess starten
                subprocess.Popen([sys.executable, "frausar_gui.py"], 
                               cwd=Path(__file__).parent)
                self.log_message("GUI erfolgreich gestartet!", "SUCCESS")
                self.log_message("🎉 Sie können dieses Fenster jetzt schließen")
                
                # Auto-Close nach 3 Sekunden
                self.root.after(3000, self.root.quit)
                return True
            except Exception as e:
                self.log_message(f"Fehler beim Starten der GUI: {str(e)}", "ERROR")
                return False
        else:
            self.log_message("❌ frausar_gui.py nicht gefunden!", "ERROR")
            return False
            
    def setup_process(self):
        """Vollständiger Setup-Prozess"""
        try:
            self.disable_buttons()
            
            # Schritt 1: Dependencies prüfen
            if not self.check_dependencies():
                self.log_message("🔧 Starte Dependency-Installation...")
                
                # Schritt 2: Dependencies installieren
                if not self.install_dependencies():
                    self.log_message("❌ Dependency-Installation fehlgeschlagen!", "ERROR")
                    return False
                    
            # Schritt 3: FRAUSAR Setup
            if not self.run_setup():
                self.log_message("⚠️ Setup-Prozess hatte Probleme", "WARN")
                
            # Schritt 4: GUI starten
            if self.start_frausar_gui():
                self.log_message("🎉 FRAUSAR erfolgreich gestartet!", "SUCCESS")
                return True
            else:
                self.log_message("❌ GUI-Start fehlgeschlagen!", "ERROR")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Unerwarteter Fehler: {str(e)}", "ERROR")
            return False
        finally:
            self.enable_buttons()
            
    def start_setup_process(self):
        """Startet Setup-Prozess in separatem Thread"""
        def run_in_thread():
            success = self.setup_process()
            if not success:
                messagebox.showerror("Fehler", "Setup-Prozess fehlgeschlagen!\nPrüfen Sie das Log für Details.")
                
        threading.Thread(target=run_in_thread, daemon=True).start()
        
    def start_gui_only(self):
        """Startet nur die GUI ohne Setup"""
        self.log_message("⚡ Starte GUI direkt...")
        if self.start_frausar_gui():
            self.log_message("✅ GUI gestartet!", "SUCCESS")
        else:
            messagebox.showerror("Fehler", "GUI konnte nicht gestartet werden!\nVersuchen Sie den vollständigen Setup.")
            
    def run(self):
        """Startet den One-Click-Starter"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("👋 Benutzer-Abbruch", "WARN")
        except Exception as e:
            messagebox.showerror("Kritischer Fehler", f"Unerwarteter Fehler:\n{str(e)}")


def main():
    """Hauptfunktion"""
    # Prüfe ob wir im richtigen Verzeichnis sind
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Starte One-Click-Starter
    app = FRAUSAROneClickStarter()
    app.run()


if __name__ == "__main__":
    main() 