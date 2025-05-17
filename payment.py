
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import mysql.connector
import uuid

# Sample data for demonstration (replace with real data as needed)
payments = []   
def populate_table():
    # Fetch all payments from the database and show in the table
    payments.clear()
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                payment_id VARCHAR(50) PRIMARY KEY,
                owner_name VARCHAR(100),
                violation_type VARCHAR(100),
                amount INT,
                status VARCHAR(20)
            )
        """)
        cursor.execute("SELECT payment_id, owner_name, violation_type, amount, status FROM payments")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            payments.append({
                "payment_id": row[0],
                "owner_name": row[1],
                "violation": row[2],
                "amount": row[3],
                "status": row[4]
            })
    except Exception:
        pass
    for i in tree.get_children():
        tree.delete(i)
    for p in payments:
        tree.insert("", tk.END, values=(p["payment_id"], p["owner_name"], p["violation"], p["amount"], p["status"]))

def mark_as_paid():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Mark as Paid", "Select a payment to mark as paid.", parent=root)
        return
    idx = tree.index(selected[0])
    payment = payments[idx]
    payments[idx]["status"] = "Paid"
    # Update status in payments table and also in violations table
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Update payments table
        cursor.execute(
            "UPDATE payments SET status=%s WHERE payment_id=%s",
            ("Paid", payment["payment_id"])
        )
        # Update violations table for the same owner and violation type
        cursor.execute(
            "UPDATE violations SET status=%s WHERE owner_name=%s AND violation_type=%s",
            ("Paid", payment["owner_name"], payment["violation"])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to update payment status in database:\n{e}", parent=root)
        return
    populate_table()

def fetch_driver_names_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT owner_name FROM vehicles")
        rows = cursor.fetchall()
        conn.close()
        return sorted([row[0] for row in rows if row[0]])
    except Exception:
        return []

def fetch_violations_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        # Only show violation types that exist in the violations table, have a price, and are not already paid
        cursor.execute("SELECT DISTINCT violation_type FROM violations WHERE price IS NOT NULL AND (status IS NULL OR status != 'Paid')")
        rows = cursor.fetchall()
        conn.close()
        # Return as a list of strings for the dropdown
        return [str(row[0]) for row in rows if row[0]]
    except Exception:
        return []

def fetch_violation_amount_from_db(violation_type):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='vvm_db'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM violations WHERE violation_type=%s ORDER BY violation_id DESC LIMIT 1", (violation_type,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return ""
    except Exception:
        return ""

def add_payment():
    def update_amount(*args):
        violation = violation_var.get()
        amount = fetch_violation_amount_from_db(violation)
        entry_amount_var.set(str(amount) if amount != "" else "")

    def save():
        pid = entry_pid_var.get().strip()
        driver = driver_var.get().strip()
        violation = violation_var.get().strip()
        amount = entry_amount_var.get().strip()
        if not pid or not driver or not violation or not amount or not amount.isdigit():
            messagebox.showwarning("Input Error", "All fields are required and amount must be a number.", parent=add_win)
            return
        payments.append({"payment_id": pid, "owner_name": driver, "violation": violation, "amount": int(amount), "status": "Unpaid"})
        # Store in database
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id VARCHAR(50) PRIMARY KEY,
                    owner_name VARCHAR(100),
                    violation_type VARCHAR(100),
                    amount INT,
                    status VARCHAR(20)
                )
            """)
            cursor.execute(
                "INSERT INTO payments (payment_id, owner_name, violation_type, amount, status) VALUES (%s, %s, %s, %s, %s)",
                (pid, driver, violation, int(amount), "Unpaid")
            )
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save payment to database:\n{e}", parent=add_win)
            return
        populate_table()
        add_win.destroy()

    driver_names = fetch_driver_names_from_db()
    violations = fetch_violations_from_db()

    add_win = tk.Toplevel(root)
    add_win.title("Add Payment")
    add_win.geometry("350x300")
    add_win.configure(bg="#f7faff")
    tk.Label(add_win, text="Payment ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
    entry_pid_var = tk.StringVar(value=str(uuid.uuid4())[:8])
    entry_pid = tk.Entry(add_win, font=("Arial", 11), textvariable=entry_pid_var, state="readonly")
    entry_pid.pack()
    tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    driver_var = tk.StringVar()
    driver_menu = ttk.Combobox(add_win, textvariable=driver_var, values=driver_names, state="readonly", font=("Arial", 11))
    driver_menu.pack()
    tk.Label(add_win, text="Violation:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    violation_var = tk.StringVar()
    violation_menu = ttk.Combobox(add_win, textvariable=violation_var, values=violations, state="readonly", font=("Arial", 11))
    violation_menu.pack()
    entry_amount_var = tk.StringVar()
    violation_var.trace_add("write", lambda *args: update_amount())
    tk.Label(add_win, text="Amount:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
    entry_amount = tk.Entry(add_win, font=("Arial", 11), textvariable=entry_amount_var, state="readonly")
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
