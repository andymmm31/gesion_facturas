import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('facturacion.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_tables():
    """Create the database tables."""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE,
                    password TEXT
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    createdAt TEXT,
                    deleted INTEGER DEFAULT 0,
                    deletedAt TEXT
                );
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    createdAt TEXT,
                    deleted INTEGER DEFAULT 0,
                    company_id INTEGER,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                );
            """)
            c.execute("""
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
        except Error as e:
            print(e)
        finally:
            conn.close()

if __name__ == '__main__':
    create_tables()
