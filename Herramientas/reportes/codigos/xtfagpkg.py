import os
import subprocess
import shutil  # Asegurarse de importar shutil
import webbrowser
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt


def obtener_ruta_ili2gpkg():
    """
    Obtiene la ruta al archivo ili2gpkg-5.1.0.jar dentro de la estructura del plugin.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta principal del plugin
    ili2gpkg_path = os.path.join(plugin_dir, "ili2", "ili2gpkg-5.1.0.jar")
    
    if not os.path.exists(ili2gpkg_path):
        raise FileNotFoundError(f"No se encontró ili2gpkg en la ruta esperada: {ili2gpkg_path}")

    return ili2gpkg_path


def obtener_ruta_modelos_ili(usando_palmira=False):
    """
    Obtiene la ruta a la carpeta que contiene los modelos .ili dentro de la estructura del proyecto.
    Si usando_palmira es True, usa la carpeta 'modelos2'. De lo contrario, usa 'modelos'.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta principal del plugin

    if usando_palmira:
        modelos_ili_path = os.path.join(plugin_dir, "modelos2")
    else:
        modelos_ili_path = os.path.join(plugin_dir, "modelos")

    if not os.path.exists(modelos_ili_path):
        raise FileNotFoundError(f"No se encontró la carpeta de modelos .ili en la ruta esperada: {modelos_ili_path}")

    return modelos_ili_path


def copiar_gpkg_estructurado(output_gpkg):
    """
    Copia el archivo GPKG estructurado a la ruta de salida especificada por el usuario.
    """
    plugin_dir = os.path.dirname(os.path.abspath(__file__))  # Carpeta principal del plugin
    gpkg_original = os.path.join(plugin_dir, "ili2", "Captura_Campo_ANT_LADM.gpkg")
    
    if not os.path.exists(gpkg_original):
        raise FileNotFoundError(f"El archivo GPKG no se encuentra en '{gpkg_original}'.")

    # Copiar el archivo GPKG estructurado a la ruta de salida
    shutil.copy(gpkg_original, output_gpkg)


def obtener_modelos_desde_ili(modelos_ili_path):
    """
    Obtiene la lista de modelos a partir de los archivos .ili en la carpeta especificada.
    """
    modelos = [os.path.splitext(f)[0] for f in os.listdir(modelos_ili_path) if f.endswith(".ili")]
    return ";".join(modelos)


def importar_xtfs(input_folder, output_gpkg, java_path, usando_palmira=False, update_progress=None):
    """
    Importa todos los archivos XTF en una carpeta a un archivo GPKG usando ili2gpkg.
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"La carpeta {input_folder} no existe.")

    xtf_files = [f for f in os.listdir(input_folder) if f.endswith(".xtf")]

    if not xtf_files:
        raise ValueError("No se encontraron archivos XTF en la carpeta.")

    ili2gpkg_path = obtener_ruta_ili2gpkg()
    modelos_ili_path = obtener_ruta_modelos_ili(usando_palmira)

    # Copiar el GPKG estructurado al lugar de salida
    copiar_gpkg_estructurado(output_gpkg)

    # Obtener los modelos desde los archivos .ili
    modelos = obtener_modelos_desde_ili(modelos_ili_path)
    if not modelos:
        raise ValueError("No se encontraron modelos .ili en la carpeta especificada.")

    total_files = len(xtf_files)
    for index, xtf_file in enumerate(xtf_files):
        xtf_path = os.path.normpath(os.path.join(input_folder, xtf_file))

        cmd = [
            java_path, "-jar", ili2gpkg_path,
            "--import",
            "--dbfile", output_gpkg,
            "--disableValidation",
            "--disableRounding",
            "--models", modelos,
            xtf_path
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"Error al importar {xtf_file}: {stderr.decode('utf-8')}")

        if update_progress:
            progress = int(((index + 1) / total_files) * 100)
            update_progress(progress, xtf_file)

    mostrar_mensaje_exito(output_gpkg)


def obtener_ruta_java():
    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir la ruta esperada para java.exe dentro de la carpeta "JM_TOOLS/Herramientas/java-portable/bin/"
    java_path = os.path.join(current_dir, 'java-portable', 'bin', 'java.exe')
    
    # Verificar si la ruta existe
    if os.path.exists(java_path):
        return java_path
    else:
        raise FileNotFoundError(f"No se encontró 'java.exe' en la ruta: {java_path}")


def mostrar_mensaje_exito(output_gpkg):
    """
    Muestra un mensaje de éxito con un hipervínculo para abrir la carpeta donde se guardó el archivo GPKG.
    """
    carpeta_salida = os.path.dirname(output_gpkg)

    # Crear un diálogo personalizado
    dialog = QDialog()
    dialog.setWindowTitle("Importación completa")

    # Crear el layout principal
    layout = QVBoxLayout()

    # Texto del mensaje
    label = QLabel(f"La importación de los archivos XTF al GPKG se completó con éxito.<br>"
                   f"<a href='file:///{carpeta_salida}'>Abrir carpeta</a>")
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


class ImportarXtfsDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Importador de XTF a GPKG")
        self.setMinimumSize(400, 300)

        self.java_path = obtener_ruta_java()

        # Layout principal
        layout = QVBoxLayout()

        # Selección de carpeta de entrada (XTF)
        self.input_folder = QLineEdit(self)
        button_input_folder = QPushButton("Seleccionar carpeta de entrada (XTF)", self)
        button_input_folder.clicked.connect(self.seleccionar_carpeta_entrada)

        # Selección de archivo GPKG de salida
        self.output_gpkg = QLineEdit(self)
        button_output_gpkg = QPushButton("Seleccionar archivo de salida (GPKG)", self)
        button_output_gpkg.clicked.connect(self.seleccionar_archivo_salida)

        # Checkbox para seleccionar si se usa la carpeta "modelos2" o "modelos"
        self.checkbox_palmira = QCheckBox("Usar modelos de Palmira (modelos2)")

        # Layout horizontal para checkbox y botón de importación
        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox_palmira)

        # Botón para iniciar importación
        button_importar = QPushButton("Iniciar Importación", self)
        button_importar.clicked.connect(self.iniciar_importacion)
        hbox.addWidget(button_importar)

        # Barra de progreso
        self.progress_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Añadir widgets al layout principal
        layout.addWidget(QLabel("Carpeta de entrada (XTF):"))
        layout.addWidget(self.input_folder)
        layout.addWidget(button_input_folder)

        layout.addWidget(QLabel("Archivo de salida (GPKG):"))
        layout.addWidget(self.output_gpkg)
        layout.addWidget(button_output_gpkg)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        # Añadir el layout horizontal (checkbox + botón) al layout principal
        layout.addLayout(hbox)

        self.setLayout(layout)

    def seleccionar_carpeta_entrada(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccione la carpeta de entrada (XTF)")
        if folder:
            self.input_folder.setText(folder)

    def seleccionar_archivo_salida(self):
        file, _ = QFileDialog.getSaveFileName(self, "Seleccione el archivo de salida (GPKG)", "", "GeoPackage (*.gpkg)")
        if file:
            self.output_gpkg.setText(file)

    def iniciar_importacion(self):
        input_folder = self.input_folder.text()
        output_gpkg = self.output_gpkg.text()
        usando_palmira = self.checkbox_palmira.isChecked()

        if not input_folder or not output_gpkg:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione la carpeta XTF y el archivo de salida GPKG.")
            return

        try:
            importar_xtfs(input_folder, output_gpkg, self.java_path, usando_palmira, self.update_progress)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_progress(self, progress, current_file):
        self.progress_label.setText(f"Progreso: {progress}% - Procesando: {current_file}")
        self.progress_bar.setValue(progress)


def abrir_ventana_importacion(iface):
    dialog = ImportarXtfsDialog(iface)
    dialog.exec_()
