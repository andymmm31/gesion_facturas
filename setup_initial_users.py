import database
import sqlite3

def setup_users():
    """
    Crea las tablas de la base de datos y registra los usuarios iniciales.
    Utiliza un bloque try-except para manejar el caso en que los usuarios ya existan.
    """
    print("Iniciando la configuración inicial de usuarios...")

    # 1. Asegurarse de que las tablas existen
    database.create_tables()

    # 2. Registrar usuarios iniciales
    users_to_register = [
        ('luandy1220@gmail.com', 'administrador'),
        ('farmaciamanchareal@gmail.com', 'administrador')
    ]

    for email, password in users_to_register:
        try:
            database.register_user(email, password)
        except sqlite3.IntegrityError:
            # Esta excepción es manejada dentro de register_user,
            # pero la volvemos a capturar aquí por si acaso y para mayor claridad.
            print(f"El usuario {email} ya existe en la base de datos.")
        except Exception as e:
            print(f"Ocurrió un error inesperado al registrar a {email}: {e}")

    print("Configuración inicial de usuarios completada.")

if __name__ == '__main__':
    setup_users()
