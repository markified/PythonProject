"""
Project Objective:
- Fine payment processing
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys

# Sample data for demonstration (replace with real data as needed)
payments = [
    {"payment_id": "P001", "driver_name": "John Doe", "violation": "Speeding", "amount": 500, "status": "Unpaid"},
    {"payment_id": "P002", "driver_name": "Jane Smith", "violation": "Illegal Parking", "amount": 300, "status": "Paid"},
    {"payment_id": "P003", "driver_name": "Carlos Reyes", "violation": "Signal Violation", "amount": 400, "status": "Unpaid"},
]

def populate_table():
    for i in tree.get_children():
        tree.delete(i)
    for p in payments:
        tree.insert("", tk.END, values=(p["payment_id"], p["driver_name"], p["violation"], p["amount"], p["status"]))

def mark_as_paid():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Mark as Paid", "Select a payment to mark as paid.", parent=root)
        return
    idx = tree.index(selected[0])
    payments[idx]["status"] = "Paid"
    populate_table()

def add_payment():
    def save():
        pid = entry_pid.get().strip()
        driver = entry_driver.get().strip()
        violation = entry_violation.get().strip()
        amount = entry_amount.get().strip()
        if not pid or not driver or not violation or not amount or not amount.isdigit():
            messagebox.showwarning("Input Error", "All fields are required and amount must be a number.", parent=add_win)
            return
        payments.append({"payment_id": pid, "driver_name": driver, "violation": violation, "amount": int(amount), "status": "Unpaid"})
        populate_table()
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add Payment")
    add_win.geometry("350x300")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Payment ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_pid = tk.Entry(add_win, font=("Arial", 11))
    entry_pid.pack()
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_driver = tk.Entry(add_win, font=("Arial", 11))
    entry_driver.pack()
    tk.Label(add_win, text="Violation:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_violation = tk.Entry(add_win, font=("Arial", 11))
    entry_violation.pack()
    tk.Label(add_win, text="Amount:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_amount = tk.Entry(add_win, font=("Arial", 11))
    entry_amount.pack()
    tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

root = tk.Tk()
root.title("Fine Payment Processing")
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
        root.destroy()
        subprocess.Popen([sys.executable, "record&tracking.py"])
    elif name == "Payments":
        pass  # Already on this page
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

title = tk.Label(main, text="Fine Payment Processing", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Payment ID", "Driver Name", "Violation", "Amount", "Status")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=150)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

# Buttons
btn_frame = tk.Frame(main, bg="#f7faff")
btn_frame.pack(pady=(0, 10))
tk.Button(btn_frame, text="Add Payment", command=add_payment, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Mark as Paid", command=mark_as_paid, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

populate_table()
root.mainloop()
