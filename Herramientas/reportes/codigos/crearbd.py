import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import psycopg2


def abrir_ventana_creacion(parent, conexion, entry_password, entry_host, entry_port, entry_usuario):
    global creacion_bd_window, db_var, esquema_var, esquema_menu
    
    # Si la conexión no está establecida, intentamos conectarnos solo con el host, puerto, usuario y contraseña.
    if not validar_conexion_bd(conexion):
        host = entry_host.get()
        port = entry_port.get()
        usuario = entry_usuario.get()
        contraseña = entry_password.get()

        try:
            conexion = psycopg2.connect(
                host=host,
                port=port,
                user=usuario,
                password=contraseña
            )
        except psycopg2.OperationalError as e:
            messagebox.showerror("Error", f"Error al conectar al servidor: {e}")
            return

    creacion_bd_window = tk.Toplevel(parent)
    creacion_bd_window.title("Crear Base de Datos y Esquema")

    db_var = tk.StringVar()
    esquema_var = tk.StringVar()

    frame_db = ttk.Frame(creacion_bd_window)
    frame_db.pack(pady=10, padx=10, fill='x')

    label_db = ttk.Label(frame_db, text="Bases de datos existentes:")
    label_db.pack(side=tk.LEFT)

    db_menu = ttk.Combobox(frame_db, textvariable=db_var, values=listar_bases_datos(conexion), state="readonly")
    db_menu.pack(side=tk.LEFT, fill='x', expand=True)
    db_menu.bind("<<ComboboxSelected>>", lambda event: actualizar_esquemas(conexion, db_menu.get()))

    button_nueva_bd = ttk.Button(frame_db, text="+", command=lambda: crear_nueva_base_datos(entry_host, entry_port, entry_usuario, entry_password, db_menu))
    button_nueva_bd.pack(side=tk.LEFT, padx=5)

    frame_esquema = ttk.Frame(creacion_bd_window)
    frame_esquema.pack(pady=10, padx=10, fill='x')

    label_esquema = ttk.Label(frame_esquema, text="Esquemas existentes:")
    label_esquema.pack(side=tk.LEFT)

    esquema_menu = ttk.Combobox(frame_esquema, textvariable=esquema_var, state="readonly")
    esquema_menu.pack(side=tk.LEFT, fill='x', expand=True)

    button_nuevo_esquema = ttk.Button(frame_esquema, text="+", command=lambda: crear_nuevo_esquema(conexion, db_var.get(), esquema_menu))
    button_nuevo_esquema.pack(side=tk.LEFT, padx=5)

    # Inicia el listado de esquemas para la base de datos seleccionada inicialmente (si la hay)
    if db_var.get():
        actualizar_esquemas(conexion, db_var.get())










def listar_bases_datos(conexion):
    """
    Lista las bases de datos existentes en el servidor PostgreSQL.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        bases_datos = [row[0] for row in cursor.fetchall()]
        return bases_datos
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo listar las bases de datos: {e}")
        return []

def actualizar_esquemas(conexion, nombre_bd):
    """
    Actualiza el menú de esquemas basándose en la base de datos seleccionada.
    """
    esquemas = listar_esquemas(conexion, nombre_bd)
    esquema_menu['values'] = esquemas
    if esquemas:
        esquema_var.set(esquemas[0])


def crear_nueva_base_datos(entry_host, entry_port, entry_usuario, entry_password, db_menu):
    """
    Permite al usuario crear una nueva base de datos.
    """
    nombre_bd = simpledialog.askstring("Crear Base de Datos", "Ingrese el nombre de la nueva base de datos:")

    if nombre_bd:
        try:
            # Crear una nueva conexión sin transacción automática para ejecutar CREATE DATABASE
            nueva_conexion = psycopg2.connect(
                host=entry_host.get(),
                port=entry_port.get(),
                user=entry_usuario.get(),
                password=entry_password.get()
            )
            nueva_conexion.autocommit = True

            cursor = nueva_conexion.cursor()
            cursor.execute(f"CREATE DATABASE {nombre_bd};")
            nueva_conexion.close()

            messagebox.showinfo("Éxito", f"La base de datos '{nombre_bd}' fue creada exitosamente.")
            bases_datos = listar_bases_datos(nueva_conexion)
            db_menu['values'] = bases_datos
            db_var.set(nombre_bd)
            actualizar_esquemas(nueva_conexion, nombre_bd)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la base de datos: {e}")



def listar_esquemas(conexion, nombre_bd):
    """
    Lista los esquemas existentes en la base de datos seleccionada.
    """
    try:
        nueva_conexion = psycopg2.connect(
            host=conexion.get_dsn_parameters()['host'],
            port=conexion.get_dsn_parameters()['port'],
            database=nombre_bd,  # Conectar a la base de datos seleccionada
            user=conexion.get_dsn_parameters()['user'],
            password=conexion.get_dsn_parameters().get('password')
        )
        cursor = nueva_conexion.cursor()
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        esquemas = [row[0] for row in cursor.fetchall()]
        nueva_conexion.close()
        return esquemas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo listar los esquemas: {e}")
        return []


def crear_nuevo_esquema(conexion, nombre_bd, esquema_menu):
    """
    Permite al usuario crear un nuevo esquema en la base de datos seleccionada.
    """
    nombre_esquema = simpledialog.askstring("Crear Esquema", "Ingrese el nombre del nuevo esquema:")

    if nombre_esquema:
        try:
            nueva_conexion = psycopg2.connect(
                host=conexion.get_dsn_parameters()['host'],
                port=conexion.get_dsn_parameters()['port'],
                database=nombre_bd,  # Conectar a la base de datos seleccionada
                user=conexion.get_dsn_parameters()['user'],
                password=conexion.get_dsn_parameters().get('password')
            )
            nueva_conexion.autocommit = True

            cursor = nueva_conexion.cursor()
            cursor.execute(f"CREATE SCHEMA {nombre_esquema};")
            nueva_conexion.close()

            messagebox.showinfo("Éxito", f"El esquema '{nombre_esquema}' fue creado exitosamente en la base de datos '{nombre_bd}'.")
            esquemas = listar_esquemas(conexion, nombre_bd)
            esquema_menu['values'] = esquemas
            esquema_var.set(nombre_esquema)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el esquema: {e}")

def validar_conexion_bd(conexion):
    """
    Valida que la conexión a la base de datos esté establecida antes de proceder.
    """
    try:
        if conexion is None or conexion.closed:
            return False
        cursor = conexion.cursor()
        cursor.execute("SELECT 1;")
        return True
    except psycopg2.Error:
        return False
