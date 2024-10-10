import psycopg2
import fiona
from pyproj import CRS
from shapely import wkb
from shapely.geometry import mapping, shape, MultiPolygon, Polygon
from datetime import datetime  # Importar la librería datetime
from qgis.core import QgsVectorLayer, QgsProject,QgsFillSymbol, QgsLineSymbolLayer  # Importar clases de QGIS para agregar capas
from PyQt5.QtWidgets import QMessageBox  # Importar QMessageBox para los diálogos
from PyQt5.QtGui import QColor  # Importar para manejo de colores



def export_to_geopackage2(conexion, output_folder, esquema):
    queries = {
        'FORMAL': f"""
            select te.t_id, pd.qr_operacion_definitivo, 
                CASE 
                    WHEN mmtj.naturaleza_predio IN('PRIVADO','privado','Privado') then 'PRIVADO'
                    WHEN mmtj.naturaleza_predio IN ('PUBLICO', 'PÚBLICO', 'Público','Publico') then 'PUBLICO'
                    ELSE 'REVISAR_ERROR'
                end as naturaleza_predio,
                    pd.numero_predial, cpt.ilicode as condicion_predio, ST_AsBinary(ST_SetSRID(te.geometria, 9377)) AS geometria
            from {esquema}.cca_predio pd
            join {esquema}.cca_condicionprediotipo cpt on pd.condicion_predio=cpt.t_id
            join {esquema}.cca_terreno te on pd.terreno = te.t_id
            Join mtj.matriz_mtj mmtj on pd.qr_operacion_definitivo = mmtj.id_operacion
            where cpt.ilicode = 'NPH'
        """,
        'INFORMAL': f"""
            select te.t_id, pd.qr_operacion_definitivo, 
                CASE 
                    WHEN mmtj.naturaleza_predio IN('PRIVADO','privado','Privado') then 'PRIVADO'
                    WHEN mmtj.naturaleza_predio IN ('PUBLICO', 'PÚBLICO', 'Público','Publico') then 'PUBLICO'
                    ELSE CONCAT(mmtj.naturaleza_predio,'_','REVISAR_ERROR')
                end as naturaleza_predio,
                    pd.numero_predial, cpt.ilicode as condicion_predio, ST_AsBinary(ST_SetSRID(te.geometria, 9377)) AS geometria
            from {esquema}.cca_predio pd
            join {esquema}.cca_condicionprediotipo cpt on pd.condicion_predio=cpt.t_id
            join {esquema}.cca_terreno te on pd.terreno = te.t_id
            Join mtj.matriz_mtj mmtj on pd.qr_operacion_definitivo = mmtj.id_operacion
            where cpt.ilicode = 'Informal'
        """,
        'UNIFICADO': f"""
            select te.t_id, pd.qr_operacion_definitivo, 
                CASE 
                    WHEN mmtj.naturaleza_predio IN('PRIVADO','privado','Privado') then 'PRIVADO'
                    WHEN mmtj.naturaleza_predio IN ('PUBLICO', 'PÚBLICO', 'Público','Publico') then 'PUBLICO'
                    ELSE 'REVISAR_ERROR'
                end as naturaleza_predio,
                    pd.numero_predial, cpt.ilicode as condicion_predio, ST_AsBinary(ST_SetSRID(te.geometria, 9377)) AS geometria
            from {esquema}.cca_predio pd
            join {esquema}.cca_condicionprediotipo cpt on pd.condicion_predio=cpt.t_id
            join {esquema}.cca_terreno te on pd.terreno = te.t_id
            Join mtj.matriz_mtj mmtj on pd.qr_operacion_definitivo = mmtj.id_operacion
        """
    }

    cursor = conexion.cursor()

    # Obtener el timestamp actual
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")

    # folder de salida
    output_file = f'{output_folder}/formal_informal_nat_{esquema}_{timestamp}.gpkg'

    formal_has_geometry = False
    informal_has_geometry = False

    # Proceso para FORMAL e INFORMAL
    for key in ['FORMAL', 'INFORMAL']:
        query = queries[key]
        cursor.execute(query)
        records = cursor.fetchall()

        # Filtrar los registros con geometría válida
        records_with_geometry = [
            record for record in records if record[5] is not None
        ]

        # Si no hay registros con geometría, omitir esta capa
        if not records_with_geometry:
            print(f"La consulta {key} no devolvió ningún registro con geometría. La capa no se creará.")
            continue  # Saltar esta capa si no hay geometría

        # Establecer el indicador de geometría
        if key == 'FORMAL':
            formal_has_geometry = True
        elif key == 'INFORMAL':
            informal_has_geometry = True

        # Definir esquema de datos
        schema = {
            'geometry': 'Unknown',  
            'properties': {
                't_id':'int64',
                'cca_predio_qr_operacion_definitivo': 'str',
                'naturaleza_predio': 'str',
                'cca_predio_numero_predial': 'str',
                'condicion_predio': 'str'
            }
        }

        # Crear GPKG y escribir datos
        with fiona.open(output_file, 'w', driver='GPKG', crs=CRS.from_epsg(9377).to_wkt(), schema=schema, layer=key) as layer:
            for record in records_with_geometry:
                try:
                    geom = wkb.loads(bytes(record[5]))  
             
                    if isinstance(geom, (Polygon, MultiPolygon)):
                        layer.write({
                            'geometry': mapping(geom),
                            'properties': {
                                't_id': record[0],
                                'cca_predio_qr_operacion_definitivo': record[1],
                                'naturaleza_predio': record[2],
                                'cca_predio_numero_predial': record[3],
                                'condicion_predio': record[4]
                            }
                        })
                    else:
                        print(f"Omitiendo, geometría inválida {record}")
                except Exception as e:
                    print(f"Error al analizar registro {record}: {e}")
                    continue

    # Verificar si ambas capas (FORMAL e INFORMAL) tienen geometría antes de generar UNIFICADO
    if formal_has_geometry and informal_has_geometry:
        query_unificado = queries['UNIFICADO']
        cursor.execute(query_unificado)
        records_unificado = cursor.fetchall()

        # Filtrar registros con geometría válida para UNIFICADO
        records_with_geometry_unificado = [
            record for record in records_unificado if record[5] is not None
        ]

        if records_with_geometry_unificado:
            # Definir esquema de datos para UNIFICADO
            schema_unificado = {
                'geometry': 'Unknown',  
                'properties': {
                    't_id':'int64',
                    'cca_predio_qr_operacion_definitivo': 'str',
                    'naturaleza_predio': 'str',
                    'cca_predio_numero_predial': 'str',
                    'condicion_predio': 'str'
                }
            }

            # Crear la capa UNIFICADO en el GPKG
            with fiona.open(output_file, 'w', driver='GPKG', crs=CRS.from_epsg(9377).to_wkt(), schema=schema_unificado, layer='UNIFICADO') as layer:
                for record in records_with_geometry_unificado:
                    try:
                        geom = wkb.loads(bytes(record[5]))  
                 
                        if isinstance(geom, (Polygon, MultiPolygon)):
                            layer.write({
                                'geometry': mapping(geom),
                                'properties': {
                                    't_id': record[0],
                                    'cca_predio_qr_operacion_definitivo': record[1],
                                    'naturaleza_predio': record[2],
                                    'cca_predio_numero_predial': record[3],
                                    'condicion_predio': record[4]
                                }
                            })
                        else:
                            print(f"Omitiendo, geometría inválida {record}")
                    except Exception as e:
                        print(f"Error al analizar registro {record}: {e}")
                        continue
        else:
            print("No se generó la capa UNIFICADO porque no hay geometría válida.")
    else:
        print("No se generará la capa UNIFICADO porque FORMAL o INFORMAL no tienen geometría.")

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
    else:
        # Si el usuario selecciona "No", no se realiza ninguna acción adicional
        pass








def agregar_gpkg_a_qgis(gpkg_path):
    # Agregar las capas del GeoPackage a QGIS
    layers = fiona.listlayers(gpkg_path)
    
    for layer_name in layers:
        uri = f"{gpkg_path}|layername={layer_name}"
        vlayer = QgsVectorLayer(uri, layer_name, "ogr")
        
        if not vlayer.isValid():
            print(f"Error al cargar la capa {layer_name} desde {gpkg_path}")
            continue  # Saltar a la siguiente capa si no es válida

        if vlayer.featureCount() == 0:
            print(f"La capa {layer_name} no contiene geometría o registros, no se añadirá a QGIS.")
            continue  # No agregar capas sin geometría o vacías

        # Crear el símbolo de relleno con las propiedades especificadas
        fill_symbol = QgsFillSymbol.createSimple({
            'color': '#72b572',  # Color de relleno
            'outline_color': '#838682',  # Color del borde
            'outline_width': '0.26',  # Ancho del borde en milímetros
        })

        # Configurar opacidad para el relleno y el borde
        fill_symbol.setOpacity(0.5)  # Opacidad del relleno (50%)

        # Cambiar la opacidad del borde
        for layer in fill_symbol.symbolLayers():
            if isinstance(layer, QgsLineSymbolLayer):
                layer.setOpacity(0.5)  # Opacidad del borde (50%)
                layer.setColor(QColor('#838682'))  # Color del borde
                layer.setWidth(0.26)  # Ancho del borde en milímetros

        # Aplicar el estilo a la capa solo si vlayer es válido
        vlayer.renderer().setSymbol(fill_symbol)

        # Añadir la capa al proyecto
        QgsProject.instance().addMapLayer(vlayer)
        print(f"Capa {layer_name} agregada con estilo desde {gpkg_path}")
