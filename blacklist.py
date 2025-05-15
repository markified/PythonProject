"""
Project Objective:
- License suspension and blacklist management
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import uuid


def populate_table():
    # Fetch all blacklist data from the database and show in the table
    global blacklist
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                blacklist_id VARCHAR(50) PRIMARY KEY,
                driver_name VARCHAR(100),
                plate_number VARCHAR(50),
                reason VARCHAR(255),
                status VARCHAR(20)
            )
        """)
        cursor.execute("SELECT blacklist_id, driver_name, plate_number, reason, status FROM blacklist")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            blacklist.append({
                "blacklist_id": row[0],
                "driver_name": row[1],
                "plate_number": row[2],
                "reason": row[3],
                "status": row[4]
            })
    except Exception:
        pass
    for i in tree.get_children():
        tree.delete(i)
    for b in blacklist:
        tree.insert("", tk.END, values=(b["blacklist_id"], b["driver_name"], b["plate_number"], b["reason"], b["status"]))

def fetch_driver_names_and_plates():
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Only fetch drivers with 3 or more unpaid violations
        cursor.execute("""
            SELECT v.owner_name, v.Plate_number
            FROM vehicles v
            WHERE v.owner_name IN (
                SELECT owner_name
                FROM violations
                WHERE status = 'Unpaid'
                GROUP BY owner_name
                HAVING COUNT(*) >= 3
            )
        """)
        rows = cursor.fetchall()
        conn.close()
        driver_names = sorted(set(row[0] for row in rows if row[0]))
        plate_numbers = sorted(set(row[1] for row in rows if row[1]))
        return driver_names, plate_numbers
    except Exception:
        return [], []

def add_blacklist():
    def save():
        bid = entry_bid_var.get().strip()
        driver = driver_var.get().strip()
        plate_number = plate_var.get().strip()
        reason = entry_reason.get().strip()
        status = status_var.get().strip()
        if not bid or not driver or not plate_number or not reason or not status:
            messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
            return
        # Store in database
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blacklist (
                    blacklist_id VARCHAR(50) PRIMARY KEY,
                    driver_name VARCHAR(100),
                    plate_number VARCHAR(50),
                    reason VARCHAR(255),
                    status VARCHAR(20)
                )
            """)
            cursor.execute(
                "INSERT INTO blacklist (blacklist_id, driver_name, plate_number, reason, status) VALUES (%s, %s, %s, %s, %s)",
                (bid, driver, plate_number, reason, status)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save blacklist to database:\n{e}", parent=add_win)
            return
        blacklist.append({"blacklist_id": bid, "driver_name": driver, "plate_number": plate_number, "reason": reason, "status": status})
        populate_table()
        add_win.destroy()

    driver_names, plate_numbers = fetch_driver_names_and_plates()

    add_win = tk.Toplevel(root)
    add_win.title("Add to Blacklist")
    add_win.geometry("350x350")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Blacklist ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_bid_var = tk.StringVar(value=str(uuid.uuid4())[:8])
    entry_bid = tk.Entry(add_win, font=("Arial", 11), textvariable=entry_bid_var, state="readonly")
    entry_bid.pack()
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    driver_var = tk.StringVar()
    driver_menu = ttk.Combobox(add_win, textvariable=driver_var, values=driver_names, state="readonly", font=("Arial", 11))
    driver_menu.pack()
    tk.Label(add_win, text="Plate Number:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    plate_var = tk.StringVar()
    plate_menu = ttk.Combobox(add_win, textvariable=plate_var, values=plate_numbers, state="readonly", font=("Arial", 11))
    plate_menu.pack()
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
        subprocess.Popen([sys.executable, "history_reports.py"])
    elif name == "Blacklist":
        pass  # Already on this page
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

title = tk.Label(main, text="License Suspension & Blacklist Management", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Blacklist ID", "Driver Name", "Plate Number", "Reason", "Status")
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

# Initialize the blacklist list
blacklist = []
populate_table()
root.mainloop()
