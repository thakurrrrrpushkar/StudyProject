import tkinter as tk
window = tk.Tk()
window.geometry("1920x1080")
window.resizable(True, True)
lbl = tk.Label(window, text="StudyTools", font = ("Helvetica", 50, "bold"), fg="#423C3C")
lbl.pack()
window.title("StudyTools Subapplication")
window.mainloop()
