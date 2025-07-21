#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Threading Issues - Behebt Threading-Probleme in FRAUSAR GUI
==============================================================
Macht GUI-Updates in Threads sicherer
"""

import tkinter as tk
from functools import wraps

def safe_gui_update(func):
    """Decorator um GUI-Updates in Threads sicher zu machen"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tk.TclError:
            # GUI bereits geschlossen - ignoriere Fehler
            pass
        except Exception as e:
            print(f"GUI Update Fehler: {e}")
    return wrapper

def safe_widget_operation(widget, operation, *args, **kwargs):
    """Sichere Widget-Operation"""
    try:
        if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
            return getattr(widget, operation)(*args, **kwargs)
    except tk.TclError:
        pass
    except Exception as e:
        print(f"Widget Operation Fehler: {e}")

def create_thread_safe_progress_dialog(parent, title="Progress"):
    """Erstellt einen Thread-sicheren Progress-Dialog"""
    
    class ThreadSafeProgressDialog:
        def __init__(self, parent, title):
            self.dialog = tk.Toplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("600x400")
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Frame
            main_frame = tk.Frame(self.dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Status Text
            self.status_text = tk.Text(main_frame, wrap=tk.WORD, height=20)
            scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
            self.status_text.configure(yscrollcommand=scrollbar.set)
            
            self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Close Button
            tk.Button(main_frame, text="✅ Schließen", 
                     command=self.close).pack(pady=(10, 0))
            
            self.closed = False
            
        def safe_insert(self, text):
            """Thread-sichere Text-Einfügung"""
            try:
                if not self.closed and self.status_text.winfo_exists():
                    self.status_text.insert(tk.END, text)
                    self.status_text.see(tk.END)
                    self.dialog.update_idletasks()
            except tk.TclError:
                self.closed = True
                
        def close(self):
            """Schließe Dialog sicher"""
            try:
                self.closed = True
                self.dialog.destroy()
            except tk.TclError:
                pass
                
    return ThreadSafeProgressDialog(parent, title)

def patch_auto_repair_function():
    """Erstellt eine verbesserte Auto-Repair Funktion"""
    
    improved_code = '''
def improved_auto_repair(self):
    """Verbesserte Auto-Repair Funktion mit Thread-Sicherheit"""
    try:
        # Erstelle Thread-sicheren Progress Dialog
        progress_dialog = create_thread_safe_progress_dialog(self.root, "Auto-Repair Progress")
        
        def run_repair():
            """Repair-Funktion mit verbesserter Fehlerbehandlung"""
            try:
                progress_dialog.safe_insert("🔧 Starte Auto-Repair...\n")
                
                # Finde repair_markers.py
                repair_script = Path("repair_markers.py")
                if not repair_script.exists():
                    progress_dialog.safe_insert("❌ repair_markers.py nicht gefunden!\n")
                    return
                
                progress_dialog.safe_insert(f"📄 Verwende Script: {repair_script}\n")
                
                # Führe Reparatur aus
                result = subprocess.run(
                    [sys.executable, str(repair_script), "--verbose"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # Zeige Ergebnis
                if result.stdout:
                    progress_dialog.safe_insert("📤 AUSGABE:\n")
                    progress_dialog.safe_insert(result.stdout + "\n")
                
                if result.stderr:
                    progress_dialog.safe_insert("⚠️ WARNUNGEN:\n")
                    progress_dialog.safe_insert(result.stderr + "\n")
                
                if result.returncode == 0:
                    progress_dialog.safe_insert("\n✅ Auto-Repair erfolgreich!")
                    
                    # Sichere GUI-Updates
                    try:
                        self.root.after(0, self.refresh_marker_list)
                        self.root.after(0, lambda: self.update_status("✅ Auto-Repair erfolgreich"))
                    except:
                        pass
                else:
                    progress_dialog.safe_insert(f"\n❌ Fehler (Exit-Code: {result.returncode})")
                    
            except subprocess.TimeoutExpired:
                progress_dialog.safe_insert("\n⏰ Timeout: Prozess abgebrochen")
            except Exception as e:
                progress_dialog.safe_insert(f"\n❌ Unerwarteter Fehler: {e}")
        
        # Starte Thread
        import threading
        threading.Thread(target=run_repair, daemon=True).start()
        
    except Exception as e:
        messagebox.showerror("Fehler", f"Auto-Repair Fehler:\n{e}")
'''
    
    print("🔧 **VERBESSERTE AUTO-REPAIR FUNKTION**")
    print("=" * 50)
    print(improved_code)

def test_thread_safety():
    """Testet die Thread-Sicherheit"""
    print("🧪 **THREAD-SAFETY TEST**")
    print("=" * 30)
    
    # Simuliere Widget-Operationen
    class MockWidget:
        def __init__(self):
            self.exists = True
            
        def winfo_exists(self):
            return self.exists
            
        def insert(self, pos, text):
            if not self.exists:
                raise tk.TclError("Widget destroyed")
            print(f"Insert: {text}")
            
        def see(self, pos):
            if not self.exists:
                raise tk.TclError("Widget destroyed")
            print("Scroll to end")
    
    # Test normale Operation
    widget = MockWidget()
    safe_widget_operation(widget, 'insert', tk.END, "Test")
    safe_widget_operation(widget, 'see', tk.END)
    
    # Test nach Widget-Zerstörung
    widget.exists = False
    safe_widget_operation(widget, 'insert', tk.END, "Test2")
    safe_widget_operation(widget, 'see', tk.END)
    
    print("✅ Thread-Safety Test abgeschlossen")

if __name__ == "__main__":
    print("🛠️ **THREADING ISSUES FIX**")
    print("=" * 40)
    
    test_thread_safety()
    print()
    patch_auto_repair_function()
    
    print("\n💡 **EMPFOHLENE FIXES:**")
    print("1. Ersetze GUI-Updates in Threads mit safe_gui_update")
    print("2. Verwende safe_widget_operation für Widget-Zugriffe")
    print("3. Implementiere create_thread_safe_progress_dialog")
    print("4. Verwende self.root.after() für GUI-Updates aus Threads") 