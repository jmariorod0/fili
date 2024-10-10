import os
import subprocess
import psycopg2
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QCheckBox, QHBoxLayout)
from PyQt5.QtCore import Qt


def validar_conexion_bd(conexion):
    """
    Valida que la conexión a la base de datos esté establecida antes de proceder con la exportación.
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


def verificar_postgis(conexion):
    """
    Verifica si PostGIS está instalado en la base de datos conectada.
    """
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT PostGIS_Full_Version();")
        postgis_version = cursor.fetchone()
        if postgis_version:
            return True
    except psycopg2.Error as e:
        print(f"Error al verificar PostGIS: {e}")
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
    Obtiene la ruta a la carpeta que contiene los modelos .ili dentro de la estructura del plugin.
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


def exportar_bd_a_xtf(host, port, nombre_base_datos, usuario, contraseña, output_file, esquema, modelos, conexion, java_path, update_progress=None):
    """
    Exporta la base de datos PostgreSQL a un archivo XTF usando ili2pg.
    """
    if not verificar_postgis(conexion):
        raise Exception("PostGIS no está disponible en la base de datos conectada.")

    ili2pg_path = obtener_ruta_ili2pg()

    cmd = [
        java_path, "-jar", ili2pg_path,
        "--export",
        "--disableValidation",
        "--disableRounding",
        "--dbhost", host,
        "--dbport", port,
        "--dbusr", usuario,
        "--dbpwd", contraseña,
        "--dbdatabase", nombre_base_datos,
        "--dbschema", esquema,
        "--models", modelos,
        output_file
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    try:
        stderr = stderr.decode('utf-8')
    except UnicodeDecodeError:
        stderr = stderr.decode('ISO-8859-1')

    if process.returncode != 0:
        raise Exception(f"Error al exportar la base de datos: {stderr}")

    if update_progress:
        update_progress(100, output_file)


    # Crear el cuadro de diálogo
    dialog = QDialog()
    dialog.setWindowTitle("Exportación completada")

    # Obtener la carpeta de salida
    carpeta_output = os.path.dirname(output_file)

    # Crear el layout principal
    layout = QVBoxLayout()

    # Texto del mensaje
    label = QLabel(f"La exportación de la base de datos a {output_file} se completó con éxito.<br>"
                   f"<a href='file:///{carpeta_output}'>Abrir carpeta</a>")
    label.setTextFormat(Qt.RichText)
    label.setTextInteractionFlags(Qt.TextBrowserInteraction)
    label.setOpenExternalLinks(True)

    # Botón Aceptar
    button_aceptar = QPushButton("Aceptar")
    button_aceptar.clicked.connect(dialog.accept)

    # Añadir los widgets al layout
    layout.addWidget(label)
    layout.addWidget(button_aceptar)

    dialog.setLayout(layout)

    # Mostrar el cuadro de diálogo
    dialog.exec_()
 


class ExportarBdAXtfDialog(QDialog):
    def __init__(self, iface, conexion, esquema, password):
        super().__init__()
        self.iface = iface
        self.conexion = conexion
        self.esquema = esquema
        self.password = password
        self.setWindowTitle("Exportar BD a XTF")
        self.setMinimumSize(400, 300)

        # Java Path
        self.java_path = os.path.join(os.path.dirname(__file__), "java-portable", "bin", "java.exe")

        # Layout principal
        layout = QVBoxLayout()

        # Selección de archivo de salida
        self.output_file = QLineEdit(self)
        button_output_file = QPushButton("Seleccionar archivo de salida (XTF)", self)
        button_output_file.clicked.connect(self.seleccionar_archivo_salida)

        # Barra de progreso
        self.progress_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Checkbox para seleccionar si se usa la carpeta "modelos2" o "modelos"
        self.checkbox_palmira = QCheckBox("Usar modelos de Palmira (modelos2)")

        # Mostrar el esquema que se está exportando
        esquema_label = QLabel(f"Esquema actual: {self.esquema}")

        # Botón para iniciar la exportación
        button_exportar = QPushButton("Iniciar Exportación", self)
        button_exportar.clicked.connect(self.iniciar_exportacion)

        # Layout horizontal para checkbox y botón
        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox_palmira)

        # Añadir widgets al layout
        layout.addWidget(QLabel("Archivo de salida (XTF):"))
        layout.addWidget(self.output_file)
        layout.addWidget(button_output_file)
        layout.addWidget(esquema_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        # Añadir el layout horizontal (checkbox + botón) al layout principal
        hbox.addWidget(button_exportar)
        layout.addLayout(hbox)

        self.setLayout(layout)

    def seleccionar_archivo_salida(self):
        file, _ = QFileDialog.getSaveFileName(self, "Guardar archivo XTF", "", "XTF files (*.xtf)")
        if file:
            self.output_file.setText(file)

    def iniciar_exportacion(self):
        output_file = self.output_file.text()
        usando_palmira = self.checkbox_palmira.isChecked()

        if not output_file:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un archivo de salida.")
            return

        if not validar_conexion_bd(self.conexion):
            return

        dsn_parameters = self.conexion.get_dsn_parameters()
        host = dsn_parameters.get('host')
        port = dsn_parameters.get('port')
        nombre_base_datos = dsn_parameters.get('dbname')
        usuario = dsn_parameters.get('user')
        contraseña = self.password

        try:
            modelos_ili_path = obtener_ruta_modelos_ili(usando_palmira)
            modelos = obtener_modelos_desde_ili(modelos_ili_path)
            exportar_bd_a_xtf(host, port, nombre_base_datos, usuario, contraseña, output_file, self.esquema, modelos, self.conexion, self.java_path, self.update_progress)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_progress(self, progress, current_file):
        self.progress_label.setText(f"Progreso: {progress}% - Procesando: {current_file}")
        self.progress_bar.setValue(progress)


def abrir_ventana_exportacion_bd_2(iface, conexion, esquema_var_global, entry_password):
    if not validar_conexion_bd(conexion):
        return

    # Asegurarse de obtener el texto seleccionado del QComboBox
    esquema_seleccionado = esquema_var_global.currentText()

    dialog = ExportarBdAXtfDialog(iface, conexion, esquema_seleccionado, entry_password)
    dialog.exec_()
