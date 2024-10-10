import psycopg2
import fiona
from pyproj import CRS
from shapely import wkb
from shapely.geometry import mapping, MultiPolygon, Polygon
from datetime import datetime
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFillSymbol, QgsLineSymbolLayer, 
    QgsSimpleFillSymbolLayer, QgsWkbTypes
)
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt



def export_to_geopackage3(conexion, output_folder, esquema):
    queries = {
        'UCONS_FORMAL': f"""
            SELECT uc.t_id AS t_id_uc, cpt.ilicode AS condicion_predio, cuc.identificador, 
                   uc.descripcion, cuc.observaciones, uc.planta_ubicacion, 
                   uct.ilicode AS tipo_ucons, ut.ilicode AS uso, pd.qr_operacion_definitivo, 
                   pd.qr_operacion, ST_AsBinary(ST_SetSRID(uc.geometria, 9377)) AS geometria
            FROM {esquema}.cca_caracteristicasunidadconstruccion cuc
            JOIN {esquema}.cca_predio pd ON cuc.predio = pd.t_id
            JOIN {esquema}.cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion = uct.t_id
            JOIN {esquema}.cca_usouconstipo ut ON cuc.uso = ut.t_id
            JOIN {esquema}.cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
            JOIN {esquema}.cca_unidadconstruccion uc ON cuc.t_id = uc.caracteristicasunidadconstruccion
            WHERE cpt.ilicode = 'NPH'
            ORDER BY uc.t_id
        """,
        'UCONS_INFORMAL': f"""
            SELECT uc.t_id AS t_id_uc, cpt.ilicode AS condicion_predio, cuc.identificador, 
                   uc.descripcion, cuc.observaciones, uc.planta_ubicacion, 
                   uct.ilicode AS tipo_ucons, ut.ilicode AS uso, pd.qr_operacion_definitivo, 
                   pd.qr_operacion, ST_AsBinary(ST_SetSRID(uc.geometria, 9377)) AS geometria
            FROM {esquema}.cca_caracteristicasunidadconstruccion cuc
            JOIN {esquema}.cca_predio pd ON cuc.predio = pd.t_id
            JOIN {esquema}.cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion = uct.t_id
            JOIN {esquema}.cca_usouconstipo ut ON cuc.uso = ut.t_id
            JOIN {esquema}.cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
            JOIN {esquema}.cca_unidadconstruccion uc ON cuc.t_id = uc.caracteristicasunidadconstruccion
            WHERE cpt.ilicode = 'Informal'
            ORDER BY uc.t_id
        """,
        'UCONS_UNIFICADO': f"""
            SELECT uc.t_id AS t_id_uc, cpt.ilicode AS condicion_predio, cuc.identificador, 
                   uc.descripcion, cuc.observaciones, uc.planta_ubicacion, 
                   uct.ilicode AS tipo_ucons, ut.ilicode AS uso, pd.qr_operacion_definitivo, 
                   pd.qr_operacion, ST_AsBinary(ST_SetSRID(uc.geometria, 9377)) AS geometria
            FROM {esquema}.cca_caracteristicasunidadconstruccion cuc
            JOIN {esquema}.cca_predio pd ON cuc.predio = pd.t_id
            JOIN {esquema}.cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion = uct.t_id
            JOIN {esquema}.cca_usouconstipo ut ON cuc.uso = ut.t_id
            JOIN {esquema}.cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
            JOIN {esquema}.cca_unidadconstruccion uc ON cuc.t_id = uc.caracteristicasunidadconstruccion
            ORDER BY uc.t_id
        """
    }

    cursor = conexion.cursor()

    # Generar timestamp
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")

    # Definir el archivo de salida
    output_file = f'{output_folder}/UCONS_formal_informal_{esquema}_{timestamp}.gpkg'

    # Verificar si 'UCONS_FORMAL' tiene datos
    cursor.execute(queries['UCONS_FORMAL'])
    formal_records = cursor.fetchall()

    # Verificar si 'UCONS_INFORMAL' tiene datos
    cursor.execute(queries['UCONS_INFORMAL'])
    informal_records = cursor.fetchall()

    if formal_records and informal_records:
        # Si hay datos tanto en 'UCONS_FORMAL' como en 'UCONS_INFORMAL', generar capa unificada
        queries_to_execute = ['UCONS_UNIFICADO']
        print("Se encontraron datos en ambas capas. Se generará la capa unificada.")
    elif formal_records:
        # Si solo hay datos en 'UCONS_FORMAL', generar esa capa
        queries_to_execute = ['UCONS_FORMAL']
        print("Solo se encontraron datos en 'UCONS_FORMAL'.")
    elif informal_records:
        # Si solo hay datos en 'UCONS_INFORMAL', generar esa capa
        queries_to_execute = ['UCONS_INFORMAL']
        print("Solo se encontraron datos en 'UCONS_INFORMAL'.")
    else:
        print("No se encontraron datos en ninguna de las capas.")
        return

    # Crear el GeoPackage
    for key in queries_to_execute:
        query = queries[key]
        cursor.execute(query)
        records = cursor.fetchall()

        # Definir el esquema de datos para el GeoPackage
        schema = {
            'geometry': 'Unknown',
            'properties': {
                't_id_uc': 'int64',
                'condicion_predio': 'str',
                'identificador': 'str',
                'descripcion': 'str',
                'observaciones': 'str',
                'planta_ubicacion': 'str',
                'tipo_ucons': 'str',
                'uso': 'str',
                'qr_operacion_definitivo': 'str',
                'qr_operacion': 'str'
            }
        }

        # Crear el GeoPackage y escribir los datos
        with fiona.open(output_file, 'w', driver='GPKG', crs=CRS.from_epsg(9377).to_wkt(), schema=schema, layer=key) as layer:
            for record in records:
                try:
                    geom = wkb.loads(bytes(record[10]))
                    if isinstance(geom, (Polygon, MultiPolygon)):
                        layer.write({
                            'geometry': mapping(geom),
                            'properties': {
                                't_id_uc': record[0],
                                'condicion_predio': record[1],
                                'identificador': record[2],
                                'descripcion': record[3],
                                'observaciones': record[4],
                                'planta_ubicacion': record[5],
                                'tipo_ucons': record[6],
                                'uso': record[7],
                                'qr_operacion_definitivo': record[8],
                                'qr_operacion': record[9]
                            }
                        })
                    else:
                        print(f"Omitiendo geometría inválida {record}")
                except Exception as e:
                    print(f"Error al analizar registro {record}: {e}")
                    continue

    cursor.close()
    conexion.close()

    # Mensaje indicando que la exportación fue exitosa
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("Exportación completada")
    msg_box.setText(f"Datos exportados correctamente a {output_file}.\n¿Desea agregar las capas a QGIS?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = msg_box.exec_()

    # Si el usuario selecciona "Sí", agregar el GeoPackage a QGIS
    if result == QMessageBox.Yes:
        agregar_gpkg_a_qgis(output_file)





def agregar_gpkg_a_qgis(gpkg_path):
    # Agregar las capas del GeoPackage a QGIS
    layers = fiona.listlayers(gpkg_path)

    for layer_name in layers:
        uri = f"{gpkg_path}|layername={layer_name}"
        vlayer = QgsVectorLayer(uri, layer_name, "ogr")

        if not vlayer.isValid():
            print(f"Error al cargar la capa {layer_name} desde {gpkg_path}")
            QMessageBox.critical(None, "Error", f"Error al cargar la capa {layer_name} desde {gpkg_path}")
            continue  # Si la capa no es válida, pasar a la siguiente

        # Verificar si la capa tiene geometría y si es válida
        if vlayer.geometryType() == QgsWkbTypes.UnknownGeometry:
            print(f"La capa {layer_name} no tiene geometría o tiene geometría desconocida.")
            QMessageBox.warning(None, "Advertencia", f"La capa {layer_name} no tiene geometría o tiene geometría desconocida.")
            continue

        # Crear el símbolo de relleno con las propiedades especificadas
        fill_symbol = QgsFillSymbol.createSimple({
            'color': '#ffa500',  # Color de relleno
            'outline_color': '#db7e4f',  # Color del borde
            'outline_width': '0.3'  # Ancho del borde en milímetros
        })

        # Configurar opacidad y colores
        for layer in fill_symbol.symbolLayers():
            if isinstance(layer, QgsSimpleFillSymbolLayer):  # Ajustar la opacidad del relleno
                layer.setBrushStyle(Qt.SolidPattern)
                layer.setColor(QColor(255, 165, 0, int(255 * 0.5)))  # 50% opacidad para el relleno
            elif isinstance(layer, QgsLineSymbolLayer):  # Ajustar la opacidad del borde
                layer.setColor(QColor(0, 0, 0, int(255 * 0.5)))  # 50% opacidad para el borde

        # Verificar si vlayer tiene un renderer antes de aplicar el símbolo
        if vlayer.renderer() is not None:
            vlayer.renderer().setSymbol(fill_symbol)

        # Añadir la capa al proyecto
        QgsProject.instance().addMapLayer(vlayer)
        print(f"Capa {layer_name} agregada con estilo desde {gpkg_path}")
