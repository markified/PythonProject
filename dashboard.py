import tkinter as tk
from tkinter import ttk, BOTH, LEFT, RIGHT, Y, X, TOP, BOTTOM, Frame, Label, messagebox
import subprocess
import sys
import mysql.connector

from AlertSystem import AlertSystem
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
        todays_violators = get_todays_violators_count()
    except Exception:
        todays_violators = 0
    try:
        high_risk_drivers = get_high_risk_drivers_count()
    except Exception:
        high_risk_drivers = 0
    try:
        active_alerts = get_active_alerts_count()
    except Exception:
        active_alerts = 0

    return {
        "violations": violations,
        "recent": recent,
        "todays_violators": todays_violators,
        "high_risk_drivers": high_risk_drivers,
        "active_alerts": active_alerts
    }

# Function to show the dashboard
def show_dashboard():
    data = fetch_dashboard_data()
    root = tk.Tk()
    root.title("Vehicle Violation & Monitoring System")
    root.geometry("1100x700")
    root.configure(bg="#f7faff")

    # Initialize AlertSystem and set root
    alert_system = AlertSystem()
    alert_system.set_root(root)

    # Sidebar
    sidebar = Frame(root, width=210, bg="#1976d2")
    sidebar.pack(side=LEFT, fill=Y)

    def sidebar_action(name):
        if name == "Home":
            root.destroy()
            subprocess.Popen([sys.executable, "dashboard.py"])
        elif name == "Violations":
            root.destroy()
            subprocess.Popen([sys.executable, "violation_detector.py"])
        elif name == "Alerts":
            alert_system.show_alerts()
        elif name == "Driver Analytics":
            root.destroy()
            subprocess.Popen([sys.executable, "driver_analytics.py"])
        elif name == "Training":
            messagebox.showinfo("Training", "Training functionality coming soon.")
        elif name == "Reports":
            messagebox.showinfo("Reports", "Reports functionality coming soon.")
        elif name == "Logout":
            root.destroy()
            subprocess.Popen([sys.executable, "auth.py"])
        else:
            messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

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
        ("Today's Violators", data["todays_violators"]),
        ("High-Risk Drivers", data["high_risk_drivers"]),
        ("Active Alerts", data["active_alerts"])
    ]:
        stat = Frame(stats_row, bg="#fff", bd=0, relief="ridge", highlightbackground="#1976d2", highlightthickness=2)
        stat.pack(side=LEFT, expand=True, fill=BOTH, padx=12, pady=0)
        Label(stat, text=title, font=("Arial", 14, "bold"), fg="#1976d2", bg="#fff").pack(pady=(18, 0))
        Label(stat, text=str(value), font=("Arial", 32, "bold"), fg="#1565c0", bg="#fff").pack(pady=(5, 18))

    # Violation Statistics Table
    Label(main, text="Violation Statistics", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
    stats_table = ttk.Treeview(main, columns=("Type", "Count"), show="headings", height=5)
    stats_table.heading("Type", text="Violation Type")
    stats_table.heading("Count", text="Count")
    stats_table.column("Type", width=200, anchor="center")
    stats_table.column("Count", width=100, anchor="center")
    for v in data["violations"]:
        stats_table.insert("", "end", values=(v[0], v[1]))
    stats_table.pack(padx=40, pady=(0, 10), fill=X)

    # Recent Violations Table
    Label(main, text="Recent Violations", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1976d2").pack(pady=(10, 0))
    recent_table = ttk.Treeview(main, columns=("ID", "Vehicle ID", "Driver ID", "Type", "Details", "Timestamp"), show="headings", height=7)
    for col, w in zip(
        ["ID", "Vehicle ID", "Driver ID", "Type", "Details", "Timestamp"],
        [50, 120, 100, 120, 200, 180]
    ):
        recent_table.heading(col, text=col)
        recent_table.column(col, width=w, anchor="center")
    for r in data["recent"]:
        recent_table.insert("", "end", values=(r[0], r[1], r[5], r[2], r[3], str(r[4])))
    recent_table.pack(padx=40, pady=(0, 20), fill=X)

    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
    style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

    root.mainloop()

if __name__ == '__main__':
    show_dashboard()
