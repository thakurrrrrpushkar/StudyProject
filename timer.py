import tkinter as tk
import time
import json
import os
class StopwatchManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Stopwatch")
        self.root.geometry("360x320")
        self.root.resizable(False, False)
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00adb5"
        self.btn_bg = "#2d2d2d"
        self.btn_fg = "#ffffff"
        self.btn_active_bg = "#3a3a3a"
        self.root.configure(bg=self.bg_color)
        self.filename = "stopwatches.json"
        self.stopwatches = self.load_data()
        self.after_id = None
        self.show_home_screen()
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    for name in data:
                        data[name]["running"] = False
                        data[name]["start_time"] = 0
                    return data
            except Exception:
                return {}
        return {}
    def save_data(self):
        try:
            save_dict = {}
            current_time = time.time()
            for name, data in self.stopwatches.items():
                elapsed = data["elapsed_time"]
                if data["running"]:
                    elapsed += current_time - data["start_time"]
                save_dict[name] = {
                    "running": False,
                    "start_time": 0,
                    "elapsed_time": elapsed
                }
            with open(self.filename, "w") as f:
                json.dump(save_dict, f, indent=4)
        except Exception:
            pass
    def clear_window(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        for widget in self.root.winfo_children():
            widget.destroy()
    def show_home_screen(self):
        self.clear_window()
        self.root.title("Stopwatch")
        title_label = tk.Label(
            self.root, 
            text="Stopwatch Manager", 
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color, 
            fg=self.fg_color
        )
        title_label.pack(pady=(15, 5))
        create_btn = tk.Button(
            self.root,
            text="Create New Stopwatch",
            command=self.show_create_screen,
            bg=self.accent_color,
            fg="#1e1e1e",
            activebackground="#007f88",
            activeforeground=self.fg_color,
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5
        )
        create_btn.pack(pady=5)
        list_label = tk.Label(
            self.root,
            text="Your Stopwatches:",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        list_label.pack(anchor="w", padx=30, pady=(5, 2))
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
        canvas = tk.Canvas(frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        if not self.stopwatches:
            empty_lbl = tk.Label(
                scrollable_frame,
                text="No stopwatches created yet.",
                font=("Helvetica", 9, "italic"),
                bg=self.bg_color,
                fg="#888888"
            )
            empty_lbl.pack(pady=10)
        else:
            for name in self.stopwatches.keys():
                row_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
                row_frame.pack(pady=3, fill=tk.X)
                
                btn = tk.Button(
                    row_frame,
                    text=name,
                    command=lambda n=name: self.show_stopwatch_screen(n),
                    bg=self.btn_bg,
                    fg=self.btn_fg,
                    activebackground=self.btn_active_bg,
                    activeforeground=self.btn_fg,
                    font=("Helvetica", 10),
                    relief="flat",
                    anchor="w",
                    padx=10,
                    pady=4,
                    width=17
                )
                btn.pack(side=tk.LEFT, padx=(0, 5))
                del_btn = tk.Button(
                    row_frame,
                    text="Delete",
                    command=lambda n=name: self.delete_stopwatch(n),
                    bg="#ff5252",
                    fg="#ffffff",
                    activebackground="#ff7979",
                    activeforeground="#ffffff",
                    font=("Helvetica", 9, "bold"),
                    relief="flat",
                    padx=6,
                    pady=4
                )
                del_btn.pack(side=tk.LEFT)
    def delete_stopwatch(self, name):
        if name in self.stopwatches:
            del self.stopwatches[name]
            self.save_data()
            self.show_home_screen()
    def show_create_screen(self):
        if len(self.stopwatches) >= 3:
            self.clear_window()
            self.root.title("Stopwatch")
            title_label = tk.Label(
                self.root, 
                text="Limit Reached", 
                font=("Helvetica", 16, "bold"),
                bg=self.bg_color, 
                fg=self.fg_color
            )
            title_label.pack(pady=(35, 10))
            limit_label = tk.Label(
                self.root,
                text="You cannot create more than 3 stopwatches.",
                font=("Helvetica", 10),
                bg=self.bg_color,
                fg="#ff6b6b"
            )
            limit_label.pack(pady=10)
            back_btn = tk.Button(
                self.root,
                text="Back to Home",
                command=self.show_home_screen,
                bg=self.accent_color,
                fg="#1e1e1e",
                activebackground="#007f88",
                activeforeground=self.fg_color,
                font=("Helvetica", 10, "bold"),
                relief="flat",
                padx=10,
                pady=5
            )
            back_btn.pack(pady=15)
            return
        self.clear_window()
        self.root.title("Stopwatch")
        title_label = tk.Label(
            self.root, 
            text="Name Your Stopwatch", 
            font=("Helvetica", 16, "bold"),
            bg=self.bg_color, 
            fg=self.fg_color
        )
        title_label.pack(pady=(35, 10))
        self.name_entry = tk.Entry(
            self.root, 
            font=("Helvetica", 12), 
            justify="center",
            bg="#2d2d2d", 
            fg=self.fg_color, 
            insertbackground=self.fg_color,
            relief="flat"
        )
        self.name_entry.pack(ipadx=10, ipady=5, pady=10)
        self.name_entry.focus()
        self.name_entry.bind("<Return>", lambda event: self.save_new_stopwatch())
        submit_btn = tk.Button(
            self.root, 
            text="Create", 
            command=self.save_new_stopwatch,
            bg=self.accent_color,
            fg="#1e1e1e",
            activebackground="#007f88",
            activeforeground=self.fg_color,
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=10,
            pady=5
        )
        submit_btn.pack(pady=10)
        back_btn = tk.Button(
            self.root,
            text="Back to Home",
            command=self.show_home_screen,
            bg=self.bg_color,
            fg="#888888",
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Helvetica", 9),
            relief="flat"
        )
        back_btn.pack(pady=5)
    def save_new_stopwatch(self):
        if len(self.stopwatches) >= 3:
            self.show_home_screen()
            return
        name = self.name_entry.get().strip()
        if not name:
            name = "Stopwatch"
        base_name = name
        counter = 1
        while name in self.stopwatches:
            name = f"{base_name} ({counter})"
            counter += 1
        self.stopwatches[name] = {
            "running": False,
            "start_time": 0,
            "elapsed_time": 0
        }
        self.save_data()
        self.show_stopwatch_screen(name)
    def show_stopwatch_screen(self, name):
        self.clear_window()
        self.current_stopwatch_name = name
        self.root.title("Stopwatch")
        self.name_label = tk.Label(
            self.root, 
            text=name.upper(), 
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color, 
            fg=self.accent_color
        )
        self.name_label.pack(pady=(20, 0))
        self.label = tk.Label(
            self.root, 
            text="00:00:00.00", 
            font=("Helvetica", 26, "bold"),
            bg=self.bg_color, 
            fg=self.fg_color
        )
        self.label.pack(pady=10)
        button_frame = tk.Frame(self.root, bg=self.bg_color)
        button_frame.pack(pady=10)
        btn_config = {
            "width": 7,
            "bg": self.btn_bg,
            "fg": self.btn_fg,
            "activebackground": self.btn_active_bg,
            "activeforeground": self.btn_fg,
            "relief": "flat",
            "bd": 0,
            "font": ("Helvetica", 10, "bold")
        }
        self.start_button = tk.Button(button_frame, text="Start", command=self.start, **btn_config)
        self.start_button.grid(row=0, column=0, padx=4)
        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop, state=tk.DISABLED, **btn_config)
        self.stop_button.grid(row=0, column=1, padx=4)
        self.reset_button = tk.Button(button_frame, text="Reset", command=self.reset, **btn_config)
        self.reset_button.grid(row=0, column=2, padx=4)
        name_frame = tk.Frame(self.root, bg=self.bg_color)
        name_frame.pack(pady=5)
        self.rename_entry = tk.Entry(
            name_frame,
            font=("Helvetica", 9),
            justify="center",
            bg="#2d2d2d",
            fg=self.fg_color,
            insertbackground=self.fg_color,
            relief="flat",
            width=15
        )
        self.rename_entry.insert(0, name)
        self.rename_entry.pack(side=tk.LEFT, padx=5)
        rename_btn = tk.Button(
            name_frame,
            text="Change Name",
            command=self.change_name,
            bg=self.btn_bg,
            fg=self.btn_fg,
            activebackground=self.btn_active_bg,
            activeforeground=self.btn_fg,
            font=("Helvetica", 8),
            relief="flat"
        )
        rename_btn.pack(side=tk.LEFT, padx=5)
        home_btn = tk.Button(
            self.root, 
            text="Home", 
            command=self.show_home_screen,
            bg=self.bg_color,
            fg="#888888",
            activebackground=self.bg_color,
            activeforeground=self.fg_color,
            font=("Helvetica", 9),
            relief="flat"
        )
        home_btn.pack(pady=5)
        data = self.stopwatches[self.current_stopwatch_name]
        if data["running"]:
            self.start_button.config(state=tk.DISABLED, bg="#333333", fg="#777777")
            self.stop_button.config(state=tk.NORMAL, bg=self.btn_bg, fg=self.btn_fg)
            self.update_clock()
        else:
            elapsed = data["elapsed_time"]
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 100)
            self.label.config(text=f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}")
            if elapsed > 0:
                self.start_button.config(state=tk.NORMAL, bg=self.btn_bg, fg=self.btn_fg)
                self.stop_button.config(state=tk.DISABLED, bg="#333333", fg="#777777")
    def update_clock(self):
        data = self.stopwatches[self.current_stopwatch_name]
        if data["running"]:
            elapsed = time.time() - data["start_time"] + data["elapsed_time"]
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 100)
            time_string = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
            if hasattr(self, 'label') and self.label.winfo_exists():
                self.label.config(text=time_string)
                self.after_id = self.root.after(50, self.update_clock)
    def start(self):
        data = self.stopwatches[self.current_stopwatch_name]
        if not data["running"]:
            data["running"] = True
            data["start_time"] = time.time()
            self.update_clock()
            self.save_data()
            self.start_button.config(state=tk.DISABLED, bg="#333333", fg="#777777")
            self.stop_button.config(state=tk.NORMAL, bg=self.btn_bg, fg=self.btn_fg)
    def stop(self):
        data = self.stopwatches[self.current_stopwatch_name]
        if data["running"]:
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            data["elapsed_time"] = time.time() - data["start_time"] + data["elapsed_time"]
            data["running"] = False
            self.save_data()
            self.start_button.config(state=tk.NORMAL, bg=self.btn_bg, fg=self.btn_fg)
            self.stop_button.config(state=tk.DISABLED, bg="#333333", fg="#777777")
    def reset(self):
        data = self.stopwatches[self.current_stopwatch_name]
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        data["running"] = False
        data["elapsed_time"] = 0
        data["start_time"] = 0
        self.save_data()
        if hasattr(self, 'label') and self.label.winfo_exists():
            self.label.config(text="00:00:00")
            self.start_button.config(state=tk.NORMAL, bg=self.btn_bg, fg=self.btn_fg)
            self.stop_button.config(state=tk.DISABLED, bg="#333333", fg="#777777")
    def change_name(self):
        new_name = self.rename_entry.get().strip()
        if not new_name or new_name == self.current_stopwatch_name:
            return
        base_name = new_name
        counter = 1
        while new_name in self.stopwatches:
            new_name = f"{base_name} ({counter})"
            counter += 1
        data = self.stopwatches.pop(self.current_stopwatch_name)
        self.stopwatches[new_name] = data
        self.current_stopwatch_name = new_name
        self.save_data()
        self.name_label.config(text=new_name.upper())
if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchManager(root)
    root.mainloop()
