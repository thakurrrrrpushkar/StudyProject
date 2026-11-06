import json
import os
import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

APP_DATA_DIR = Path(os.environ.get("APPDATA") or Path.home()) / "StudyTools"
DB_FILENAME = APP_DATA_DIR / "stickynotes.db"

# Old JSON file locations, checked only for a one-time import into the DB.
LEGACY_APPDATA_JSON = APP_DATA_DIR / "stickynotes.json"
LEGACY_SCRIPT_JSON = Path(__file__).with_name("stickynotes.json")


# ---------- database layer ----------

def get_connection():
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row   # lets us read rows like dicts, e.g. row["content"]
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            heading TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def _migrate_legacy_json_if_needed():
    """One-time import: if the database has no notes yet, and an old
    stickynotes.json exists, copy its notes into the database."""
    conn = get_connection()
    try:
        existing_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        if existing_count > 0:
            return

        legacy_path = None
        if LEGACY_APPDATA_JSON.exists():
            legacy_path = LEGACY_APPDATA_JSON
        elif LEGACY_SCRIPT_JSON.exists():
            legacy_path = LEGACY_SCRIPT_JSON

        if legacy_path is None:
            return

        with legacy_path.open("r", encoding="utf-8") as file:
            old_notes = json.load(file)

        for note in old_notes:
            heading = note.get("heading") if isinstance(note, dict) else None
            content = note.get("content", "") if isinstance(note, dict) else note
            created_at = note.get("created_at") if isinstance(note, dict) else None
            if not created_at:
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO notes (heading, content, created_at) VALUES (?, ?, ?)",
                (heading, content, created_at),
            )
        conn.commit()
    except (json.JSONDecodeError, OSError, sqlite3.Error):
        pass   # if migration fails for any reason, just start with an empty DB
    finally:
        conn.close()


def load_notes():
    """Returns a list of dicts: {id, heading, content, created_at}, oldest first."""
    init_db()
    _migrate_legacy_json_if_needed()
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, heading, content, created_at FROM notes ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def insert_note(heading, content):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute(
        "INSERT INTO notes (heading, content, created_at) VALUES (?, ?, ?)",
        (heading, content, created_at),
    )
    conn.commit()
    conn.close()


def update_note(note_id, heading, content):
    conn = get_connection()
    conn.execute(
        "UPDATE notes SET heading = ?, content = ? WHERE id = ?",
        (heading, content, note_id),
    )
    conn.commit()
    conn.close()


def delete_note_by_id(note_id):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()


# ---------- GUI layer ----------

class StickyNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sticky Notes")
        self.root.geometry("500x500")
        self.root.configure(bg="#2b2b2b")

        try:
            self.notes = load_notes()
        except (OSError, sqlite3.Error) as error:
            self.notes = []
            messagebox.showerror(
                "Unable to access notes",
                f"StudyTools could not access its notes database:\n{error}",
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

        for note in self.notes:
            self.render_note_card(note)

    def render_note_card(self, note):
        note_id = note["id"]
        heading = note.get("heading")
        content = note.get("content", "")
        created_at = note.get("created_at")

        card = tk.Frame(self.notes_frame, bg="#fff6a9", bd=0)
        card.pack(fill="x", pady=6, padx=4)

        # clicking anywhere on the card opens the edit dialog, keyed by the note's
        # database id (not its position in the list) so edits/deletes always hit
        # the right row even after notes are added or removed elsewhere
        card.bind("<Button-1>", lambda e, nid=note_id: self.open_edit_dialog(nid))

        inner = tk.Frame(card, bg="#fff6a9")
        inner.pack(fill="x", padx=10, pady=8)
        inner.bind("<Button-1>", lambda e, nid=note_id: self.open_edit_dialog(nid))

        if heading:
            heading_label = tk.Label(
                inner, text=heading, font=("Segoe UI", 11, "bold"),
                bg="#fff6a9", fg="#333333", anchor="w"
            )
            heading_label.pack(fill="x")
            heading_label.bind("<Button-1>", lambda e, nid=note_id: self.open_edit_dialog(nid))

        content_label = tk.Label(
            inner, text=content, font=("Segoe UI", 10), bg="#fff6a9",
            fg="#333333", anchor="w", justify="left", wraplength=400
        )
        content_label.pack(fill="x", pady=(2, 0))
        content_label.bind("<Button-1>", lambda e, nid=note_id: self.open_edit_dialog(nid))

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
            command=lambda nid=note_id: self.delete_note(nid)
        ).pack(side="right")

    # ---------- actions ----------

    def add_note(self):
        heading = simpledialog.askstring("Heading (optional)", "Enter a heading, or leave blank:")
        content = simpledialog.askstring("New Note", "Enter the note content:")
        if content and content.strip():
            try:
                insert_note(
                    heading.strip() if heading and heading.strip() else None,
                    content.strip(),
                )
                self.notes = load_notes()
                self.refresh_notes()
            except sqlite3.Error as error:
                messagebox.showerror(
                    "Unable to save notes",
                    f"StudyTools could not save your note:\n{error}",
                    parent=self.root,
                )
        elif content is not None:
            messagebox.showwarning("Empty note", "Note content cannot be empty.")

    def open_edit_dialog(self, note_id):
        note = next((n for n in self.notes if n["id"] == note_id), None)
        if note is None:
            return
        heading = note.get("heading") or ""
        content = note.get("content") or ""

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
        heading_entry.insert(0, heading)
        heading_entry.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(dialog, text="Content:", bg="#2b2b2b", fg="white", anchor="w").pack(
            fill="x", padx=10
        )
        content_box = tk.Text(dialog, font=("Segoe UI", 10), wrap="word", height=10)
        content_box.insert("1.0", content)   # pre-fill with EXISTING content
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
            try:
                update_note(note_id, new_heading if new_heading else None, new_content)
                self.notes = load_notes()
                self.refresh_notes()
                dialog.destroy()
            except sqlite3.Error as error:
                messagebox.showerror(
                    "Unable to save notes",
                    f"StudyTools could not save your changes:\n{error}",
                    parent=dialog,
                )

        tk.Button(
            button_bar, text="Save", bg="#4CAF50", fg="white", relief="flat",
            padx=14, pady=4, command=save_changes
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            button_bar, text="Cancel", bg="#555555", fg="white", relief="flat",
            padx=14, pady=4, command=dialog.destroy
        ).pack(side="right")

    def delete_note(self, note_id):
        confirm = messagebox.askyesno("Delete Note", "Delete this sticky note?")
        if confirm:
            try:
                delete_note_by_id(note_id)
                self.notes = load_notes()
                self.refresh_notes()
            except sqlite3.Error as error:
                messagebox.showerror(
                    "Unable to delete note",
                    f"StudyTools could not delete your note:\n{error}",
                    parent=self.root,
                )


if __name__ == "__main__":
    root = tk.Tk()
    app = StickyNotesApp(root)
    root.mainloop()