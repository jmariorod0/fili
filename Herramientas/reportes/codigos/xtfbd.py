import os
import subprocess
import psycopg2
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt


def validar_conexion_bd(conexion):
    """
    Valida que la conexión a la base de datos esté establecida antes de proceder con la importación.
    """
    try:
        if conexion is None or conexion.closed:
            raise psycopg2.Error("La conexión a la base de datos no está establecida.")
        cursor = conexion.cursor()
        cursor.execute("SELECT 1;")
        return True
    except psycopg2.Error:
        QMessageBox.critical(None, "Error", "La conexión a la base de datos no está establecida. Conéctese antes de proceder.")
        return False


def obtener_ruta_ili2pg():
    """
    Obtiene la ruta al archivo ili2pg-5.1.0.jar dentro de la estructura del plugin.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    ili2pg_path = os.path.join(plugin_dir, "ilidb", "ili2pg-5.1.0.jar")
    
    if not os.path.exists(ili2pg_path):
        raise FileNotFoundError(f"No se encontró ili2pg en la ruta esperada: {ili2pg_path}")

    return ili2pg_path


def obtener_ruta_modelos_ili(usando_palmira=False):
    """
    Obtiene la ruta a la carpeta que contiene los modelos .ili dentro de la estructura del proyecto.
    Si usando_palmira es True, usa la carpeta 'modelos2'.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    if usando_palmira:
        modelos_ili_path = os.path.join(plugin_dir, "modelos2")
    else:
        modelos_ili_path = os.path.join(plugin_dir, "modelos")

    if not os.path.exists(modelos_ili_path):
        raise FileNotFoundError(f"No se encontró la carpeta de modelos .ili en la ruta esperada: {modelos_ili_path}")

    return modelos_ili_path


def obtener_modelos_desde_ili(modelos_ili_path):
    """
    Obtiene la lista de modelos a partir de los archivos .ili en la carpeta especificada.
    """
    modelos = [os.path.splitext(f)[0] for f in os.listdir(modelos_ili_path) if f.endswith(".ili")]
    return ";".join(modelos)


def importar_xtfs_bd(host, port, nombre_base_datos, usuario, contraseña, input_folder, esquema, java_path, usando_palmira=False, update_progress=None):
    """
    Importa todos los archivos XTF en una carpeta a la base de datos PostgreSQL usando ili2pg.
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"La carpeta {input_folder} no existe.")

    xtf_files = [f for f in os.listdir(input_folder) if f.endswith(".xtf")]

    if not xtf_files:
        raise ValueError("No se encontraron archivos XTF en la carpeta.")

    ili2pg_path = obtener_ruta_ili2pg()
    modelos_ili_path = obtener_ruta_modelos_ili(usando_palmira)

    # Obtener los modelos desde los archivos .ili
    modelos = obtener_modelos_desde_ili(modelos_ili_path)
    if not modelos:
        raise ValueError("No se encontraron modelos .ili en la carpeta especificada.")

    total_files = len(xtf_files)
    for index, xtf_file in enumerate(xtf_files):
        xtf_path = os.path.normpath(os.path.join(input_folder, xtf_file))

        cmd = [
            java_path, "-jar", ili2pg_path,
            "--import",
            "--disableValidation",
            "--dbhost", host,
            "--dbport", port,
            "--dbusr", usuario,
            "--dbpwd", contraseña,
            "--dbdatabase", nombre_base_datos,
            "--dbschema", esquema,
            "--iliMetaAttrs", "NULL",
            "--models", modelos,
            xtf_path
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # Si hay un error, lanzar una excepción con detalles del archivo que falló
            raise Exception(f"Error al importar el archivo {xtf_file}: {stderr.decode('utf-8')}")

        if update_progress:
            progress = int(((index + 1) / total_files) * 100)
            update_progress(progress, xtf_file)

    QMessageBox.information(None, "Importación completada", "La importación de los archivos XTF a la base de datos se completó con éxito.")


class ImportarXtfABdDialog(QDialog):
    def __init__(self, iface, conexion, esquema_menu, password):
        super().__init__()
        self.iface = iface
        self.conexion = conexion
        self.esquema_menu = esquema_menu
        self.password = password
        self.setWindowTitle("Importador de XTF a BD")
        self.setMinimumSize(400, 300)

        # Verificar la conexión antes de crear la ventana
        if not validar_conexion_bd(self.conexion):
            return  # Salir si la conexión no es válida

        # Verificar que se haya seleccionado un esquema
        self.esquema_seleccionado = self.esquema_menu.currentText()
        if not self.esquema_seleccionado:
            QMessageBox.critical(self, "Error", "Debe seleccionar un esquema antes de continuar.")
            return  # Salir si no se seleccionó un esquema

        # Java Path
        self.java_path = os.path.join(os.path.dirname(__file__), "java-portable", "bin", "java.exe")

        # Layout principal
        layout = QVBoxLayout()

        # Etiqueta con el esquema seleccionado
        layout.addWidget(QLabel(f"Esquema seleccionado: {self.esquema_seleccionado}"))

        # Selección de carpeta de entrada
        self.input_folder = QLineEdit(self)
        button_input_folder = QPushButton("Seleccionar carpeta de entrada (XTF)", self)
        button_input_folder.clicked.connect(self.seleccionar_carpeta_entrada)

        # Barra de progreso
        self.progress_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Checkbox para seleccionar si se usa la carpeta "modelos2" o "modelos"
        self.checkbox_palmira = QCheckBox("Usar modelos de Palmira (modelos2)")

        # Botón para iniciar la importación
        button_importar = QPushButton("Iniciar Importación", self)
        button_importar.clicked.connect(self.iniciar_importacion)

        # Layout horizontal para checkbox y botón
        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox_palmira)

        # Añadir widgets al layout
        layout.addWidget(QLabel("Carpeta de entrada (XTF):"))
        layout.addWidget(self.input_folder)
        layout.addWidget(button_input_folder)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        # Añadir el layout horizontal (checkbox + botón) al layout principal
        hbox.addWidget(button_importar)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def seleccionar_carpeta_entrada(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccione la carpeta de entrada (XTF)")
        if folder:
            self.input_folder.setText(folder)

    def iniciar_importacion(self):
        input_folder = self.input_folder.text()
        usando_palmira = self.checkbox_palmira.isChecked()

        if not input_folder:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione una carpeta de entrada.")
            return

        dsn_parameters = self.conexion.get_dsn_parameters()
        host = dsn_parameters.get('host')
        port = dsn_parameters.get('port')
        nombre_base_datos = dsn_parameters.get('dbname')
        usuario = dsn_parameters.get('user')
        contraseña = self.password

        try:
            importar_xtfs_bd(
                host, port, nombre_base_datos, usuario, contraseña,
                input_folder, self.esquema_seleccionado, self.java_path,
                usando_palmira, self.update_progress
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_progress(self, progress, current_file):
        self.progress_label.setText(f"Progreso: {progress}% - Procesando: {current_file}")
        self.progress_bar.setValue(progress)


def abrir_ventana_importacionbd(iface, conexion, esquema_menu, entry_password):
    # Verificar que exista una conexión válida antes de abrir la ventana
    if not validar_conexion_bd(conexion):
        return  # Si no hay conexión, no hacer nada

    dialog = ImportarXtfABdDialog(iface, conexion, esquema_menu, entry_password)
    dialog.exec_()
