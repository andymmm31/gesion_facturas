import tkinter as tk
from tkinter import ttk
import database

class LoginScreen(ttk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)

        self.create_widgets()

    def create_widgets(self):
        """Crea y posiciona los widgets en la pantalla de login."""
        # Contenedor para centrar los widgets
        center_frame = ttk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(center_frame, text="Email:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(center_frame, width=30)
        self.email_entry.grid(row=0, column=1, pady=5)

        ttk.Label(center_frame, text="Contraseña:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(center_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Vincular la tecla Enter al botón de ingresar
        self.password_entry.bind("<Return>", self._perform_login_event)


        login_button = ttk.Button(center_frame, text="Ingresar", command=self._perform_login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.error_label = ttk.Label(center_frame, text="", foreground="red")
        self.error_label.grid(row=3, column=0, columnspan=2)

    def _perform_login(self):
        """Gestiona el evento de clic del botón de login."""
        email = self.email_entry.get()
        password = self.password_entry.get()

        if database.login_user(email, password):
            self.on_login_success()
        else:
            self.error_label.config(text="Email o contraseña incorrecta.")

    def _perform_login_event(self, event):
        """Permite que la tecla Enter active el evento de login."""
        self._perform_login()
