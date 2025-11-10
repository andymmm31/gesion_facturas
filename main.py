import tkinter as tk
from tkinter import ttk
import database

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Facturas")
        self.geometry("800x600")

        # Crear tablas de la base de datos al iniciar
        database.create_tables()

        # Crear el Notebook (sistema de pestañas)
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        # Pestaña de Empresas
        empresas_frame = ttk.Frame(notebook)
        notebook.add(empresas_frame, text='Empresas')
        ttk.Label(empresas_frame, text="Contenido de Empresas").pack(pady=20, padx=20)

        # Pestaña de Registrar Factura
        registrar_factura_frame = ttk.Frame(notebook)
        notebook.add(registrar_factura_frame, text='Registrar Factura')
        ttk.Label(registrar_factura_frame, text="Contenido de Registrar Factura").pack(pady=20, padx=20)

        # Pestaña de Reportes
        reportes_frame = ttk.Frame(notebook)
        notebook.add(reportes_frame, text='Reportes')
        ttk.Label(reportes_frame, text="Contenido de Reportes").pack(pady=20, padx=20)

if __name__ == '__main__':
    app = App()
    app.mainloop()
