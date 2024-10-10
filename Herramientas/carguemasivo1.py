import os
import shutil
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFileDialog, QMessageBox, QDialog, QScrollArea, QWidget,QApplication
)
from PyQt5.QtCore import Qt

# Función para copiar archivos masivamente con eliminación de archivos similares y mensajes personalizados
class cargue_masivo(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Cargue Masivo de Archivos a Expedientes")
        self.setMinimumSize(700, 500)

        # Layout principal
        layout = QVBoxLayout()

        # Ruta principal
        ruta_layout = QHBoxLayout()
        ruta_label = QLabel("Ruta principal:")
        self.ruta_entry = QLineEdit()
        boton_ruta = QPushButton("Seleccionar ruta")
        boton_ruta.clicked.connect(self.seleccionar_ruta_principal)
        ruta_layout.addWidget(ruta_label)
        ruta_layout.addWidget(self.ruta_entry)
        ruta_layout.addWidget(boton_ruta)
        layout.addLayout(ruta_layout)

        # Carpetas separadas por comas
        carpetas_layout = QHBoxLayout()
        carpetas_label = QLabel("Carpetas (separadas por comas):")
        self.carpetas_entry = QLineEdit()
        carpetas_layout.addWidget(carpetas_label)
        carpetas_layout.addWidget(self.carpetas_entry)
        layout.addLayout(carpetas_layout)

        # Archivo a copiar
        archivo_layout = QHBoxLayout()
        archivo_label = QLabel("Ruta completa del archivo a copiar:")
        self.archivo_ruta_entry = QLineEdit()
        boton_archivo = QPushButton("Seleccionar archivo")
        boton_archivo.clicked.connect(self.seleccionar_archivo_a_copiar)
        archivo_layout.addWidget(archivo_label)
        archivo_layout.addWidget(self.archivo_ruta_entry)
        archivo_layout.addWidget(boton_archivo)
        layout.addLayout(archivo_layout)

        # Botón para ejecutar la copia
        boton_ejecutar = QPushButton("Ejecutar")
        boton_ejecutar.clicked.connect(self.copiar_archivos_masivamente)
        layout.addWidget(boton_ejecutar)

        # Barra de progreso
        self.progreso = QProgressBar()
        layout.addWidget(self.progreso)

        # Área de texto para resultados
        self.resultado_text = QTextEdit()
        self.resultado_text.setReadOnly(True)
        layout.addWidget(self.resultado_text)

        # Aplicar el layout al diálogo
        self.setLayout(layout)

    # Función para seleccionar la ruta principal
    def seleccionar_ruta_principal(self):
        ruta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta principal")
        if ruta:
            self.ruta_entry.setText(ruta)

    # Función para seleccionar el archivo a copiar
    def seleccionar_archivo_a_copiar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
        if archivo:
            self.archivo_ruta_entry.setText(archivo)

    # Función para ejecutar el copiado masivo
    def copiar_archivos_masivamente(self):
        ruta_principal = self.ruta_entry.text()
        carpetas = self.carpetas_entry.text().split(',')
        archivo_a_copiar = self.archivo_ruta_entry.text()
        nombre_archivo = os.path.basename(archivo_a_copiar).strip()

        if not ruta_principal or not carpetas or not archivo_a_copiar:
            QMessageBox.critical(self, "Error", "Por favor, complete todos los campos.")
            return

        # Verificar que el archivo a copiar exista
        if not os.path.exists(archivo_a_copiar):
            QMessageBox.critical(self, "Error", f"El archivo especificado no existe: {archivo_a_copiar}")
            return

        total_carpetas = len(carpetas)
        self.progreso.setValue(0)

        for index, carpeta in enumerate(carpetas):
            carpeta = carpeta.strip()
            carpeta_path = os.path.join(ruta_principal, carpeta)
            subcarpeta_path = os.path.join(carpeta_path, "02_doc_sop")

            if not os.path.exists(carpeta_path):
                self.resultado_text.append(f"Error: No se encontró la carpeta {carpeta}")
                continue

            if not os.path.exists(subcarpeta_path):
                self.resultado_text.append(f"Error: No se encontró la subcarpeta '02_doc_sop' en {carpeta}")
                continue

            # Buscar archivos similares
            archivos_similares = []
            base_nombre_archivo = os.path.splitext(nombre_archivo)[0]
            for archivo_existente in os.listdir(subcarpeta_path):
                if archivo_existente.startswith(base_nombre_archivo):
                    archivos_similares.append(archivo_existente)

            # Eliminar o reemplazar archivos similares
            if len(archivos_similares) > 1:
                respuesta_eliminacion = QMessageBox.question(
                    self, "Archivos similares encontrados",
                    f"Se encontraron varios archivos con la misma base en la carpeta '{subcarpeta_path}'. "
                    "¿Deseas eliminarlos y dejar solo el archivo que estás cargando?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta_eliminacion == QMessageBox.Yes:
                    for archivo_existente in archivos_similares:
                        os.remove(os.path.join(subcarpeta_path, archivo_existente))
                        self.resultado_text.append(f"Archivo '{archivo_existente}' eliminado de {subcarpeta_path}")

            elif len(archivos_similares) == 1:
                respuesta_reemplazo = QMessageBox.question(
                    self, "Archivo encontrado",
                    f"Se encontró 1 archivo similar en la carpeta '{subcarpeta_path}'. "
                    "¿Deseas reemplazarlo?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta_reemplazo == QMessageBox.Yes:
                    os.remove(os.path.join(subcarpeta_path, archivos_similares[0]))
                    self.resultado_text.append(f"Archivo '{archivos_similares[0]}' eliminado de {subcarpeta_path}")

            archivo_destino = os.path.join(subcarpeta_path, nombre_archivo)

            try:
                shutil.copy2(archivo_a_copiar, archivo_destino)
                self.resultado_text.append(f"Archivo copiado de {archivo_a_copiar} a {archivo_destino}")
            except Exception as e:
                self.resultado_text.append(f"Error al copiar el archivo: {str(e)}")
                QMessageBox.critical(self, "Error", f"Hubo un error al copiar el archivo: {str(e)}")

            # Actualizar progreso
            self.progreso.setValue(int(((index + 1) / total_carpetas) * 100))
            QApplication.processEvents()

        QMessageBox.information(self, "Proceso completado", "Se completó el proceso de copia masiva de archivos.")
