"""
Project Objective:
- Record and track violations (speeding, illegal parking, etc.)
"""

import tkinter as tk
from tkinter import ttk
from random import randint, choice
import subprocess
import sys
import os

# Sample data for demonstration (replace with real data as needed)
violations = [
    {"driver_name": "John Doe", "vehicle_id": "A123", "violation_type": "Speeding", "count": 4},
    {"driver_name": "Jane Smith", "vehicle_id": "B456", "violation_type": "Illegal Parking", "count": 2},
    {"driver_name": "Carlos Reyes", "vehicle_id": "C789", "violation_type": "Signal Violation", "count": 3},
    {"driver_name": "Fatima Khan", "vehicle_id": "D321", "violation_type": "Speeding", "count": 1},
    {"driver_name": "Mike Lee", "vehicle_id": "E654", "violation_type": "Illegal Parking", "count": 4},
]

def populate_table():
    for i in tree.get_children():
        tree.delete(i)
    for v in violations:
        tree.insert("", tk.END, values=(v['driver_name'], v['vehicle_id'], v['violation_type'], v['count']))

root = tk.Tk()
root.title("Violation Record & Tracking")
root.geometry("900x700")
root.configure(bg="#f7faff")

# Sidebar
sidebar = tk.Frame(root, width=210, bg="#1976d2")
sidebar.pack(side=tk.LEFT, fill=tk.Y)

def sidebar_action(name):
    if name == "Dashboard":
        root.destroy()
        subprocess.Popen([sys.executable, "dashboard.py"])
    elif name == "Vehicle Registry":
        root.destroy()
        subprocess.Popen([sys.executable, "violation_detector.py"])
    elif name == "Record":
        pass  # Already on this page
    elif name == "Payments":
        root.destroy()
        subprocess.Popen([sys.executable, "payment.py"])
    elif name == "History Reports":
        root.destroy()
        subprocess.Popen([sys.executable, "reports.py"])
    elif name == "Blacklist":
        root.destroy()
        subprocess.Popen([sys.executable, "blacklist.py"])
    elif name == "Violation Reports":
        root.destroy()
        subprocess.Popen([sys.executable, "violation_reports.py"])
    elif name == "Logout":
        root.destroy()
    else:
        tk.messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

sidebar_items = [
    ("Dashboard", "\u2302"),
    ("Vehicle Registry", "\u26FD"),
    ("Record", "\U0001F50E"),
    ("Payments", "\U0001F4B3"),
    ("History Reports", "\U0001F4C8"),
    ("Blacklist", "\u26D4"),
    ("Violation Reports", "\U0001F4C4"),
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

title = tk.Label(main, text="Violation Record & Tracking", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Driver Name", "Vehicle ID", "Violation Type", "Count")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=180)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

def add_violation():
    def save():
        driver = entry_driver.get().strip()
        vehicle = entry_vehicle.get().strip()
        vtype = violation_type_var.get().strip()
        count = entry_count.get().strip()
        if not driver or not vehicle or not vtype or not count or not count.isdigit():
            tk.messagebox.showwarning("Input Error", "All fields are required and count must be a number.", parent=add_win)
            return
        violations.append({"driver_name": driver, "vehicle_id": vehicle, "violation_type": vtype, "count": int(count)})
        populate_table()
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add Violation")
    add_win.geometry("350x300")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_driver = tk.Entry(add_win, font=("Arial", 11))
    entry_driver.pack()
    tk.Label(add_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_vehicle = tk.Entry(add_win, font=("Arial", 11))
    entry_vehicle.pack()
    tk.Label(add_win, text="Violation Type:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    violation_type_var = tk.StringVar(value="Speeding")
    violation_type_menu = ttk.Combobox(
        add_win, textvariable=violation_type_var,
        values=["Speeding", "Signal Violation", "Illegal Parking"],
        state="readonly", font=("Arial", 11)
    )
    violation_type_menu.pack()
    tk.Label(add_win, text="Count:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_count = tk.Entry(add_win, font=("Arial", 11))
    entry_count.pack()
    tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

def delete_violation():
    selected = tree.selection()
    if not selected:
        tk.messagebox.showwarning("Delete", "Select a row to delete.", parent=root)
        return
    idx = tree.index(selected[0])
    del violations[idx]
    populate_table()

def edit_violation():
    selected = tree.selection()
    if not selected:
        tk.messagebox.showwarning("Edit", "Select a row to edit.", parent=root)
        return
    idx = tree.index(selected[0])
    violation = violations[idx]

    def save_edit():
        driver = entry_driver.get().strip()
        vehicle = entry_vehicle.get().strip()
        vtype = violation_type_var.get().strip()
        count = entry_count.get().strip()
        if not driver or not vehicle or not vtype or not count or not count.isdigit():
            tk.messagebox.showwarning("Input Error", "All fields are required and count must be a number.", parent=edit_win)
            return
        violations[idx] = {"driver_name": driver, "vehicle_id": vehicle, "violation_type": vtype, "count": int(count)}
        populate_table()
        edit_win.destroy()

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Violation")
    edit_win.geometry("350x300")
    edit_win.configure(bg="#f7faff")
    tk.Label(edit_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_driver = tk.Entry(edit_win, font=("Arial", 11))
    entry_driver.insert(0, violation["driver_name"])
    entry_driver.pack()
    tk.Label(edit_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_vehicle = tk.Entry(edit_win, font=("Arial", 11))
    entry_vehicle.insert(0, violation["vehicle_id"])
    entry_vehicle.pack()
    tk.Label(edit_win, text="Violation Type:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    violation_type_var = tk.StringVar(value=violation["violation_type"])
    violation_type_menu = ttk.Combobox(
        edit_win, textvariable=violation_type_var,
        values=["Speeding", "Signal Violation", "Illegal Parking"],
        state="readonly", font=("Arial", 11)
    )
    violation_type_menu.pack()
    tk.Label(edit_win, text="Count:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_count = tk.Entry(edit_win, font=("Arial", 11))
    entry_count.insert(0, str(violation["count"]))
    entry_count.pack()
    tk.Button(edit_win, text="Save", command=save_edit, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

# CRUD Buttons
btn_frame = tk.Frame(main, bg="#f7faff")
btn_frame.pack(pady=(0, 10))
tk.Button(btn_frame, text="Add Violation", command=add_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Edit Selected", command=edit_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Delete Selected", command=delete_violation, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

populate_table()
root.mainloop()
