import tkinter as tk
from tkinter import ttk
from random import randint, choice
import subprocess
import sys
import os

# Sample data (normally this would come from a database)
drivers = [
    {"name": "John Doe", "speeding": 4, "signal": 1, "parking": 2},
    {"name": "Jane Smith", "speeding": 1, "signal": 0, "parking": 0},
    {"name": "Carlos Reyes", "speeding": 5, "signal": 3, "parking": 1},
    {"name": "Fatima Khan", "speeding": 0, "signal": 2, "parking": 0},
    {"name": "Mike Lee", "speeding": 3, "signal": 0, "parking": 4},
]

def calculate_risk(driver):
    score = driver['speeding'] * 5 + driver['signal'] * 7 + driver['parking'] * 3
    if score >= 25:
        return "High"
    elif score >= 10:
        return "Medium"
    else:
        return "Low"

def populate_table():
    for i in tree.get_children():
        tree.delete(i)
    for driver in drivers:
        risk = calculate_risk(driver)
        tree.insert("", tk.END, values=(driver['name'], driver['speeding'], driver['signal'], driver['parking'], risk))

# Sidebar
root = tk.Tk()
root.title("Driver Analytics Dashboard")
root.geometry("900x700")
root.configure(bg="#f7faff")

sidebar = tk.Frame(root, width=210, bg="#1976d2")
sidebar.pack(side=tk.LEFT, fill=tk.Y)

def sidebar_action(name):
    if name == "Home":
        root.destroy()
        subprocess.Popen([sys.executable, "dashboard.py"])
    elif name == "Violations":
        root.destroy()
        subprocess.Popen([sys.executable, "violation_detector.py"])
    elif name == "Alerts":
        try:
            from AlertSystem import AlertSystem
            alert_system = AlertSystem()
            alert_system.set_root(root)
            alert_system.show_alerts()
        except Exception:
            tk.messagebox.showinfo("Alerts", "Alerts functionality coming soon.")
    elif name == "Driver Analytics":
        pass  # Already on this page
    elif name == "Training":
        tk.messagebox.showinfo("Training", "Training functionality coming soon.")
    elif name == "Reports":
        tk.messagebox.showinfo("Reports", "Reports functionality coming soon.")
    elif name == "Logout":
        root.destroy()
        subprocess.Popen([sys.executable, "main.py"])
    else:
        tk.messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

sidebar_items = [
    ("Home", "\u2302"),
    ("Violations", "\U0001F697"),
    ("Alerts", "\u26A0"),
    ("Driver Analytics", "\U0001F50E"),
    ("Training Woduns", "\U0001F4CA"),
    ("Reports", "\U0001F552"),
    ("Logout", "\u274C")
]

for text, icon in sidebar_items:
    lbl = tk.Label(
        sidebar, text=f"{icon} {text}", anchor="w", bg="#1976d2", fg="#fff",
        font=("Arial", 13), padx=24, pady=15, justify=tk.LEFT, cursor="hand2"
    )
    lbl.pack(fill=tk.X)
    lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#1565c0"))
    lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="#1976d2"))
    lbl.bind("<Button-1>", lambda e, name=text: sidebar_action(name))

# Main content
main = tk.Frame(root, bg="#f7faff")
main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

title = tk.Label(main, text="Driver Violation Analytics", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Name", "Speeding", "Signal Violation", "Illegal Parking", "Risk Level")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=10)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=130)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

btn_refresh = tk.Button(main, text="Refresh Data", command=populate_table,
                        font=("Arial", 11, "bold"), bg="#1976d2", fg="white",
                        activebackground="#1565c0", activeforeground="white",
                        width=18, bd=0, pady=7)
btn_refresh.pack(pady=(5, 8))

populate_table()
root.mainloop()
