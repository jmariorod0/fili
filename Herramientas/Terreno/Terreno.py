from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsWkbTypes, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import QVariant, QDateTime
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
import math

class CreateTerrenoLayer(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Create Terreno Layer")
        
        layout = QVBoxLayout()

        self.layer_label = QLabel("Seleccionar capa de poligonos:")
        layout.addWidget(self.layer_label)

        self.layer_combo = QComboBox()
        self.populate_layers()
        layout.addWidget(self.layer_combo)

        self.field_label = QLabel("Seleccionar campo para etiqueta y local_id:")
        layout.addWidget(self.field_label)

        self.field_combo = QComboBox()
        layout.addWidget(self.field_combo)

        self.run_button = QPushButton("Crear Capa")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)

        self.layer_combo.currentIndexChanged.connect(self.populate_fields)

        self.setLayout(layout)

    def populate_layers(self):
        self.layer_combo.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.layer_combo.addItem(layer.name(), layer)

    def populate_fields(self):
        self.field_combo.clear()
        layer = self.layer_combo.currentData()
        if layer:
            fields = layer.fields()
            for field in fields:
                self.field_combo.addItem(field.name())

    def run(self):
        layer = self.layer_combo.currentData()
        selected_field = self.field_combo.currentText()

        if not layer:
            self.iface.messageBar().pushMessage("Error", "Capa tipo poligono no seleccionada", level=3)
            return

        if not selected_field:
            self.iface.messageBar().pushMessage("Error", "No se ha seleccionado un campo para etiqueta", level=3)
            return

        # Define CRS for the new layer
        crs = QgsCoordinateReferenceSystem("EPSG:9377")

        new_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "TerrenoLayer", "memory")
        new_layer_data = new_layer.dataProvider()
        new_layer.startEditing()

        # Add original attributes
        new_layer_data.addAttributes(layer.fields())
        
        # Add new fields
        new_fields = [
            QgsField("t_id", QVariant.Int),
            QgsField("t_ili_tid", QVariant.String),
            QgsField("area_terreno", QVariant.Double),
            QgsField("avaluo_terreno", QVariant.Double),
            QgsField("manzana_vereda_codigo", QVariant.String),
            QgsField("dimension", QVariant.String),
            QgsField("etiqueta", QVariant.String),
            QgsField("relacion_superficie", QVariant.String),
            QgsField("comienzo_vida_util_version", QVariant.DateTime),
            QgsField("fin_vida_util_version", QVariant.DateTime),
            QgsField("espacio_de_nombres", QVariant.String),
            QgsField("local_id", QVariant.String)
        ]
        new_layer_data.addAttributes(new_fields)
        new_layer.updateFields()

        # Copy features from the original layer
        for feature in layer.getFeatures():
            new_feat = QgsFeature()
            new_feat.setGeometry(feature.geometry())
            new_feat.setAttributes(feature.attributes() + [None] * len(new_fields))  # Initialize new fields with None
            new_layer_data.addFeature(new_feat)

        new_layer.commitChanges()
        new_layer.startEditing()

        # Update fields
        for feature in new_layer.getFeatures():
            feature.setAttribute('etiqueta', feature[selected_field])
            feature.setAttribute('local_id', feature[selected_field])
            feature.setAttribute('dimension', 'Dim2D')
            feature.setAttribute('relacion_superficie', 'En_Rasante')
            feature.setAttribute('comienzo_vida_util_version', QDateTime.currentDateTime())
            area_value = round(feature.geometry().area(), 2)
            feature.setAttribute('area_terreno', area_value)
            new_layer.updateFeature(feature)

        new_layer.commitChanges()
        QgsProject.instance().addMapLayer(new_layer)
        self.iface.messageBar().pushMessage("Info", "Capa de Terreno estandarizado correctamente", level=0)

class CreateTerrenoLayerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Create Terreno Layer", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&CreateTerrenoLayer", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&CreateTerrenoLayer", self.action)

    def run(self):
        dialog = CreateTerrenoLayer(self.iface)
        dialog.exec_()
