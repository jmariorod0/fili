import os
import subprocess
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QProgressBar, QFileDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices


def obtener_ruta_ili2gpkg():
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    ili2gpkg_path = os.path.join(plugin_dir, "ili2", "ili2gpkg-5.1.0.jar")
    
    if not os.path.exists(ili2gpkg_path):
        raise FileNotFoundError(f"No se encontró ili2gpkg en la ruta esperada: {ili2gpkg_path}")

    return ili2gpkg_path


def obtener_ruta_modelos_ili(usando_palmira=False):
    plugin_dir = os.path.dirname(os.path.abspath(__file__))

    if usando_palmira:
        modelos_ili_path = os.path.join(plugin_dir, "modelos2")
    else:
        modelos_ili_path = os.path.join(plugin_dir, "modelos")

    if not os.path.exists(modelos_ili_path):
        raise FileNotFoundError(f"No se encontró la carpeta de modelos .ili en la ruta esperada: {modelos_ili_path}")

    return modelos_ili_path


def obtener_modelos_desde_ili(modelos_ili_path):
    modelos = [os.path.splitext(f)[0] for f in os.listdir(modelos_ili_path) if f.endswith(".ili")]
    return ";".join(modelos)


def obtener_ruta_java():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    java_path = os.path.join(current_dir, 'java-portable', 'bin', 'java.exe')

    if not os.path.exists(java_path):
        raise FileNotFoundError(f"No se encontró 'java.exe' en la ruta: {java_path}")

    return java_path


def exportar_ili(input_folder, output_folder, java_path, usando_palmira, update_progress=None):
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"La carpeta {input_folder} no existe.")

    gpkg_files = [f for f in os.listdir(input_folder) if f.endswith(".gpkg")]

    if not gpkg_files:
        raise ValueError("No se encontraron archivos GPKG en la carpeta.")

    ili2gpkg_path = obtener_ruta_ili2gpkg()
    modelos_ili_path = obtener_ruta_modelos_ili(usando_palmira)
    modelos = obtener_modelos_desde_ili(modelos_ili_path)

    if not modelos:
        raise ValueError("No se encontraron modelos .ili en la carpeta especificada.")

    total_files = len(gpkg_files)
    for index, gpkg_file in enumerate(gpkg_files):
        gpkg_path = os.path.normpath(os.path.join(input_folder, gpkg_file))
        xtf_path = os.path.normpath(os.path.join(output_folder, os.path.splitext(gpkg_file)[0] + ".xtf"))

        cmd = [
            java_path, "-jar", ili2gpkg_path,
            "--dbfile", gpkg_path,
            "--export",
            "--disableValidation",
            "--models", modelos,
            "--iliMetaAttrs", "NULL",
            xtf_path
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"Error al exportar {gpkg_file}: {stderr.decode('utf-8')}")

        if update_progress:
            progress = int(((index + 1) / total_files) * 100)
            update_progress(progress, gpkg_file)

    mostrar_mensaje_exito(output_folder)


def mostrar_mensaje_exito(output_folder):
    """
    Muestra un diálogo personalizado con un hipervínculo que abre la carpeta donde se guardaron los archivos exportados.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Exportación completada")

    layout = QVBoxLayout()

    label = QLabel(f"Exportación completada con éxito. <a href='file:///{output_folder}'>Abrir carpeta</a>")
    label.setTextFormat(Qt.RichText)  # Permitir que el texto sea interpretado como HTML
    label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # Habilitar clics en los hipervínculos
    label.linkActivated.connect(lambda: QDesktopServices.openUrl(QUrl(f"file:///{output_folder}")))

    ok_button = QPushButton("OK")
    ok_button.clicked.connect(dialog.accept)

    layout.addWidget(label)
    layout.addWidget(ok_button)

    dialog.setLayout(layout)
    dialog.exec_()


class ExportarGpkgAxtfDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Exportador de GPKG a XTF")
        self.setMinimumSize(400, 300)

        self.java_path = obtener_ruta_java()

        layout = QVBoxLayout()

        self.input_folder = QLineEdit(self)
        button_input_folder = QPushButton("Seleccionar carpeta de entrada (GPKG)", self)
        button_input_folder.clicked.connect(self.seleccionar_carpeta_entrada)

        self.output_folder = QLineEdit(self)
        button_output_folder = QPushButton("Seleccionar carpeta de salida (XTF)", self)
        button_output_folder.clicked.connect(self.seleccionar_carpeta_salida)

        self.progress_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.checkbox_palmira = QCheckBox("Usar modelos de Palmira (modelos2)")

        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox_palmira)

        button_exportar = QPushButton("Iniciar Exportación", self)
        button_exportar.clicked.connect(self.iniciar_exportacion)
        hbox.addWidget(button_exportar)

        layout.addWidget(QLabel("Carpeta de entrada (GPKG):"))
        layout.addWidget(self.input_folder)
        layout.addWidget(button_input_folder)

        layout.addWidget(QLabel("Carpeta de salida (XTF):"))
        layout.addWidget(self.output_folder)
        layout.addWidget(button_output_folder)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        layout.addLayout(hbox)

        self.setLayout(layout)

    def seleccionar_carpeta_entrada(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccione la carpeta de entrada (GPKG)")
        if folder:
            self.input_folder.setText(folder)

    def seleccionar_carpeta_salida(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccione la carpeta de salida (XTF)")
        if folder:
            self.output_folder.setText(folder)

    def iniciar_exportacion(self):
        input_folder = self.input_folder.text()
        output_folder = self.output_folder.text()
        usando_palmira = self.checkbox_palmira.isChecked()

        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione ambas carpetas.")
            return

        try:
            exportar_ili(input_folder, output_folder, self.java_path, usando_palmira, self.update_progress)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_progress(self, progress, current_file):
        self.progress_label.setText(f"Progreso: {progress}% - Exportando: {current_file}")
        self.progress_bar.setValue(progress)


def abrir_ventana_exportacion(iface):
    dialog = ExportarGpkgAxtfDialog(iface)
    dialog.exec_()
