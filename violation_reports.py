"""
Project Objective:
- Generate violation reports
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import mysql.connector

# Sample data for demonstration (replace with real data as needed)
violation_reports = []

def fetch_violation_reports_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.payment_id, 
                p.owner_name, 
                v.vehicle_id, 
                p.violation_type, 
                DATE_FORMAT(p.timestamp, '%Y-%m-%d'), 
                p.amount, 
                p.status 
            FROM payments p
            LEFT JOIN vehicles v ON v.owner_name = p.owner_name
            ORDER BY p.timestamp DESC
            LIMIT 100
        """)
        rows = cursor.fetchall()
        # Fetch suspended and blacklisted drivers
        cursor.execute("""
            SELECT driver_name, plate_number, status
            FROM blacklist
            WHERE status IN ('Suspended', 'Blacklisted')
        """)
        bl_rows = cursor.fetchall()
        conn.close()
        reports = [
            {
                "report_id": row[0],
                "driver_name": row[1],
                "vehicle_id": row[2] if row[2] is not None else "",
                "violation": row[3],
                "date": row[4],
                "fine": row[5],
                "status": row[6]
            }
            for row in rows
        ]
        # Add suspended/blacklisted as extra rows
        for bl in bl_rows:
            reports.append({
                "report_id": "",
                "driver_name": bl[0],
                "vehicle_id": bl[1],
                "violation": "",
                "date": "",
                "fine": "",
                "status": bl[2]
            })
       
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to fetch violation reports:\n{e}")
        return []

def populate_table():
    violation_reports = fetch_violation_reports_from_db()
    for i in tree.get_children():
        tree.delete(i)
    for v in violation_reports:
        tree.insert("", tk.END, values=(v["report_id"], v["driver_name"], v["vehicle_id"], v["violation"], v["date"], v["fine"], v["status"]))

def export_report():
    try:
        export_data = fetch_violation_reports_from_db()
        with open("violation_report_export.csv", "w", encoding="utf-8") as f:
            f.write("Report ID,Driver Name,Vehicle ID,Violation,Date,Fine,Status\n")
            for v in export_data:
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
        subprocess.Popen([sys.executable, "history_reports.py"])
    elif name == "Blacklist":
        root.destroy()
        subprocess.Popen([sys.executable, "blacklist.py"])
    elif name == "Violation Reports":
        pass  # Already on this page
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

def add_blacklist():
    def save():
        # Replace 'license_no' with 'plate_number'
        plate_number = entry_plate_number.get().strip()
        driver_name = entry_driver_name.get().strip()
        reason = entry_reason.get().strip()
        if not plate_number or not driver_name or not reason:
            messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
            return
        # Save to database or list as needed
        # Example: blacklist.append({"plate_number": plate_number, "driver_name": driver_name, "reason": reason})
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add to Blacklist")
    add_win.geometry("350x250")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Plate Number:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_plate_number = tk.Entry(add_win, font=("Arial", 11))
    entry_plate_number.pack()
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_driver_name = tk.Entry(add_win, font=("Arial", 11))
    entry_driver_name.pack()
    tk.Label(add_win, text="Reason:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_reason = tk.Entry(add_win, font=("Arial", 11))
    entry_reason.pack()
    tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)
