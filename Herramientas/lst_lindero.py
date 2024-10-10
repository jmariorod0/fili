from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QMessageBox, QDialog, QTreeWidget, QTreeWidgetItem, QInputDialog
from PyQt5.QtCore import Qt
import pandas as pd
import os
import webbrowser

class ColumnAdjusterApp(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Visualizador archivos .LST")
        self.setGeometry(100, 100, 800, 600)

        # Variables
        self.file_path = None
        self.data = []
        self.columns = []

        # Crear el layout principal
        self.layout = QVBoxLayout(self)

        # Crear botones
        self.create_buttons()

        # Crear el QTreeWidget para mostrar datos
        self.create_treeview()

    def create_buttons(self):
        # Botón para abrir archivo
        self.btn_open_file = QPushButton("Abrir archivo", self)
        self.btn_open_file.clicked.connect(self.open_file)
        self.layout.addWidget(self.btn_open_file)

        # Botón para guardar como Excel
        self.btn_save_excel = QPushButton("Guardar como Excel", self)
        self.btn_save_excel.clicked.connect(self.save_to_excel)
        self.layout.addWidget(self.btn_save_excel)

        # Botón para agregar columna
        #self.btn_add_column = QPushButton("Agregar Columna", self)
        #self.btn_add_column.clicked.connect(self.add_column)
        #self.layout.addWidget(self.btn_add_column)

        # Botón para eliminar columna
        #self.btn_remove_column = QPushButton("Eliminar Columna", self)
        #self.btn_remove_column.clicked.connect(self.remove_column)
        #self.layout.addWidget(self.btn_remove_column)

    def create_treeview(self):
        # Crear el widget para mostrar datos
        self.tree = QTreeWidget(self)
        self.layout.addWidget(self.tree)

    def open_file(self):
        # Abrir cuadro de diálogo para seleccionar archivo
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Archivos de texto (*.txt *.csv *.lst);;Todos los archivos (*.*)")
        
        if not file_path:
            return
        
        self.file_path = file_path

        # Definir anchos de columnas
        column_widths = [16, 3000]

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = []
                for line in file:
                    columns = []
                    start = 0
                    for width in column_widths:
                        columns.append(line[start:start+width].strip())
                        start += width
                    self.data.append(columns)

            # Crear encabezados de columnas
            self.columns = [f"Columna {i+1}" for i in range(len(column_widths))]

            # Actualizar el QTreeWidget con los datos
            self.update_treeview()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer el archivo:\n{str(e)}")

    def update_treeview(self):
        # Limpiar el QTreeWidget antes de cargar nuevos datos
        self.tree.clear()
        self.tree.setColumnCount(len(self.columns))
        self.tree.setHeaderLabels(self.columns)

        # Insertar filas en el QTreeWidget
        for row in self.data:
            item = QTreeWidgetItem(row)
            self.tree.addTopLevelItem(item)

    def save_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Advertencia", "No hay datos para guardar.")
            return

        # Cuadro de diálogo para guardar el archivo Excel
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo Excel", "", "Archivos Excel (*.xlsx)")
        
        if not save_path:
            return

        # Crear DataFrame con los datos del QTreeWidget
        tree_data = []
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            tree_data.append([item.text(i) for i in range(self.tree.columnCount())])

        df = pd.DataFrame(tree_data, columns=self.columns)

        # Procesar la segunda columna (índice 1)
        df.iloc[:, 1] = df.iloc[:, 1].apply(lambda x: self.reemplazar_caracteres(x))

        try:
            # Guardar como archivo Excel
            df.to_excel(save_path, index=False, engine='openpyxl')
            self.show_success_message(save_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")



            

    def show_success_message(self, save_path):
        # Mostrar mensaje de éxito con enlace clickeable
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Proceso Completado")

        # Crear el mensaje con la ruta clickeable
        message = f"Archivo guardado exitosamente en:<br><a href='file:///{save_path}'>{save_path}</a>"
        msg_box.setText(message)

        # Habilitar formato RichText para hacer la ruta clickeable
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def add_column(self):
        if not self.columns:
            position = 0
        else:
            position, ok = QInputDialog.getInt(self, "Agregar Columna", f"Ingrese la posición de la nueva columna (1 - {len(self.columns) + 1}):", min=1, max=len(self.columns) + 1)

            if not ok:
                return

            position -= 1  # Ajustar índice a 0

        new_column_name = f"Columna {len(self.columns) + 1}"
        self.columns.insert(position, new_column_name)

        # Agregar columna vacía a cada fila de datos
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            item.insertColumn(position)

        self.update_treeview()

    def remove_column(self):
        if not self.columns:
            QMessageBox.warning(self, "Advertencia", "No hay columnas para eliminar.")
            return

        column_index, ok = QInputDialog.getInt(self, "Eliminar Columna", f"Ingrese el número de la columna a eliminar (1 - {len(self.columns)}):", min=1, max=len(self.columns))

        if not ok:
            return

        column_index -= 1  # Ajustar índice a 0

        if column_index == 0:
            QMessageBox.warning(self, "Advertencia", "No se puede eliminar la primera columna.")
            return

        # Eliminar la columna de los datos y del QTreeWidget
        for index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(index)
            item.takeChildren()

        self.columns.pop(column_index)
        self.update_treeview()

    def reemplazar_caracteres(self, texto):
        caracteres_a_reemplazar = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
            "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
            ".": ""
        }
        texto = str(texto)  # Asegurarse de que sea texto
        for viejo, nuevo in caracteres_a_reemplazar.items():
            texto = texto.replace(viejo, nuevo)
        return texto
