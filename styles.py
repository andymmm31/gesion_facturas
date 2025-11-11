from tkinter import ttk

def setup_styles():
    """Configura los estilos personalizados para la aplicación."""
    style = ttk.Style()

    # Tema base
    style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'

    # --- Colores ---
    BG_COLOR = "#ECEFF1"         # Un gris azulado claro
    PRIMARY_COLOR = "#263238"    # Un gris oscuro para texto y bordes
    SECONDARY_COLOR = "#546E7A"  # Un gris medio para texto secundario
    ACCENT_COLOR = "#0277BD"     # Un azul para elementos interactivos

    # --- Configuración General ---
    style.configure('.',
                    background=BG_COLOR,
                    foreground=PRIMARY_COLOR,
                    font=('Helvetica', 10))

    # --- TFrame ---
    style.configure('TFrame', background=BG_COLOR)

    # --- TNotebook ---
    style.configure('TNotebook', background=BG_COLOR, borderwidth=1)
    style.configure('TNotebook.Tab',
                    background="#B0BEC5", # Pestaña inactiva
                    foreground=PRIMARY_COLOR,
                    padding=[10, 5],
                    font=('Helvetica', 11, 'bold'))
    style.map('TNotebook.Tab',
              background=[('selected', BG_COLOR)], # Pestaña activa
              foreground=[('selected', ACCENT_COLOR)])

    # --- TLabel ---
    style.configure('TLabel', background=BG_COLOR, foreground=PRIMARY_COLOR)
    style.configure('TSecondary.TLabel', foreground=SECONDARY_COLOR)
    style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))

    # --- TLabelFrame ---
    style.configure('TLabelFrame', background=BG_COLOR, borderwidth=1, relief="solid")
    style.configure('TLabelFrame.Label',
                    foreground=ACCENT_COLOR,
                    background=BG_COLOR,
                    font=('Helvetica', 11, 'bold'))


    # --- TButton ---
    style.configure('TButton',
                    background=ACCENT_COLOR,
                    foreground='white',
                    font=('Helvetica', 10, 'bold'),
                    padding=6,
                    borderwidth=0)
    style.map('TButton',
              background=[('active', '#039BE5'), ('disabled', '#B0BEC5')])

    # --- TEntry y TCombobox ---
    style.configure('TEntry',
                    fieldbackground='white',
                    foreground=PRIMARY_COLOR,
                    insertcolor=PRIMARY_COLOR)
    style.map('TEntry',
              bordercolor=[('focus', ACCENT_COLOR)])

    style.configure('TCombobox',
                    fieldbackground='white',
                    foreground=PRIMARY_COLOR,
                    selectbackground=ACCENT_COLOR,
                    selectforeground='white',
                    arrowcolor=ACCENT_COLOR)

    # --- TTreeview ---
    style.configure('Treeview',
                    rowheight=25,
                    fieldbackground=BG_COLOR)
    style.configure('Treeview.Heading',
                    background="#CFD8DC", # Cabecera de la tabla
                    font=('Helvetica', 10, 'bold'),
                    foreground=PRIMARY_COLOR)
    style.map('Treeview.Heading',
              background=[('active', '#B0BEC5')])

    # Cambiar el color de la fila seleccionada
    style.map('Treeview',
              background=[('selected', ACCENT_COLOR)],
              foreground=[('selected', 'white')])
