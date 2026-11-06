"""
Sticky Notes — Tkinter GUI version.

Click any note to open it in an edit box pre-filled with its current
content (so nothing is lost, unlike the CLI's full-overwrite prompt).
Uses the same stickynotes.json file format as stickynotesCLI.py, so
notes created in one are visible in the other.
"""

import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

APP_DATA_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "StudyTools"
FILENAME = APP_DATA_DIR / "stickynotes.json"
LEGACY_FILENAME = Path(__file__).with_name("stickynotes.json")


def load_notes():
    try:
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not FILENAME.exists() and LEGACY_FILENAME.exists():
            with LEGACY_FILENAME.open("r", encoding="utf-8") as file:
                notes = json.load(file)
            save_notes(notes)
            return notes
        if FILENAME.exists():
            with FILENAME.open("r", encoding="utf-8") as file:
                return json.load(file)
    except json.JSONDecodeError:
        return []
    return []


def save_notes(notes):
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    with FILENAME.open("w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4)


class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")
        self.root.geometry("500x500")
        self.root.configure(bg="#2b2b2b")

        try:
            self.notes = load_notes()
        except OSError as error:
            self.notes = []
            messagebox.showerror(
                "Unable to access notes",
                f"StudyTools could not access its notes file:\n{error}",
                parent=root,
            )

        # --- top bar ---
        top_bar = tk.Frame(root, bg="#2b2b2b")
        top_bar.pack(fill="x", padx=10, pady=10)

        tk.Label(
            top_bar, text="Sticky Notes", font=("Segoe UI", 16, "bold"),
            bg="#2b2b2b", fg="white"
        ).pack(side="left")

        tk.Button(
            top_bar, text="+ Add Note", command=self.add_note,
            bg="#4CAF50", fg="white", relief="flat", padx=10, pady=4
        ).pack(side="right")

        # --- scrollable notes area ---
        container = tk.Frame(root, bg="#2b2b2b")
        container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(container, bg="#2b2b2b", highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.notes_frame = tk.Frame(canvas, bg="#2b2b2b")

        self.notes_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.notes_frame, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_notes()

    # ---------- rendering ----------

    def refresh_notes(self):
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        if not self.notes:
            tk.Label(
                self.notes_frame, text="No sticky notes yet. Click '+ Add Note' to create one.",
                bg="#2b2b2b", fg="#999999", font=("Segoe UI", 10)
            ).pack(pady=20)
            return

        for index, note in enumerate(self.notes):
            self.render_note_card(index, note)

    def render_note_card(self, index, note):
        heading = note.get("heading") if isinstance(note, dict) else None
        content = note.get("content") if isinstance(note, dict) else note
        created_at = note.get("created_at") if isinstance(note, dict) else None

        card = tk.Frame(self.notes_frame, bg="#fff6a9", bd=0)
        card.pack(fill="x", pady=6, padx=4)

        # clicking anywhere on the card opens the edit dialog
        card.bind("<Button-1>", lambda e, i=index: self.open_edit_dialog(i))

        inner = tk.Frame(card, bg="#fff6a9")
        inner.pack(fill="x", padx=10, pady=8)
        inner.bind("<Button-1>", lambda e, i=index: self.open_edit_dialog(i))

        if heading:
            heading_label = tk.Label(
                inner, text=heading, font=("Segoe UI", 11, "bold"),
                bg="#fff6a9", fg="#333333", anchor="w"
            )
            heading_label.pack(fill="x")
            heading_label.bind("<Button-1>", lambda e, i=index: self.open_edit_dialog(i))

        content_label = tk.Label(
            inner, text=content, font=("Segoe UI", 10), bg="#fff6a9",
            fg="#333333", anchor="w", justify="left", wraplength=400
        )
        content_label.pack(fill="x", pady=(2, 0))
        content_label.bind("<Button-1>", lambda e, i=index: self.open_edit_dialog(i))

        meta_bar = tk.Frame(inner, bg="#fff6a9")
        meta_bar.pack(fill="x", pady=(6, 0))

        if created_at:
            tk.Label(
                meta_bar, text=created_at, font=("Segoe UI", 8),
                bg="#fff6a9", fg="#777777"
            ).pack(side="left")

        tk.Button(
            meta_bar, text="Delete", font=("Segoe UI", 8), bg="#e57373",
            fg="white", relief="flat", padx=6,
            command=lambda i=index: self.delete_note(i)
        ).pack(side="right")

    # ---------- actions ----------

    def add_note(self):
        heading = simpledialog.askstring("Heading (optional)", "Enter a heading, or leave blank:")
        content = simpledialog.askstring("New Note", "Enter the note content:")
        if content and content.strip():
            self.notes.append({
                "heading": heading.strip() if heading and heading.strip() else None,
                "content": content.strip(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            if self._save_notes():
                self.refresh_notes()
            else:
                self.notes.pop()
        elif content is not None:
            messagebox.showwarning("Empty note", "Note content cannot be empty.")

    def open_edit_dialog(self, index):
        note = self.notes[index]
        heading = note.get("heading", "") if isinstance(note, dict) else ""
        content = note.get("content", "") if isinstance(note, dict) else note

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note")
        dialog.geometry("400x350")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.root)
        dialog.grab_set()  # modal

        tk.Label(dialog, text="Heading:", bg="#2b2b2b", fg="white", anchor="w").pack(
            fill="x", padx=10, pady=(10, 0)
        )
        heading_entry = tk.Entry(dialog, font=("Segoe UI", 10))
        heading_entry.insert(0, heading or "")
        heading_entry.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(dialog, text="Content:", bg="#2b2b2b", fg="white", anchor="w").pack(
            fill="x", padx=10
        )
        content_box = tk.Text(dialog, font=("Segoe UI", 10), wrap="word", height=10)
        content_box.insert("1.0", content or "")   # pre-fill with EXISTING content
        content_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        content_box.focus_set()

        button_bar = tk.Frame(dialog, bg="#2b2b2b")
        button_bar.pack(fill="x", padx=10, pady=(0, 10))

        def save_changes():
            new_content = content_box.get("1.0", "end").strip()
            new_heading = heading_entry.get().strip()
            if not new_content:
                messagebox.showwarning("Empty note", "Note content cannot be empty.", parent=dialog)
                return
            if isinstance(note, dict):
                note["content"] = new_content
                note["heading"] = new_heading if new_heading else None
            else:
                self.notes[index] = {
                    "heading": new_heading if new_heading else None,
                    "content": new_content,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            if self._save_notes():
                self.refresh_notes()
                dialog.destroy()

        tk.Button(
            button_bar, text="Save", bg="#4CAF50", fg="white", relief="flat",
            padx=14, pady=4, command=save_changes
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            button_bar, text="Cancel", bg="#555555", fg="white", relief="flat",
            padx=14, pady=4, command=dialog.destroy
        ).pack(side="right")

    def delete_note(self, index):
        confirm = messagebox.askyesno("Delete Note", "Delete this sticky note?")
        if confirm:
            removed_note = self.notes.pop(index)
            if self._save_notes():
                self.refresh_notes()
            else:
                self.notes.insert(index, removed_note)

    def _save_notes(self):
        try:
            save_notes(self.notes)
            return True
        except OSError as error:
            messagebox.showerror(
                "Unable to save notes",
                f"StudyTools could not save your notes:\n{error}",
                parent=self.root,
            )
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()