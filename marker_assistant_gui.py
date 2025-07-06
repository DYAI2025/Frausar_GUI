#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FRAUSAR Marker Assistant GUI
============================
Grafische Benutzeroberfläche für den intelligenten Marker-Assistenten
mit Master-Dokumentations-Generierung.

Features:
- One-Click Master-Export-Generierung
- Marker-Verwaltung und -Analyse
- Live-Preview der generierten Dateien
- Backup-Management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from datetime import datetime
import webbrowser

# Import des erweiterten MarkerAssistant
from marker_assistant_bot import MarkerAssistant

class MarkerAssistantGUI:
    """Grafische Benutzeroberfläche für den FRAUSAR Marker Assistant"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 FRAUSAR Marker Assistant - Master Generator")
        self.root.geometry("900x700")
        
        # Initialisiere MarkerAssistant
        self.assistant = MarkerAssistant()
        
        # Status-Variablen
        self.is_generating = False
        self.last_generation_results = {}
        
        self._setup_ui()
        self._setup_styles()
        
    def _setup_styles(self):
        """Konfiguriert die UI-Styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom Styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        style.configure('Big.TButton', font=('Arial', 12, 'bold'), padding=10)
        
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titel
        title_label = ttk.Label(main_frame, text="🤖 FRAUSAR Marker Assistant", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # === MASTER-GENERIERUNG SEKTION ===
        master_frame = ttk.LabelFrame(main_frame, text="📚 Master-Dokumentation Generierung", padding="10")
        master_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Beschreibung
        desc_text = ("Generiert automatisch alle Master-Dateien aus den vorhandenen Markern:\n"
                    "• marker_master_export.yaml/json - Zentrale Marker-Datenbank\n"
                    "• MARKER_SYSTEM_README.md - Detaillierte Systemdokumentation\n"
                    "• MARKER_MASTER_README.md - Marker-spezifische Dokumentation")
        
        desc_label = ttk.Label(master_frame, text=desc_text, justify=tk.LEFT)
        desc_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Output-Verzeichnis Auswahl
        output_frame = ttk.Frame(master_frame)
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(output_frame, text="Output-Verzeichnis:").grid(row=0, column=0, sticky=tk.W)
        
        self.output_var = tk.StringVar(value=str(Path.cwd()))
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=0, column=1, padx=(10, 5), sticky=(tk.W, tk.E))
        
        browse_btn = ttk.Button(output_frame, text="Durchsuchen...", 
                               command=self._browse_output_directory)
        browse_btn.grid(row=0, column=2, padx=(5, 0))
        
        output_frame.columnconfigure(1, weight=1)
        
        # Haupt-Generierungs-Button
        self.generate_btn = ttk.Button(master_frame, 
                                      text="🚀 Alle Master-Dateien generieren",
                                      style='Big.TButton',
                                      command=self._start_generation)
        self.generate_btn.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Progress Bar
        self.progress = ttk.Progressbar(master_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status Label
        self.status_var = tk.StringVar(value="Bereit zur Master-Generierung")
        self.status_label = ttk.Label(master_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=2)
        
        # === ERGEBNISSE SEKTION ===
        results_frame = ttk.LabelFrame(main_frame, text="📋 Generierte Dateien", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Datei-Liste mit Buttons
        self.results_tree = ttk.Treeview(results_frame, columns=('path', 'size'), show='tree headings', height=8)
        self.results_tree.heading('#0', text='Datei')
        self.results_tree.heading('path', text='Pfad')
        self.results_tree.heading('size', text='Größe')
        
        self.results_tree.column('#0', width=250)
        self.results_tree.column('path', width=300)
        self.results_tree.column('size', width=100)
        
        self.results_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar für Datei-Liste
        results_scroll = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        results_scroll.grid(row=0, column=3, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=results_scroll.set)
        
        # Buttons für Datei-Aktionen
        file_actions_frame = ttk.Frame(results_frame)
        file_actions_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.open_file_btn = ttk.Button(file_actions_frame, text="📄 Datei öffnen", 
                                       command=self._open_selected_file)
        self.open_file_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.open_folder_btn = ttk.Button(file_actions_frame, text="📁 Ordner öffnen", 
                                         command=self._open_output_folder)
        self.open_folder_btn.grid(row=0, column=1, padx=5)
        
        self.preview_btn = ttk.Button(file_actions_frame, text="👁 Preview", 
                                     command=self._preview_selected_file)
        self.preview_btn.grid(row=0, column=2, padx=5)
        
        # Neuer Button für GPT-YAML
        self.gpt_yaml_btn = ttk.Button(file_actions_frame, text="🤖 GPT-YAML generieren", 
                                      command=self._generate_gpt_yaml)
        self.gpt_yaml_btn.grid(row=0, column=3, padx=(5, 0))
        
        # === MARKER-STATISTIKEN SEKTION ===
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Marker-Statistiken", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=6, width=80)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Statistiken laden
        self._load_initial_stats()
        
        # Grid-Konfiguration für Responsive Design
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        master_frame.columnconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _browse_output_directory(self):
        """Öffnet Dialog zur Auswahl des Output-Verzeichnisses"""
        directory = filedialog.askdirectory(
            title="Output-Verzeichnis wählen",
            initialdir=self.output_var.get()
        )
        if directory:
            self.output_var.set(directory)
    
    def _start_generation(self):
        """Startet die Master-Dateien-Generierung in separatem Thread"""
        if self.is_generating:
            return
        
        output_dir = self.output_var.get()
        if not output_dir or not Path(output_dir).exists():
            messagebox.showerror("Fehler", "Bitte wählen Sie ein gültiges Output-Verzeichnis!")
            return
        
        # UI für Generierung vorbereiten
        self.is_generating = True
        self.generate_btn.configure(state='disabled')
        self.progress.start()
        self.status_var.set("Sammle Marker aus allen Verzeichnissen...")
        
        # Generierung in separatem Thread starten
        thread = threading.Thread(target=self._generate_master_files, args=(output_dir,))
        thread.daemon = True
        thread.start()
    
    def _generate_master_files(self, output_dir):
        """Generiert alle Master-Dateien (läuft in separatem Thread)"""
        try:
            # Status-Updates
            self.root.after(0, lambda: self.status_var.set("Sammle alle Marker..."))
            
            # Generiere alle Master-Dateien
            results = self.assistant.generate_all_master_files(output_dir)
            
            # UI Update im Main Thread
            self.root.after(0, lambda: self._generation_completed(results, None))
            
        except Exception as e:
            # Fehler-Handling im Main Thread
            self.root.after(0, lambda: self._generation_completed(None, str(e)))
    
    def _generation_completed(self, results, error):
        """Wird aufgerufen wenn die Generierung abgeschlossen ist"""
        # UI zurücksetzen
        self.is_generating = False
        self.generate_btn.configure(state='normal')
        self.progress.stop()
        
        if error:
            self.status_var.set(f"Fehler: {error}")
            messagebox.showerror("Generierungs-Fehler", f"Fehler bei der Master-Generierung:\n{error}")
            return
        
        if results:
            self.last_generation_results = results
            self.status_var.set(f"✅ {len(results)} Master-Dateien erfolgreich generiert!")
            
            # Aktualisiere Datei-Liste
            self._update_results_display(results)
            
            # Aktualisiere Statistiken
            self._update_stats_display()
            
            # Erfolgs-Nachricht
            message = f"Master-Dateien erfolgreich generiert:\n\n"
            for key, path in results.items():
                if isinstance(path, str):
                    file_name = Path(path).name
                    message += f"• {file_name}\n"
            
            messagebox.showinfo("Erfolgreich generiert", message)
    
    def _update_results_display(self, results):
        """Aktualisiert die Anzeige der generierten Dateien"""
        # Liste leeren
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Neue Einträge hinzufügen
        for key, path in results.items():
            if isinstance(path, str) and Path(path).exists():
                file_path = Path(path)
                file_size = self._format_file_size(file_path.stat().st_size)
                
                # Icon basierend auf Dateityp
                if file_path.suffix == '.yaml':
                    icon = "📄"
                elif file_path.suffix == '.json':
                    icon = "📊"
                elif file_path.suffix == '.md':
                    icon = "📝"
                else:
                    icon = "📁"
                
                display_name = f"{icon} {file_path.name}"
                
                self.results_tree.insert('', 'end', 
                                        text=display_name, 
                                        values=(str(file_path), file_size),
                                        tags=(str(file_path),))
    
    def _format_file_size(self, size_bytes):
        """Formatiert Dateigröße in lesbare Form"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _open_selected_file(self):
        """Öffnet die ausgewählte Datei im Standard-Editor"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Datei aus!")
            return
        
        file_path = self.results_tree.item(selection[0])['values'][0]
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{file_path}"')
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei konnte nicht geöffnet werden:\n{e}")
    
    def _open_output_folder(self):
        """Öffnet das Output-Verzeichnis im Datei-Explorer"""
        output_dir = self.output_var.get()
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS/Linux
                os.system(f'open "{output_dir}"')
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden:\n{e}")
    
    def _preview_selected_file(self):
        """Zeigt eine Vorschau der ausgewählten Datei"""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("Keine Auswahl", "Bitte wählen Sie eine Datei aus!")
            return
        
        file_path = self.results_tree.item(selection[0])['values'][0]
        self._show_file_preview(file_path)
    
    def _show_file_preview(self, file_path):
        """Zeigt Datei-Vorschau in separatem Fenster"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vorschau-Fenster erstellen
            preview_window = tk.Toplevel(self.root)
            preview_window.title(f"Vorschau: {Path(file_path).name}")
            preview_window.geometry("800x600")
            
            # Text-Widget mit Scrollbar
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            text_widget.insert(tk.END, content)
            text_widget.configure(state='disabled')  # Read-only
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Datei-Vorschau fehlgeschlagen:\n{e}")
    
    def _load_initial_stats(self):
        """Lädt initiale Marker-Statistiken"""
        try:
            # Sammle Marker-Statistiken
            self.assistant.collect_all_markers()
            self._update_stats_display()
        except Exception as e:
            self.stats_text.insert(tk.END, f"Fehler beim Laden der Statistiken: {e}")
    
    def _update_stats_display(self):
        """Aktualisiert die Statistiken-Anzeige"""
        try:
            self.stats_text.delete(1.0, tk.END)
            
            if not self.assistant.all_markers:
                self.stats_text.insert(tk.END, "Keine Marker geladen. Bitte erst Master-Dateien generieren.")
                return
            
            # Berechne Statistiken
            total_markers = len(self.assistant.all_markers)
            total_examples = sum(len(m.get('beispiele', [])) for m in self.assistant.all_markers.values())
            
            # Kategorien zählen
            categories = {}
            for marker_data in self.assistant.all_markers.values():
                cat = marker_data.get('kategorie', 'UNCATEGORIZED')
                categories[cat] = categories.get(cat, 0) + 1
            
            # Top Marker nach Beispielen
            top_markers = sorted(
                [(name, len(data.get('beispiele', []))) for name, data in self.assistant.all_markers.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
            
            # Statistiken formatieren
            stats_text = f"""📊 MARKER-STATISTIKEN
═══════════════════════════════════════

📈 Gesamt-Übersicht:
   • Marker insgesamt: {total_markers}
   • Beispiele insgesamt: {total_examples}
   • Durchschnitt pro Marker: {total_examples/total_markers:.1f} Beispiele

📂 Kategorien ({len(categories)}):"""
            
            for cat, count in sorted(categories.items()):
                percentage = (count / total_markers) * 100
                stats_text += f"\n   • {cat}: {count} ({percentage:.1f}%)"
            
            stats_text += f"\n\n🏆 Top Marker (nach Beispielen):"
            for name, count in top_markers:
                stats_text += f"\n   • {name}: {count} Beispiele"
            
            stats_text += f"\n\n⏰ Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            self.stats_text.insert(tk.END, f"Fehler bei Statistik-Update: {e}")
    
    def _generate_gpt_yaml(self):
        """Generiert eine vereinheitlichte YAML-Datei für GPT"""
        output_dir = self.output_var.get()
        if not output_dir:
            output_dir = str(Path.cwd())
        
        try:
            # Status Update
            self.status_var.set("Generiere vereinheitlichte YAML für GPT...")
            
            # Generiere die Datei
            output_file = self.assistant.generate_unified_yaml_for_gpt(
                str(Path(output_dir) / "marker_unified_for_gpt.yaml")
            )
            
            # Erfolgs-Nachricht
            self.status_var.set("✅ GPT-YAML erfolgreich generiert!")
            
            # Füge zu Ergebnisliste hinzu
            self._update_results_display({
                'gpt_yaml': output_file,
                'gpt_yaml_compact': str(Path(output_file).parent / "marker_unified_for_gpt_compact.yaml")
            })
            
            # Info-Dialog
            message = f"""GPT-YAML erfolgreich generiert!

📄 Hauptdatei: marker_unified_for_gpt.yaml
📄 Kompakte Version: marker_unified_for_gpt_compact.yaml

Die Dateien enthalten:
• {len(self.assistant.all_markers)} Marker im einheitlichen Format
• Alle Beispiele und Beschreibungen
• Statistiken und Kategorisierung
• Optimiert für GPT-Analyse

Du kannst die Datei jetzt an GPT übergeben für:
• Bestandsaufnahme aller Marker
• Analyse der Marker-Struktur
• Identifikation von Lücken
• Verbesserungsvorschläge"""
            
            messagebox.showinfo("GPT-YAML generiert", message)
            
        except Exception as e:
            self.status_var.set(f"Fehler: {str(e)}")
            messagebox.showerror("Fehler", f"Fehler beim Generieren der GPT-YAML:\n{str(e)}")

def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = MarkerAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 