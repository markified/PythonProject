# alert_system.py - Notification handling

import tkinter as tk
from tkinter import messagebox

class AlertSystem:
    def __init__(self):
        # Initialize any required attributes
        self.violations_queue = []
        self.root = None
        self.alert_window = None

    def set_root(self, root):
        """Set the Tk root for displaying alerts."""
        self.root = root

    def queue_violations(self, violations):
        # Add violations to the queue (placeholder logic)
        self.violations_queue.extend(violations)

    def show_alerts(self):
        if not self.root:
            return
        if self.alert_window and tk.Toplevel.winfo_exists(self.alert_window):
            self.update_alert_window()
            return

        self.alert_window = tk.Toplevel(self.root)
        self.alert_window.title("Violation Alerts")
        self.alert_window.geometry("400x300")
        self.alert_window.resizable(False, False)
        self.alert_window.configure(bg="#f7faff")  # Blue/white theme

        tk.Label(self.alert_window, text="New Violations", font=("Arial", 14, "bold"), bg="#f7faff", fg="#1565c0").pack(pady=10)
        self.alert_listbox = tk.Listbox(self.alert_window, width=50, height=10, font=("Arial", 11), bd=2, relief="groove")
        self.alert_listbox.pack(padx=10, pady=10)

        for v in self.violations_queue:
            self.alert_listbox.insert(tk.END, f"{v.get('type', '')}: {v.get('details', '')}")

        tk.Button(
            self.alert_window, text="Acknowledge All", command=self.acknowledge_alerts,
            font=("Arial", 11, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white",
            width=18, bd=0, pady=7
        ).pack(pady=10)

    def update_alert_window(self):
        if self.alert_window and self.alert_listbox:
            self.alert_listbox.delete(0, tk.END)
            for v in self.violations_queue:
                self.alert_listbox.insert(tk.END, f"{v.get('type', '')}: {v.get('details', '')}")

    def acknowledge_alerts(self):
        self.violations_queue.clear()
        if self.alert_window:
            self.alert_window.destroy()
            self.alert_window = None