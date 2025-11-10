import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import database

class CompanyManagementTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.selected_company_id = None
        self.selected_company_name = None

        self._create_widgets()
        self._load_companies()

    def _create_widgets(self):
        """Crea la interfaz de usuario de la pestaña de gestión de empresas."""
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        # Panel Izquierdo: Empresas
        company_frame = ttk.LabelFrame(main_pane, text="Empresas")
        main_pane.add(company_frame, weight=1)
        self._create_company_panel(company_frame)

        # Panel Derecho: Clientes
        client_frame = ttk.LabelFrame(main_pane, text="Clientes")
        main_pane.add(client_frame, weight=2)
        self._create_client_panel(client_frame)

    def _create_company_panel(self, parent):
        """Crea el panel de gestión de empresas."""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.company_tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre"), show="headings")
        self.company_tree.heading("ID", text="ID")
        self.company_tree.heading("Nombre", text="Nombre")
        self.company_tree.column("ID", width=50)
        self.company_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.company_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.company_tree.configure(yscrollcommand=scrollbar.set)

        self.company_tree.bind("<<TreeviewSelect>>", self._on_company_select)

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Añadir Empresa", command=self._add_company).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Empresa", command=self._edit_company).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Empresa", command=self._delete_company).pack(side=tk.LEFT, padx=5)

    def _create_client_panel(self, parent):
        """Crea el panel de gestión de clientes."""
        self.client_label = ttk.Label(parent, text="Clientes de: (Seleccione una empresa)", font=("Arial", 12))
        self.client_label.pack(pady=10)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.client_tree = ttk.Treeview(tree_frame, columns=("ID", "Nombre"), show="headings")
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Nombre", text="Nombre")
        self.client_tree.column("ID", width=50)
        self.client_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.client_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.client_tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Añadir Cliente", command=self._add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Cliente", command=self._edit_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Cliente", command=self._delete_client).pack(side=tk.LEFT, padx=5)

    def _clear_treeview(self, tree):
        """Elimina todos los elementos de un Treeview."""
        for item in tree.get_children():
            tree.delete(item)

    def _load_companies(self):
        """Carga las empresas desde la base de datos y las muestra en el Treeview."""
        self._clear_treeview(self.company_tree)
        companies = database.get_companies()
        for company in companies:
            self.company_tree.insert("", tk.END, values=company)

    def _on_company_select(self, event):
        """Maneja la selección de una empresa en el Treeview."""
        selected_items = self.company_tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        item_data = self.company_tree.item(selected_item)
        self.selected_company_id = item_data["values"][0]
        self.selected_company_name = item_data["values"][1]

        self.client_label.config(text=f"Clientes de: {self.selected_company_name}")
        self._load_clients(self.selected_company_id)

    def _load_clients(self, company_id):
        """Carga los clientes de una empresa específica."""
        self._clear_treeview(self.client_tree)
        clients = database.get_clients_for_company(company_id)
        for client in clients:
            self.client_tree.insert("", tk.END, values=client)

    # --- Lógica de Botones de Empresas ---
    def _add_company(self):
        name = simpledialog.askstring("Añadir Empresa", "Nombre de la empresa:")
        if name:
            database.add_company(name)
            self._load_companies()

    def _edit_company(self):
        selected_items = self.company_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una empresa para editar.")
            return

        old_name = self.selected_company_name
        new_name = simpledialog.askstring("Editar Empresa", "Nuevo nombre:", initialvalue=old_name)

        if new_name and new_name != old_name:
            if database.rename_company_and_update_invoices(self.selected_company_id, old_name, new_name):
                self._load_companies()
                self.client_label.config(text=f"Clientes de: {new_name}")
            else:
                messagebox.showerror("Error", "No se pudo renombrar la empresa.")

    def _delete_company(self):
        if not self.selected_company_id:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una empresa para eliminar.")
            return

        if messagebox.askyesno("Confirmar", f"¿Seguro que quiere eliminar la empresa '{self.selected_company_name}'?"):
            database.delete_company(self.selected_company_id)
            self._load_companies()
            self._clear_treeview(self.client_tree)
            self.client_label.config(text="Clientes de: (Seleccione una empresa)")
            self.selected_company_id = None
            self.selected_company_name = None

    # --- Lógica de Botones de Clientes ---
    def _add_client(self):
        if not self.selected_company_id:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una empresa para añadirle un cliente.")
            return

        name = simpledialog.askstring("Añadir Cliente", f"Nombre del nuevo cliente para '{self.selected_company_name}':")
        if name:
            database.add_client(self.selected_company_id, name)
            self._load_clients(self.selected_company_id)

    def _edit_client(self):
        selected_items = self.client_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un cliente para editar.")
            return

        selected_item = selected_items[0]
        client_id = self.client_tree.item(selected_item)["values"][0]
        old_name = self.client_tree.item(selected_item)["values"][1]

        new_name = simpledialog.askstring("Editar Cliente", "Nuevo nombre:", initialvalue=old_name)
        if new_name and new_name != old_name:
            database.edit_client(client_id, new_name)
            self._load_clients(self.selected_company_id)

    def _delete_client(self):
        selected_items = self.client_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un cliente para eliminar.")
            return

        selected_item = selected_items[0]
        client_id = self.client_tree.item(selected_item)["values"][0]
        client_name = self.client_tree.item(selected_item)["values"][1]

        if messagebox.askyesno("Confirmar", f"¿Seguro que quiere eliminar al cliente '{client_name}'?"):
            database.delete_client(client_id)
            self._load_clients(self.selected_company_id)
