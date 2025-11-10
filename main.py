import tkinter as tk
from tkinter import ttk
import database
from login_screen import LoginScreen
from company_management_tab import CompanyManagementTab

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Facturas")
        self.geometry("1024x768") # Aumentamos el tamaño para la nueva interfaz

        # Crear tablas de la base de datos al iniciar
        database.create_tables()

        # Configurar el contenedor principal
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self._create_main_tabs()
        self._show_login_screen()

    def _create_main_tabs(self):
        """Crea el Notebook con las pestañas principales, pero no lo muestra."""
        self.main_notebook = ttk.Notebook(self.container)

        # Pestaña 1: Empresas (ahora funcional)
        company_tab = CompanyManagementTab(self.main_notebook)
        self.main_notebook.add(company_tab, text='Empresas')

        # Pestaña 2: Registrar Factura (placeholder)
        registrar_factura_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(registrar_factura_frame, text='Registrar Factura')
        ttk.Label(registrar_factura_frame, text="Contenido de Registrar Factura").pack(pady=20, padx=20)

        # Pestaña 3: Reportes (placeholder)
        reportes_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(reportes_frame, text='Reportes')
        ttk.Label(reportes_frame, text="Contenido de Reportes").pack(pady=20, padx=20)

    def _show_login_screen(self):
        """Muestra la pantalla de login."""
        self.login_screen = LoginScreen(self.container, on_login_success=self._on_login_success)
        self.login_screen.pack(fill="both", expand=True)

    def _on_login_success(self):
        """Callback que se ejecuta cuando el login es exitoso."""
        # Oculta la pantalla de login
        self.login_screen.pack_forget()
        self.login_screen.destroy()

        # Muestra el contenido principal de la aplicación
        self.main_notebook.pack(expand=True, fill='both')

if __name__ == '__main__':
    app = App()
    app.mainloop()
