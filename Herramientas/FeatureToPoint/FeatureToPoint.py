from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel, QComboBox, QRadioButton, QPushButton, QCheckBox

class FeatureToPoint(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Feature to Point")
        
        layout = QVBoxLayout()

        self.layer_label = QLabel("Seleccionar capa de entrada:")
        layout.addWidget(self.layer_label)

        self.layer_combo = QComboBox()
        self.populate_layers()
        layout.addWidget(self.layer_combo)

        self.radio_centroid = QRadioButton("Centroide")
        self.radio_inside = QRadioButton("Forza dentro del Poligono")
        self.radio_centroid.setChecked(True)
        layout.addWidget(self.radio_centroid)
        layout.addWidget(self.radio_inside)

        self.selected_only_checkbox = QCheckBox("Procesar sólo lo seleccionado")
        layout.addWidget(self.selected_only_checkbox)

        self.ladm_checkbox = QCheckBox("Estandarizar Dirección LADM")
        self.ladm_checkbox.stateChanged.connect(self.toggle_tipo_direccion)
        layout.addWidget(self.ladm_checkbox)

        self.tipo_direccion_label = QLabel("Tipo de Dirección:")
        layout.addWidget(self.tipo_direccion_label)
        
        self.tipo_direccion_combo = QComboBox()
        self.tipo_direccion_combo.addItems(["Estructurada", "No_Estructurada"])
        layout.addWidget(self.tipo_direccion_combo)

        self.run_button = QPushButton("Procesar")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)

        self.setLayout(layout)

        self.toggle_tipo_direccion()

    def populate_layers(self):
        self.layer_combo.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() in [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry]:
                self.layer_combo.addItem(layer.name(), layer)

    def toggle_tipo_direccion(self):
        is_checked = self.ladm_checkbox.isChecked()
        self.tipo_direccion_label.setVisible(is_checked)
        self.tipo_direccion_combo.setVisible(is_checked)





    def run(self):
        layer = self.layer_combo.currentData()
        if not layer:
            self.iface.messageBar().pushMessage("Error", "Capa vectorial no seleccionada", level=3)
            return

        ladm_enabled = self.ladm_checkbox.isChecked()

        if ladm_enabled:
            # Verificar los campos requeridos si LADM está activado
            required_fields = ["Predio_nombre", "col_uebaunit_baunit", "t_id"]
            for field in required_fields:
                if field not in [f.name() for f in layer.fields()]:
                    self.iface.messageBar().pushMessage("Error", "Realice la unión con la tabla predio", level=3)
                    return

        selected_only = self.selected_only_checkbox.isChecked()
        new_layer = QgsVectorLayer("Point?crs=" + layer.crs().authid(), "FeatureToPoint", "memory")
        new_layer_data = new_layer.dataProvider()
        new_layer.startEditing()

        # Añadir atributos de la capa original
        new_layer_data.addAttributes(layer.fields())
        new_layer.updateFields()

        if ladm_enabled:
            # Añadir campos específicos para LADM si está activado
            ladm_fields = [
                QgsField("t_seq", QVariant.Int),
                QgsField("tipo_direccion", QVariant.String),
                QgsField("es_direccion_principal", QVariant.Bool),
                QgsField("codigo_postal", QVariant.String),
                QgsField("clase_via_principal", QVariant.Int),
                QgsField("valor_via_principal", QVariant.String),
                QgsField("letra_via_principal", QVariant.String),
                QgsField("sector_ciudad", QVariant.Int),
                QgsField("valor_via_generadora", QVariant.String),
                QgsField("letra_via_generadora", QVariant.String),
                QgsField("numero_predio", QVariant.String),
                QgsField("sector_predio", QVariant.Int),
                QgsField("complemento", QVariant.String),
                QgsField("nombre_predio", QVariant.String),
                QgsField("extunidadedificcnfsica_ext_direccion_id", QVariant.Int),
                QgsField("extinteresado_ext_direccion_id", QVariant.Int),
                QgsField("lc_construccion_ext_direccion_id", QVariant.Int),
                QgsField("lc_terreno_ext_direccion_id", QVariant.Int),
                QgsField("lc_predio_direccion", QVariant.Int),
                QgsField("lc_servidumbretransito_ext_direccion_id", QVariant.Int),
                QgsField("lc_unidadconstruccion_ext_direccion_id", QVariant.Int),
            ]
            new_layer_data.addAttributes(ladm_fields)
            new_layer.updateFields()

        if selected_only:
            features = layer.selectedFeatures()
        else:
            features = layer.getFeatures()

        new_features = []
        for feature in features:
            if self.radio_centroid.isChecked():
                point_geom = feature.geometry().centroid()
            else:
                point_geom = feature.geometry().pointOnSurface()

            new_feat = QgsFeature()
            new_feat.setGeometry(point_geom)
            new_feat.setAttributes(feature.attributes())
            new_features.append(new_feat)

        new_layer_data.addFeatures(new_features)
        new_layer.commitChanges()

        if ladm_enabled:
            # Si LADM está activado, realizar actualizaciones adicionales
            tipo_direccion_value = self.tipo_direccion_combo.currentText()

            new_layer.startEditing()
            for feature in new_layer.getFeatures():
                feature.setAttribute('tipo_direccion', tipo_direccion_value)
                feature.setAttribute('lc_terreno_ext_direccion_id', feature['t_id'])
                feature.setAttribute('lc_predio_direccion', feature['col_uebaunit_baunit'])
                feature.setAttribute('nombre_predio', feature['Predio_nombre'])
                new_layer.updateFeature(feature)

            new_layer.commitChanges()

            # Crear una nueva capa con solo los campos deseados para LADM
            desired_fields = [
                "t_id", "t_seq", "tipo_direccion", "es_direccion_principal", "codigo_postal", "clase_via_principal", 
                "valor_via_principal", "letra_via_principal", "sector_ciudad", "valor_via_generadora", "letra_via_generadora", 
                "numero_predio", "sector_predio", "complemento", "nombre_predio", 
                "extunidadedificcnfsica_ext_direccion_id", "extinteresado_ext_direccion_id", 
                "lc_construccion_ext_direccion_id", "lc_predio_direccion", "lc_terreno_ext_direccion_id", 
                "lc_servidumbretransito_ext_direccion_id", "lc_unidadconstruccion_ext_direccion_id"
            ]
            new_layer_final = QgsVectorLayer("Point?crs=" + layer.crs().authid(), "FeatureToPointFinal", "memory")
            new_layer_final_data = new_layer_final.dataProvider()
            new_layer_final.startEditing()

            # Añadir solo los campos deseados
            for field_name in desired_fields:
                field = new_layer.fields().field(new_layer.fields().indexFromName(field_name))
                new_layer_final_data.addAttributes([field])
            new_layer_final.updateFields()

            # Añadir las características con solo los atributos deseados
            for feature in new_layer.getFeatures():
                new_feat = QgsFeature()
                new_feat.setGeometry(feature.geometry())
                new_feat.setAttributes([feature[field_name] for field_name in desired_fields])
                new_layer_final_data.addFeatures([new_feat])

            new_layer_final.commitChanges()
            QgsProject.instance().addMapLayer(new_layer_final)
        else:
            # Si no se procesa LADM, simplemente añadir la capa al proyecto
            QgsProject.instance().addMapLayer(new_layer)

        self.iface.messageBar().pushMessage("Info", "Feature to Point completado", level=0)
        self.close()






class FeatureToPointPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Feature to Point", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&FeatureToPoint", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&FeatureToPoint", self.action)

    def run(self):
        dialog = FeatureToPoint(self.iface)
        dialog.exec_()
