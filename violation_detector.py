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
from tkinter import ttk
import subprocess
import sys

# Sample data for demonstration (replace with real data as needed)
vehicles = [
    {"vehicle_id": "3003768", "owner_name": "Jan Smril", "plate_number": "ABC123", "model": "Toyota Camry", "color": "White"},
    {"vehicle_id": "V4071373", "owner_name": "Anna Lee", "plate_number": "XYZ789", "model": "Honda Civic", "color": "Black"},
    {"vehicle_id": "Jo23698", "owner_name": "Mark Smith", "plate_number": "JKL456", "model": "Ford Focus", "color": "Blue"},
]

def run_gui():
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

    # CRUD Functions
    def populate_table():
        for i in tree.get_children():
            tree.delete(i)
        for v in vehicles:
            tree.insert("", tk.END, values=(v["vehicle_id"], v["owner_name"], v["plate_number"], v["model"], v["color"]))

    def add_vehicle():
        def save():
            v_id = entry_vehicle_id.get().strip()
            owner = entry_owner_name.get().strip()
            plate = entry_plate_number.get().strip()
            model = entry_model.get().strip()
            color = entry_color.get().strip()
            if not v_id or not owner or not plate or not model or not color:
                tk.messagebox.showwarning("Input Error", "All fields are required.", parent=add_win)
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

    def delete_vehicle():
        selected = tree.selection()
        if not selected:
            tk.messagebox.showwarning("Delete", "Select a row to delete.", parent=root)
            return
        idx = tree.index(selected[0])
        del vehicles[idx]
        populate_table()

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

    # CRUD Buttons
    btn_frame = tk.Frame(main, bg="#f7faff")
    btn_frame.pack(pady=(0, 10))
    tk.Button(btn_frame, text="Add Vehicle", command=add_vehicle, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Edit Selected", command=edit_vehicle, bg="#1976d2", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Delete Selected", command=delete_vehicle, bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), width=16).pack(side=tk.LEFT, padx=8)

    populate_table()

    root.mainloop()

if __name__ == "__main__":
    run_gui()