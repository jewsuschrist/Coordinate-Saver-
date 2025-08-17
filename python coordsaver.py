import tkinter as tk
from tkinter import simpledialog, messagebox, font
import json, os, hashlib, re

DATA_FILE = "coords.json"

# --- Utility Functions ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"password": None, "coords": [], "font": {"family": "Arial", "size": 10}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- App Class ---
class CoordSaverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Coord Saver")
        self.data = load_data()

        # Apply font settings
        self.app_font = font.Font(family=self.data["font"]["family"], size=self.data["font"]["size"])

        # If password is set, ask for it
        if self.data["password"]:
            self.login_screen()
        else:
            self.main_screen()

    # ----- Login -----
    def login_screen(self):
        pw = simpledialog.askstring("Login", "Enter password:", show="*")
        if not pw or hash_password(pw) != self.data["password"]:
            messagebox.showerror("Error", "Wrong password!")
            self.root.destroy()
        else:
            self.main_screen()

    # ----- Main GUI -----
    def main_screen(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack()

        # Coordinate entry
        tk.Label(frame, text="Coords (X Y Z):", font=self.app_font).grid(row=0, column=0, sticky="w")
        self.coords_entry = tk.Entry(frame, width=30, font=self.app_font)
        self.coords_entry.grid(row=0, column=1)

        tk.Label(frame, text="Label:", font=self.app_font).grid(row=1, column=0, sticky="w")
        self.label_entry = tk.Entry(frame, width=30, font=self.app_font)
        self.label_entry.grid(row=1, column=1)

        tk.Button(frame, text="Save Coord", command=self.save_coord, font=self.app_font).grid(row=2, column=0, columnspan=2, pady=5)

        # Listbox for saved coords
        self.listbox = tk.Listbox(frame, width=50, height=10, font=self.app_font)
        self.listbox.grid(row=3, column=0, columnspan=2, pady=5)

        tk.Button(frame, text="Delete Selected", command=self.delete_coord, font=self.app_font).grid(row=4, column=0, columnspan=2)

        # Settings button
        tk.Button(frame, text="Settings ⚙️", command=self.open_settings, font=self.app_font).grid(row=5, column=0, columnspan=2, pady=10)

        self.refresh_list()

    # ----- Save coord -----
    def save_coord(self):
        coords_text = self.coords_entry.get().strip()
        label = self.label_entry.get().strip()

        match = re.match(r"(-?\d+)[,\s]+(-?\d+)[,\s]+(-?\d+)", coords_text)
        if not match or not label:
            messagebox.showerror("Error", "Enter coords (X Y Z) and a label!")
            return

        x, y, z = match.groups()
        self.data["coords"].append({"x": x, "y": y, "z": z, "label": label})
        save_data(self.data)
        self.refresh_list()

    # ----- Delete coord -----
    def delete_coord(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.data["coords"][index]
        save_data(self.data)
        self.refresh_list()

    # ----- Refresh list -----
    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for c in self.data["coords"]:
            self.listbox.insert(tk.END, f"{c['label']} - ({c['x']}, {c['y']}, {c['z']})")

    # ----- Settings window -----
    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")

        # Font settings
        tk.Label(settings_win, text="Font Family:").grid(row=0, column=0, sticky="w")
        font_family_entry = tk.Entry(settings_win)
        font_family_entry.insert(0, self.data["font"]["family"])
        font_family_entry.grid(row=0, column=1)

        tk.Label(settings_win, text="Font Size:").grid(row=1, column=0, sticky="w")
        font_size_entry = tk.Entry(settings_win)
        font_size_entry.insert(0, str(self.data["font"]["size"]))
        font_size_entry.grid(row=1, column=1)

        def save_font():
            self.data["font"]["family"] = font_family_entry.get() or "Arial"
            try:
                self.data["font"]["size"] = int(font_size_entry.get())
            except ValueError:
                self.data["font"]["size"] = 10
            save_data(self.data)
            messagebox.showinfo("Saved", "Font updated. Restart app to apply.")
        
        tk.Button(settings_win, text="Save Font", command=save_font).grid(row=2, column=0, columnspan=2, pady=5)

        # Password settings
        def change_password():
            if self.data["password"]:  # already has one
                old_pw = simpledialog.askstring("Auth", "Enter current password:", show="*")
                if not old_pw or hash_password(old_pw) != self.data["password"]:
                    messagebox.showerror("Error", "Wrong password!")
                    return

            new_pw = simpledialog.askstring("New Password", "Enter new password (leave blank to remove):", show="*")
            if new_pw:
                self.data["password"] = hash_password(new_pw)
                messagebox.showinfo("Updated", "Password set/changed successfully.")
            else:
                self.data["password"] = None
                messagebox.showinfo("Updated", "Password removed.")
            save_data(self.data)

        tk.Button(settings_win, text="Change Password", command=change_password).grid(row=3, column=0, columnspan=2, pady=10)


# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CoordSaverApp(root)
    root.mainloop()
