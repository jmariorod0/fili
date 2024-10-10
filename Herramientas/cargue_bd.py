import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, 
                             QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox, QToolButton)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsExpression, QgsExpressionContext, QgsExpressionContextScope
from qgis.gui import QgsFieldExpressionWidget,QgsExpressionBuilderDialog
from qgis.core import QgsExpressionContextUtils




class cargue_bd(QDialog):
    def __init__(self, iface, parent=None):
        super(cargue_bd, self).__init__(parent)
        self.iface = iface
        self.setWindowTitle("Cargar de datos por correspondencia")
        self.resize(800, 600)  # Ajustar tamaño de la interfaz

        # Layout principal
        layout = QVBoxLayout()

        # Seleccionar capa base cargada en QGIS
        base_layer_layout = QHBoxLayout()
        self.base_layer_label = QLabel("Seleccionar capa base:")
        self.base_layer_combo = QComboBox()
        layout.addWidget(self.base_layer_label)
        layout.addWidget(self.base_layer_combo)

        # ComboBox para seleccionar la capa de QGIS (para añadir datos)
        self.qgis_layer_combo = QComboBox()
        layout.addWidget(QLabel("Seleccionar capa a cargar:"))
        layout.addWidget(self.qgis_layer_combo)

        # Botón para leer la capa seleccionada
        self.read_layer_button = QPushButton("Leer Capa")
        layout.addWidget(self.read_layer_button)

        # Tabla para asignar columnas y expresiones
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Botón para cargar datos
        self.load_button = QPushButton("Cargar Datos")
        layout.addWidget(self.load_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Conectar eventos a funciones
        self.read_layer_button.clicked.connect(self.load_qgis_layer_columns)
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
        self.table.setColumnCount(3)  # Añadir una tercera columna para expresiones
        self.table.setRowCount(len(base_field_names))
        self.table.setHorizontalHeaderLabels(["Campo Capa Base", "Campo Capa QGIS", "Expresión (Opcional)"])

        for row, base_field in enumerate(base_field_names):
            self.table.setItem(row, 0, QTableWidgetItem(base_field))
            combo = QComboBox()

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

            # Añadir botón de calculadora de expresiones
            expression_button = QPushButton()
            expression_button.setIcon(QIcon("path_to_calculator_icon"))  # Asegúrate de tener el ícono correcto
            expression_button.clicked.connect(lambda _, r=row: self.open_expression_dialog(r))  # Conectar el botón con la función
            self.table.setCellWidget(row, 2, expression_button)




    def update_mapping_table_with_qgis_fields(self, qgis_field_names):
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 1)
            if combo:  # Verificar si existe el QComboBox antes de usarlo
                combo.clear()

                base_field = self.table.item(row, 0).text()

                # Si el campo base es 'fid', dejar la opción predeterminada deshabilitada
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

                    # Añadir los campos de la capa QGIS
                    combo.addItems(qgis_field_names)

                    # Pre-seleccionar campos que coincidan o sean similares
                    if base_field in qgis_field_names:
                        index = qgis_field_names.index(base_field) + 1
                        combo.setCurrentIndex(index)



    def open_expression_dialog(self, row):
        # Crear el contexto de expresión para la capa seleccionada
        expression_context = QgsExpressionContext()
        
        # Agregar cada scope al contexto de expresión
        for scope in QgsExpressionContextUtils.globalProjectLayerScopes(self.selected_qgis_layer):
            expression_context.appendScope(scope)
        
        # Crear un diálogo para la construcción de expresiones
        expression_dialog = QgsExpressionBuilderDialog(self.selected_qgis_layer, None, self)
        expression_dialog.setWindowTitle("Editor de Expresión")
        
        # Obtener el campo de expresión (QLineEdit) correspondiente
        expression_field = self.table.cellWidget(row, 2)
        
        # Si ya existe una expresión en la celda, cargarla en el diálogo
        if expression_field and expression_field.text():
            expression_dialog.setExpressionText(expression_field.text())
        
        # Conectar el resultado del diálogo con la tabla
        if expression_dialog.exec_() == QDialog.Accepted:
            expression_text = expression_dialog.expressionText()
            expression_field.setText(expression_text)





    def set_expression_value(self, expression_widget, row, dialog):
        # Obtener la expresión seleccionada y guardarla en la celda correspondiente
        expression_text = expression_widget.currentText()
        expression_field = self.table.cellWidget(row, 2)
        
        # Establecer la expresión en la columna de expresión opcional
        expression_field.setText(expression_text)
        
        # Cerrar el diálogo
        dialog.accept()




    def load_data(self):
        if not self.selected_base_layer:
            QMessageBox.warning(self, "Error", "No se ha seleccionado correctamente la capa base.")
            return

        if not self.selected_qgis_layer:
            QMessageBox.warning(self, "Error", "No se ha seleccionado correctamente la capa de QGIS.")
            return

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Error", "No se han cargado los campos para la capa base o la capa de QGIS.")
            return

        self.progress_bar.setValue(0)
        data_provider = self.selected_base_layer.dataProvider()

        total_features_qgis = self.selected_qgis_layer.featureCount()
        if total_features_qgis == 0:
            QMessageBox.information(self, "Advertencia", "La capa de QGIS está vacía.")
            return

        self.progress_bar.setMaximum(total_features_qgis)
        features_to_add = []

        # Crear contexto de expresión para las características
        expression_context = QgsExpressionContext()

        # Agregar todos los scopes de la capa seleccionada al contexto de expresión
        for scope in QgsExpressionContextUtils.globalProjectLayerScopes(self.selected_qgis_layer):
            expression_context.appendScope(scope)

        try:
            for i, feature in enumerate(self.selected_qgis_layer.getFeatures()):
                new_feature = QgsFeature(self.selected_base_layer.fields())
                expression_context.setFeature(feature)

                for row in range(self.table.rowCount()):
                    base_field_item = self.table.item(row, 0)  # Obtener el campo base
                    if base_field_item is None:
                        continue  # Si no hay campo base, saltar esta fila

                    base_field = base_field_item.text()
                    # Evitar asignar manualmente el campo 'fid'
                    if base_field.lower() == "fid":
                        continue

                    # Si el campo es 'AREA_M2', calcular el área automáticamente
                    if base_field.lower() == "area_m2":
                        area_value = round(feature.geometry().area(), 2)
                        new_feature.setAttribute(base_field, area_value)
                    else:
                        qgis_field_combo = self.table.cellWidget(row, 1)  # ComboBox para seleccionar el campo QGIS
                        expression_field = self.table.cellWidget(row, 2)  # QLineEdit para la expresión

                        if qgis_field_combo is None:
                            continue  # Si no hay combo, saltar esta fila

                        expression_text = expression_field.text() if expression_field else ""  # Obtener la expresión si existe

                        # Evaluar expresión si se proporciona una
                        if expression_text:
                            expression = QgsExpression(expression_text)
                            if expression.hasParserError():
                                raise Exception(f"Error en la expresión en el campo '{base_field}', fila {row + 1}: {expression.parserErrorString()}")

                            # Evaluar expresión y asignar resultado
                            value = expression.evaluate(expression_context)
                            if expression.hasEvalError():
                                raise Exception(f"Error al evaluar la expresión en el campo '{base_field}', fila {row + 1}: {expression.evalErrorString()}")

                            try:
                                new_feature.setAttribute(base_field, value)
                            except Exception as e:
                                raise Exception(f"Error al asignar el valor '{value}' al campo '{base_field}', fila {row + 1}: {str(e)}")

                        # Si no hay expresión, asignar el valor del combo box sin validación de tipo de dato
                        elif qgis_field_combo.currentText() != "SIN CORRESPONDENCIA":
                            qgis_field = qgis_field_combo.currentText()
                            value = feature[qgis_field]

                            # Si el valor es nulo y el campo no puede ser nulo (ej. qr_operacion), asignar el valor predeterminado
                            if value is None and (base_field == "qr_operacion" or base_field == "qr_operacion_definitivo"):
                                new_feature.setAttribute(base_field, '0000000000')
                            else:
                                try:
                                    new_feature.setAttribute(base_field, value)
                                except Exception as e:
                                    raise Exception(f"Error al asignar el valor '{value}' al campo '{base_field}', fila {row + 1}: {str(e)}")

                # Establecer la geometría
                new_feature.setGeometry(feature.geometry())  
                features_to_add.append(new_feature)
                self.progress_bar.setValue(i + 1)

            # Intentar agregar las características
            success, added_features = data_provider.addFeatures(features_to_add)
            self.selected_base_layer.updateFields()

        except Exception as e:
            # Capturar y mostrar el error específico, incluyendo la fila y el campo
            QMessageBox.critical(self, "Error", f"Ocurrió un error al añadir las características: {str(e)}")
            return

        if success:
            QMessageBox.information(self, "Éxito", f"Se han añadido {len(added_features)} características correctamente.")
        else:
            QMessageBox.warning(self, "Error", "Ocurrió un error al añadir las características.")

