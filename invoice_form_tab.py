import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database
import datetime

class InvoiceFormTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Variables para los cálculos
        self.base_amount_var = tk.DoubleVar(value=0.0)
        self.iva_percent_var = tk.DoubleVar(value=21.0)
        self.re_percent_var = tk.DoubleVar(value=0.0)

        self.base_amount_var.trace_add("write", self._calculate_totals)
        self.iva_percent_var.trace_add("write", self._calculate_totals)
        self.re_percent_var.trace_add("write", self._calculate_totals)

        self._create_widgets()
        self._load_companies()

    def _create_widgets(self):
        """Crea la interfaz de usuario del formulario de factura."""
        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.X)

        # --- Fila 1: Empresa y Cliente ---
        ttk.Label(form_frame, text="Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.company_combo = ttk.Combobox(form_frame, state="readonly")
        self.company_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_select)

        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.client_combo = ttk.Combobox(form_frame, state="readonly")
        self.client_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # --- Fila 2: Importe Base, IVA %, RE % ---
        ttk.Label(form_frame, text="Importe Base (€):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.base_amount_entry = ttk.Entry(form_frame, textvariable=self.base_amount_var)
        self.base_amount_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="IVA %:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.iva_combo = ttk.Combobox(form_frame, values=[21, 10, 4, 0], textvariable=self.iva_percent_var)
        self.iva_combo.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="RE %:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.re_entry = ttk.Entry(form_frame, textvariable=self.re_percent_var)
        self.re_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # --- Fila 3: Fechas ---
        ttk.Label(form_frame, text="Fecha Factura:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.invoice_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=17)
        self.invoice_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Fecha Vencimiento:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.due_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=17)
        self.due_date_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # --- Sección de Cálculos ---
        calculations_frame = ttk.LabelFrame(self, text="Cálculos")
        calculations_frame.pack(fill=tk.X, pady=10)

        self.iva_amount_label = ttk.Label(calculations_frame, text="Importe IVA (€): 0.00")
        self.iva_amount_label.pack(anchor="w", padx=10)
        self.re_amount_label = ttk.Label(calculations_frame, text="Importe RE (€): 0.00")
        self.re_amount_label.pack(anchor="w", padx=10)
        self.total_amount_label = ttk.Label(calculations_frame, text="TOTAL (€): 0.00", font=("Arial", 12, "bold"))
        self.total_amount_label.pack(anchor="w", padx=10, pady=5)

        # --- Botones de Acción ---
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Guardar Factura", command=self._save_invoice).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar Formulario", command=self._clear_form).pack(side=tk.LEFT, padx=5)

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

    def _load_companies(self):
        """Carga las empresas en el combobox."""
        self.companies_data = database.get_companies()
        company_names = [company[1] for company in self.companies_data]
        self.company_combo['values'] = company_names

    def _on_company_select(self, event):
        """Maneja la selección de una empresa."""
        selected_company_name = self.company_combo.get()
        company_id = None
        for cid, cname in self.companies_data:
            if cname == selected_company_name:
                company_id = cid
                break

        if company_id:
            self._load_clients(company_id)

    def _load_clients(self, company_id):
        """Carga los clientes de la empresa seleccionada."""
        self.clients_data = database.get_clients_for_company(company_id)
        client_names = [client[1] for client in self.clients_data]
        self.client_combo['values'] = client_names
        if client_names:
            self.client_combo.set(client_names[0])
        else:
            self.client_combo.set('')

    def _calculate_totals(self, *args):
        """Calcula los importes de IVA, RE y el total."""
        try:
            base = self.base_amount_var.get()
            iva_p = self.iva_percent_var.get()
            re_p = self.re_percent_var.get()
        except (tk.TclError, ValueError):
            base, iva_p, re_p = 0.0, 0.0, 0.0

        iva_amount = base * (iva_p / 100)
        re_amount = base * (max(0.0, re_p) / 100)
        total = base + iva_amount + re_amount

        self.iva_amount_label.config(text=f"Importe IVA (€): {iva_amount:.2f}")
        self.re_amount_label.config(text=f"Importe RE (€): {re_amount:.2f}")
        self.total_amount_label.config(text=f"TOTAL (€): {total:.2f}")

    def _save_invoice(self):
        """Valida y guarda la factura en la base de datos."""
        # --- Validación ---
        if self.base_amount_var.get() <= 0:
            messagebox.showerror("Error de Validación", "El importe base debe ser mayor que cero.")
            return
        if not self.client_combo.get():
            messagebox.showerror("Error de Validación", "Debe seleccionar un cliente.")
            return

        invoice_date = self.invoice_date_entry.get_date()
        due_date = self.due_date_entry.get_date()
        if invoice_date > due_date:
            messagebox.showerror("Error de Validación", "La fecha de factura no puede ser posterior a la fecha de vencimiento.")
            return

        # --- Recopilación de datos ---
        base = self.base_amount_var.get()
        iva_p = self.iva_percent_var.get()
        re_p = self.re_percent_var.get()
        iva_amount = base * (iva_p / 100)
        re_amount = base * (max(0.0, re_p) / 100)
        total = base + iva_amount + re_amount

        invoice_data = {
            "company": self.company_combo.get(),
            "client": self.client_combo.get(),
            "baseAmount": base,
            "iva_percent": iva_p,
            "iva": iva_amount,
            "re_percent": re_p,
            "re": re_amount,
            "amount": total,
            "invoiceDate": invoice_date.isoformat(),
            "dueDate": due_date.isoformat(),
            "timestamp": datetime.datetime.now().isoformat()
        }

        # --- Guardado ---
        if database.add_invoice(invoice_data):
            messagebox.showinfo("Éxito", "Factura guardada correctamente.")
            self.master.event_generate("<<InvoiceSaved>>")
            self._clear_form()
        else:
            messagebox.showerror("Error de Base de Datos", "No se pudo guardar la factura.")

    def _clear_form(self):
        """Limpia todos los campos del formulario."""
        self.company_combo.set('')
        self.client_combo.set('')
        self.client_combo['values'] = []
        self.base_amount_var.set(0.0)
        self.iva_percent_var.set(21.0)
        self.re_percent_var.set(0.0)
        today = datetime.date.today()
        self.invoice_date_entry.set_date(today)
        self.due_date_entry.set_date(today)
        self._calculate_totals()
