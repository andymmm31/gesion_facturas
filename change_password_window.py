import tkinter as tk
from tkinter import ttk, messagebox
import database

class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.title("Cambiar Contraseña")
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()

        self.user_email = user_email

        self._create_widgets()

    def _create_widgets(self):
        """Crea la interfaz de la ventana."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Contraseña Antigua:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.old_password_entry = ttk.Entry(main_frame, show="*")
        self.old_password_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(main_frame, text="Nueva Contraseña:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.new_password_entry = ttk.Entry(main_frame, show="*")
        self.new_password_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(main_frame, text="Confirmar Nueva Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.confirm_password_entry = ttk.Entry(main_frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Guardar Cambios", command=self._save_new_password).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side="left")

        main_frame.grid_columnconfigure(1, weight=1)

    def _save_new_password(self):
        """Valida y guarda la nueva contraseña."""
        old_pw = self.old_password_entry.get()
        new_pw = self.new_password_entry.get()
        confirm_pw = self.confirm_password_entry.get()

        if not all([old_pw, new_pw, confirm_pw]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.", parent=self)
            return

        if new_pw != confirm_pw:
            messagebox.showerror("Error", "La nueva contraseña y su confirmación no coinciden.", parent=self)
            return

        if len(new_pw) < 8:
            messagebox.showerror("Error", "La nueva contraseña debe tener al menos 8 caracteres.", parent=self)
            return

        success, message = database.change_password(self.user_email, old_pw, new_pw)

        if success:
            messagebox.showinfo("Éxito", message, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Error", message, parent=self)
