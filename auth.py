from mysql.connector import Error  # Fix: use correct Error import
import tkinter as tk
from tkinter import Tk, messagebox
from database import Database

def register_user(db, root):
    reg_win = tk.Toplevel(root)
    reg_win.title("Register")
    reg_win.geometry("350x340")
    reg_win.configure(bg="#f7faff")
    reg_win.grab_set()
    reg_win.resizable(False, False)

    header = tk.Label(reg_win, text="Create New Account", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1565c0")
    header.pack(pady=(25, 10))

    user_frame = tk.Frame(reg_win, bg="#f7faff")
    user_frame.pack(pady=(10, 5))
    tk.Label(user_frame, text="Username:", font=("Arial", 12), bg="#f7faff", fg="#1565c0").grid(row=0, column=0, sticky="e", padx=5)
    username_entry = tk.Entry(user_frame, font=("Arial", 12), width=22, bd=2, relief="groove")
    username_entry.grid(row=0, column=1, padx=5)

    pass_frame = tk.Frame(reg_win, bg="#f7faff")
    pass_frame.pack(pady=(5, 10))
    tk.Label(pass_frame, text="Password:", font=("Arial", 12), bg="#f7faff", fg="#1565c0").grid(row=0, column=0, sticky="e", padx=5)
    password_entry = tk.Entry(pass_frame, show="*", font=("Arial", 12), width=22, bd=2, relief="groove")
    password_entry.grid(row=0, column=1, padx=5)

    def do_register():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.", parent=reg_win)
            return
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password)
            )
            db.connection.commit()
            messagebox.showinfo("Success", "User registered successfully!", parent=reg_win)
            reg_win.destroy()
        except Error as e:  # Fix: catch mysql.connector.Error
            messagebox.showerror("Registration Error", str(e), parent=reg_win)

    reg_btn = tk.Button(reg_win, text="Register", command=do_register, font=("Arial", 12, "bold"),
                        bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white",
                        width=18, bd=0, pady=7)
    reg_btn.pack(pady=(20, 8))

    cancel_btn = tk.Button(reg_win, text="Cancel", command=reg_win.destroy,
                           font=("Arial", 10), bg="#e3f0fc", fg="#1976d2", activebackground="#bbdefb",
                           activeforeground="#1976d2", bd=0, pady=5)
    cancel_btn.pack()

    reg_win.wait_window()

def login_user(db, root):
    login_win = tk.Toplevel(root)
    login_win.title("Login")
    login_win.geometry("350x320")
    login_win.configure(bg="#f7faff")
    login_win.grab_set()
    login_win.resizable(False, False)

    header = tk.Label(login_win, text="Vehicle Violation Login", font=("Arial", 16, "bold"), bg="#f7faff", fg="#1565c0")
    header.pack(pady=(25, 10))

    user_frame = tk.Frame(login_win, bg="#f7faff")
    user_frame.pack(pady=(10, 5))
    tk.Label(user_frame, text="Username:", font=("Arial", 12), bg="#f7faff", fg="#1565c0").grid(row=0, column=0, sticky="e", padx=5)
    username_entry = tk.Entry(user_frame, font=("Arial", 12), width=22, bd=2, relief="groove")
    username_entry.grid(row=0, column=1, padx=5)

    pass_frame = tk.Frame(login_win, bg="#f7faff")
    pass_frame.pack(pady=(5, 10))
    tk.Label(pass_frame, text="Password:", font=("Arial", 12), bg="#f7faff", fg="#1565c0").grid(row=0, column=0, sticky="e", padx=5)
    password_entry = tk.Entry(pass_frame, show="*", font=("Arial", 12), width=22, bd=2, relief="groove")
    password_entry.grid(row=0, column=1, padx=5)

    result = {'success': False}

    def try_login():
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.", parent=login_win)
            return
        try:
            db._ensure_connection()
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND password_hash=%s",
                (username, password)
            )
            user = cursor.fetchone()
            if user:
                result['success'] = True
                login_win.destroy()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.", parent=login_win)
        except Error as e:  # Fix: catch mysql.connector.Error
            messagebox.showerror("Login Error", str(e), parent=login_win)

    def do_register():
        login_win.destroy()
        register_user(db, root)
        login_user(db, root)

    login_btn = tk.Button(login_win, text="Login", command=try_login, font=("Arial", 12, "bold"),
                          bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white",
                          width=18, bd=0, pady=7)
    login_btn.pack(pady=(20, 8))

    register_btn = tk.Button(login_win, text="Don't have an account? Register", command=do_register,
                             font=("Arial", 10), bg="#e3f0fc", fg="#1976d2", activebackground="#bbdefb",
                             activeforeground="#1976d2", bd=0, pady=5)
    register_btn.pack()

    login_win.wait_window()
    return result['success']

if __name__ == "__main__":
    try:
        db = Database()
        root = Tk()
        root.withdraw()

        # Show login dialog
        if login_user(db, root):

            import subprocess
            import sys
            import os
            dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.py")
            if not os.path.exists(dashboard_path):
                messagebox.showerror("Dashboard Error", f"Dashboard file not found:\n{dashboard_path}", parent=root)
            else:
                root.destroy()  # Close the login/main window
                subprocess.Popen([sys.executable, dashboard_path])
        else:
            root.destroy()
    except Error as e:
        messagebox.showerror("Startup Error", f"Database connection failed: {str(e)}")
