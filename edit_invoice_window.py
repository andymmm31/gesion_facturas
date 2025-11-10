import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import database
import datetime

class EditInvoiceWindow(tk.Toplevel):
    def __init__(self, parent, invoice_id, on_save_callback):
        super().__init__(parent)
        self.title("Editar Factura")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        self.invoice_id = invoice_id
        self.on_save_callback = on_save_callback

        # Cargar los datos de la factura a editar
        self.invoice_data = database.get_invoice_by_id(self.invoice_id)
        if not self.invoice_data:
            messagebox.showerror("Error", "No se pudieron cargar los datos de la factura.", parent=self)
            self.destroy()
            return

        # Convertir la fila a un diccionario si es necesario (depende de la configuración de row_factory)
        if not isinstance(self.invoice_data, dict):
            # Asumimos el orden de las columnas de la tabla 'invoices'
            keys = ['id', 'company', 'client', 'amount', 'baseAmount', 'iva_percent', 'iva', 're_percent', 're', 'invoiceDate', 'dueDate', 'timestamp', 'factor']
            self.invoice_data = dict(zip(keys, self.invoice_data))


        # Variables para los campos del formulario
        self.base_amount_var = tk.DoubleVar(value=self.invoice_data.get('baseAmount', 0.0))
        self.iva_percent_var = tk.DoubleVar(value=self.invoice_data.get('iva_percent', 21.0))
        self.re_percent_var = tk.DoubleVar(value=self.invoice_data.get('re_percent', 0.0))
        self.factor_var = tk.DoubleVar(value=self.invoice_data.get('factor', 1.0))

        self.base_amount_var.trace_add("write", self._calculate_totals)
        self.iva_percent_var.trace_add("write", self._calculate_totals)
        self.re_percent_var.trace_add("write", self._calculate_totals)
        self.factor_var.trace_add("write", self._calculate_totals)

        self._create_widgets()
        self._load_combobox_data()
        self._calculate_totals() # Calcular totales iniciales

    def _create_widgets(self):
        """Crea la interfaz de usuario de la ventana de edición."""
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill="both", expand=True)

        # --- Campos del Formulario ---
        ttk.Label(form_frame, text="Empresa:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.company_combo = ttk.Combobox(form_frame, state="readonly")
        self.company_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.company_combo.bind("<<ComboboxSelected>>", self._on_company_select)

        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.client_combo = ttk.Combobox(form_frame, state="readonly")
        self.client_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Importe Base (€):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(form_frame, textvariable=self.base_amount_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="IVA %:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(form_frame, values=[21, 10, 4, 0], textvariable=self.iva_percent_var).grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="RE %:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(form_frame, textvariable=self.re_percent_var).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Factor:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        ttk.Entry(form_frame, textvariable=self.factor_var).grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Fecha Factura:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.invoice_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.invoice_date_entry.set_date(self.invoice_data.get('invoiceDate'))
        self.invoice_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(form_frame, text="Fecha Vencimiento:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        self.due_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        self.due_date_entry.set_date(self.invoice_data.get('dueDate'))
        self.due_date_entry.grid(row=3, column=3, padx=5, pady=5, sticky="ew")

        # --- Cálculos ---
        calculations_frame = ttk.LabelFrame(form_frame, text="Cálculos")
        calculations_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=10)
        self.iva_amount_label = ttk.Label(calculations_frame, text="Importe IVA (€): 0.00")
        self.iva_amount_label.pack(anchor="w", padx=10)
        self.re_amount_label = ttk.Label(calculations_frame, text="Importe RE (€): 0.00")
        self.re_amount_label.pack(anchor="w", padx=10)
        self.total_amount_label = ttk.Label(calculations_frame, text="TOTAL (€): 0.00", font=("Arial", 12, "bold"))
        self.total_amount_label.pack(anchor="w", padx=10, pady=5)

        # --- Botones ---
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Guardar Cambios", command=self._save_changes).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side="left")

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

    def _load_combobox_data(self):
        """Carga los datos de empresas y clientes y establece los valores iniciales."""
        self.companies_data = database.get_companies()
        company_names = [c[1] for c in self.companies_data]
        self.company_combo['values'] = company_names
        self.company_combo.set(self.invoice_data.get('company', ''))

        self._on_company_select(None) # Cargar clientes para la empresa seleccionada
        self.client_combo.set(self.invoice_data.get('client', ''))

    def _on_company_select(self, event):
        """Carga los clientes cuando se selecciona una empresa."""
        selected_company_name = self.company_combo.get()
        company_id = next((cid for cid, cname in self.companies_data if cname == selected_company_name), None)
        if company_id:
            clients = database.get_clients_for_company(company_id)
            self.client_combo['values'] = [c[1] for c in clients]

    def _calculate_totals(self, *args):
        """Calcula y muestra los totales de la factura."""
        try:
            base = self.base_amount_var.get()
            iva_p = self.iva_percent_var.get()
            re_p = self.re_percent_var.get()
            factor = self.factor_var.get()
        except (tk.TclError, ValueError):
            return

        iva_amount = base * (iva_p / 100)
        re_amount = base * (max(0.0, re_p) / 100)
        total = (base + iva_amount + re_amount) * factor

        self.iva_amount_label.config(text=f"Importe IVA (€): {iva_amount:.2f}")
        self.re_amount_label.config(text=f"Importe RE (€): {re_amount:.2f}")
        self.total_amount_label.config(text=f"TOTAL (€): {total:.2f}")

    def _save_changes(self):
        """Valida y guarda los cambios en la base de datos."""
        if self.base_amount_var.get() <= 0:
            messagebox.showerror("Error", "El importe base debe ser mayor que cero.", parent=self)
            return
        if not self.client_combo.get():
            messagebox.showerror("Error", "Debe seleccionar un cliente.", parent=self)
            return

        # Recalcular valores finales
        base = self.base_amount_var.get()
        iva_p = self.iva_percent_var.get()
        re_p = self.re_percent_var.get()
        factor = self.factor_var.get()
        iva = base * (iva_p / 100)
        re = base * (max(0.0, re_p) / 100)
        amount = (base + iva + re) * factor

        updated_data = {
            "company": self.company_combo.get(),
            "client": self.client_combo.get(),
            "baseAmount": base,
            "iva_percent": iva_p,
            "iva": iva,
            "re_percent": re_p,
            "re": re,
            "factor": factor,
            "amount": amount,
            "invoiceDate": self.invoice_date_entry.get_date().isoformat(),
            "dueDate": self.due_date_entry.get_date().isoformat()
        }

        if database.update_invoice(self.invoice_id, updated_data):
            messagebox.showinfo("Éxito", "Factura actualizada correctamente.", parent=self)
            self.on_save_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la factura.", parent=self)
