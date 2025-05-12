# violation_detector.py - Violation Tracker Table GUI
import tkinter as tk
from tkinter import ttk
import subprocess
import sys
import os

# Sample data for demonstration (replace with real data as needed)
violations = [
    {"vehicle_id": "3003768", "driver_name": "Jan Smril", "violation_type": "Violation"},
    {"vehicle_id": "V4071373", "driver_name": "Speeding", "violation_type": "Violation"},
    {"vehicle_id": "Jo23698", "driver_name": "High-Risk", "violation_type": "Violation"},
    {"vehicle_id": "Titte0071", "driver_name": "Jinan Willam", "violation_type": "Timestamp"},
    {"vehicle_id": "Tifle1042", "driver_name": "Erlon, Juton", "violation_type": "Timestamp"},
]

def run_gui():
    root = tk.Tk()
    root.title("Violation Tracker")
    root.geometry("900x700")
    root.configure(bg="#f7faff")

    # Sidebar
    sidebar = tk.Frame(root, width=210, bg="#1976d2")
    sidebar.pack(side=tk.LEFT, fill=tk.Y)

    def sidebar_action(name):
        if name == "Home":
            root.destroy()
            subprocess.Popen([sys.executable, "dashboard.py"])
        elif name == "Violations":
            pass  # Already on this page
        elif name == "Alerts":
            try:
                from AlertSystem import AlertSystem
                alert_system = AlertSystem()
                alert_system.set_root(root)
                alert_system.show_alerts()
            except Exception:
                tk.messagebox.showinfo("Alerts", "Alerts functionality coming soon.")
        elif name == "Driver Analytics":
            root.destroy()
            subprocess.Popen([sys.executable, "driver_analytics.py"])
        elif name == "Training":
            tk.messagebox.showinfo("Training", "Training functionality coming soon.")
        elif name == "Reports":
            tk.messagebox.showinfo("Reports", "Reports functionality coming soon.")
        elif name == "Logout":
            root.destroy()
            subprocess.Popen([sys.executable, "main.py"])
        else:
            tk.messagebox.showinfo("Sidebar Clicked", f"You clicked: {name}")

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
    tk.Label(main, text="Violation Tracker", font=("Arial", 16, "bold"), bg="#f7faff", fg="#222").pack(anchor="nw", padx=18, pady=(18, 0))

    # Table Frame
    table_frame = tk.Frame(main, bg="#f7faff")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

    columns = ("vehicle_id", "driver_name", "violation_type")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    tree.heading("vehicle_id", text="Vehicle ID")
    tree.heading("driver_name", text="Driver Name")
    tree.heading("violation_type", text="Violation Type")
    tree.column("vehicle_id", anchor=tk.CENTER, width=120)
    tree.column("driver_name", anchor=tk.CENTER, width=180)
    tree.column("violation_type", anchor=tk.CENTER, width=180)
    tree.pack(fill=tk.BOTH, expand=True)

    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1976d2", foreground="#fff")
    style.configure("Treeview", font=("Arial", 11), rowheight=28, background="#fff", fieldbackground="#fff")

    # CRUD Functions
    def populate_table():
        for i in tree.get_children():
            tree.delete(i)
        for v in violations:
            tree.insert("", tk.END, values=(v["vehicle_id"], v["driver_name"], v["violation_type"]))

    def add_violation():
        def save():
            v_id = entry_vehicle_id.get().strip()
            d_name = entry_driver_name.get().strip()
            v_type = violation_type_var.get().strip()
            if not v_id or not d_name or not v_type:
                tk.messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
                return
            violations.append({"vehicle_id": v_id, "driver_name": d_name, "violation_type": v_type})
            populate_table()
            add_win.destroy()

        add_win = tk.Toplevel(root)
        add_win.title("Add Violation")
        add_win.geometry("350x250")
        add_win.configure(bg="#f7faff")
        tk.Label(add_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
        entry_vehicle_id = tk.Entry(add_win, font=("Arial", 11))
        entry_vehicle_id.pack()
        tk.Label(add_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_driver_name = tk.Entry(add_win, font=("Arial", 11))
        entry_driver_name.pack()
        tk.Label(add_win, text="Violation Type:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        violation_type_var = tk.StringVar(value="Speeding")
        violation_type_menu = ttk.Combobox(
            add_win, textvariable=violation_type_var,
            values=["Speeding", "Signal Violation", "Illegal Parking"],
            state="readonly", font=("Arial", 11)
        )
        violation_type_menu.pack()
        tk.Button(add_win, text="Add", command=save, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

    def delete_violation():
        selected = tree.selection()
        if not selected:
            tk.messagebox.showwarning("Delete", "Select a row to delete.", parent=root)
            return
        idx = tree.index(selected[0])
        del violations[idx]
        populate_table()

    def edit_violation():
        selected = tree.selection()
        if not selected:
            tk.messagebox.showwarning("Edit", "Select a row to edit.", parent=root)
            return
        idx = tree.index(selected[0])
        violation = violations[idx]

        def save_edit():
            v_id = entry_vehicle_id.get().strip()
            d_name = entry_driver_name.get().strip()
            v_type = violation_type_var.get().strip()
            if not v_id or not d_name or not v_type:
                tk.messagebox.showwarning("Input Error", "All fields are required.", parent=edit_win)
                return
            violations[idx] = {"vehicle_id": v_id, "driver_name": d_name, "violation_type": v_type}
            populate_table()
            edit_win.destroy()

        edit_win = tk.Toplevel(root)
        edit_win.title("Edit Violation")
        edit_win.geometry("350x250")
        edit_win.configure(bg="#f7faff")
        tk.Label(edit_win, text="Vehicle ID:", bg="#f7faff", font=("Arial", 11)).pack(pady=(15, 0))
        entry_vehicle_id = tk.Entry(edit_win, font=("Arial", 11))
        entry_vehicle_id.insert(0, violation["vehicle_id"])
        entry_vehicle_id.pack()
        tk.Label(edit_win, text="Driver Name:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        entry_driver_name = tk.Entry(edit_win, font=("Arial", 11))
        entry_driver_name.insert(0, violation["driver_name"])
        entry_driver_name.pack()
        tk.Label(edit_win, text="Violation Type:", bg="#f7faff", font=("Arial", 11)).pack(pady=(10, 0))
        violation_type_var = tk.StringVar(value=violation["violation_type"])
        violation_type_menu = ttk.Combobox(
            edit_win, textvariable=violation_type_var,
            values=["Speeding", "Signal Violation", "Illegal Parking"],
            state="readonly", font=("Arial", 11)
        )
        violation_type_menu.pack()
        tk.Button(edit_win, text="Save", command=save_edit, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=12).pack(pady=15)

    # CRUD Buttons
    btn_frame = tk.Frame(main, bg="#f7faff")
    btn_frame.pack(pady=(0, 10))
    tk.Button(btn_frame, text="Add Violation", command=add_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Edit Selected", command=edit_violation, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Delete Selected", command=delete_violation, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

    populate_table()

    root.mainloop()

if __name__ == "__main__":
    run_gui()