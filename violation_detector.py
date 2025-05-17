
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import sys
import mysql.connector


# Sample data for demonstration (replace with real data as needed)S

def run_gui():
    vehicles = []  # List to store vehicle data
    root = tk.Tk()
    root.title("Vehicle Registration & Owner Details")
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
            pass  # Already on this page
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
            tk.messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

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

    # Title
    tk.Label(main, text="Vehicle Registration & Owner Details", font=("Arial", 16, "bold"), bg="#f7faff", fg="#222").pack(anchor="nw", padx=18, pady=(18, 0))

    # Table Frame
    table_frame = tk.Frame(main, bg="#f7faff")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

    columns = ("vehicle_id", "owner_name", "plate_number", "model", "color")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    tree.heading("vehicle_id", text="Vehicle ID")
    tree.heading("owner_name", text="Owner Name")
    tree.heading("plate_number", text="Plate Number")
    tree.heading("model", text="Model")
    tree.heading("color", text="Color")
    tree.column("vehicle_id", anchor=tk.CENTER, width=120)
    tree.column("owner_name", anchor=tk.CENTER, width=180)
    tree.column("plate_number", anchor=tk.CENTER, width=120)
    tree.column("model", anchor=tk.CENTER, width=140)
    tree.column("color", anchor=tk.CENTER, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
    style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

    def fetch_vehicles_from_db():
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            # Try to fetch all columns, fallback to only those that exist
            try:
                cursor.execute("SELECT vehicle_id, owner_name, plate_number, model, color FROM vehicles")
            except:
                cursor.execute("SELECT vehicle_id, owner_name, '' as plate_number, '' as model, '' as color FROM vehicles")
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "vehicle_id": row[0],
                    "owner_name": row[1],
                    "plate_number": row[2],
                    "model": row[3],
                    "color": row[4]
                }
                for row in rows
            ]
        except Exception:
            return []

    def fetch_archived_vehicles_from_db():
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT vehicle_id, owner_name, plate_number, model, color FROM vehicles_archive")
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "vehicle_id": row[0],
                    "owner_name": row[1],
                    "plate_number": row[2],
                    "model": row[3],
                    "color": row[4]
                }
                for row in rows
            ]
        except Exception:
            return []

    def restore_vehicle_from_archive(vehicle):
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='vvm_db'
            )
            cursor = conn.cursor()
            # Insert back to vehicles table
            cursor.execute("""
                INSERT INTO vehicles (vehicle_id, owner_name, Plate_number, MOdel, color, timestamp)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (vehicle["vehicle_id"], vehicle["owner_name"], vehicle["plate_number"], vehicle["model"], vehicle["color"]))
            # Remove from archive
            cursor.execute(
                "DELETE FROM vehicles_archive WHERE vehicle_id=%s",
                (vehicle["vehicle_id"],)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to restore vehicle:\n{e}", parent=root)

    # CRUD Functions
    def populate_table():
        vehicles.clear()
        vehicles.extend(fetch_vehicles_from_db())
        for i in tree.get_children():
            tree.delete(i)
        for v in vehicles:
            tree.insert("", tk.END, values=(v["vehicle_id"], v["owner_name"], v["plate_number"], v["model"], v["color"]))

    def delete_vehicle():
        selected = tree.selection()
        if not selected:
            tk.messagebox.showwarning("Delete", "Select a row to delete.", parent=root)
            return
        idx = tree.index(selected[0])
        vehicle = vehicles[idx]
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
                CREATE TABLE IF NOT EXISTS vehicles_archive (
                    vehicle_id VARCHAR(36),
                    owner_name VARCHAR(20),
                    plate_number VARCHAR(20),
                    model VARCHAR(20),
                    color VARCHAR(20),
                    archived_at DATETIME DEFAULT NOW()
                )
            """)
            # Copy the vehicle to archive
            cursor.execute(
                "INSERT INTO vehicles_archive (vehicle_id, owner_name, plate_number, model, color) VALUES (%s, %s, %s, %s, %s)",
                (vehicle["vehicle_id"], vehicle["owner_name"], vehicle["plate_number"], vehicle["model"], vehicle["color"])
            )
            # Delete from main vehicles table
            cursor.execute(
                "DELETE FROM vehicles WHERE vehicle_id=%s",
                (vehicle["vehicle_id"],)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            tk.messagebox.showerror("Database Error", f"Failed to archive vehicle:\n{e}", parent=root)
            return
        populate_table()

    def add_vehicle():
        def save():
            v_id = entry_vehicle_id.get().strip()
            owner = entry_owner_name.get().strip()
            plate = entry_plate_number.get().strip()
            model = entry_model.get().strip()
            color = entry_color.get().strip()
            if not v_id or not owner or not plate or not model or not color:
                messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
                return
            # Store in database
            try:
                conn = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='',
                    database='vvm_db'
                )
                cursor = conn.cursor()
                vehicles.clear()
                cursor.execute("SELECT vehicle_id, owner_name, Plate_number, MOdel, color FROM vehicles")
                for row in cursor.fetchall():
                    vehicles.append({
                        "vehicle_id": row[0],
                        "owner_name": row[1],
                        "plate_number": row[2],
                        "model": row[3],
                        "color": row[4]
                    })
                cursor.execute("""
                    INSERT INTO vehicles (vehicle_id, owner_name, Plate_number, MOdel, color, timestamp)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (v_id, owner, plate, model, color))
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to add vehicle to database:\n{e}", parent=add_win)
                return
            vehicles.append({"vehicle_id": v_id, "owner_name": owner, "plate_number": plate, "model": model, "color": color})
            populate_table()
            add_win.destroy()

        add_win = tk.Toplevel(root)
        add_win.title("Add Vehicle")
        add_win.geometry("400x350")
        add_win.configure(bg="#f7faff")
        tk.Label(add_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
        entry_vehicle_id = tk.Entry(add_win, font=("Arial", 11))
        entry_vehicle_id.pack()
        tk.Label(add_win, text="Owner Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_owner_name = tk.Entry(add_win, font=("Arial", 11))
        entry_owner_name.pack()
        tk.Label(add_win, text="Plate Number:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_plate_number = tk.Entry(add_win, font=("Arial", 11))
        entry_plate_number.pack()
        tk.Label(add_win, text="Model:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_model = tk.Entry(add_win, font=("Arial", 11))
        entry_model.pack()
        tk.Label(add_win, text="Color:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_color = tk.Entry(add_win, font=("Arial", 11))
        entry_color.pack()
        tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

    def edit_vehicle():
        selected = tree.selection()
        if not selected:
            tk.messagebox.showwarning("Edit", "Select a row to edit.", parent=root)
            return
        idx = tree.index(selected[0])
        vehicle = vehicles[idx]

        def save_edit():
            v_id = entry_vehicle_id.get().strip()
            owner = entry_owner_name.get().strip()
            plate = entry_plate_number.get().strip()
            model = entry_model.get().strip()
            color = entry_color.get().strip()
            if not v_id or not owner or not plate or not model or not color:
                tk.messagebox.showwarning("Input Error", "All fields are required.", parent=edit_win)
                return
            vehicles[idx] = {"vehicle_id": v_id, "owner_name": owner, "plate_number": plate, "model": model, "color": color}
            populate_table()
            edit_win.destroy()

        edit_win = tk.Toplevel(root)
        edit_win.title("Edit Vehicle")
        edit_win.geometry("400x350")
        edit_win.configure(bg="#f7faff")
        tk.Label(edit_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
        entry_vehicle_id = tk.Entry(edit_win, font=("Arial", 11))
        entry_vehicle_id.insert(0, vehicle["vehicle_id"])
        entry_vehicle_id.pack()
        tk.Label(edit_win, text="Owner Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_owner_name = tk.Entry(edit_win, font=("Arial", 11))
        entry_owner_name.insert(0, vehicle["owner_name"])
        entry_owner_name.pack()
        tk.Label(edit_win, text="Plate Number:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_plate_number = tk.Entry(edit_win, font=("Arial", 11))
        entry_plate_number.insert(0, vehicle["plate_number"])
        entry_plate_number.pack()
        tk.Label(edit_win, text="Model:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_model = tk.Entry(edit_win, font=("Arial", 11))
        entry_model.insert(0, vehicle["model"])
        entry_model.pack()
        tk.Label(edit_win, text="Color:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_color = tk.Entry(edit_win, font=("Arial", 11))
        entry_color.insert(0, vehicle["color"])
        entry_color.pack()
        tk.Button(edit_win, text="Save", command=save_edit, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

    def show_archived_vehicles():
        archive_win = tk.Toplevel(root)
        archive_win.title("Archived Vehicles")
        archive_win.geometry("700x500")
        archive_win.configure(bg="#f7faff")
        tk.Label(archive_win, text="Archived Vehicles", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1565c0").pack(pady=18)
        frame = tk.Frame(archive_win, bg="#f7faff")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        columns = ("Vehicle ID", "Owner Name", "Plate Number", "Model", "Color")
        tree_arch = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col in columns:
            tree_arch.heading(col, text=col)
            tree_arch.column(col, anchor=tk.CENTER, width=120)
        tree_arch.pack(fill=tk.BOTH, expand=True)
        # Style for Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
        style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")
        # Populate data
        for v in fetch_archived_vehicles_from_db():
            tree_arch.insert("", tk.END, values=(v["vehicle_id"], v["owner_name"], v["plate_number"], v["model"], v["color"]))

        def restore_selected():
            selected = tree_arch.selection()
            if not selected:
                messagebox.showwarning("Restore", "Select a row to restore.", parent=archive_win)
                return
            idx = tree_arch.index(selected[0])
            archived_vehicles = fetch_archived_vehicles_from_db()
            if idx < len(archived_vehicles):
                vehicle = archived_vehicles[idx]
                restore_vehicle_from_archive(vehicle)
                # Refresh both archive and main table
                for i in tree_arch.get_children():
                    tree_arch.delete(i)
                for v in fetch_archived_vehicles_from_db():
                    tree_arch.insert("", tk.END, values=(v["vehicle_id"], v["owner_name"], v["plate_number"], v["model"], v["color"]))
                populate_table()

        btn_restore = tk.Button(frame, text="Restore Selected", command=restore_selected, bg="#388e3c", fg="white", font=("Arial", 11, "bold"), width=16)
        btn_restore.pack(pady=10)

    # CRUD Buttons
    btn_frame = tk.Frame(main, bg="#f7faff")
    btn_frame.pack(pady=(0, 10))
    tk.Button(btn_frame, text="Add Vehicle", command=add_vehicle, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Edit Selected", command=edit_vehicle, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Delete Selected", command=delete_vehicle, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Show Archived", command=show_archived_vehicles, bg="#607d8b", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

    populate_table()

    root.mainloop()

if __name__ == "__main__":
    run_gui()