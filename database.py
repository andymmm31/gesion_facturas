import sqlite3
from sqlite3 import Error
import hashlib
import datetime

def _hash_password(password):
    """Hashea una contraseña usando SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    conn = None
    try:
        conn = sqlite3.connect('facturacion.db')
        print(f"Conexión a SQLite DB exitosa (versión {sqlite3.version})")
    except Error as e:
        print(e)
    return conn

def create_tables():
    """Crea las tablas en la base de datos si no existen."""
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Tabla de usuarios
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                password TEXT
            );
            """)

            # Tabla de empresas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                createdAt TEXT,
                deleted INTEGER DEFAULT 0,
                deletedAt TEXT
            );
            """)

            # Tabla de clientes
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY,
                name TEXT,
                createdAt TEXT,
                deleted INTEGER DEFAULT 0,
                deletedAt TEXT,
                company_id INTEGER,
                FOREIGN KEY(company_id) REFERENCES companies(id)
            );
            """)

            # Tabla de facturas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY,
                company TEXT,
                client TEXT,
                amount REAL,
                baseAmount REAL,
                iva_percent REAL,
                iva REAL,
                re_percent REAL,
                re REAL,
                invoiceDate TEXT,
                dueDate TEXT,
                timestamp TEXT,
                factor REAL DEFAULT 1.0
            );
            """)

            conn.commit()
            print("Tablas creadas exitosamente.")
        except Error as e:
            print(e)
        finally:
            conn.close()
    else:
        print("Error! No se pudo crear la conexión a la base de datos.")

def register_user(email, password):
    """Registra un nuevo usuario con una contraseña hasheada."""
    password_hash = _hash_password(password)
    conn = create_connection()
    if conn is None:
        return False

    sql = ''' INSERT INTO users(email,password)
              VALUES(?,?) '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (email, password_hash))
        conn.commit()
        print(f"Usuario {email} registrado exitosamente.")
        return True
    except sqlite3.IntegrityError:
        # Esto es esperado si el usuario ya existe, no es un error fatal.
        print(f"Info: El email {email} ya existe.")
        return False
    except Error as e:
        print(e)
        return False
    finally:
        if conn:
            conn.close()

def login_user(email, password):
    """Verifica las credenciales de un usuario."""
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user_record = cursor.fetchone()

        if user_record is None:
            return False # Usuario no encontrado

        stored_password_hash = user_record[0]
        entered_password_hash = _hash_password(password)

        # Comparación segura de hashes
        return stored_password_hash == entered_password_hash
    except Error as e:
        print(e)
        return False
    finally:
        if conn:
            conn.close()

# --- Funciones de Companies ---

def add_company(name):
    """Inserta una nueva empresa en la base de datos."""
    conn = create_connection()
    if conn is None:
        return None

    sql = ''' INSERT INTO companies(name, createdAt, deleted)
              VALUES(?,?,?) '''
    try:
        cursor = conn.cursor()
        current_time = datetime.datetime.now().isoformat()
        cursor.execute(sql, (name, current_time, 0))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al añadir empresa: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_companies(include_deleted=False):
    """Devuelve una lista de todas las empresas."""
    conn = create_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = "SELECT id, name FROM companies"
        if not include_deleted:
            query += " WHERE deleted = 0"
        query += " ORDER BY name"

        cursor.execute(query)
        companies = cursor.fetchall()
        return companies
    except Error as e:
        print(f"Error al obtener empresas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_company(company_id):
    """Marca una empresa como eliminada (soft delete)."""
    conn = create_connection()
    if conn is None:
        return False

    sql = ''' UPDATE companies
              SET deleted = 1, deletedAt = ?
              WHERE id = ? '''
    try:
        cursor = conn.cursor()
        current_time = datetime.datetime.now().isoformat()
        cursor.execute(sql, (current_time, company_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar empresa: {e}")
        return False
    finally:
        if conn:
            conn.close()

def rename_company_and_update_invoices(company_id, old_name, new_name):
    """
    Renombra una empresa y actualiza todas las facturas asociadas
    dentro de una única transacción.
    """
    conn = create_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        # Iniciar transacción
        cursor.execute("BEGIN")

        # 1. Actualizar el nombre en la tabla 'companies'
        cursor.execute("UPDATE companies SET name = ? WHERE id = ?", (new_name, company_id))

        # 2. Actualizar el nombre en la tabla 'invoices'
        cursor.execute("UPDATE invoices SET company = ? WHERE company = ?", (new_name, old_name))

        # Confirmar transacción
        conn.commit()
        return True
    except Error as e:
        print(f"Error en la transacción de renombrar empresa: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- Funciones de Clients ---

def add_client(company_id, client_name):
    """Añade un nuevo cliente asociado a una empresa."""
    conn = create_connection()
    if conn is None:
        return None

    sql = ''' INSERT INTO clients(name, createdAt, deleted, company_id)
              VALUES(?,?,?,?) '''
    try:
        cursor = conn.cursor()
        current_time = datetime.datetime.now().isoformat()
        cursor.execute(sql, (client_name, current_time, 0, company_id))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al añadir cliente: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_clients_for_company(company_id):
    """Devuelve una lista de clientes para una empresa específica."""
    conn = create_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM clients WHERE company_id = ? AND deleted = 0 ORDER BY name", (company_id,))
        clients = cursor.fetchall()
        return clients
    except Error as e:
        print(f"Error al obtener clientes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def edit_client(client_id, new_name):
    """Actualiza el nombre de un cliente."""
    conn = create_connection()
    if conn is None:
        return False

    sql = ''' UPDATE clients
              SET name = ?
              WHERE id = ? '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_name, client_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al editar cliente: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_client(client_id):
    """Marca un cliente como eliminado (soft delete)."""
    conn = create_connection()
    if conn is None:
        return False

    sql = ''' UPDATE clients
              SET deleted = 1, deletedAt = ?
              WHERE id = ? '''
    try:
        cursor = conn.cursor()
        current_time = datetime.datetime.now().isoformat()
        cursor.execute(sql, (current_time, client_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar cliente: {e}")
        return False
    finally:
        if conn:
            conn.close()


# --- Funciones de Invoices ---

def add_invoice(invoice_data):
    """Añade una nueva factura a la base de datos."""
    conn = create_connection()
    if conn is None:
        return None

    sql = ''' INSERT INTO invoices(company, client, baseAmount, iva_percent, iva,
                                  re_percent, re, amount, invoiceDate, dueDate, timestamp, factor)
              VALUES(:company, :client, :baseAmount, :iva_percent, :iva,
                     :re_percent, :re, :amount, :invoiceDate, :dueDate, :timestamp, :factor) '''
    try:
        cursor = conn.cursor()
        # Asegurarse de que el factor tiene un valor por defecto
        invoice_data.setdefault('factor', 1.0)
        cursor.execute(sql, invoice_data)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al añadir factura: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_last_invoice():
    """Devuelve la última factura insertada."""
    conn = create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 1")
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener la última factura: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_invoice_by_id(invoice_id):
    """Devuelve una factura por su ID."""
    conn = create_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener factura por ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_invoice(invoice_id, invoice_data):
    """Actualiza una factura existente."""
    conn = create_connection()
    if conn is None:
        return False

    # Construir la sentencia SET dinámicamente
    fields = ", ".join([f"{key} = :{key}" for key in invoice_data])
    sql = f"UPDATE invoices SET {fields} WHERE id = :id"
    invoice_data['id'] = invoice_id

    try:
        cursor = conn.cursor()
        cursor.execute(sql, invoice_data)
        conn.commit()
        return True
    except Error as e:
        print(f"Error al actualizar factura: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_invoices_for_report(start_date=None, end_date=None, company=None, client=None):
    """
    Obtiene facturas para un reporte, con filtros opcionales.
    """
    conn = create_connection()
    if conn is None:
        return []

    try:
        conn.row_factory = sqlite3.Row # Devolver filas como diccionarios
        cursor = conn.cursor()
        query = "SELECT * FROM invoices WHERE 1=1"
        params = {}

        if start_date:
            query += " AND invoiceDate >= :start_date"
            params['start_date'] = start_date

        if end_date:
            query += " AND invoiceDate <= :end_date"
            params['end_date'] = end_date

        if company:
            query += " AND company = :company"
            params['company'] = company

        if client:
            query += " AND client = :client"
            params['client'] = client

        query += " ORDER BY invoiceDate DESC"

        cursor.execute(query, params)
        # Convertir las filas a diccionarios estándar
        rows = [dict(row) for row in cursor.fetchall()]
        return rows
    except Error as e:
        print(f"Error al obtener facturas para reporte: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_invoice(invoice_id):
    """Elimina una factura de la base de datos."""
    conn = create_connection()
    if conn is None:
        return False

    sql = 'DELETE FROM invoices WHERE id = ?'
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (invoice_id,))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar factura: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_invoice_factor_and_amount(invoice_id, new_factor, base_amount, iva_amount, re_amount):
    """Actualiza el factor y el importe total de una factura."""
    conn = create_connection()
    if conn is None:
        return False

    new_total = (base_amount + iva_amount + re_amount) * new_factor
    sql = 'UPDATE invoices SET factor = ?, amount = ? WHERE id = ?'

    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_factor, new_total, invoice_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al actualizar el factor de la factura: {e}")
        return False
    finally:
        if conn:
            conn.close()


def change_password(email, old_password, new_password):
    """
    Cambia la contraseña de un usuario si la contraseña antigua es correcta.
    """
    # Primero, verificar la contraseña antigua
    if not login_user(email, old_password):
        return False, "La contraseña antigua es incorrecta."

    # Si la verificación es exitosa, actualizar con la nueva contraseña
    conn = create_connection()
    if conn is None:
        return False, "No se pudo conectar a la base de datos."

    new_password_hash = _hash_password(new_password)
    sql = 'UPDATE users SET password = ? WHERE email = ?'

    try:
        cursor = conn.cursor()
        cursor.execute(sql, (new_password_hash, email))
        conn.commit()
        return True, "Contraseña actualizada correctamente."
    except Error as e:
        print(f"Error al cambiar la contraseña: {e}")
        return False, "Error al actualizar la base de datos."
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_tables()
