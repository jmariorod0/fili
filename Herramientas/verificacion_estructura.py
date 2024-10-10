import os
import pandas as pd
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QFileDialog, QMessageBox)
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from qgis.core import QgsVectorLayer
from datetime import datetime
from urllib.parse import quote
import subprocess

class verificacion_estructura(QDialog):
    def __init__(self, iface, parent=None):
        super(verificacion_estructura, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Verificar Estructura GPKG/GDB")
        self.resize(600, 400) 

        # Layout principal
        layout = QVBoxLayout()

        # Layout para seleccionar carpeta
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Carpeta:")
        self.folderLineEdit = QLineEdit()
        self.browseButton = QPushButton("Buscar")
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folderLineEdit)
        folder_layout.addWidget(self.browseButton)

        # Lista de resultados
        self.resultListWidget = QListWidget()

        # Botón para procesar
        self.processButton = QPushButton("Procesar")

        # Agregar elementos al layout principal
        layout.addLayout(folder_layout)
        layout.addWidget(self.resultListWidget)
        layout.addWidget(self.processButton)

        # Asignar layout al diálogo
        self.setLayout(layout)

        # Conectar botones a funciones
        self.browseButton.clicked.connect(self.select_folder)
        self.processButton.clicked.connect(self.verify_structures)

        # Inicializar variables
        self.folder_path = None
        self.gpkg_base = os.path.join(os.path.dirname(__file__), 'gpkg_base.gpkg')

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", "", QFileDialog.ShowDirsOnly)
        if self.folder_path:
            self.folderLineEdit.setText(self.folder_path)

    def verify_structures(self):
        if not self.folder_path:
            QMessageBox.warning(self, "Error", "Debe seleccionar una carpeta.")
            return

        if not os.path.exists(self.gpkg_base):
            QMessageBox.warning(self, "Error", "El archivo base gpkg_base.gpkg no existe.")
            return

        # Obtener lista de archivos GPKG o GDB
        files_to_check = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path) if f.endswith('.gpkg') or f.endswith('.gdb')]
        if not files_to_check:
            QMessageBox.warning(self, "Error", "No se encontraron archivos GPKG o GDB en la carpeta seleccionada.")
            return

        # Leer la estructura del archivo base
        base_structure = self.get_gpkg_structure(self.gpkg_base)

        # Comparar la estructura de cada archivo
        results = []
        dominio_results = []
        for file in files_to_check:
            structure = self.get_gpkg_structure(file)
            comparison_result = self.compare_structures(base_structure, structure)
            
            # Extraer el resultado y las diferencias para cada archivo
            for table, result, extra_columns_str, missing_columns_str in comparison_result:
                results.append((os.path.basename(file), result, extra_columns_str, missing_columns_str))
            
            # Verificar los dominios en el archivo actual
            dominio_result = self.verify_domains(file)
            dominio_results.append(dominio_result)

        # Generar archivo Excel con los resultados
        report_path = self.generate_excel_report(results, dominio_results)

        # Mostrar los resultados en la interfaz
        self.show_results(results)

        # Mostrar el mensaje de éxito con un enlace clickeable
        self.show_message_with_link(report_path)

    def get_gpkg_structure(self, file_path):
        structure = {}

        # Cargar el GPKG como una colección de capas
        layer = QgsVectorLayer(file_path, '', 'ogr')

        if not layer.isValid():
            print(f"Error al cargar el archivo: {file_path}")
            return structure

        # Iterar sobre las capas y extraer nombres de tablas y campos
        fields = layer.fields()
        structure[layer.name()] = [field.name() for field in fields]

        return structure

    def compare_structures(self, base_structure, other_structure):
        results = []
        for table, base_columns in base_structure.items():
            if table not in other_structure:
                results.append((table, "Tabla faltante", "Ninguno", "Todos los campos faltantes"))
            else:
                base_columns_set = set(base_columns)
                other_columns_set = set(other_structure[table])

                # Identificar columnas adicionales y faltantes
                extra_columns = other_columns_set - base_columns_set
                missing_columns = base_columns_set - other_columns_set

                # Convertir los conjuntos en strings para facilitar su lectura en el Excel
                extra_columns_str = ", ".join(extra_columns) if extra_columns else "Ninguno"
                missing_columns_str = ", ".join(missing_columns) if missing_columns else "Ninguno"

                # Añadir los resultados
                results.append((table, "Cumple" if not extra_columns and not missing_columns else "Difiere", extra_columns_str, missing_columns_str))

        return results





    def verify_domains(self, file):
        tipo_derecho_column = "TIPO_DERECHO"
        formal_informal_column = "FORMAL_INFORMAL"
        naturaleza_column = "NATURALEZA"

        tipo_derecho_valid_values = {"DOMINIO", "OCUPACION", "POSESION"}
        formal_informal_valid_values = {"FORMAL", "FORMAL_REMANENTE", "FORMAL_SIN_REMANENTE", "INFORMAL"}
        naturaleza_valid_values = {"PUBLICO", "PRIVADO"}

        tipo_derecho_invalid_values = []
        formal_informal_invalid_values = []
        naturaleza_invalid_values = []

        tipo_derecho_result = "OK"
        formal_informal_result = "OK"
        naturaleza_result = "OK"

        # Abrir la capa de GPKG
        layer = QgsVectorLayer(file, '', 'ogr')
        
        if not layer.isValid():
            print(f"Error al cargar la capa de dominios: {file}")
            return os.path.basename(file), "ERROR", "ERROR", "ERROR"

        # Verificar si las columnas existen
        field_names = [field.name() for field in layer.fields()]
        
        if tipo_derecho_column not in field_names:
            tipo_derecho_result = "NO EXISTE COLUMNA"
        if formal_informal_column not in field_names:
            formal_informal_result = "NO EXISTE COLUMNA"
        if naturaleza_column not in field_names:
            naturaleza_result = "NO EXISTE COLUMNA"

        # Si las columnas existen, validamos los valores
        if tipo_derecho_result != "NO EXISTE COLUMNA":
            for feature in layer.getFeatures():
                value = feature[tipo_derecho_column]
                if value not in tipo_derecho_valid_values:
                    tipo_derecho_invalid_values.append(str(value))  # Convertir el valor a cadena

        if formal_informal_result != "NO EXISTE COLUMNA":
            for feature in layer.getFeatures():
                value = feature[formal_informal_column]
                if value not in formal_informal_valid_values:
                    formal_informal_invalid_values.append(str(value))  # Convertir el valor a cadena

        if naturaleza_result != "NO EXISTE COLUMNA":
            for feature in layer.getFeatures():
                value = feature[naturaleza_column]
                if value not in naturaleza_valid_values:
                    naturaleza_invalid_values.append(str(value))  # Convertir el valor a cadena

        # Preparar los resultados finales
        if tipo_derecho_invalid_values:
            tipo_derecho_result = f"NO CUMPLE ({', '.join(set(tipo_derecho_invalid_values))})"

        if formal_informal_invalid_values:
            formal_informal_result = f"NO CUMPLE ({', '.join(set(formal_informal_invalid_values))})"

        if naturaleza_invalid_values:
            naturaleza_result = f"NO CUMPLE ({', '.join(set(naturaleza_invalid_values))})"

        return os.path.basename(file), tipo_derecho_result, formal_informal_result, naturaleza_result







    def generate_excel_report(self, results, dominio_results):
        import xlsxwriter

        # Crear un archivo Excel con el nombre VERIFICACION_ESTRUCTURA_<timestamp>.xlsx
        timestamp = datetime.now().strftime('%d_%m_%Y_%S')
        report_name = f"VERIFICACION_ESTRUCTURA_{timestamp}.xlsx"
        report_path = os.path.join(self.folder_path, report_name)

        # Crear el libro de trabajo de Excel usando xlsxwriter
        workbook = xlsxwriter.Workbook(report_path)
        worksheet = workbook.add_worksheet("Estructura")

        # Formato para colorear "Cumple" en verde claro
        green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

        # Escribir los encabezados
        worksheet.write(0, 0, "Archivo")
        worksheet.write(0, 1, "Resultado")
        worksheet.write(0, 2, "Campos adicionales")
        worksheet.write(0, 3, "Campos faltantes")

        # Escribir los datos y agregar hipervínculos
        for row_num, (file, result, extra_columns, missing_columns) in enumerate(results, start=1):
            file_path = os.path.join(self.folder_path, file)
            file_path_normalized = os.path.normpath(file_path)  # Convertir la ruta al formato correcto para el sistema operativo
            link = f'file:///{quote(file_path_normalized)}'  # Codificar el link correctamente

            # Escribir el archivo con hipervínculo
            worksheet.write_url(row_num, 0, link, string=file)

            # Colorear en verde si el resultado es "Cumple"
            if result == "Cumple":
                worksheet.write(row_num, 1, result, green_format)
            else:
                worksheet.write(row_num, 1, result)

            # Escribir los otros datos
            worksheet.write(row_num, 2, extra_columns)
            worksheet.write(row_num, 3, missing_columns)

        # Crear una nueva hoja para la verificación de dominios
        dominio_sheet = workbook.add_worksheet("VERIFICACION_DOMINIOS")
        dominio_sheet.write(0, 0, "Archivo")
        dominio_sheet.write(0, 1, "Resultado TIPO_DERECHO")
        dominio_sheet.write(0, 2, "Resultado FORMAL_INFORMAL")
        dominio_sheet.write(0, 3, "Resultado NATURALEZA")

        # Escribir los resultados de los dominios en la segunda hoja
        for row_num, (file, tipo_derecho_result, formal_informal_result, naturaleza_result) in enumerate(dominio_results, start=1):
            file_path = os.path.join(self.folder_path, file)
            file_path_normalized = os.path.normpath(file_path)
            link = f'file:///{quote(file_path_normalized)}'

            # Escribir el archivo con hipervínculo
            dominio_sheet.write_url(row_num, 0, link, string=file)

            # Escribir los resultados de cada campo validado
            dominio_sheet.write(row_num, 1, tipo_derecho_result)
            dominio_sheet.write(row_num, 2, formal_informal_result)
            dominio_sheet.write(row_num, 3, naturaleza_result)

        # Cerrar el libro de trabajo
        workbook.close()

        return report_path










    def show_message_with_link(self, report_path):
        # Crear un cuadro de diálogo personalizado para hacer la ruta clickeable
        msg = QMessageBox(self)
        msg.setWindowTitle("Éxito")
        msg.setText(f"Reporte generado:")
        
        # Crear una etiqueta con un enlace clickeable
        link_label = QLabel(f'<a href="file:///{report_path}">{report_path}</a>', self)
        link_label.setOpenExternalLinks(True)
        link_label.setCursor(QCursor(Qt.PointingHandCursor))

        msg.layout().addWidget(link_label, 1, 1)  # Añadir la etiqueta con el link al mensaje

        # Establecer botón de "Aceptar"
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def open_file(self, file_path):
        # Intentar abrir el archivo Excel
        try:
            if os.name == 'nt':  # Para Windows
                os.startfile(file_path)
            else:  # Para otros sistemas operativos
                subprocess.call(['open', file_path])
        except Exception as e:
            print(f"Error al intentar abrir el archivo: {e}")

    def show_results(self, results):
        self.resultListWidget.clear()
        for result in results:
            self.resultListWidget.addItem(f"{result[0]} - {result[1]}")
