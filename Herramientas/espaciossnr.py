from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QDialog, QTextEdit, QGridLayout, QLineEdit
import pandas as pd
import os

# Clase para emitir señales entre el hilo de trabajo y la interfaz gráfica
class WorkerSignals(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

# Clase que ejecuta el procesamiento en un hilo separado
class ExcelProcessor(QThread):
    def __init__(self, input_path, output_folder):
        super().__init__()
        self.input_path = input_path
        self.output_folder = output_folder
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.normalize_excel()
        except Exception as e:
            self.signals.error.emit(f"Ocurrió un error: {str(e)}")

    def normalize_excel(self):
        self.signals.progress.emit("Iniciando proceso de normalización...\n")
        
        # Leer el archivo Excel
        df = pd.read_excel(self.input_path, dtype=str, na_filter=False)
        self.signals.progress.emit("Archivo cargado exitosamente.\n")

        # Eliminar filas que contienen "MATRICULA" en la primera columna (excepto la primera fila)
        df = df[~((df.index != 0) & (df.iloc[:, 0].str.contains('MATRICULA')))]

        # Eliminar filas que contienen solamente guiones en todas las columnas
        def is_separator_row(row):
            return all(isinstance(x, str) and set(x.strip()) == {'-'} for x in row)

        df = df[~df.apply(is_separator_row, axis=1)]

        processed_rows = []
        last_valid_row = None

        for index, row in df.iterrows():
            if row[0]:
                last_valid_row = row.copy()
                processed_rows.append(last_valid_row)
            else:
                if last_valid_row is not None:
                    for col in df.columns:
                        if row[col]:
                            value_to_add = str(row[col]).strip() if isinstance(row[col], str) else str(row[col])
                            self.signals.progress.emit(f"Fila {index + 1}: Se agregó '{value_to_add}' a la columna '{col}' para el registro con valor '{last_valid_row[0]}' en la primera columna.\n")
                            last_valid_row[col] = str(last_valid_row[col]) + " " + value_to_add

            if index % 100 == 0:
                self.signals.progress.emit(f"Procesadas {index + 1} filas...\n")

        processed_df = pd.DataFrame(processed_rows)

        for col in ["COMPLEMENTO", "LINDERO"]:
            if col in processed_df.columns:
                processed_df[col] = processed_df[col].apply(self.reemplazar_caracteres)

        file_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_path = os.path.join(self.output_folder, f"{file_name}_depurado.xlsx")
        processed_df.to_excel(output_path, index=False, engine='openpyxl')

        self.signals.finished.emit(output_path)

    @staticmethod
    def reemplazar_caracteres(texto):
        caracteres_a_reemplazar = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
            ".": ""
        }

        texto = str(texto)  # Convertir a texto cualquier valor numérico
        for viejo, nuevo in caracteres_a_reemplazar.items():
            texto = texto.replace(viejo, nuevo)
        return texto

# Clase principal que maneja la interfaz gráfica (similar a tu diseño en tkinter)

class EspaciosSNRDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Depuración de espaciado SNR")
        self.setMinimumSize(600, 400)

        # Crear layout en formato Grid para replicar la interfaz en tkinter
        layout = QGridLayout(self)
        
        # Etiquetas y campos de entrada
        self.entry_input = QLineEdit(self)
        self.entry_output = QLineEdit(self)
        
        layout.addWidget(QLabel("Archivo de entrada:"), 0, 0)
        layout.addWidget(self.entry_input, 0, 1)
        btn_seleccionar_archivo = QPushButton("Seleccionar archivo", self)
        btn_seleccionar_archivo.clicked.connect(self.select_file)
        layout.addWidget(btn_seleccionar_archivo, 0, 2)

        layout.addWidget(QLabel("Carpeta de salida:"), 1, 0)
        layout.addWidget(self.entry_output, 1, 1)
        btn_seleccionar_carpeta = QPushButton("Seleccionar carpeta", self)
        btn_seleccionar_carpeta.clicked.connect(self.select_folder)
        layout.addWidget(btn_seleccionar_carpeta, 1, 2)

        # Botón para procesar
        btn_procesar = QPushButton("Procesar", self)
        btn_procesar.clicked.connect(self.start_processing)
        layout.addWidget(btn_procesar, 2, 0, 1, 3)

        # Cuadro de texto para el log de proceso
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text, 3, 0, 1, 3)

        # Atributos para almacenar las rutas seleccionadas
        self.input_path = ""
        self.output_folder = ""

    def select_file(self):
        # Abrir cuadro de diálogo para seleccionar archivo de entrada
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo Excel", "", "Excel files (*.xlsx *.xls)")
        if file_path:
            self.input_path = file_path
            self.entry_input.setText(file_path)
            self.log_text.append(f"Archivo de entrada seleccionado: {self.input_path}\n")

    def select_folder(self):
        # Abrir cuadro de diálogo para seleccionar carpeta de salida
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if folder_path:
            self.output_folder = folder_path
            self.entry_output.setText(folder_path)
            self.log_text.append(f"Carpeta de salida seleccionada: {self.output_folder}\n")

    def start_processing(self):
        if not self.input_path or not self.output_folder:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un archivo y una carpeta de salida.")
            return

        # Iniciar el proceso en un hilo separado
        self.worker = ExcelProcessor(self.input_path, self.output_folder)
        self.worker.signals.progress.connect(self.update_log)
        self.worker.signals.finished.connect(self.processing_finished)
        self.worker.signals.error.connect(self.show_error)
        self.worker.start()

    def update_log(self, message):
        # Actualizar el log en la interfaz gráfica
        self.log_text.append(message)



    def processing_finished(self, output_path):
        # Mostrar el mensaje de finalización y permitir abrir el archivo
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Proceso Completado")

        # Crear el enlace para el archivo procesado
        file_link = f"<a href='file:///{output_path}'>{output_path}</a>"
        
        # Añadir el texto con el enlace directamente en el mensaje
        msg_box.setText(f"Archivo procesado correctamente: {file_link}")
        
        # Asegurar que se permita la interacción con enlaces
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.exec_()

    def show_error(self, error_message):
        # Mostrar el mensaje de error si ocurre algún problema
        QMessageBox.critical(self, "Error", error_message)