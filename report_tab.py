import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
import database
import export_service
import datetime

class ReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)

        self.current_invoice_list = []
        self.current_summary_data = {}

        self._create_widgets()
        self._load_initial_data()

    def _create_widgets(self):
        """Crea la interfaz de la pestaña de reportes."""
        # --- A. Filtros ---
        filter_frame = ttk.LabelFrame(self, text="Filtros")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Fecha Inicio:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Fecha Fin:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="Empresa:").grid(row=1, column=0, padx=5, pady=5)
        self.company_combo = ttk.Combobox(filter_frame, state="readonly")
        self.company_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_select)

        ttk.Label(filter_frame, text="Cliente:").grid(row=1, column=2, padx=5, pady=5)
        self.client_combo = ttk.Combobox(filter_frame, state="readonly")
        self.client_combo.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Button(filter_frame, text="Filtrar / Recargar", command=self._load_report).grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky="nsew")

        # --- B. Agregados ---
        summary_frame = ttk.LabelFrame(self, text="Agregados")
        summary_frame.pack(fill=tk.X, pady=5)

        self.total_invoiced_label = ttk.Label(summary_frame, text="Total Facturado (€): 0.00", font=("Arial", 10, "bold"))
        self.total_invoiced_label.pack(side=tk.LEFT, padx=10)
        self.invoice_count_label = ttk.Label(summary_frame, text="Nº de Facturas: 0")
        self.invoice_count_label.pack(side=tk.LEFT, padx=10)
        self.total_base_label = ttk.Label(summary_frame, text="Total Base (€): 0.00")
        self.total_base_label.pack(side=tk.LEFT, padx=10)
        self.total_iva_label = ttk.Label(summary_frame, text="Total IVA (€): 0.00")
        self.total_iva_label.pack(side=tk.LEFT, padx=10)
        self.total_re_label = ttk.Label(summary_frame, text="Total RE (€): 0.00")
        self.total_re_label.pack(side=tk.LEFT, padx=10)

        # --- C. Tabla de Reportes ---
        report_frame = ttk.LabelFrame(self, text="Facturas")
        report_frame.pack(fill="both", expand=True, pady=5)

        columns = ("ID", "Empresa", "Cliente", "Fecha Factura", "Base", "IVA", "RE", "Factor", "Total")
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show="headings")

        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100, anchor='center')
        self.report_tree.column("Empresa", width=150)
        self.report_tree.column("Cliente", width=150)

        self.report_tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.report_tree.configure(yscrollcommand=scrollbar.set)

        self.report_tree.bind("<Double-1>", self._on_double_click)

        # --- Botones de Acción ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text="Exportar a Excel", command=self._export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Borrar Factura Seleccionada", command=self._delete_invoice).pack(side=tk.LEFT, padx=5)

    def _load_initial_data(self):
        """Carga los datos iniciales para los filtros."""
        # Set initial dates (e.g., this month)
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        self.start_date_entry.set_date(first_day_of_month)
        self.end_date_entry.set_date(today)

        self._load_company_filter()
        self._load_report()

    def _load_company_filter(self):
        self.companies_data = database.get_companies()
        company_names = ["Todos"] + [c[1] for c in self.companies_data]
        self.company_combo['values'] = company_names
        self.company_combo.set("Todos")
        self._load_client_filter(None)

    def _on_company_select(self, event):
        selected_company_name = self.company_combo.get()
        if selected_company_name == "Todos":
            self._load_client_filter(None)
        else:
            company_id = next((cid for cid, cname in self.companies_data if cname == selected_company_name), None)
            if company_id:
                self._load_client_filter(company_id)

    def _load_client_filter(self, company_id):
        if company_id:
            clients = database.get_clients_for_company(company_id)
            client_names = ["Todos"] + [c[1] for c in clients]
        else:
            client_names = ["Todos"]
        self.client_combo['values'] = client_names
        self.client_combo.set("Todos")

    def _load_report(self):
        """Carga los datos del reporte según los filtros seleccionados."""
        start = self.start_date_entry.get_date().isoformat()
        end = self.end_date_entry.get_date().isoformat()
        company = self.company_combo.get() if self.company_combo.get() != "Todos" else None
        client = self.client_combo.get() if self.client_combo.get() != "Todos" else None

        self.current_invoice_list = database.get_invoices_for_report(start, end, company, client)

        # Limpiar Treeview
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Calcular agregados
        total_invoiced = sum(inv['amount'] for inv in self.current_invoice_list)
        total_base = sum(inv['baseAmount'] for inv in self.current_invoice_list)
        total_iva = sum(inv['iva'] for inv in self.current_invoice_list)
        total_re = sum(inv['re'] for inv in self.current_invoice_list)
        invoice_count = len(self.current_invoice_list)

        self.current_summary_data = {
            "Total Facturado (€)": f"{total_invoiced:.2f}",
            "Nº de Facturas": invoice_count,
            "Total Base (€)": f"{total_base:.2f}",
            "Total IVA (€)": f"{total_iva:.2f}",
            "Total RE (€)": f"{total_re:.2f}"
        }

        # Actualizar labels
        self.total_invoiced_label.config(text=f"Total Facturado (€): {total_invoiced:.2f}")
        self.invoice_count_label.config(text=f"Nº de Facturas: {invoice_count}")
        self.total_base_label.config(text=f"Total Base (€): {total_base:.2f}")
        self.total_iva_label.config(text=f"Total IVA (€): {total_iva:.2f}")
        self.total_re_label.config(text=f"Total RE (€): {total_re:.2f}")

        # Llenar Treeview
        for inv in self.current_invoice_list:
            self.report_tree.insert("", tk.END, values=(
                inv['id'], inv['company'], inv['client'], inv['invoiceDate'],
                f"{inv['baseAmount']:.2f}", f"{inv['iva']:.2f}", f"{inv['re']:.2f}",
                f"{inv['factor']:.2f}", f"{inv['amount']:.2f}"
            ))

    def _export_to_excel(self):
        if not self.current_invoice_list:
            messagebox.showwarning("Nada que Exportar", "No hay facturas en el reporte actual para exportar.")
            return

        if export_service.export_to_excel(self.current_invoice_list, self.current_summary_data):
            messagebox.showinfo("Éxito", "El reporte se ha exportado a Excel correctamente.")
        else:
            messagebox.showerror("Error", "Ocurrió un error al exportar el archivo.")

    def _delete_invoice(self):
        selected_items = self.report_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una factura para eliminar.")
            return

        item_data = self.report_tree.item(selected_items[0])
        invoice_id = item_data['values'][0]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar la factura ID {invoice_id}?"):
            if database.delete_invoice(invoice_id):
                self._load_report()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la factura.")

    def _on_double_click(self, event):
        """Maneja el doble clic para editar el factor."""
        selected_items = self.report_tree.selection()
        if not selected_items:
            return

        item_id = selected_items[0]
        # Encontrar la factura correspondiente en nuestra lista de datos
        invoice_id = self.report_tree.item(item_id)['values'][0]
        invoice = next((inv for inv in self.current_invoice_list if inv['id'] == invoice_id), None)

        if not invoice:
            return

        current_factor = invoice['factor']
        new_factor = simpledialog.askfloat("Editar Factor", "Nuevo valor para el factor:",
                                           initialvalue=current_factor, minvalue=0.0)

        if new_factor is not None and new_factor != current_factor:
            if database.update_invoice_factor_and_amount(invoice_id, new_factor, invoice['baseAmount'], invoice['iva'], invoice['re']):
                self._load_report()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el factor.")

    def handle_invoice_saved(self, event=None):
        """Receptor de eventos para recargar el reporte."""
        print("Evento <<InvoiceSaved>> recibido. Recargando reporte...")
        self._load_report()
