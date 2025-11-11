import tkinter as tk
from tkinter import ttk, messagebox
import database
from company_management_tab import CompanyManagementTab
from invoice_form_tab import InvoiceFormTab
from report_tab import ReportTab
from login_screen import LoginScreen
from change_password_window import ChangePasswordWindow
import styles

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Facturas")
        self.geometry("1280x720")
        self.logged_in = False
        self.current_user_email = None

        # Aplicar estilos
        styles.setup_styles()

        database.create_tables()
        self._create_widgets()
        self._update_login_status()

    def _create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Notebook para las pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Pestaña 1: Registrar Factura (siempre visible)
        self.invoice_form_tab = InvoiceFormTab(self.notebook)
        self.notebook.add(self.invoice_form_tab, text='Registrar Factura')

        # Pestaña 2: Empresas (placeholder inicial)
        self.company_tab_placeholder = self._create_placeholder_tab("Empresas")
        self.notebook.add(self.company_tab_placeholder, text='Empresas', state='disabled')

        # Pestaña 3: Reportes (placeholder inicial)
        self.report_tab_placeholder = self._create_placeholder_tab("Reportes")
        self.notebook.add(self.report_tab_placeholder, text='Reportes', state='disabled')

        # Barra de estado
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(side="bottom", fill="x")
        self.login_status_label = ttk.Label(self.status_bar, text="No ha iniciado sesión")
        self.login_status_label.pack(side="left", padx=10)

        self.change_password_button = ttk.Button(self.status_bar, text="Cambiar Contraseña", command=self._show_change_password_window)
        # El botón de cambiar contraseña se mostrará/ocultará en _update_login_status

        self.login_button = ttk.Button(self.status_bar, text="Iniciar Sesión", command=self._show_login_screen)
        self.login_button.pack(side="right", padx=10)

    def _create_placeholder_tab(self, tab_name):
        frame = ttk.Frame(self.notebook)
        ttk.Label(frame, text=f"Inicie sesión para acceder a '{tab_name}'").pack(pady=50)
        return frame

    def _update_login_status(self):
        if self.logged_in:
            self.login_status_label.config(text=f"Sesión iniciada como: {self.current_user_email}")
            self.login_button.config(text="Cerrar Sesión", command=self._logout)
            self.change_password_button.pack(side="right", padx=5)
            self._enable_protected_tabs()
        else:
            self.current_user_email = None
            self.login_status_label.config(text="No ha iniciado sesión")
            self.login_button.config(text="Iniciar Sesión", command=self._show_login_screen)
            self.change_password_button.pack_forget()
            self._disable_protected_tabs()

    def _show_login_screen(self):
        login_window = tk.Toplevel(self)
        login_window.title("Iniciar Sesión")
        login_window.geometry("400x300")
        # Pasamos el email a on_login_success
        login_screen = LoginScreen(login_window, on_login_success=lambda email: self._on_login_success(login_window, email))

    def _on_login_success(self, login_window, email):
        login_window.destroy()
        self.logged_in = True
        self.current_user_email = email
        self._update_login_status()

    def _logout(self):
        self.logged_in = False
        self._update_login_status()

    def _show_change_password_window(self):
        if self.current_user_email:
            ChangePasswordWindow(self, self.current_user_email)
        else:
            messagebox.showwarning("No ha iniciado sesión", "Debe iniciar sesión para cambiar la contraseña.")

    def _enable_protected_tabs(self):
        # Eliminar placeholders en orden inverso para evitar problemas de índice
        self.notebook.forget(2) # Eliminar placeholder de Reportes
        self.notebook.forget(1) # Eliminar placeholder de Empresas

        # Añadir las pestañas funcionales en el orden correcto
        self.company_tab = CompanyManagementTab(self.notebook)
        self.notebook.insert(1, self.company_tab, text='Empresas')

        self.report_tab = ReportTab(self.notebook)
        self.notebook.insert(2, self.report_tab, text='Reportes')

        # Habilitar las pestañas
        self.notebook.tab(1, state='normal')
        self.notebook.tab(2, state='normal')

        # Configurar bindings después de crear las pestañas
        self.bind("<<InvoiceSaved>>", self.report_tab.handle_invoice_saved)
        self.bind("<<CompaniesUpdated>>", self.invoice_form_tab.handle_companies_updated)
        self.bind("<<CompaniesUpdated>>", self.report_tab.handle_companies_updated, add='+')

    def _disable_protected_tabs(self):
        # Revertir a placeholders si las pestañas existen
        # Esta lógica es compleja, una simplificación por ahora es solo deshabilitar
        if hasattr(self, 'company_tab'):
            self.notebook.tab(1, state='disabled')
        if hasattr(self, 'report_tab'):
            self.notebook.tab(2, state='disabled')

if __name__ == '__main__':
    app = App()
    app.mainloop()
