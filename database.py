import sqlite3
from sqlite3 import Error
import hashlib

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
                iva REAL,
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

if __name__ == '__main__':
    create_tables()
