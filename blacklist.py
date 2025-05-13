"""
Project Objective:
- License suspension and blacklist management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

# Sample data for demonstration (replace with real data as needed)
blacklist = [
    {"blacklist_id": "BL001", "driver_name": "John Doe", "license_no": "L12345", "reason": "Multiple Violations", "status": "Suspended"},
    {"blacklist_id": "BL002", "driver_name": "Jane Smith", "license_no": "L54321", "reason": "Unpaid Fines", "status": "Blacklisted"},
    {"blacklist_id": "BL003", "driver_name": "Carlos Reyes", "license_no": "L67890", "reason": "Fraudulent Documents", "status": "Blacklisted"},
]

def populate_table():
    for i in tree.get_children():
        tree.delete(i)
    for b in blacklist:
        tree.insert("", tk.END, values=(b["blacklist_id"], b["driver_name"], b["license_no"], b["reason"], b["status"]))

def add_blacklist():
    def save():
        bid = entry_bid.get().strip()
        driver = entry_driver.get().strip()
        license_no = entry_license.get().strip()
        reason = entry_reason.get().strip()
        status = status_var.get().strip()
        if not bid or not driver or not license_no or not reason or not status:
            messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
            return
        blacklist.append({"blacklist_id": bid, "driver_name": driver, "license_no": license_no, "reason": reason, "status": status})
        populate_table()
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add to Blacklist")
    add_win.geometry("350x350")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Blacklist ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_bid = tk.Entry(add_win, font=("Arial", 11))
    entry_bid.pack()
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_driver = tk.Entry(add_win, font=("Arial", 11))
    entry_driver.pack()
    tk.Label(add_win, text="License No:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_license = tk.Entry(add_win, font=("Arial", 11))
    entry_license.pack()
    tk.Label(add_win, text="Reason:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_reason = tk.Entry(add_win, font=("Arial", 11))
    entry_reason.pack()
    tk.Label(add_win, text="Status:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    status_var = tk.StringVar(value="Suspended")
    status_menu = ttk.Combobox(
        add_win, textvariable=status_var,
        values=["Suspended", "Blacklisted"],
        state="readonly", font=("Arial", 11)
    )
    status_menu.pack()
    tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

def remove_blacklist():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Remove", "Select a row to remove.", parent=root)
        return
    idx = tree.index(selected[0])
    del blacklist[idx]
    populate_table()

root = tk.Tk()
root.title("License Suspension & Blacklist Management")
root.geometry("1000x700")
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
        pass  # Already on this page
    elif name == "Violation Reports":
        root.destroy()
        subprocess.Popen([sys.executable, "violation_reports.py"])
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

title = tk.Label(main, text="License Suspension & Blacklist Management", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Blacklist ID", "Driver Name", "License No", "Reason", "Status")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=160)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

# Buttons
btn_frame = tk.Frame(main, bg="#f7faff")
btn_frame.pack(pady=(0, 10))
tk.Button(btn_frame, text="Add to Blacklist", command=add_blacklist, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Remove Selected", command=remove_blacklist, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

populate_table()
root.mainloop()
