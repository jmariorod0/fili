from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QTextEdit, QDialog, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
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
            self.process_excel()
        except Exception as e:
            self.signals.error.emit(f"Ocurrió un error: {str(e)}")

    def process_excel(self):
        self.signals.progress.emit("Iniciando procesamiento del archivo...\n")

        # Leer el archivo Excel
        df = pd.read_excel(self.input_path, dtype=str, na_filter=False)
        self.signals.progress.emit("Archivo cargado exitosamente.\n")

        # Crear la columna DERIVADO_CALCULADO
        df['DERIVADO_CALCULADO'] = df.groupby('MATRICULA')['MAT_SEGREGADA'].transform(lambda x: ';'.join(x))

        # Crear la columna MATRIZ_CALCULADO
        df['MATRIZ_CALCULADO'] = df.groupby('MAT_SEGREGADA')['MATRICULA'].transform(lambda x: ';'.join(x))

        self.signals.progress.emit("Cálculos completados.\n")

        # Obtener el nombre del archivo de entrada sin la extensión
        file_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_path = os.path.join(self.output_folder, f"{file_name}_calculado.xlsx")

        # Guardar el DataFrame procesado en un nuevo archivo Excel
        df.to_excel(output_path, index=False, engine='openpyxl')

        self.signals.finished.emit(output_path)

# Clase principal que maneja la interfaz gráfica
class calculo_derivado(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cálculo de FMI Matriz/Segregado")
        self.setGeometry(100, 100, 600, 400)

        # Crear el layout principal
        self.layout = QVBoxLayout(self)

        # Layout para archivo de entrada
        layout_entrada = QHBoxLayout()
        label_entrada = QLabel("Archivo de entrada:")
        self.entry_input = QLineEdit()
        btn_seleccionar_archivo = QPushButton("Seleccionar archivo")
        btn_seleccionar_archivo.clicked.connect(self.select_file)
        layout_entrada.addWidget(label_entrada)
        layout_entrada.addWidget(self.entry_input)
        layout_entrada.addWidget(btn_seleccionar_archivo)
        self.layout.addLayout(layout_entrada)

        # Layout para carpeta de salida
        layout_salida = QHBoxLayout()
        label_salida = QLabel("Carpeta de salida:")
        self.entry_output = QLineEdit()
        btn_seleccionar_carpeta = QPushButton("Seleccionar carpeta")
        btn_seleccionar_carpeta.clicked.connect(self.select_folder)
        layout_salida.addWidget(label_salida)
        layout_salida.addWidget(self.entry_output)
        layout_salida.addWidget(btn_seleccionar_carpeta)
        self.layout.addLayout(layout_salida)

        # Botón para iniciar el procesamiento
        self.btn_procesar = QPushButton("Procesar archivo")
        self.btn_procesar.clicked.connect(self.start_processing)
        self.layout.addWidget(self.btn_procesar)

        # Cuadro de texto para el log de proceso
        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text)

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
        msg_box.setText(f"Archivo procesado correctamente: ")
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Cambiar el texto del mensaje para que sea clickeable
        link = f"<a href='file:///{output_path}'>{output_path}</a>"
        msg_box.setInformativeText(link)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg_box.exec_()

    def show_error(self, error_message):
        # Mostrar el mensaje de error si ocurre algún problema
        QMessageBox.critical(self, "Error", error_message)
