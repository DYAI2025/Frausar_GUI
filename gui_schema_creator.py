#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Schema Creator - Interaktiver Wizard zur Erstellung von Analyse-Schemata
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import os
from schema_creator_controller import SchemaCreatorController
import json
import re

class SchemaCreatorWindow(tk.Toplevel):
    """
    Ein Toplevel-Fenster, das den Nutzer durch die Erstellung eines
    neuen Analyse-Schemas führt (Wizard-Interface).
    """
    def __init__(self, parent, assistant):
        super().__init__(parent)
        self.title("Analyse-Schema-Creator")
        self.geometry("1100x800")
        self.parent = parent
        self.assistant = assistant
        self.controller = SchemaCreatorController(self.assistant)
        self.current_step = 0

        # Datenspeicher für das neue Schema
        self.schema_data = {
            'name': '',
            'description': '',
            'template': None,
            'markers': [],
            'detectors': []
        }
        
        self.all_markers_list = [] # Cache für alle Marker-Namen

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self._create_widgets()
        self._load_templates()

    def _create_widgets(self):
        """Erstellt die UI-Elemente für den Wizard."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook für die Wizard-Schritte
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Erstelle die einzelnen Schritte als Tabs
        self._create_step1_domain()
        self._create_step2_markers()
        self._create_step3_detectors() # NEU
        self._create_step4_review()   # NEU
        
        # Deaktiviere alle Tabs außer dem ersten
        for i in range(1, self.notebook.index('end')):
            self.notebook.tab(i, state='disabled')

        # Navigationsbuttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        self.prev_button = ttk.Button(button_frame, text="<< Zurück", command=self.prev_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(button_frame, text="Weiter >>", command=self.next_step)
        self.next_button.pack(side=tk.RIGHT, padx=5)

        self.finish_button = ttk.Button(button_frame, text="Schema erstellen", command=self._finish_creation, state=tk.DISABLED)
        self.finish_button.pack(side=tk.RIGHT, padx=5)
        
    def _create_step1_domain(self):
        """UI für Schritt 1: Domäne, Name und Beschreibung - überarbeitet für bessere Übersicht."""
        step1_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(step1_frame, text="1. Domäne definieren")

        ttk.Label(step1_frame, text="Schritt 1: Grundlegende Schema-Informationen", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(step1_frame, text="Definieren Sie hier den Zweck und die Identität Ihres neuen Analyse-Schemas.", wraplength=800, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        # --- Rahmen 1: Identität ---
        identity_frame = ttk.LabelFrame(step1_frame, text="Schema-Identität", padding="15")
        identity_frame.pack(fill=tk.X, pady=(0, 15))

        # Schema-Name
        ttk.Label(identity_frame, text="Name des Analyse-Schemas (z.B. 'Toxische Kommunikationsmuster'):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.schema_name_entry = ttk.Entry(identity_frame, width=80, font=('Arial', 10))
        self.schema_name_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Beschreibung
        ttk.Label(identity_frame, text="Beschreibung (Wichtig für KI-Vorschläge! Beschreiben Sie genau, was analysiert werden soll):", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.schema_desc_text = tk.Text(identity_frame, height=5, font=('Arial', 10))
        self.schema_desc_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # --- Rahmen 2: Vorlage ---
        template_frame = ttk.LabelFrame(step1_frame, text="Vorlage (Optional)", padding="15")
        template_frame.pack(fill=tk.X)
        
        ttk.Label(template_frame, text="Wählen Sie eine bestehende Vorlage, um die Konfiguration zu beschleunigen.").pack(anchor=tk.W, pady=(0, 10))
        
        combo_frame = ttk.Frame(template_frame)
        combo_frame.pack(fill=tk.X)
        
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(combo_frame, textvariable=self.template_var, state="readonly")
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        browse_button = ttk.Button(combo_frame, text="Durchsuchen...", command=self._browse_for_template)
        browse_button.pack(side=tk.LEFT, padx=(10, 0))

    def _create_step2_markers(self):
        """UI für Schritt 2: Marker auswählen"""
        step2_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(step2_frame, text="2. Marker auswählen")

        ttk.Label(step2_frame, text="Schritt 2: Marker für die Analyse auswählen und gewichten", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        marker_selection_frame = ttk.Frame(step2_frame)
        marker_selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte: Verfügbare Marker
        left_frame = ttk.LabelFrame(marker_selection_frame, text="Verfügbare Marker", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT)
        self.marker_search_var = tk.StringVar()
        self.marker_search_var.trace('w', self.filter_available_markers) # Aktiviert
        search_entry = ttk.Entry(search_frame, textvariable=self.marker_search_var)
        search_entry.pack(fill=tk.X, expand=True, padx=5)

        self.available_markers_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.available_markers_listbox.pack(fill=tk.BOTH, expand=True)

        # Mittlere Spalte: Buttons
        middle_frame = ttk.Frame(marker_selection_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        add_button = ttk.Button(middle_frame, text=">>", command=self.add_marker)
        add_button.pack(pady=5)
        remove_button = ttk.Button(middle_frame, text="<<", command=self.remove_marker)
        remove_button.pack(pady=5)
        
        # Rechte Spalte: Ausgewählte Marker
        right_frame = ttk.LabelFrame(marker_selection_frame, text="Marker im Schema", padding="10")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.selected_markers_listbox = tk.Listbox(right_frame)
        self.selected_markers_listbox.pack(fill=tk.BOTH, expand=True)
        
        # NEU: Button für KI-Vorschläge
        ai_suggestion_button = ttk.Button(right_frame, text="🤖 KI-basierte Marker vorschlagen", command=self.run_ai_suggestions)
        ai_suggestion_button.pack(fill=tk.X, pady=(5, 0))

    def _create_step3_detectors(self):
        """UI für Schritt 3: Detektoren auswählen"""
        step3_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(step3_frame, text="3. Detektoren auswählen")

        ttk.Label(step3_frame, text="Schritt 3: Detektoren für die Analyse auswählen", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        detector_selection_frame = ttk.Frame(step3_frame)
        detector_selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Linke Spalte: Verfügbare Detektoren
        left_frame = ttk.LabelFrame(detector_selection_frame, text="Verfügbare Detektoren", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.available_detectors_listbox = tk.Listbox(left_frame, selectmode=tk.EXTENDED)
        self.available_detectors_listbox.pack(fill=tk.BOTH, expand=True)

        # Mittlere Spalte: Buttons
        middle_frame = ttk.Frame(detector_selection_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Commands für Buttons hinzufügen
        add_button = ttk.Button(middle_frame, text=">>", command=self.add_detector)
        add_button.pack(pady=5)
        remove_button = ttk.Button(middle_frame, text="<<", command=self.remove_detector)
        remove_button.pack(pady=5)
        
        # Rechte Spalte: Ausgewählte Detektoren
        right_frame = ttk.LabelFrame(detector_selection_frame, text="Detektoren im Schema", padding="10")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.selected_detectors_listbox = tk.Listbox(right_frame, selectmode=tk.EXTENDED)
        self.selected_detectors_listbox.pack(fill=tk.BOTH, expand=True)

    def _create_step4_review(self):
        """UI für Schritt 4: Review und Validierung"""
        step4_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(step4_frame, text="4. Überprüfung & Abschluss")

        ttk.Label(step4_frame, text="Schritt 4: Überprüfen Sie Ihr Analyse-Schema", font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Haupt-Frame für die Übersicht
        review_frame = ttk.Frame(step4_frame)
        review_frame.pack(fill=tk.BOTH, expand=True)

        # Linke Seite: Zusammenfassung
        summary_frame = ttk.LabelFrame(review_frame, text="Zusammenfassung", padding="10")
        summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.summary_text = tk.Text(summary_frame, height=20, width=50, state=tk.DISABLED, font=('Consolas', 10))
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Rechte Seite: Validierungs-Checkliste
        validation_frame = ttk.LabelFrame(review_frame, text="Validierungs-Checkliste", padding="10")
        validation_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        
        self.validation_checks_frame = ttk.Frame(validation_frame)
        self.validation_checks_frame.pack(fill=tk.BOTH, expand=True)
        
        # Platzhalter für die Checks
        ttk.Label(self.validation_checks_frame, text="[ ] Schema-Name ist gültig").pack(anchor=tk.W)
        ttk.Label(self.validation_checks_frame, text="[ ] Mindestens 5 Marker ausgewählt").pack(anchor=tk.W)
        ttk.Label(self.validation_checks_frame, text="[ ] Mindestens 1 Detektor ausgewählt").pack(anchor=tk.W)
        ttk.Label(self.validation_checks_frame, text="[ ] Keine fehlenden Marker-Referenzen").pack(anchor=tk.W)

    def _load_templates(self):
        """Lädt verfügbare Schema-Vorlagen aus dem templates-Ordner."""
        templates_path = Path("analysis_schemas/templates")
        if templates_path.exists():
            templates = ["(Keine Vorlage)"] + [f.name for f in templates_path.glob("*.json")]
            self.template_combo['values'] = templates
            self.template_combo.set(templates[0])
        else:
            self.template_combo['values'] = ["(Keine Vorlagen gefunden)"]
            self.template_combo.set("(Keine Vorlagen gefunden)")
            self.template_combo.config(state='disabled')
            
    def add_marker(self):
        """Fügt ausgewählte Marker zum Schema hinzu."""
        selected_indices = self.available_markers_listbox.curselection()
        for i in selected_indices:
            marker = self.available_markers_listbox.get(i)
            if marker not in self.selected_markers_listbox.get(0, tk.END):
                self.selected_markers_listbox.insert(tk.END, marker)
    
    def remove_marker(self):
        """Entfernt ausgewählte Marker aus dem Schema."""
        selected_indices = self.selected_markers_listbox.curselection()
        # Rückwärts iterieren, um Index-Probleme zu vermeiden
        for i in sorted(selected_indices, reverse=True):
            self.selected_markers_listbox.delete(i)

    def filter_available_markers(self, *args):
        """Filtert die Liste der verfügbaren Marker basierend auf der Sucheingabe."""
        search_term = self.marker_search_var.get().lower()
        
        # Leere die aktuelle Liste
        self.available_markers_listbox.delete(0, tk.END)
        
        if not search_term:
            # Zeige alle Marker, wenn die Suche leer ist
            for marker_name in self.all_markers_list:
                self.available_markers_listbox.insert(tk.END, marker_name)
        else:
            # Zeige nur passende Marker
            for marker_name in self.all_markers_list:
                if search_term in marker_name.lower():
                    self.available_markers_listbox.insert(tk.END, marker_name)

    def add_detector(self):
        """Fügt ausgewählte Detektoren zum Schema hinzu."""
        selected_indices = self.available_detectors_listbox.curselection()
        for i in selected_indices:
            detector = self.available_detectors_listbox.get(i)
            if detector not in self.selected_detectors_listbox.get(0, tk.END):
                self.selected_detectors_listbox.insert(tk.END, detector)

    def remove_detector(self):
        """Entfernt ausgewählte Detektoren aus dem Schema."""
        selected_indices = self.selected_detectors_listbox.curselection()
        for i in sorted(selected_indices, reverse=True):
            self.selected_detectors_listbox.delete(i)

    def next_step(self):
        """Geht zum nächsten Schritt im Wizard."""
        if self.current_step < self.notebook.index('end') - 1:
            # Schritt-spezifische Aktionen vor dem Wechsel
            if self.current_step == 0: # Nach Domänen-Definition
                name = self.schema_name_entry.get().strip()
                desc = self.schema_desc_text.get(1.0, tk.END).strip()
                if not name:
                    messagebox.showerror("Fehler", "Bitte geben Sie einen Namen für das Schema ein.")
                    return
                self.schema_data['name'] = name
                self.schema_data['description'] = desc
                self.schema_data['template'] = self.template_var.get()
                self._populate_marker_step()

            elif self.current_step == 1: # Nach Marker-Auswahl
                self.schema_data['markers'] = list(self.selected_markers_listbox.get(0, tk.END))
                self._populate_detector_step()
                
            elif self.current_step == 2: # Nach Detektor-Auswahl
                self.schema_data['detectors'] = list(self.selected_detectors_listbox.get(0, tk.END))
                self._populate_review_step()

            # Allgemeiner Schrittwechsel
            self.current_step += 1
            self.notebook.tab(self.current_step, state='normal')
            self.notebook.select(self.current_step)
            self.prev_button.config(state=tk.NORMAL)
            
            if self.current_step == self.notebook.index('end') - 1:
                self.next_button.config(state=tk.DISABLED)
                self.finish_button.config(state=tk.NORMAL)
    
    def _populate_marker_step(self):
        """Füllt den Marker-Auswahl-Schritt mit Daten."""
        # 1. Alle Marker laden
        all_markers_data = self.controller._get_all_markers()
        self.all_markers_list = sorted(all_markers_data.keys())
        
        # 2. Vorschläge vom Controller holen
        suggested_markers = self.controller.suggest_markers(
            description=self.schema_data['description'],
            name=self.schema_data['name']
        )
        
        # 3. Listboxen leeren
        self.available_markers_listbox.delete(0, tk.END)
        self.selected_markers_listbox.delete(0, tk.END)
        
        # 4. Listboxen füllen
        for marker_name in self.all_markers_list:
            if marker_name not in suggested_markers:
                self.available_markers_listbox.insert(tk.END, marker_name)
                
        for marker_name in suggested_markers:
            self.selected_markers_listbox.insert(tk.END, marker_name)
            
        # Korrigierter Aufruf der Status-Update-Funktion
        if self.assistant and self.assistant.update_status_callback:
            self.assistant.update_status_callback(f"{len(suggested_markers)} Marker vorgeschlagen für Schema '{self.schema_data['name']}'.")

    def _populate_detector_step(self):
        """Füllt den Detektor-Auswahl-Schritt mit Daten."""
        all_detectors = self.controller._get_all_detectors()
        all_detector_names = [data.get('file_path', name) for name, data in all_detectors.items()]
        
        suggested_detectors = self.controller.suggest_detectors(self.schema_data['markers'])
        
        self.available_detectors_listbox.delete(0, tk.END)
        self.selected_detectors_listbox.delete(0, tk.END)
        
        for name in sorted(all_detector_names):
            if name not in suggested_detectors:
                self.available_detectors_listbox.insert(tk.END, name)
                
        for name in suggested_detectors:
            self.selected_detectors_listbox.insert(tk.END, name)
            
        if self.assistant and self.assistant.update_status_callback:
            self.assistant.update_status_callback(f"{len(suggested_detectors)} Detektoren vorgeschlagen.")

    def _populate_review_step(self):
        """Füllt die Review-Seite mit der Zusammenfassung und Validierung."""
        # 1. Zusammenfassung generieren und anzeigen
        summary = self.controller.build_summary_text(self.schema_data)
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        # 2. Validierung durchführen und anzeigen
        validation_results = self.controller.validate_configuration(self.schema_data)
        
        # Alte Checks löschen
        for widget in self.validation_checks_frame.winfo_children():
            widget.destroy()
            
        all_valid = True
        for check in validation_results:
            icon = "✅" if check['valid'] else "❌"
            color = "green" if check['valid'] else "red"
            ttk.Label(self.validation_checks_frame, text=f"{icon} {check['text']}", foreground=color).pack(anchor=tk.W)
            if not check['valid']:
                all_valid = False
        
        # Finish-Button nur aktivieren, wenn alles valide ist
        self.finish_button.config(state=tk.NORMAL if all_valid else tk.DISABLED)

    def prev_step(self):
        """Geht zum vorherigen Schritt im Wizard."""
        if self.current_step > 0:
            self.notebook.tab(self.current_step, state='disabled')
            self.current_step -= 1
            self.notebook.select(self.current_step)
            self.next_button.config(state=tk.NORMAL)
            self.finish_button.config(state=tk.DISABLED)

            if self.current_step == 0:
                self.prev_button.config(state=tk.DISABLED)

    def on_close(self):
        """Wird aufgerufen, wenn das Fenster geschlossen wird."""
        if messagebox.askokcancel("Schließen", "Möchten Sie den Schema-Creator wirklich schließen? Nicht gespeicherte Änderungen gehen verloren."):
            self.destroy()

    def run_ai_suggestions(self):
        """Startet den Prozess für KI-basierte Marker-Vorschläge."""
        if self.assistant and self.assistant.update_status_callback:
            self.assistant.update_status_callback("🤖 Frage LLM nach Marker-Vorschlägen...")
        
        # Holen der aktuellen Schema-Daten
        name = self.schema_data.get('name', 'Unbenanntes Schema')
        description = self.schema_data.get('description', 'Keine Beschreibung')

        # Rufe die Controller-Methode auf
        try:
            suggestions = self.controller.suggest_markers_with_llm(description, name)
            if self.assistant and self.assistant.update_status_callback:
                self.assistant.update_status_callback(f"✅ {len(suggestions)} Vorschläge vom LLM erhalten.")

            if suggestions:
                self._show_ai_suggestion_dialog(suggestions)
            else:
                messagebox.showinfo("KI-Vorschläge", "Das LLM konnte keine passenden Vorschläge generieren.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist bei der Kommunikation mit dem LLM aufgetreten:\n{e}")
            if self.assistant and self.assistant.update_status_callback:
                self.assistant.update_status_callback("❌ Fehler bei der LLM-Anfrage.")

    def _show_ai_suggestion_dialog(self, suggestions: list):
        """Zeigt einen Dialog an, um vom LLM vorgeschlagene Marker auszuwählen."""
        dialog = tk.Toplevel(self)
        dialog.title("🤖 KI-generierte Marker-Vorschläge")
        dialog.geometry("700x500")
        dialog.transient(self)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Wähle die Marker aus, die du zum Schema hinzufügen möchtest:", 
                  font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))

        # Scrollbarer Bereich für die Checkboxen
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        suggestion_vars = []
        for suggestion in suggestions:
            var = tk.BooleanVar()
            frame = ttk.Frame(scrollable_frame, padding=(0, 5))
            cb = ttk.Checkbutton(frame, text=suggestion['marker_name'], variable=var)
            cb.pack(anchor=tk.W)
            desc_label = ttk.Label(frame, text=suggestion['beschreibung'], wraplength=600, justify=tk.LEFT, foreground="gray")
            desc_label.pack(anchor=tk.W, padx=(20, 0))
            frame.pack(fill=tk.X, pady=5)
            suggestion_vars.append((var, suggestion['marker_name']))

        # Buttons
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        def add_selected():
            added_count = 0
            for var, name in suggestion_vars:
                if var.get():
                    # Füge zur Liste der ausgewählten Marker hinzu (verhindere Duplikate)
                    if name not in self.selected_markers_listbox.get(0, tk.END):
                        self.selected_markers_listbox.insert(tk.END, name)
                        added_count += 1
            
            if self.assistant and self.assistant.update_status_callback:
                self.assistant.update_status_callback(f"👍 {added_count} KI-Vorschläge zum Schema hinzugefügt.")
            dialog.destroy()

        ttk.Button(button_frame, text="Ausgewählte hinzufügen", command=add_selected).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _finish_creation(self):
        """Baut das Schema-JSON, speichert es und schließt den Wizard."""
        try:
            # 1. Finale JSON-Struktur vom Controller erstellen lassen
            final_schema_json = self.controller.build_schema_json(self.schema_data)
            
            # 2. Dateinamen generieren (sicher für Dateisysteme)
            base_name = re.sub(r'[^a-zA-Z0-9_-]', '', self.schema_data['name'].replace(' ', '_'))
            filename = f"{base_name}_schema.json"
            
            # 3. Datei im Zielordner speichern
            output_path = Path("analysis_schemas") / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_schema_json, f, indent=2, ensure_ascii=False)
                
            # 4. Erfolgsmeldung und Abschluss
            if self.assistant and self.assistant.update_status_callback:
                self.assistant.update_status_callback(f"✅ Neues Schema '{filename}' erfolgreich gespeichert.")
            
            messagebox.showinfo("Erfolg", f"Das Analyse-Schema wurde erfolgreich erstellt und unter\n{output_path}\ngespeichert.")
            
            self.destroy() # Schließt den Wizard
            
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", f"Das Schema konnte nicht gespeichert werden:\n{e}")
            if self.assistant and self.assistant.update_status_callback:
                self.assistant.update_status_callback("❌ Fehler beim Speichern des Schemas.")

if __name__ == '__main__':
    # Demo zum Testen des Fensters
    root = tk.Tk()
    root.title("FRAUSAR Hauptfenster (Demo)")
    
    # Mock Assistant für Testzwecke
    class MockAssistant:
        def collect_all_markers(self):
            return {
                'GASLIGHTING_MARKER': {'beschreibung': 'Realität verdrehen', 'tags': ['manipulation']},
                'LOVE_BOMBING_MARKER': {'beschreibung': 'Übermäßige Zuneigung', 'tags': ['manipulation', 'liebe']},
                'ISOLATION_MARKER': {'beschreibung': 'Sozial isolieren', 'tags': ['kontrolle']},
                'FINANCIAL_REQUEST_MARKER': {'beschreibung': 'Nach Geld fragen', 'tags': ['betrug']},
            }
            
        def update_status_callback(self, message):
            print(f"[STATUS UPDATE]: {message}")
            
    mock_assistant = MockAssistant()
    
    def open_creator():
        creator_window = SchemaCreatorWindow(root, mock_assistant)
        creator_window.grab_set()
        
    test_button = ttk.Button(root, text="Neues Analyse-Schema erstellen", command=open_creator)
    test_button.pack(padx=50, pady=50)
    
    root.mainloop() 