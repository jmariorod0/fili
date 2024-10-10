import uuid
from datetime import datetime
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsGeometry, QgsWkbTypes, QgsPointXY
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QAction, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QGroupBox, QFormLayout, QCheckBox, QLineEdit

class FeatureVerticesToPoints(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Feature Vertices to Points")
        
        layout = QVBoxLayout()

        self.layer_label = QLabel("Seleccionar Capa:")
        layout.addWidget(self.layer_label)

        self.layer_combo = QComboBox()
        self.populate_layers(self.layer_combo, [QgsWkbTypes.LineGeometry, QgsWkbTypes.PolygonGeometry])
        layout.addWidget(self.layer_combo)

        self.group_box = QGroupBox("Tipo de Punto")
        group_layout = QFormLayout()

        self.combo_point_type = QComboBox()
        self.combo_point_type.addItems([
            "Todos los vertices",
            "Punto Medio",
            "Vertice inicial",
            "Vertice final",
            "Vertice inicial y final",
            "Dangling vertex"  # No se proporcionó la traducción para esta opción.
        ])
        group_layout.addRow(QLabel("Tipo de Punto:"), self.combo_point_type)
        self.group_box.setLayout(group_layout)
        layout.addWidget(self.group_box)

        self.selection_only_check = QCheckBox("Procesar solo registros seleccionados")
        layout.addWidget(self.selection_only_check)

        self.ladm_check = QCheckBox("Estructura LADM")
        layout.addWidget(self.ladm_check)
        self.ladm_check.stateChanged.connect(self.toggle_ladm_options)

        self.ladm_layer_label = QLabel("Seleccionar capa de referencia de Puntos:")
        self.ladm_layer_combo = QComboBox()
        self.populate_layers(self.ladm_layer_combo, [QgsWkbTypes.PointGeometry])
        self.ladm_start_seq_label = QLabel("Ingrese Secuencial de Inicio para id_punto_lindero:")
        self.ladm_start_seq_input = QLineEdit()

        self.puntotipo_label = QLabel("Seleccione Tipo de Punto:")
        self.puntotipo_combo = QComboBox()
        self.puntotipo_combo.addItems([
            "Poste",
            "Construccion",
            "Punto_Dinamico",
            "Elemento_Natural",
            "Piedra",
            "Sin_Materializacion",
            "Mojon",
            "Incrustacion",
            "Pilastra"
        ])

        self.acuerdo_label = QLabel("Seleccione Acuerdo:")
        self.acuerdo_combo = QComboBox()
        self.acuerdo_combo.addItems([
            "Acuerdo",
            "Desacuerdo"
        ])

        self.metodoproduccion_label = QLabel("Seleccione Método de Producción:")
        self.metodoproduccion_combo = QComboBox()
        self.metodoproduccion_combo.addItems([
            "Metodo_Directo",
            "Metodo_Indirecto",
            "Metodo_Declarativo_y_Colaborativo"
        ])

        # Adding new checkbox for reference layer difference
        self.dif_capa_ref_check = QCheckBox("Diferencia capa referencia")
        layout.addWidget(self.dif_capa_ref_check)
        self.dif_capa_ref_check.stateChanged.connect(self.toggle_dif_capa_ref_options)

        layout.addWidget(self.ladm_layer_label)
        layout.addWidget(self.ladm_layer_combo)
        layout.addWidget(self.ladm_start_seq_label)
        layout.addWidget(self.ladm_start_seq_input)
        layout.addWidget(self.puntotipo_label)
        layout.addWidget(self.puntotipo_combo)
        layout.addWidget(self.acuerdo_label)
        layout.addWidget(self.acuerdo_combo)
        layout.addWidget(self.metodoproduccion_label)
        layout.addWidget(self.metodoproduccion_combo)

        self.run_button = QPushButton("Procesar")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)

        self.setLayout(layout)
        self.toggle_ladm_options()
        self.toggle_dif_capa_ref_options()

    def populate_layers(self, combo_box, geometry_types):
        combo_box.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() in geometry_types:
                combo_box.addItem(layer.name(), layer)

    def toggle_ladm_options(self):
        ladm_enabled = self.ladm_check.isChecked()
        self.ladm_layer_label.setVisible(ladm_enabled)
        self.ladm_layer_combo.setVisible(ladm_enabled)
        self.ladm_start_seq_label.setVisible(ladm_enabled)
        self.ladm_start_seq_input.setVisible(ladm_enabled)
        self.puntotipo_label.setVisible(ladm_enabled)
        self.puntotipo_combo.setVisible(ladm_enabled)
        self.acuerdo_label.setVisible(ladm_enabled)
        self.acuerdo_combo.setVisible(ladm_enabled)
        self.metodoproduccion_label.setVisible(ladm_enabled)
        self.metodoproduccion_combo.setVisible(ladm_enabled)

    def toggle_dif_capa_ref_options(self):
        dif_capa_ref_enabled = self.dif_capa_ref_check.isChecked()
        self.ladm_layer_label.setVisible(dif_capa_ref_enabled)
        self.ladm_layer_combo.setVisible(dif_capa_ref_enabled)

    def run(self):
        layer = self.layer_combo.currentData()
        if not layer:
            self.iface.messageBar().pushMessage("Error", "Capa vectorial no seleccionada", level=3)
            return
        
        point_type = self.combo_point_type.currentText()
        selection_only = self.selection_only_check.isChecked()
        ladm_enabled = self.ladm_check.isChecked()
        dif_capa_ref_enabled = self.dif_capa_ref_check.isChecked()

        new_layer_fields = layer.fields() if not ladm_enabled else []
        if ladm_enabled:
            ladm_layer = self.ladm_layer_combo.currentData()
            start_seq = self.ladm_start_seq_input.text()
            puntotipo_value = self.puntotipo_combo.currentText()
            acuerdo_value = self.acuerdo_combo.currentText()
            metodoproduccion_value = self.metodoproduccion_combo.currentText()
            if not ladm_layer or not start_seq or not puntotipo_value or not acuerdo_value or not metodoproduccion_value:
                self.iface.messageBar().pushMessage("Error", "Capa, secuencial, tipo de punto, acuerdo o método de producción no proporcionados", level=3)
                return

            new_layer_fields = [
                QgsField("t_id", QVariant.Int),
                QgsField("t_ili_tid", QVariant.String),
                QgsField("id_punto_lindero", QVariant.String),
                QgsField("puntotipo", QVariant.String),  # Change the data type to String
                QgsField("acuerdo", QVariant.String),  # Change the data type to String
                QgsField("fotoidentificacion", QVariant.Int),
                QgsField("exactitud_horizontal", QVariant.Double),
                QgsField("exactitud_vertical", QVariant.Double),
                QgsField("posicion_interpolacion", QVariant.Int),
                QgsField("metodoproduccion", QVariant.String),  # Change the data type to String
                QgsField("ue_lc_terreno", QVariant.Int),
                QgsField("ue_lc_construccion", QVariant.Int),
                QgsField("ue_lc_unidadconstruccion", QVariant.Int),
                QgsField("ue_lc_servidumbretransito", QVariant.Int),
                QgsField("comienzo_vida_util_version", QVariant.String),
                QgsField("fin_vida_util_version", QVariant.String),
                QgsField("espacio_de_nombres", QVariant.String),
                QgsField("local_id", QVariant.String)
            ]

        new_layer = QgsVectorLayer("Point?crs=" + layer.crs().authid(), "FeatureVerticesToPoints", "memory")
        new_layer_data = new_layer.dataProvider()
        new_layer.startEditing()
        
        # Add attributes from the original layer or LADM fields
        new_layer_data.addAttributes(new_layer_fields)
        new_layer.updateFields()

        features = layer.selectedFeatures() if selection_only else layer.getFeatures()

        existing_points = set()
        if ladm_enabled:
            for feat in ladm_layer.getFeatures():
                existing_points.add(feat.geometry().asPoint())

        if dif_capa_ref_enabled:
            ref_layer = self.ladm_layer_combo.currentData()
            reference_points = {feat.geometry().asPoint() for feat in ref_layer.getFeatures()}

        seq_counter = int(start_seq.split('-')[-1]) if ladm_enabled else None

        for feature in features:
            geom = feature.geometry()
            if point_type == "Todos los vertices":
                points = list(geom.vertices())
            elif point_type == "Punto Medio":
                points = [geom.centroid().asPoint()]
            elif point_type == "Vertice inicial":
                points = [next(geom.vertices())]
            elif point_type == "Vertice final":
                points = [list(geom.vertices())[-1]]
            elif point_type == "Vertice inicial y final":
                vertices = list(geom.vertices())
                points = [vertices[0], vertices[-1]]
            elif point_type == "Dangling vertex":
                points = [p for p in geom.vertices() if geom.vertexAt(p) is None]
            else:
                points = []

            for point in points:
                if ladm_enabled and QgsPointXY(point) in existing_points:
                    continue

                if dif_capa_ref_enabled and QgsPointXY(point) in reference_points:
                    continue  # Skip this vertex if it's in the reference layer

                new_feat = QgsFeature()
                new_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(point)))

                if ladm_enabled:
                    id_punto_lindero = f"{start_seq.split('-')[0]}-{seq_counter}"
                    t_ili_tid = str(uuid.uuid4())
                    new_feat.setAttributes([
                        seq_counter, t_ili_tid, id_punto_lindero,
                        puntotipo_value, acuerdo_value, None, 0.5, None, None, metodoproduccion_value, None, None, None, None, 
                        datetime.now().isoformat(), None, None, None
                    ])
                    seq_counter += 1
                else:
                    new_feat.setAttributes(feature.attributes())

                new_layer_data.addFeature(new_feat)
        
        if ladm_enabled:
            # Recalculate local_id field with values from id_punto_lindero
            new_layer.startEditing()
            idx_id_punto_lindero = new_layer.fields().indexFromName("id_punto_lindero")
            idx_local_id = new_layer.fields().indexFromName("local_id")
            for f in new_layer.getFeatures():
                f[idx_local_id] = f[idx_id_punto_lindero]
                new_layer.updateFeature(f)
            new_layer.commitChanges()
        
        new_layer.commitChanges()
        QgsProject.instance().addMapLayer(new_layer)
        self.iface.messageBar().pushMessage("Info", "Vertices a puntos completado satisfactoriamente", level=0)
        self.close()

class FeatureVerticesToPointsPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        self.action = QAction("Feature Vertices to Points", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&FeatureVerticesToPoints", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("&FeatureVerticesToPoints", self.action)

    def run(self):
        dialog = FeatureVerticesToPoints(self.iface)
        dialog.exec_()
