import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
from qgis.gui import QgsProjectionSelectionWidget
from qgis.core import QgsProject, QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer, QgsField
from qgis.PyQt.QtCore import QVariant

class XY(QDialog):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.setWindowTitle("Go To XY")
        
        self.layout = QVBoxLayout()

        # Widget de selección de CRS
        self.crs_label = QLabel("Input CRS:")
        self.layout.addWidget(self.crs_label)
        self.crs_input = QgsProjectionSelectionWidget()
        self.layout.addWidget(self.crs_input)
        
        self.x_label = QLabel("Enter X Coordinate:")
        self.layout.addWidget(self.x_label)
        self.x_input = QLineEdit()
        self.layout.addWidget(self.x_input)
        
        self.y_label = QLabel("Enter Y Coordinate:")
        self.layout.addWidget(self.y_label)
        self.y_input = QLineEdit()
        self.layout.addWidget(self.y_input)
        
        self.create_marker_checkbox = QCheckBox("Create point marker")
        self.layout.addWidget(self.create_marker_checkbox)
        
        self.go_button = QPushButton("Go To XY")
        self.layout.addWidget(self.go_button)
        self.go_button.clicked.connect(self.create_point)
        
        self.setLayout(self.layout)
        
    def create_point(self):
        try:
            crs = self.crs_input.crs()
            epsg_code = crs.authid()
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            
            point = QgsPointXY(x, y)
            
            if self.create_marker_checkbox.isChecked():
                self.add_point_marker(point, crs)
            
            QMessageBox.information(self, "Point Created", f"Point created at ({point.x()}, {point.y()}) in CRS {epsg_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_point_marker(self, point, crs):
        # Crear una capa temporal de puntos si no existe
        layer_name = "Temporary Points Layer"
        layer = QgsProject.instance().mapLayersByName(layer_name)
        if not layer:
            vl = QgsVectorLayer(f"Point?crs={crs.authid()}", layer_name, "memory")
            pr = vl.dataProvider()
            pr.addAttributes([QgsField("name", QVariant.String)])
            vl.updateFields()
            QgsProject.instance().addMapLayer(vl)
        else:
            vl = layer[0]
            pr = vl.dataProvider()

        # Asegurar que la capa tiene el CRS correcto
        vl.setCrs(crs)

        # Obtener el número secuencial del punto
        num_points = vl.featureCount() + 1
        point_name = f"Punto {num_points} ({point.x()}, {point.y()})"
        
        # Crear una característica con el punto
        feat = QgsFeature(vl.fields())
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        feat.setAttribute("name", point_name)
        
        # Añadir la característica a la capa y actualizar la extensión
        pr.addFeatures([feat])
        vl.updateExtents()
        vl.triggerRepaint()

class XYPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        
    def run(self):
        dialog = XY(self.iface)
        dialog.exec_()

# Aquí no se necesita simulación de FakeIface, ya que se ejecutará dentro de QGIS
