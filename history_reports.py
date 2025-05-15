"""
Project Objective:
- Violation history and reports
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import mysql.connector

def fetch_violation_history_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Fetch violation records history
        cursor.execute("""
            SELECT 
                violation_id,
                vehicle_id,
                violation_type,
                owner_name,
                count,
                price,
                timestamp
            FROM violations
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        violation_rows = cursor.fetchall()

        # Fetch payment/violation report history (as before)
        cursor.execute("""
            SELECT 
                p.payment_id,
                v.owner_name,
                v.vehicle_id,
                p.violation_type,
                p.amount,
                p.status,
                p.timestamp,
                vl.count,
                vl.price
            FROM payments p
            LEFT JOIN vehicles v ON v.owner_name = p.owner_name
            LEFT JOIN violations vl ON vl.violation_type = p.violation_type AND vl.owner_name = p.owner_name
            ORDER BY p.timestamp DESC, p.payment_id DESC
            LIMIT 100
        """)
        payment_rows = cursor.fetchall()
        conn.close()

        # Compose lists for each table
        violation_history = [
            {
                "violation_id": row[0],
                "vehicle_id": row[1],
                "violation_type": row[2],
                "owner_name": row[3],
                "count": row[4],
                "price": row[5],
                "date": row[6].strftime("%Y-%m-%d %H:%M") if row[6] else ""
            }
            for row in violation_rows
        ]
        payment_history = [
            {
                "report_id": row[0],
                "driver_name": row[1],
                "vehicle_id": row[2],
                "violation": row[3],
                "amount": row[4],
                "status": row[5],
                "date": row[6].strftime("%Y-%m-%d %H:%M") if row[6] else "",
                "violation_count": row[7] if row[7] is not None else "",
                "violation_price": row[8] if row[8] is not None else ""
            }
            for row in payment_rows
        ]
        return violation_history, payment_history
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to fetch history:\n{e}")
        return [], []

def populate_table():
    violation_history, payment_history = fetch_violation_history_from_db()
    # Violation Table
    for i in tree_violation.get_children():
        tree_violation.delete(i)
    for v in violation_history:
        tree_violation.insert("", tk.END, values=(
            v["violation_id"], v["vehicle_id"], v["violation_type"], v["owner_name"], v["count"], v["price"], v["date"]
        ))
    # Payment/Report Table
    for i in tree.get_children():
        tree.delete(i)
    for v in payment_history:
        tree.insert("", tk.END, values=(
            v["report_id"], v["driver_name"], v["vehicle_id"], v["violation"], v["amount"], v["status"], v["date"], v["violation_count"], v["violation_price"]
        ))

def refresh_and_show():
    populate_table()
    root.deiconify()
    root.lift()

root = tk.Tk()
root.title("Violation History & Reports")
root.geometry("1250x700")
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
        subprocess.Popen([sys.executable, "history_reports.py"])
    elif name == "Blacklist":
        root.destroy()
        subprocess.Popen([sys.executable, "blacklist.py"])
    elif name == "Violation Reports":
        root.destroy()
        subprocess.Popen([sys.executable, "violation_reports.py"])
    elif name == "Logout":
        root.destroy()
        subprocess.Popen([sys.executable, "auth.py"])
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

title = tk.Label(main, text="Violation History & Reports", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

# Violation Records History Table
tk.Label(main, text="Violation Records History", font=("Arial", 14, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
frame_violation = tk.Frame(main, bg="#f7faff")
frame_violation.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
columns_violation = ("Violation ID", "Vehicle ID", "Violation Type", "Owner Name", "Count", "Price", "Date")
tree_violation = ttk.Treeview(frame_violation, columns=columns_violation, show='headings', height=6)
for col in columns_violation:
    tree_violation.heading(col, text=col)
    tree_violation.column(col, anchor=tk.CENTER, width=120)
tree_violation.pack(fill=tk.BOTH, expand=True)

# Payment/Report Table (already present)
tk.Label(main, text="Recent Payments & Violation Reports", font=("Arial", 14, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
columns = ("Report ID", "Driver Name", "Vehicle ID", "Violation", "Amount", "Status", "Date", "Violation Count", "Violation Price")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=6)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER, width=120)
tree.pack(fill=tk.BOTH, expand=True)

# Style for Treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

populate_table()
root.mainloop()
