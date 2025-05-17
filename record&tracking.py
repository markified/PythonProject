
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from random import randint, choice
import subprocess
import sys
import os
import importlib.util
import mysql.connector

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

title = tk.Label(main, text="Violation Record & Tracking", font=("Arial", 18, "bold"), bg="#f7faff", fg="#1565c0")
title.pack(pady=18)

frame = tk.Frame(main, bg="#f7faff")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

columns = ("Driver Name", "Vehicle ID", "Violation Type", "Count", "Price", "Status")
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

# Fetch driver names and vehicle IDs from database
def fetch_driver_names_and_vehicle_ids():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT owner_name, vehicle_id FROM vehicles")
        rows = cursor.fetchall()
        conn.close()
        driver_names = sorted(list(set(row[0] for row in rows if row[0])))
        vehicle_ids = sorted(list(set(row[1] for row in rows if row[1])))
        return driver_names, vehicle_ids
    except Exception:
        return [], []

driver_names_list, vehicle_ids_list = fetch_driver_names_and_vehicle_ids()
violations = []

# Violation types and their prices
VIOLATION_PRICES = {
    "Speeding": 100,
    "Signal Violation": 150,
    "Illegal Parking": 80
}

def add_violation():
    def update_price(*args):
        selected_indices = violation_types_listbox.curselection()
        total = 0
        for idx in selected_indices:
            vtype = list(VIOLATION_PRICES.keys())[idx]
            count_str = count_vars[vtype].get()
            count = int(count_str) if count_str.isdigit() else 0
            total += VIOLATION_PRICES[vtype] * count
        price_var.set(f"Total Price: ₱{total}")

    def save():
        driver = driver_name_var.get().strip()
        vehicle = vehicle_id_var.get().strip()
        selected_indices = violation_types_listbox.curselection()
        if not driver or not vehicle or not selected_indices:
            messagebox.showwarning("Input Error", "All fields are required and at least one violation must be selected.", parent=add_win)
            return
        added = False
        for idx in selected_indices:
            vtype = list(VIOLATION_PRICES.keys())[idx]
            count_str = count_vars[vtype].get()
            if not count_str.isdigit() or int(count_str) <= 0:
                continue
            count = int(count_str)
            price = VIOLATION_PRICES[vtype]
            # Check for duplicate in DB
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vvm_db'
                )
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT count FROM violations WHERE owner_name=%s AND vehicle_id=%s AND violation_type=%s",
                    (driver, vehicle, vtype)
                )
                row = cursor.fetchone()
                if row:
                    # If exists, update count and price
                    new_count = row[0] + count
                    cursor.execute(
                        "UPDATE violations SET count=%s, price=%s WHERE owner_name=%s AND vehicle_id=%s AND violation_type=%s",
                        (new_count, price, driver, vehicle, vtype)
                    )
                else:
                    # If not exists, insert new
                    cursor.execute(
                        "INSERT INTO violations (owner_name, vehicle_id, violation_type, count, price) VALUES (%s, %s, %s, %s, %s)",
                        (driver, vehicle, vtype, count, price)
                    )
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save violation to database:\n{e}", parent=add_win)
                return
            added = True
        if not added:
            messagebox.showwarning("Input Error", "Please enter a valid count for at least one violation.", parent=add_win)
            return
        populate_table()
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add Violation")
    add_win.geometry("400x420")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    driver_name_var = tk.StringVar()
    driver_name_menu = ttk.Combobox(
        add_win, textvariable=driver_name_var,
        values=driver_names_list,
        state="readonly", font=("Arial", 11)
    )
    driver_name_menu.pack()
    tk.Label(add_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    vehicle_id_var = tk.StringVar()
    vehicle_id_menu = ttk.Combobox(
        add_win, textvariable=vehicle_id_var,
        values=vehicle_ids_list,
        state="readonly", font=("Arial", 11)
    )
    vehicle_id_menu.pack()
    tk.Label(add_win, text="Violation Types (select one or more):", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    violation_types_listbox = tk.Listbox(add_win, selectmode=tk.MULTIPLE, font=("Arial", 11), height=len(VIOLATION_PRICES))
    for vtype in VIOLATION_PRICES.keys():
        violation_types_listbox.insert(tk.END, vtype)
    violation_types_listbox.pack()
    count_vars = {vtype: tk.StringVar(value="1") for vtype in VIOLATION_PRICES}
    for vtype in VIOLATION_PRICES.keys():
        frame = tk.Frame(add_win, bg="#f7faff")
        frame.pack(fill=tk.X, padx=10)
        tk.Label(frame, text=f"{vtype} Count:", bg="#f7faff", font=("Arial", 10)).pack(side=tk.LEFT)
        entry = tk.Entry(frame, textvariable=count_vars[vtype], width=5, font=("Arial", 10))
        entry.pack(side=tk.LEFT, padx=(5, 0))
        entry.bind("<KeyRelease>", lambda e: update_price())
    price_var = tk.StringVar()
    update_price()
    violation_types_listbox.bind("<<ListboxSelect>>", lambda e: update_price())
    tk.Label(add_win, textvariable=price_var, bg="#f7faff", font=("Arial", 11, "italic"), fg="#1976d2").pack(pady=(5, 0))
    tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

def delete_violation():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Delete", "Select a row to delete.", parent=root)
        return
    idx = tree.index(selected[0])
    violation = violations[idx]
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Create archive table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations_archive (
                violation_id INT AUTO_INCREMENT PRIMARY KEY,
                owner_name VARCHAR(20),
                vehicle_id VARCHAR(36),
                violation_type VARCHAR(50),
                count INT DEFAULT 0,
                price INT DEFAULT 0,
                archived_at DATETIME DEFAULT NOW()
            )
        """)
        # Copy the violation to archive
        cursor.execute(
            "INSERT INTO violations_archive (owner_name, vehicle_id, violation_type, count, price) VALUES (%s, %s, %s, %s, %s)",
            (violation["owner_name"], violation["vehicle_id"], violation["violation_type"], violation["count"], violation.get("price", 0))
        )
        # Delete from main violations table
        cursor.execute(
            "DELETE FROM violations WHERE owner_name=%s AND vehicle_id=%s AND violation_type=%s",
            (violation["owner_name"], violation["vehicle_id"], violation["violation_type"])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to archive violation:\n{e}", parent=root)
        return
    populate_table()

def edit_violation():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Edit", "Select a row to edit.", parent=root)
        return
    idx = tree.index(selected[0])
    violation = violations[idx]

    def update_price(*args):
        vtype = violation_type_var.get()
        price = VIOLATION_PRICES.get(vtype, 0)
        price_var.set(f"Price: ₱{price}")

    def save_edit():
        driver = driver_name_var.get().strip()
        vehicle = vehicle_id_var.get().strip()
        vtype = violation_type_var.get().strip()
        count = entry_count.get().strip()
        price = VIOLATION_PRICES.get(vtype, 0)
        if not driver or not vehicle or not vtype or not count or not count.isdigit():
            messagebox.showwarning("Input Error", "All fields are required and count must be a number.", parent=edit_win)
            return
        violations[idx] = {
            "owner_name": driver,
            "vehicle_id": vehicle,
            "violation_type": vtype,
            "count": int(count),
            "price": price
        }
        # Update in database
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE violations SET count=%s, price=%s WHERE owner_name=%s AND vehicle_id=%s AND violation_type=%s",
                (int(count), price, driver, vehicle, vtype)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update violation in database:\n{e}", parent=edit_win)
            return
        populate_table()
        edit_win.destroy()

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Violation")
    edit_win.geometry("350x340")
    edit_win.configure(bg="#f7faff")
    tk.Label(edit_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    driver_name_var = tk.StringVar(value=violation["owner_name"])
    driver_name_menu = ttk.Combobox(
        edit_win, textvariable=driver_name_var,
        values=driver_names_list,
        state="readonly", font=("Arial", 11)
    )
    driver_name_menu.pack()
    tk.Label(edit_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    vehicle_id_var = tk.StringVar(value=violation["vehicle_id"])
    vehicle_id_menu = ttk.Combobox(
        edit_win, textvariable=vehicle_id_var,
        values=vehicle_ids_list,
        state="readonly", font=("Arial", 11)
    )
    vehicle_id_menu.pack()
    tk.Label(edit_win, text="Violation Type:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    violation_type_var = tk.StringVar(value=violation["violation_type"])
    violation_type_menu = ttk.Combobox(
        edit_win, textvariable=violation_type_var,
        values=list(VIOLATION_PRICES.keys()),
        state="readonly", font=("Arial", 11)
    )
    violation_type_menu.pack()
    price_var = tk.StringVar()
    update_price()
    violation_type_var.trace_add("write", update_price)
    tk.Label(edit_win, textvariable=price_var, bg="#f7faff", font=("Arial", 11, "italic"), fg="#1976d2").pack(pady=(5, 0))
    tk.Label(edit_win, text="Count:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_count = tk.Entry(edit_win, font=("Arial", 11))
    entry_count.insert(0, str(violation["count"]))
    entry_count.pack()
    tk.Button(edit_win, text="Save", command=save_edit, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

def fetch_archived_violations_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT owner_name, vehicle_id, violation_type, count, price FROM violations_archive")
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "owner_name": row[0],
                "vehicle_id": row[1],
                "violation_type": row[2],
                "count": row[3],
                "price": row[4] if len(row) > 4 else 0
            }
            for row in rows
        ]
    except Exception:
        return []

def restore_violation_from_archive(violation):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Insert back to violations table
        cursor.execute(
            "INSERT INTO violations (owner_name, vehicle_id, violation_type, count, price, timestamp) VALUES (%s, %s, %s, %s, %s, NOW())",
            (violation["owner_name"], violation["vehicle_id"], violation["violation_type"], violation["count"], violation.get("price", 0))
        )
        # Remove from archive
        cursor.execute(
            "DELETE FROM violations_archive WHERE owner_name=%s AND vehicle_id=%s AND violation_type=%s",
            (violation["owner_name"], violation["vehicle_id"], violation["violation_type"])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to restore violation:\n{e}", parent=root)

def show_archived_violations():
    archive_win = tk.Toplevel(root)
    archive_win.title("Archived Violations")
    archive_win.geometry("700x500")
    archive_win.configure(bg="#f7faff")
    tk.Label(archive_win, text="Archived Violations", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1565c0").pack(pady=18)
    frame = tk.Frame(archive_win, bg="#f7faff")
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    columns = ("Driver Name", "Vehicle ID", "Violation Type", "Count")
    tree_arch = ttk.Treeview(frame, columns=columns, show='headings', height=15)
    for col in columns:
        tree_arch.heading(col, text=col)
        tree_arch.column(col, anchor=tk.CENTER, width=150)
    tree_arch.pack(fill=tk.BOTH, expand=True)
    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
    style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")
    # Populate data
    archived_violations = fetch_archived_violations_from_db()
    for v in archived_violations:
        tree_arch.insert("", tk.END, values=(v["owner_name"], v["vehicle_id"], v["violation_type"], v["count"]))

    def restore_selected():
        selected = tree_arch.selection()
        if not selected:
            messagebox.showwarning("Restore", "Select a row to restore.", parent=archive_win)
            return
        idx = tree_arch.index(selected[0])
        archived_violations = fetch_archived_violations_from_db()
        if idx < len(archived_violations):
            violation = archived_violations[idx]
            restore_violation_from_archive(violation)
            # Refresh both archive and main table
            for i in tree_arch.get_children():
                tree_arch.delete(i)
            for v in fetch_archived_violations_from_db():
                tree_arch.insert("", tk.END, values=(v["owner_name"], v["vehicle_id"], v["violation_type"], v["count"]))
            populate_table()

    btn_restore = tk.Button(frame, text="Restore Selected", command=restore_selected, bg="#388e3c", fg="white", font=("Arial", 11, "bold"), width=16)
    btn_restore.pack(pady=10)

# CRUD Buttons
btn_frame = tk.Frame(main, bg="#f7faff")
btn_frame.pack(pady=(0, 10))
tk.Button(btn_frame, text="Add Violation", command=add_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Edit Selected", command=edit_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Delete Selected", command=delete_violation, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
tk.Button(btn_frame, text="Show Archived", command=show_archived_violations, bg="#607d8b", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

def fetch_violations_from_db():
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
        return [
            {
                "owner_name": row[0],
                "vehicle_id": row[1],
                "violation_type": row[2],
                "count": row[3],
                "price": row[4],
                "status": row[5] if len(row) > 5 else ""
            }
            for row in rows
        ]
    except Exception:
        return []

def populate_table():
    # Fetch from database
    violations.clear()
    violations.extend(fetch_violations_from_db())
    # Clear the tree
    for row in tree.get_children():
        tree.delete(row)
    # Insert all violations
    for v in violations:
        tree.insert("", tk.END, values=(
            v["owner_name"], v["vehicle_id"], v["violation_type"], v["count"], v.get("price", ""), v.get("status", "")
        ))

populate_table()
root.mainloop()
