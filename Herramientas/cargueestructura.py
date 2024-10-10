import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
from dateutil import parser 

class cargue_estructura(QDialog):
    def __init__(self, iface, parent=None):
        super(cargue_estructura, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Cargar Datos a gpkg de Seguimiento")
        self.resize(800, 600)  # Ajustar tamaño de la interfaz

        # Layout principal
        layout = QVBoxLayout()

        # Seleccionar capa base cargada en QGIS
        base_layer_layout = QHBoxLayout()
        self.base_layer_label = QLabel("Seleccionar capa base de seguimiento:")
        self.base_layer_combo = QComboBox()
        layout.addWidget(self.base_layer_label)
        layout.addWidget(self.base_layer_combo)

        # ComboBox para seleccionar la capa de QGIS (para añadir datos)
        self.qgis_layer_combo = QComboBox()
        layout.addWidget(QLabel("Seleccionar capa a cargar:"))
        layout.addWidget(self.qgis_layer_combo)

        # Botón para leer la capa seleccionada
        self.read_layer_button = QPushButton("Leer Capa")  # Botón para leer la capa seleccionada
        layout.addWidget(self.read_layer_button)

        # Tabla para asignar columnas
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Botón para cargar datos
        self.load_button = QPushButton("Cargar Datos")
        layout.addWidget(self.load_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Conectar eventos a funciones
        self.read_layer_button.clicked.connect(self.load_qgis_layer_columns)  # Conectar el botón "Leer Capa"
        self.load_button.clicked.connect(self.load_data)
        self.base_layer_combo.currentIndexChanged.connect(self.load_base_layer_columns)

        # Cargar capas de QGIS inmediatamente
        self.load_qgis_layers()
        self.load_base_layers()

        # Inicializar variables
        self.selected_base_layer = None
        self.selected_qgis_layer = None
        self.setLayout(layout)

    def load_base_layers(self):
        # Cargar todas las capas cargadas en QGIS para la capa base
        self.base_layer_combo.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.type() == QgsVectorLayer.VectorLayer]
        for layer in layers:
            self.base_layer_combo.addItem(layer.name())

    def load_qgis_layers(self):
        # Cargar capas vectoriales cargadas en QGIS
        self.qgis_layer_combo.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if layer.type() == QgsVectorLayer.VectorLayer]
        for layer in layers:
            self.qgis_layer_combo.addItem(layer.name())

    def load_base_layer_columns(self):
        # Leer los campos de la capa base seleccionada
        selected_layer_name = self.base_layer_combo.currentText()
        
        if not selected_layer_name:
            QMessageBox.warning(self, "Error", "No se ha seleccionado una capa base.")
            return
        
        layers = QgsProject.instance().mapLayersByName(selected_layer_name)

        if layers:
            self.selected_base_layer = layers[0]  # Leer la capa base seleccionada en QGIS
            if self.selected_base_layer.isValid():
                base_fields = self.selected_base_layer.fields()
                base_field_names = [field.name() for field in base_fields]
                # Actualizar la tabla de mapeo con los campos de la capa base
                self.load_mapping_table(base_field_names)
                # Leer y actualizar la geometría de la capa base seleccionada
                self.selected_base_layer.updateExtents()
            else:
                QMessageBox.warning(self, "Error", "La capa base seleccionada no es válida.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo encontrar la capa base seleccionada en el proyecto de QGIS.")

    def load_qgis_layer_columns(self):
        # Forzar la lectura de la capa seleccionada en QGIS para el mapeo de datos
        selected_layer_name = self.qgis_layer_combo.currentText()
        
        if not selected_layer_name:
            QMessageBox.warning(self, "Error", "No se ha seleccionado una capa de QGIS.")
            return
        
        layers = QgsProject.instance().mapLayersByName(selected_layer_name)

        if layers:
            self.selected_qgis_layer = layers[0]  # Leer la capa seleccionada en el comboBox de QGIS
            if self.selected_qgis_layer.isValid():
                qgis_fields = self.selected_qgis_layer.fields()
                qgis_field_names = [field.name() for field in qgis_fields]
                # Actualizar la tabla de mapeo con los campos de la capa seleccionada en QGIS
                self.update_mapping_table_with_qgis_fields(qgis_field_names)
                # Leer y actualizar la geometría de la capa seleccionada
                self.selected_qgis_layer.updateExtents()
            else:
                QMessageBox.warning(self, "Error", "La capa seleccionada no es válida.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo encontrar la capa seleccionada en el proyecto de QGIS.")




    def load_mapping_table(self, base_field_names):
        self.table.setColumnCount(2)
        self.table.setRowCount(len(base_field_names))
        self.table.setHorizontalHeaderLabels(["Campo Capa Base", "Campo Capa QGIS"])

        # Ajustar el ancho de las columnas
        self.table.setColumnWidth(0, 200)  # Ancho de la primera columna
        self.table.setColumnWidth(1, 300)  # Ancho de la segunda columna

        for row, base_field in enumerate(base_field_names):
            self.table.setItem(row, 0, QTableWidgetItem(base_field))
            combo = QComboBox()

            # Deshabilitar el mapeo para los campos 'fid' y 'AREA_M2'
            if base_field.lower() == "fid":
                combo.addItem("Gestionado automáticamente por QGIS")
                combo.setEnabled(False)
            elif base_field.lower() == "area_m2":
                combo.addItem("Calculado automáticamente")
                combo.setEnabled(False)
            else:
                combo.addItem("SIN CORRESPONDENCIA")
                font = QFont()
                font.setBold(True)
                combo.setItemData(0, font, Qt.FontRole)
            
            self.table.setCellWidget(row, 1, combo)



    def update_mapping_table_with_qgis_fields(self, qgis_field_names):
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 1)
            combo.clear()

            base_field = self.table.item(row, 0).text()

            # Si el campo base es 'fid', dejar la opción predeterminada deshabilitada
            if base_field.lower() == "fid":
                combo.addItem("Gestionado automáticamente por QGIS")
                combo.setEnabled(False)
            # Si el campo base es 'AREA_M2', también deshabilitar y calcular automáticamente
            elif base_field.lower() == "area_m2":
                combo.addItem("Calculado automáticamente")
                combo.setEnabled(False)
            else:
                combo.addItem("SIN CORRESPONDENCIA")
                font = QFont()
                font.setBold(True)
                combo.setItemData(0, font, Qt.FontRole)

                # Añadir los campos de la capa QGIS
                combo.addItems(qgis_field_names)

                # Pre-seleccionar campos que coincidan o sean similares
                if base_field in qgis_field_names:
                    index = qgis_field_names.index(base_field) + 1  # Ajustar para tener en cuenta "SIN CORRESPONDENCIA"
                    combo.setCurrentIndex(index)

    def load_data(self):
        # Validar si las capas base y QGIS han sido seleccionadas correctamente
        if not self.selected_base_layer:
            QMessageBox.warning(self, "Error", "No se ha seleccionado correctamente la capa base. Asegúrate de haber seleccionado una capa válida en 'Seleccionar capa base'.")
            print("Error: capa base no seleccionada o no válida.")
            return
        
        if not self.selected_qgis_layer:
            QMessageBox.warning(self, "Error", "No se ha seleccionado correctamente la capa de QGIS. Asegúrate de haber seleccionado una capa válida en 'Seleccionar capa de QGIS'.")
            print("Error: capa de QGIS no seleccionada o no válida.")
            return

        # Validar si hay campos mapeados
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No se han cargado los campos para la capa base o la capa de QGIS. Verifica que ambas capas tengan campos válidos.")
            print("Error: no se han cargado campos en la tabla de mapeo.")
            return

        # Reiniciar la barra de progreso antes de iniciar una nueva carga
        self.progress_bar.setValue(0)

        data_provider = self.selected_base_layer.dataProvider()

        try:
            # Validar si la capa base está vacía pero permitir el proceso
            total_features_base = self.selected_base_layer.featureCount()
            if total_features_base == 0:
                print("Advertencia: La capa base está vacía. Procediendo a insertar nuevas características.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al leer la capa base: {str(e)}")
            print(f"Error al leer la capa base: {str(e)}")
            return

        total_features_qgis = self.selected_qgis_layer.featureCount()

        # Verificar si la capa de QGIS tiene características (features)
        if total_features_qgis == 0:
            QMessageBox.information(self, "Advertencia", "La capa de QGIS está vacía. No se procederá con la carga de datos.")
            print("Advertencia: La capa de QGIS está vacía.")
            return

        # No importa si la capa base está vacía; podemos proceder con la inserción
        self.progress_bar.setMaximum(total_features_qgis)
        features_to_add = []
        
        # Añadir depuración detallada de inserciones
        success = False
        try:
            for i, feature in enumerate(self.selected_qgis_layer.getFeatures()):
                new_feature = QgsFeature(self.selected_base_layer.fields())
                for row in range(self.table.rowCount()):
                    base_field = self.table.item(row, 0).text()

                    # Evitar asignar manualmente el campo 'fid', ya que QGIS lo gestiona automáticamente
                    if base_field.lower() == "fid":
                        continue
                    
                    # Si el campo es 'AREA_M2', calcular el área automáticamente
                    if base_field.lower() == "area_m2":
                        area_value = round(feature.geometry().area(), 2)
                        new_feature.setAttribute(base_field, area_value)
                    else:
                        qgis_field = self.table.cellWidget(row, 1).currentText()
                        # No asignar nada si es "SIN CORRESPONDENCIA", excepto para AREA_M2
                        if qgis_field != "SIN CORRESPONDENCIA":
                            new_feature.setAttribute(base_field, feature[qgis_field])
                
                # Establecemos la geometría
                new_feature.setGeometry(feature.geometry())  
                features_to_add.append(new_feature)
                self.progress_bar.setValue(i + 1)

            # Añadir las nuevas características a la capa base
            success, added_features = data_provider.addFeatures(features_to_add)
            self.selected_base_layer.updateFields()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al añadir las características: {str(e)}")
            print(f"Ocurrió un error al añadir las características: {str(e)}")
            return

        if success:
            QMessageBox.information(self, "Éxito", f"Se han añadido {len(added_features)} características correctamente.")
            print(f"Éxito: Se han añadido {len(added_features)} características correctamente.")
        else:
            QMessageBox.warning(self, "Error", "Ocurrió un error al añadir las características.")
            print("Error: No se pudieron añadir las características.")

