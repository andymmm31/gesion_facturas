import sqlite3
from sqlite3 import Error

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

if __name__ == '__main__':
    create_tables()
