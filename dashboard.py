"""
Project Objective:
- Vehicle registration and owner details
- Record and track violations (speeding, illegal parking, etc.)
- Fine payment processing
- Violation history and reports
- License suspension and blacklist management
- Generate violation reports
"""

import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM, Frame, Label, messagebox
import subprocess
import sys
import mysql.connector
from database import (
    get_violation_statistics,
    get_recent_violations,
    get_todays_violators_count,
    get_high_risk_drivers_count,
    get_active_alerts_count
)

def fetch_dashboard_data():
    try:
        violations = get_violation_statistics()
    except Exception:
        violations = []
    try:
        recent = get_recent_violations()
    except Exception:
        recent = []
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Count unique violators (distinct owner_name) who have at least one unpaid violation
        cursor.execute("""
            SELECT COUNT(DISTINCT owner_name)
            FROM violations
            WHERE status = 'Unpaid'
        """)
        total_violators = cursor.fetchone()[0]
        # High-risk drivers: owners with 3 or more unpaid violations
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT owner_name
                FROM violations
                WHERE status='Unpaid'
                GROUP BY owner_name
                HAVING COUNT(*) >= 3
            ) AS highrisk
        """)
        high_risk_drivers = cursor.fetchone()[0]
        # Blacklisted: count from blacklist table
        cursor.execute("""
            SELECT COUNT(*) FROM blacklist WHERE status='Blacklisted'
        """)
        blacklisted_total = cursor.fetchone()[0]
        conn.close()
    except Exception:
        total_violators = 0
        high_risk_drivers = 0
        blacklisted_total = 0

    return {
        "violations": violations,
        "recent": recent,
        "todays_violators": total_violators,
        "high_risk_drivers": high_risk_drivers,
        "blacklisted": blacklisted_total
    }

# Function to show the dashboard
def show_dashboard():
    data = fetch_dashboard_data()
    root = tk.Tk()
    root.title("Vehicle Violation & Monitoring System")
    root.geometry("1100x700")
    root.configure(bg="#f7faff")

    # Initialize AlertSystem and set root


    # Sidebar
    sidebar = Frame(root, width=210, bg="#1976d2")
    sidebar.pack(side=LEFT, fill=Y)

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
        lbl = Label(
            sidebar, text=f"{icon} {text}", anchor="w", bg="#1976d2", fg="#fff",
            font=("Arial", 13), padx=24, pady=15, justify=LEFT, cursor="hand2"
        )
        lbl.pack(fill=X)
        lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#1565c0"))
        lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="#1976d2"))
        lbl.bind("<Button-1>", lambda e, name=text: sidebar_action(name))

    # Main content
    main = Frame(root, bg="#f7faff")
    main.pack(side=LEFT, fill=BOTH, expand=True, padx=0, pady=0)

    # Stats row
    stats_row = Frame(main, bg="#f7faff")
    stats_row.pack(fill=X, padx=40, pady=(30, 10))
    for title, value in [
        ("Violators", data["todays_violators"]),
        ("High-Risk Drivers", data["high_risk_drivers"]),
        ("Blacklisted", data["blacklisted"])
    ]:
        stat = Frame(stats_row, bg="#fff", bd=0, relief="ridge", highlightbackground="#1976d2", highlightthickness=2)
        stat.pack(side=LEFT, expand=True, fill=BOTH, padx=12, pady=0)
        Label(stat, text=title, font=("Arial", 14, "bold"), fg="#1976d2", bg="#fff").pack(pady=(18, 0))
        Label(stat, text=str(value), font=("Arial", 32, "bold"), fg="#1565c0", bg="#fff").pack(pady=(5, 18))

    # Violation Record & Tracking Table (replace Violation Statistics Table)
    Label(main, text="Violation Record & Tracking", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
    columns = ("Driver Name", "Vehicle ID", "Violation Type", "Count", "Price", "Status")
    violation_table = ttk.Treeview(main, columns=columns, show='headings', height=8)
    for col in columns:
        violation_table.heading(col, text=col)
        violation_table.column(col, anchor="center", width=140)
    # Fetch violation records from DB (same as record&tracking.py)
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT owner_name, vehicle_id, violation_type, count, price, status FROM violations")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            violation_table.insert(
                "", "end",
                values=(row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else "")
            )
    except Exception:
        pass
    violation_table.pack(padx=40, pady=(0, 10), fill=X)

    # License Suspension & Blacklist Management Table (replace Recent Violations Table)
    Label(main, text="License Suspension & Blacklist Management", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
    columns_blacklist = ("Blacklist ID", "Driver Name", "Plate Number", "Reason", "Status")
    blacklist_table = ttk.Treeview(main, columns=columns_blacklist, show='headings', height=7)
    for col in columns_blacklist:
        blacklist_table.heading(col, text=col)
        blacklist_table.column(col, anchor="center", width=160)
    # Fetch blacklist records from DB (same as blacklist.py)
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT blacklist_id, driver_name, plate_number, reason, status FROM blacklist")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            blacklist_table.insert(
                "", "end",
                values=(row[0], row[1], row[2], row[3], row[4])
            )
    except Exception:
        pass
    blacklist_table.pack(padx=40, pady=(0, 20), fill=X)

    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
    style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

    root.mainloop()

if __name__ == '__main__':
    show_dashboard()
