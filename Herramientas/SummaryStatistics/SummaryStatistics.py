from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsFields, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout, QLineEdit, QCheckBox

class SummaryStatistics(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Summary Statistics")

        layout = QVBoxLayout()

        self.layer_label = QLabel("Ingresar Tabla:")
        layout.addWidget(self.layer_label)

        self.layer_combo = QComboBox()
        self.populate_layers(self.layer_combo)
        layout.addWidget(self.layer_combo)

        self.output_label = QLabel("Tabla resumen de salida:")
        layout.addWidget(self.output_label)

        self.output_line = QLineEdit()
        layout.addWidget(self.output_line)

        self.stat_fields_label = QLabel("Campo para estadística")
        layout.addWidget(self.stat_fields_label)

        self.stat_fields_combo = QComboBox()
        layout.addWidget(self.stat_fields_combo)

        self.stat_type_label = QLabel("Tipo de estadística")
        layout.addWidget(self.stat_type_label)

        self.stat_type_combo = QComboBox()
        self.stat_type_combo.addItems(["Recuento", "Suma", "Promedio", "Mediana", "Min", "Max", "Rango", "Desviacion Estandar"])
        layout.addWidget(self.stat_type_combo)

        self.case_field_label = QLabel("Campo de caso")
        layout.addWidget(self.case_field_label)

        self.case_field_combo = QComboBox()
        layout.addWidget(self.case_field_combo)

        self.run_button = QPushButton("Ejecutar")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)

        self.setLayout(layout)
        self.layer_combo.currentIndexChanged.connect(self.update_fields)

    def populate_layers(self, combo_box):
        combo_box.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer):
                combo_box.addItem(layer.name(), layer)

    def update_fields(self):
        layer = self.layer_combo.currentData()
        if layer:
            fields = [field.name() for field in layer.fields()]
            self.stat_fields_combo.clear()
            self.stat_fields_combo.addItems(fields)
            self.case_field_combo.clear()
            self.case_field_combo.addItems(fields)

    def run(self):
        input_layer = self.layer_combo.currentData()
        output_table_name = self.output_line.text()
        stat_field = self.stat_fields_combo.currentText()
        stat_type = self.stat_type_combo.currentText()
        case_field = self.case_field_combo.currentText()

        if not input_layer or not output_table_name or not stat_field or not case_field:
            self.iface.messageBar().pushMessage("Error", "Todos los campos son requeridos", level=3)
            return

        stat_layer = QgsVectorLayer("None", output_table_name, "memory")
        stat_layer_data = stat_layer.dataProvider()
        stat_layer.startEditing()

        # Define output fields
        fields = QgsFields()
        fields.append(QgsField(case_field, QVariant.String))
        fields.append(QgsField(stat_type + "_" + stat_field, QVariant.Double))
        stat_layer_data.addAttributes(fields)
        stat_layer.updateFields()

        # Calculate statistics
        stats = {}
        for feature in input_layer.getFeatures():
            key = feature[case_field]
            value = feature[stat_field]
            if key not in stats:
                stats[key] = []
            stats[key].append(value)

        for key, values in stats.items():
            new_feature = QgsFeature()
            new_feature.setAttributes([key, self.calculate_stat(stat_type, values)])
            stat_layer_data.addFeature(new_feature)

        stat_layer.commitChanges()
        QgsProject.instance().addMapLayer(stat_layer)
        self.iface.messageBar().pushMessage("Info", "Resumen de estadísticas completado", level=0)
        self.close()

    def calculate_stat(self, stat_type, values):
        if stat_type == "Recuento":
            return len(values)
        elif stat_type == "Suma":
            return sum(values)
        elif stat_type == "Promedio":
            return sum(values) / len(values) if values else None
        elif stat_type == "Mediana":
            return sorted(values)[len(values) // 2] if values else None
        elif stat_type == "Min":
            return min(values)
        elif stat_type == "Max":
            return max(values)
        elif stat_type == "Rango":
            return max(values) - min(values)
        elif stat_type == "Desviacion Estandar":
            mean = sum(values) / len(values) if values else None
            return (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5 if values else None
        else:
            return None

class SummaryStatisticsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Summary Statistics", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&SummaryStatistics", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&SummaryStatistics", self.action)

    def run(self):
        dialog = SummaryStatistics(self.iface)
        dialog.exec_()
