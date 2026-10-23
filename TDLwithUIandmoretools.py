import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

FILE_NAME = "tasks.json"

def load_tasks():
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to decode JSON from the tasks file.")
        return []

def save_tasks(tasks):
    with open(FILE_NAME, "w") as file:
        json.dump(tasks, file, indent=4)

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("680x700")
        self.root.config(bg="#1e1e1e")

        self.tasks = load_tasks()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        title_label = tk.Label(root, text="My To-Do List", font=("Helvetica", 24, "bold"), bg="#1e1e1e", fg="#ffffff")
        title_label.pack(pady=20)
        
        input_frame = tk.Frame(root, bg="#1e1e1e")
        input_frame.pack(pady=10)
        
        self.task_entry = tk.Entry(input_frame, font=("Helvetica", 15), width=28, relief="solid", bd=1, bg="#2d2d2d", fg="#ffffff", insertbackground="white")
        self.task_entry.grid(row=0, column=0, padx=8, ipady=6)
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        
        add_button = tk.Button(input_frame, text="Add Task", font=("Helvetica", 13, "bold"), bg="#2e7d32", fg="white", padx=16, pady=6, relief="flat", command=self.add_task)
        add_button.grid(row=0, column=1, padx=8)
        
        list_frame = tk.Frame(root, bg="#1e1e1e")
        list_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=35)
        
        self.task_listbox = tk.Listbox(list_frame, font=("Helvetica", 15), bg="#2d2d2d", fg="#ffffff", selectbackground="#0d47a1", selectforeground="#ffffff", relief="solid", bd=1, highlightthickness=0)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.task_listbox.bind("<<ListboxSelect>>", self.on_task_select)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        
        action_frame = tk.Frame(root, bg="#1e1e1e")
        action_frame.pack(pady=20)
        
        complete_button = tk.Button(action_frame, text="Complete", font=("Helvetica", 12, "bold"), bg="#1565c0", fg="white", width=12, pady=10, relief="flat", command=self.complete_task)
        complete_button.grid(row=0, column=0, padx=6)
        
        undo_button = tk.Button(action_frame, text="Pending", font=("Helvetica", 12, "bold"), bg="#e65100", fg="white", width=12, pady=10, relief="flat", command=self.undo_task)
        undo_button.grid(row=0, column=1, padx=6)
        
        self.edit_button = tk.Button(action_frame, text="Edit Task", font=("Helvetica", 12, "bold"), bg="#6a1b9a", fg="white", width=12, pady=10, relief="flat", command=self.edit_task)
        self.edit_button.grid(row=0, column=2, padx=6)
        
        delete_button = tk.Button(action_frame, text="Delete", font=("Helvetica", 12, "bold"), bg="#c62828", fg="white", width=12, pady=10, relief="flat", command=self.delete_task)
        delete_button.grid(row=0, column=3, padx=6)
        
        self.update_task_listbox()

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for index, task in enumerate(self.tasks, start=1):
            status = "Done" if task["completed"] else "Pending"
            display_text = f"{index}.  {task['Title']}  [{status}]"
            self.task_listbox.insert(tk.END, display_text)
            if task["completed"]:
                self.task_listbox.itemconfig(tk.END, fg="#888888")
            else:
                self.task_listbox.itemconfig(tk.END, fg="#ffffff")
        self.edit_button.config(state=tk.DISABLED)

    def on_task_select(self, event):
        selected = self.task_listbox.curselection()
        if not selected:
            self.edit_button.config(state=tk.DISABLED)
            return
        task_index = selected[0]
        if self.tasks[task_index]["completed"]:
            self.edit_button.config(state=tk.DISABLED, bg="#444444")
        else:
            self.edit_button.config(state=tk.NORMAL, bg="#6a1b9a")

    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Task name cannot be empty.")
            return
        self.tasks.append({"Title": title, "completed": False})
        save_tasks(self.tasks)
        self.task_entry.delete(0, tk.END)
        self.update_task_listbox()

    def complete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to mark as completed.")
            return
        task_index = selected[0]
        if self.tasks[task_index]["completed"]:
            messagebox.showinfo("Info", "This task is already completed.")
            return
        self.tasks[task_index]["completed"] = True
        save_tasks(self.tasks)
        self.update_task_listbox()
        messagebox.showinfo("Success", f"Task '{self.tasks[task_index]['Title']}' marked as completed.")

    def undo_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to undo.")
            return
        task_index = selected[0]
        if not self.tasks[task_index]["completed"]:
            messagebox.showinfo("Info", "This task is already pending.")
            return
        self.tasks[task_index]["completed"] = False
        save_tasks(self.tasks)
        self.update_task_listbox()
        messagebox.showinfo("Success", f"Task '{self.tasks[task_index]['Title']}' marked as pending.")

    def edit_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            return
        task_index = selected[0]
        
        if self.tasks[task_index]["completed"]:
            return

        current_title = self.tasks[task_index]["Title"]

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Task")
        edit_window.geometry("420x220")
        edit_window.config(bg="#1e1e1e")
        edit_window.grab_set()

        label = tk.Label(
            edit_window, text="Enter new task name:", font=("Helvetica", 14, "bold"),
            bg="#1e1e1e", fg="#ffffff"
        )
        label.pack(pady=20)

        entry = tk.Entry(
            edit_window, font=("Helvetica", 14), width=24, relief="solid", bd=1, bg="#2d2d2d", fg="#ffffff", insertbackground="white"
        )
        entry.pack(ipady=5, pady=5)
        entry.insert(0, current_title)
        entry.focus()

        def save_edit(event=None):
            new_title = entry.get().strip()
            if not new_title:
                messagebox.showwarning("Warning", "Task name cannot be empty.", parent=edit_window)
                return
            self.tasks[task_index]["Title"] = new_title
            save_tasks(self.tasks)
            self.update_task_listbox()
            edit_window.destroy()
            messagebox.showinfo("Success", "Task updated successfully.")

        entry.bind("<Return>", save_edit)

        btn_frame = tk.Frame(edit_window, bg="#1e1e1e")
        btn_frame.pack(pady=15)

        save_button = tk.Button(btn_frame, text="Save", font=("Helvetica", 11, "bold"), bg="#2e7d32", fg="white", width=10, pady=5, relief="flat", command=save_edit)
        save_button.grid(row=0, column=0, padx=8)

        cancel_button = tk.Button(btn_frame, text="Cancel", font=("Helvetica", 11, "bold"), bg="#c62828", fg="white", width=10, pady=5, relief="flat", command=edit_window.destroy)
        cancel_button.grid(row=0, column=1, padx=8)

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        task_index = selected[0]
        deleted_task = self.tasks.pop(task_index)
        save_tasks(self.tasks)
        self.update_task_listbox()
        messagebox.showinfo("Success", f"Task '{deleted_task['Title']}' deleted successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
