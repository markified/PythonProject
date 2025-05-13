"""
Project Objective:
- Generate violation reports
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

# Sample data for demonstration (replace with real data as needed)
violation_reports = [
    {"report_id": "VR001", "driver_name": "John Doe", "vehicle_id": "A123", "violation": "Speeding", "date": "2024-05-01", "fine": 500, "status": "Paid"},
    {"report_id": "VR002", "driver_name": "Jane Smith", "vehicle_id": "B456", "violation": "Illegal Parking", "date": "2024-05-03", "fine": 300, "status": "Unpaid"},
    {"report_id": "VR003", "driver_name": "Carlos Reyes", "vehicle_id": "C789", "violation": "Signal Violation", "date": "2024-05-05", "fine": 400, "status": "Paid"},
    {"report_id": "VR004", "driver_name": "Fatima Khan", "vehicle_id": "D321", "violation": "Speeding", "date": "2024-05-07", "fine": 200, "status": "Unpaid"},
]

def populate_table():
    for i in tree.get_children():
        tree.delete(i)
    for v in violation_reports:
        tree.insert("", tk.END, values=(v["report_id"], v["driver_name"], v["vehicle_id"], v["violation"], v["date"], v["fine"], v["status"]))

def export_report():
    try:
        with open("violation_report_export.csv", "w") as f:
            f.write("Report ID,Driver Name,Vehicle ID,Violation,Date,Fine,Status\n")
            for v in violation_reports:
                f.write(f'{v["report_id"]},{v["driver_name"]},{v["vehicle_id"]},{v["violation"]},{v["date"]},{v["fine"]},{v["status"]}\n')
        messagebox.showinfo("Export", "Violation report exported as violation_report_export.csv")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export report: {e}")

root = tk.Tk()
root.title("Generate Violation Reports")
root.geometry("1100x700")
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
        root.destroy()
        subprocess.Popen([sys.executable, "record&tracking.py"])
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
        pass  # Already on this page
    elif name == "Logout":
        root.destroy()
    else:
        messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

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

title = tk.Label(main, text="Generate Violation Reports", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Report ID", "Driver Name", "Vehicle ID", "Violation", "Date", "Fine", "Status")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=140)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

# Buttons
btn_frame = tk.Frame(main, bg="#f7faff")
btn_frame.pack(pady=(0, 10))
tk.Button(btn_frame, text="Export Report", command=export_report, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

populate_table()
root.mainloop()
