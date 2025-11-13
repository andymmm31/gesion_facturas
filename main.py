import tkinter as tk
from tkinter import ttk
import database

class MainApplication(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # Create Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.companies_tab = ttk.Frame(self.notebook)
        self.invoice_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.companies_tab, text='Empresas')
        self.notebook.add(self.invoice_tab, text='Registrar Factura')
        self.notebook.add(self.reports_tab, text='Reportes')

        # Add content to tabs
        ttk.Label(self.companies_tab, text='Contenido de Empresas').pack(padx=20, pady=20)
        ttk.Label(self.invoice_tab, text='Contenido de Registrar Factura').pack(padx=20, pady=20)
        ttk.Label(self.reports_tab, text='Contenido de Reportes').pack(padx=20, pady=20)

def main():
    # Initialize database
    database.create_tables()

    # Create main window
    root = tk.Tk()
    root.title("Gestión de Facturas")
    root.geometry("800x600")

    # The main application frame
    MainApplication(root).pack(side="top", fill="both", expand=True)

    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
