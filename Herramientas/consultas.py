from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QInputDialog,QTabWidget, QTextEdit, QMessageBox,QTreeWidget, QTreeWidgetItem,QScrollArea, QVBoxLayout
)
from PyQt5.QtCore import QSettings, Qt, pyqtSignal
import psycopg2
from qgis.core import QgsDataSourceUri,QgsFeature, QgsProject, QgsVectorLayer,QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry,QgsFillSymbol,QgsSimpleFillSymbolLayer,QgsLineSymbolLayer
from qgis.core import QgsField, QgsFields, QgsFeature, QgsGeometry, QgsProject, QgsFillSymbol, QgsVectorLayer, QgsCoordinateReferenceSystem,QgsSimpleFillSymbolLayer
from PyQt5.QtCore import QVariant

from PyQt5.QtWidgets import QMessageBox
from qgis.utils import iface
from qgis.gui import QgsHighlight,QgsMapToolEmitPoint
from PyQt5.QtCore import QTimer  # Importar QTimer para controlar el tiempo del resaltado
from PyQt5.QtGui import QColor  

class ConsultasDockWidget(QDockWidget):
    closed = pyqtSignal() 

    def __init__(self, iface):
        super().__init__("Consultar datos", iface.mainWindow())
        self.iface = iface

        # Crear el widget principal
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Agregar elementos de la interfaz
        layout.addWidget(QLabel("Consultas"))

        # ComboBox para seleccionar el campo de consulta
        layout.addWidget(QLabel("En el campo:"))
        self.campo_combo = QComboBox()
        self.campo_combo.addItems(["QR_Operacion_Definitivo","Número Predial", "FMI"])
        layout.addWidget(self.campo_combo)

        # Entrada para el valor
        layout.addWidget(QLabel("Valor:"))
        self.valor_line = QLineEdit()
        layout.addWidget(self.valor_line)

        # Botón de consulta
        self.consultar_button = QPushButton("Consultar predio")
        layout.addWidget(self.consultar_button)

        self.identificar_button = QPushButton("Identificar espacialmente")
        layout.addWidget(self.identificar_button)
        self.identificar_button.setEnabled(True)  # Habilitar el botón

        # Conectar el botón a la función que habilitará la herramienta de selección
        self.identificar_button.clicked.connect(self.identificar_terreno)


        # Crear el tab widget para mostrar los resultados
        self.tabs = QTabWidget()


        # Crear el QTreeWidget para la pestaña "Básica"
        self.tab_basica = QTreeWidget()
        self.tab_basica.setHeaderHidden(True)  # Ocultar encabezado de las columnas

        # Asegurarte de que el QTreeWidget tiene scrollbars habilitados
        self.tab_basica.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tab_basica.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)


        self.tabs.addTab(self.tab_basica, "Básica")
        layout.addWidget(self.tabs)


        self.tab_juridica = QTreeWidget()
        self.tab_juridica.setHeaderHidden(True)  # Ocultar el encabezado de las columnas
        self.tabs.addTab(self.tab_juridica, "Jurídica")
        layout.addWidget(self.tabs)


        # Botón para hacer zoom al polígono
        self.zoom_button = QPushButton("Zoom To")
        layout.addWidget(self.zoom_button)
        self.zoom_button.setEnabled(False)  # Deshabilitado hasta que se haga la consulta

        # Configurar el widget principal y el layout
        widget.setLayout(layout)
        self.setWidget(widget)

        # Conectar los botones de consulta y zoom con sus funciones
        self.consultar_button.clicked.connect(self.realizar_consulta)
        self.zoom_button.clicked.connect(self.zoom_to_geometry)

        # Agregar el DockWidget a la interfaz de QGIS
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self)

        # Cargar la capa `cca_terreno` al iniciar
        #self.cargar_capa_terreno()
        #self.cargar_unidades_construccion()


    def closeEvent(self, event):
        """
        Emitir la señal 'closed' cuando el DockWidget se cierre.
        """
        self.closed.emit()  # Emitir la señal de cierre
        event.accept()  # Aceptar el evento de cierre





    def configurar_scroll_area(self):
        # Crear un QScrollArea para envolver el QTreeWidget (self.tab_basica)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Permitir que el contenido se ajuste al tamaño del área de scroll

        # Asignar el QTreeWidget como el widget dentro del área de scroll
        scroll_area.setWidget(self.tab_basica)

        # Añadir el scroll area al layout
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)

        # Aplicar el layout al widget principal
        widget = QWidget()
        widget.setLayout(layout)

        # Añadir el widget con scroll al tab "Básica"
        self.tabs.addTab(widget, "Básica")



    def cargar_capa_terreno(self):
        """
        Carga la capa `cca_terreno` en el proyecto QGIS al inicializar el widget.
        """
        settings = QSettings()
        esquema = settings.value("JM_TOOLS/esquema")  # Obtener esquema dinámico
        base_datos = settings.value("JM_TOOLS/base_datos")
        host = settings.value("JM_TOOLS/host", "localhost")
        port = settings.value("JM_TOOLS/port", "5432")
        usuario = settings.value("JM_TOOLS/usuario", "postgres")
        contraseña = settings.value("JM_TOOLS/password", "")

        try:
            # Verificar qué campo geométrico existe: 'geometria', 'geometry' o 'geom'
            geom_column = self.obtener_campo_geom(esquema, base_datos, host, port, usuario, contraseña)

            if geom_column:
                # Crear el URI utilizando QgsDataSourceUri
                uri = QgsDataSourceUri()
                uri.setConnection(host, port, base_datos, usuario, contraseña)
                uri.setDataSource(esquema, "cca_terreno", geom_column, "", "t_id")
                uri.setSrid("9377")  # Especificar el sistema de referencia de coordenadas EPSG:9377

                # Crear la capa con el nombre dinámico basado en el esquema
                vlayer = QgsVectorLayer(uri.uri(), f"{esquema}.cca_terreno", "postgres")

                if not vlayer.isValid():
                    raise Exception(f"La capa no se pudo cargar en QGIS. URI: {uri.uri()}")

                # Establecer el SRID para asegurarse de que QGIS lo reconozca
                crs = QgsCoordinateReferenceSystem(9377)  # EPSG:9377
                vlayer.setCrs(crs)

                # Crear el símbolo de relleno con color y opacidad
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

                # Aplicar el estilo a la capa
                vlayer.renderer().setSymbol(fill_symbol)

                # Añadir la capa al proyecto
                QgsProject.instance().addMapLayer(vlayer)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))





    def obtener_campo_geom(self, esquema, base_datos, host, port, usuario, contraseña):
        """
        Verifica y retorna el campo geométrico ('geometria', 'geometry', o 'geom') en la tabla `cca_terreno`.
        """
        try:
            conexion = psycopg2.connect(
                host=host,
                port=port,
                database=base_datos,
                user=usuario,
                password=contraseña
            )
            cursor = conexion.cursor()

            cursor.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = '{esquema}' AND table_name = 'cca_terreno' AND 
                      (column_name = 'geometria' OR column_name = 'geometry' OR column_name = 'geom');
            """)
            geom_field = cursor.fetchone()

            if geom_field:
                return geom_field[0]  # Retorna el nombre del campo geométrico
            else:
                raise Exception("No se encontró un campo geométrico en la tabla 'cca_terreno'.")

        finally:
            if conexion:
                conexion.close()


    def bold_font(self):
        """
        Devuelve una fuente en negrita.
        """
        font = self.tab_basica.font()
        font.setBold(True)
        return font
    

    def realizar_consulta(self):
        """
        Función que ejecutará las consultas "Básica" y "Jurídica" en la base de datos según el valor ingresado y el campo seleccionado.
        """
        # Recuperar la configuración de la base de datos desde QSettings
        settings = QSettings()
        esquema = settings.value("JM_TOOLS/esquema")
        base_datos = settings.value("JM_TOOLS/base_datos")
        host = settings.value("JM_TOOLS/host", "localhost")
        port = settings.value("JM_TOOLS/port", "5432")
        usuario = settings.value("JM_TOOLS/usuario", "postgres")
        contraseña = settings.value("JM_TOOLS/password", "")

        # Obtener el valor ingresado por el usuario
        valor = self.valor_line.text()

        # Si no se ha ingresado un valor, mostrar un mensaje
        if not valor:
            QMessageBox.warning(self, "Advertencia", "Debe ingresar un valor para realizar la consulta.")
            return

        # Obtener el campo seleccionado del combo box
        campo_seleccionado = self.campo_combo.currentText()

        # Definir el campo para el WHERE según la selección
        if campo_seleccionado == "Número Predial":
            where_clause = f"pd.numero_predial = '{valor}'"
        elif campo_seleccionado == "QR_Operacion_Definitivo":
            where_clause = f"pd.qr_operacion_definitivo = '{valor}'"
        elif campo_seleccionado == "FMI":
            where_clause = f"pd.matricula_inmobiliaria = '{valor}'"
        else:
            QMessageBox.warning(self, "Advertencia", "Campo de consulta no válido.")
            return

        try:
            # Conectarse a la base de datos
            conexion = psycopg2.connect(
                host=host,
                port=port,
                database=base_datos,
                user=usuario,
                password=contraseña
            )
            cursor = conexion.cursor()

            # Ejecutar la consulta SQL
            sql_query = f"""
                SELECT ter.t_id,ROUND((ST_Area(ST_Transform(ter.geometria, 9377))::numeric), 2) as area_terreno,pd.qr_operacion_definitivo, pd.numero_predial, 
                    ST_AsBinary(ST_Transform(ter.geometria, 9377)) AS geometria,pd.t_id as pdtid,extdir.nombre_predio,pd.departamento,pd.municipio,  pd.uit ,                  
				CASE
					WHEN drtp.ilicode='Dominio' then 'Formal'
					else 'Informal' end as tipo_predio, destinatipo.ilicode as destinacion_economica, metodo.ilicode as metodo_intervencion,
				restp.ilicode as resultado_visita, TO_CHAR(pd.fecha_visita_predial,'DD/MM/YYYY') AS fecha_visita_predial,sext.ilicode as jefatura, pd.historia_predio,pd.observaciones, pd.qr_operacion

                FROM {esquema}.cca_predio pd
                JOIN {esquema}.cca_terreno ter ON pd.terreno = ter.t_id
                left join  {esquema}.cca_extdireccion extdir on pd.t_id=extdir.cca_predio_direccion
				JOIN {esquema}.cca_derecho der on pd.t_id=der.predio
				join {esquema}.cca_derechotipo drtp on der.tipo=drtp.t_id

				left join {esquema}.cca_destinacioneconomicatipo destinatipo on pd.destinacion_economica=destinatipo.t_id
				left join {esquema}.cca_condicionprediotipo cpt on pd.condicion_predio = cpt.t_id
				left join {esquema}.cca_resultadovisitatipo restp on pd.resultado_visita =restp.t_id
				left join {esquema}.cca_metodointervenciontipo metodo on pd.metodointervencion=metodo.t_id
				left join {esquema}.cca_sexotipo sext on pd.jefatura=sext.t_id

                WHERE {where_clause};
            """
            cursor.execute(sql_query)
            resultados = cursor.fetchone()

            # Si no hay resultados, mostrar un mensaje
            if not resultados:
                self.tab_basica.clear()
                QMessageBox.warning(self, "Advertencia", "No se encontraron resultados.")
                self.zoom_button.setEnabled(False)  # Deshabilitar el botón si no hay resultados
                return

            # Guardar los resultados de la consulta
            self.resultados = {
                't_id': resultados[0],
                'area_terreno': resultados[1],
                'qr_operacion_definitivo': resultados[2],
                'numero_predial': resultados[3],
                'geometria': resultados[4].hex() if resultados[4] else None,
                'pdtid': resultados[5],
                'nombre_predio': resultados[6],
                'departamento': resultados[7],
                'municipio': resultados[8],
                'uit': resultados[9],
                'tipo_predio': resultados[10],
                'destinacion_economica': resultados[11],
                'metodo_intervencion': resultados[12],
                'resultado_visita': resultados[13],
                'fecha_visita_predial': resultados[14],
                'jefatura': resultados[15],
                'historia_predio': resultados[16],
                'observaciones': resultados[17],
                'qr_operacion': resultados[18]


            }

            # Obtener el área en m² desde los resultados
            area_m2 = float(self.resultados['area_terreno'])  # Asegúrate de convertir a float si no lo es

            # Calcular el área en hectáreas
            area_ha = area_m2 / 10000

            # Calcular el área en formato combinado (Ha + m²)
            ha_completas = int(area_ha)  # Hectáreas completas
            m2_restantes = area_m2 % 10000  # Restante en metros cuadrados


            # Limpiar el árbol antes de agregar los nuevos resultados
            self.tab_basica.clear()

            # Crear el nodo raíz "Terreno"
            terreno_item = QTreeWidgetItem(self.tab_basica, ["Terreno"])

            # Crear el elemento t_id en negrita
            t_id_item = QTreeWidgetItem(terreno_item, [f"t_id: {self.resultados['t_id']}"])
            t_id_item.setFont(0, self.bold_font())  # Aplica negrita al texto de t_id

            QTreeWidgetItem(t_id_item, [f"Área terreno m²: {self.resultados['area_terreno']}"])
            # Mostrar el área en hectáreas
            QTreeWidgetItem(t_id_item, [f"Área terreno ha: {area_ha:.2f} ha"])
            # Mostrar el área en formato "ha + m²"
            QTreeWidgetItem(t_id_item, [f"Área terreno: {ha_completas} ha + {m2_restantes:.2f} m²"])

            # Crear el sub-elemento "Predio" bajo t_id
            predio_item = QTreeWidgetItem(t_id_item, ["Predio"])

            # Crear el elemento t_id en negrita
            pdt_id_item = QTreeWidgetItem(predio_item, [f"t_id: {self.resultados['pdtid']}"])
            pdt_id_item.setFont(0, self.bold_font())  # Aplica negrita al texto de t_id

            # Agregar los elementos de qr_operacion_definitivo y numero_predial bajo t_id
            QTreeWidgetItem(pdt_id_item, [f"Nombre Predio: {self.resultados['nombre_predio']}"])
            QTreeWidgetItem(pdt_id_item, [f"Departamento: {self.resultados['departamento']}"])
            QTreeWidgetItem(pdt_id_item, [f"Municipio: {self.resultados['municipio']}"])
            QTreeWidgetItem(pdt_id_item, [f"UIT: {self.resultados['uit']}"])
            QTreeWidgetItem(pdt_id_item, [f"QR Operación o Matriz: {self.resultados['qr_operacion']}"])
            QTreeWidgetItem(pdt_id_item, [f"QR Operación Definitivo: {self.resultados['qr_operacion_definitivo']}"])
            QTreeWidgetItem(pdt_id_item, [f"Número Predial: {self.resultados['numero_predial']}"])
            QTreeWidgetItem(pdt_id_item, [f"Tipo de Predio: {self.resultados['tipo_predio']}"])

            # Crear el sub-elemento "Caracterización"
            caracterizacion_item = QTreeWidgetItem(t_id_item, ["Caracterización"])
            QTreeWidgetItem(caracterizacion_item, [f"Resultado de Visita: {self.resultados['resultado_visita']}"])
            QTreeWidgetItem(caracterizacion_item, [f"Fecha de Visita Predial: {self.resultados['fecha_visita_predial']}"])
            QTreeWidgetItem(caracterizacion_item, [f"Destinación Económica: {self.resultados['destinacion_economica']}"])
            QTreeWidgetItem(caracterizacion_item, [f"Jefe de Hogar: {self.resultados['jefatura']}"])

            # Añadir un QTextEdit para "Historia del Predio"
            historia_text_edit = QTextEdit()
            historia_text_edit.setReadOnly(True)
            historia_text_edit.setText(f"Historia del Predio: {self.resultados['historia_predio']}")
            historia_text_edit.setMinimumHeight(20)  # Ajustar el alto mínimo
            self.tab_basica.setItemWidget(QTreeWidgetItem(caracterizacion_item, []), 0, historia_text_edit)

            # Añadir un QTextEdit para "Observaciones"
            observaciones_text_edit = QTextEdit()
            observaciones_text_edit.setReadOnly(True)
            observaciones_text_edit.setText(f"Observaciones: {self.resultados['observaciones']}")
            observaciones_text_edit.setMinimumHeight(20)  # Ajustar el alto mínimo
            self.tab_basica.setItemWidget(QTreeWidgetItem(caracterizacion_item, []), 0, observaciones_text_edit)

            pdt_id_item.setExpanded(True)
            predio_item.setExpanded(True)



            # -------------------------------------
            # Ejecutar la consulta SQL para contar las construcciones
            sql_construcciones = f"""
                SELECT COUNT(cuc.t_id)
                FROM {esquema}.cca_predio pd
                JOIN {esquema}.cca_caracteristicasunidadconstruccion cuc ON pd.t_id = cuc.predio
                WHERE {where_clause};
            """
 
            cursor.execute(sql_construcciones)

            resultado2 = cursor.fetchone()  # Guardar el resultado de la segunda consulta

            # Asumimos que el resultado de la segunda consulta es un conteo de construcciones
            if resultado2:
                num_construcciones = resultado2[0]
            else:
                num_construcciones = 0

            # Crear el nodo "Construcciones" con el número de construcciones entre paréntesis
            ucons_item = QTreeWidgetItem(t_id_item, [f"Construcciones ({num_construcciones})"])


            # -------------------------------------
            # Nueva consulta para obtener los detalles de cada construcción
            sql_detalles_construccion = f"""
                select pd.qr_operacion_definitivo, uc.t_id, uc.planta_ubicacion,cuc.identificador,ST_AsBinary(ST_Transform(uc.geometria, 9377)) AS geometria,
                ROUND((ST_Area(ST_Transform(uc.geometria, 9377))::numeric), 2) as area_uconstruccion,
                uct.ilicode as tipo_ucons, usotp.ilicode as uso, estado.ilicode as conservacion_tipologia,
                planta.ilicode as tipo_planta, uc.altura     


                from {esquema}.cca_predio pd
                join {esquema}.cca_caracteristicasunidadconstruccion cuc on pd.t_id=cuc.predio
                join {esquema}.cca_unidadconstruccion uc on cuc.t_id= uc.caracteristicasunidadconstruccion
                left join {esquema}.cca_unidadconstrucciontipo uct on cuc.tipo_unidad_construccion=uct.t_id
                left join {esquema}.cca_usouconstipo usotp on cuc.uso=usotp.t_id
                left join {esquema}.cca_estadoconservaciontipo estado on cuc.conservacion_tipologia=estado.t_id
                left join {esquema}.cca_construccionplantatipo planta on uc.tipo_planta =planta.t_id
                WHERE {where_clause};
            """




            cursor.execute(sql_detalles_construccion)
            detalles_construcciones = cursor.fetchall()  # Esta consulta obtiene varias construcciones

            # Crear subnodos para cada construcción bajo el nodo "Construcciones"
            for detalle in detalles_construcciones:
                # Información de la construcción
                t_iducons = detalle[1]  # ID de la unidad de construcción
                planta_ubicacion = detalle[2]  # Planta de la unidad
                identificador = detalle[3]
                area_uconstruccion = detalle[5]
                tipo_ucons = detalle[6]
                uso = detalle[7]
                conservacion_tipologia = detalle[8]
                tipo_planta = detalle[9]
                altura = detalle[10]  

                # Crear un nodo para cada construcción (t_iducons)
                construccion_item = QTreeWidgetItem(ucons_item, [f"Id: {identificador}"])
                construccion_item.setFont(0, self.bold_font())  # Aplica negrita al texto de t_id

                # Crear subnodos con los detalles de la construcción bajo cada t_id de la construcción
                QTreeWidgetItem(construccion_item, [f"t_id: {t_iducons}"])
                QTreeWidgetItem(construccion_item, [f"Área construida: {area_uconstruccion} m²"])
                QTreeWidgetItem(construccion_item, [f"Tipo Unidad: {tipo_ucons}"])
                QTreeWidgetItem(construccion_item, [f"Uso: {uso}"])
                QTreeWidgetItem(construccion_item, [f"Tipología Conservación': {conservacion_tipologia}"])
                QTreeWidgetItem(construccion_item, [f"Planta ubicación: {planta_ubicacion}"])
                QTreeWidgetItem(construccion_item, [f"Tipo Planta: {tipo_planta}"])
                QTreeWidgetItem(construccion_item, [f"Altura: {altura}"])








            # Definir qué elementos están expandidos o colapsados
            terreno_item.setExpanded(True)  # Expande el nodo "Terreno"
            t_id_item.setExpanded(True)      # Expande el nodo "t_id"
            predio_item.setExpanded(False)   # Mantén el nodo "Predio" colapsado
            ucons_item.setExpanded(False)


            # Habilitar el botón de "Zoom To" si la geometría está disponible
            if self.resultados['geometria']:
                self.zoom_button.setEnabled(True)  # Habilitar el botón si se encontró geometría
            else:
                self.zoom_button.setEnabled(False)  # Deshabilitar el botón si no hay geometría




            # -------------------------------------
            # Consulta para la pestaña "Jurídica"
            # -------------------------------------
           

            sql_query_juridica = f"""
            SELECT pd.t_id, pd.qr_operacion, pd.qr_operacion_definitivo, der.t_id, drtp.ilicode as tipo_derecho, 
            TO_CHAR(der.fecha_inicio_tenencia,'DD/MM/YYYY') as fecha_inicio_tenencia, der.observacion, pd.codigo_orip,pd.matricula_inmobiliaria,
            fadt.ilicode as tipo_fuente_administrativa, fad.numero_fuente, TO_CHAR(fad.fecha_documento_fuente,'DD/MM/YYYY'), fad.ente_emisor, fad.observacion as obs2
            FROM {esquema}.cca_predio pd 
            JOIN {esquema}.cca_derecho der ON pd.t_id=der.predio
            LEFT JOIN {esquema}.cca_derechotipo drtp ON der.tipo=drtp.t_id
			LEFt join {esquema}.cca_fuenteadministrativa fad on der.t_id=fad.derecho
			left join {esquema}.cca_fuenteadministrativatipo fadt on fad.tipo=fadt.t_id
            WHERE {where_clause};
            """

            cursor.execute(sql_query_juridica)
            resultados_juridica = cursor.fetchall()

            if resultados_juridica:
                resultado = resultados_juridica[0]  # Asumiendo que sólo te interesa la primera fila

                self.resultadojuridico = {
                    'predio_t_id': resultado[0],
                    'qr_operacion': resultado[1],
                    'qr_operacion_definitivo': resultado[2],
                    'derecho_t_id': resultado[3],
                    'tipo_derecho': resultado[4],
                    'fecha_inicio_tenencia': resultado[5],
                    'observacion': resultado[6],
                    'codigo_orip': resultado[7],
                    'matricula_inmobiliaria': resultado[8]

                }

                # Limpiar el árbol antes de agregar los nuevos resultados
                self.tab_juridica.clear()

                # Crear el nodo raíz "Predio"
                predio_item2 = QTreeWidgetItem(self.tab_juridica, ["Predio"])

                # Añadir el t_id del predio en negrita
                t_id_item2 = QTreeWidgetItem(predio_item2, [f"t_id: {self.resultadojuridico['predio_t_id']}"])
                t_id_item2.setFont(0, self.bold_font())  # Aplica negrita al texto de t_id

                # Añadir qr_operacion y qr_operacion_definitivo bajo t_id
                QTreeWidgetItem(t_id_item2, [f"QR Operación: {self.resultadojuridico['qr_operacion']}"])
                QTreeWidgetItem(t_id_item2, [f"QR Operación Definitivo: {self.resultadojuridico['qr_operacion_definitivo']}"])

                # Crear el nodo "Derecho" bajo "Predio"
                derecho_item = QTreeWidgetItem(predio_item2, ["Derecho"])

                # Añadir el t_id del derecho en negrita
                derecho_t_id_item = QTreeWidgetItem(derecho_item, [f"t_id: {self.resultadojuridico['derecho_t_id']}"])
                derecho_t_id_item.setFont(0, self.bold_font())  # Aplica negrita al texto de t_id del derecho

                # Añadir tipo_derecho, fecha_inicio_tenencia y observacion bajo el t_id del derecho
                QTreeWidgetItem(derecho_t_id_item, [f"Tipo Derecho: {self.resultadojuridico['tipo_derecho']}"])
                QTreeWidgetItem(derecho_t_id_item, [f"Código ORIP: {self.resultadojuridico['codigo_orip']}"])
                QTreeWidgetItem(derecho_t_id_item, [f"Número Matrícula: {self.resultadojuridico['matricula_inmobiliaria']}"])
                QTreeWidgetItem(derecho_t_id_item, [f"Fecha de Inicio de Tenencia: {self.resultadojuridico['fecha_inicio_tenencia']}"])


                # Añadir un QTextEdit para "Observaciones"
                observaciones_text_edit1 = QTextEdit()
                observaciones_text_edit1.setReadOnly(True)
                observaciones_text_edit1.setText(f"Observaciones: {self.resultadojuridico['observacion']}")
                observaciones_text_edit1.setMinimumHeight(20)  # Ajustar el alto mínimo
                self.tab_juridica.setItemWidget(QTreeWidgetItem(derecho_t_id_item, []), 0, observaciones_text_edit1)


                # Expandir el nodo principal para que se vea inmediatamente
                t_id_item2.setExpanded(True)
                derecho_item.setExpanded(True)

                   # Crear el nodo "Fuente Administrativa" bajo "Derecho"
                fuente_administrativa_item = QTreeWidgetItem(derecho_item, ["Fuente Administrativa"])


                # Iterar sobre los resultados para las fuentes administrativas
                for resultado in resultados_juridica:
                    tipo_fuente = resultado[9]  # tipo_fuente_administrativa
                    numero_fuente = resultado[10]  # Número de la fuente
                    fecha_documento = resultado[11]  # Fecha del documento fuente
                    ente_emisor = resultado[12]  # Ente emisor
                    obs_fuente = resultado[13]  # Observaciones

                    if tipo_fuente:  # Solo mostrar si hay un tipo de fuente
                        # Crear un subnodo para cada fuente administrativa con el tipo como título
                        tipo_fuente_item = QTreeWidgetItem(fuente_administrativa_item, [f"{tipo_fuente}"])
                        tipo_fuente_item.setFont(0, self.bold_font())  # Aplicar negrita al título del tipo de fuente

                        # Añadir los detalles bajo el tipo de fuente
                        QTreeWidgetItem(tipo_fuente_item, [f"Número Fuente: {numero_fuente}"])
                        QTreeWidgetItem(tipo_fuente_item, [f"Fecha Documento Fuente: {fecha_documento}"])
                        QTreeWidgetItem(tipo_fuente_item, [f"Ente Emisor: {ente_emisor}"])

                        # Añadir un QTextEdit para las observaciones de la fuente administrativa
                        obs_fuente_text_edit = QTextEdit()
                        obs_fuente_text_edit.setReadOnly(True)
                        obs_fuente_text_edit.setText(f"Observaciones: {obs_fuente}")
                        obs_fuente_text_edit.setMinimumHeight(20)  # Ajustar el alto mínimo
                        self.tab_juridica.setItemWidget(QTreeWidgetItem(tipo_fuente_item, []), 0, obs_fuente_text_edit)




                # Ejecutar la consulta para obtener los resultados de la familia predial
                sql_familia_predial = f"""
                    SELECT 
                        pd.qr_operacion_definitivo AS "QR DERIVADO CONSULTADO",
                        pd.qr_operacion AS "QR MATRIZ O QR CONTENEDOR",
                        sub.qr_operacion_definitivo AS "QR FAMILIA PREDIAL",
                        ter.t_id AS "T_ID TERRENO",
                        ROUND((ST_Area(ST_Transform(ter.geometria, 9377))::numeric), 2) AS "ÁREA TERRENO",
                        CASE
                            WHEN drtp.ilicode = 'Dominio' THEN 'Formal Contenedor'
                            ELSE ''
                        END AS tipo_predio
                    FROM {esquema}.cca_predio pd
                    JOIN {esquema}.cca_predio sub ON sub.qr_operacion = pd.qr_operacion
                    JOIN {esquema}.cca_terreno ter ON sub.terreno = ter.t_id
                    JOIN {esquema}.cca_derecho der ON sub.t_id = der.predio  -- Relación corregida con la tabla de derechos
                    LEFT JOIN {esquema}.cca_derechotipo drtp ON der.tipo = drtp.t_id
                    WHERE {where_clause};
                """
                cursor.execute(sql_familia_predial)
                familia_predial_resultados = cursor.fetchall() 


                # Crear el nodo "Familia Predial" bajo "Predio"
                familia_predial_item = QTreeWidgetItem(predio_item, ["Familia Predial del QR contenedor/Matriz"])

            # Iterar sobre los resultados de la familia predial
            for resultado in familia_predial_resultados:
                qr_familia = resultado[2]  # QR de la familia predial
                t_id_terreno = resultado[3]  # T_ID del terreno
                area_terreno = resultado[4]  # Área del terreno
                tipo_predio = resultado[5]  # Tipo de predio ('Formal' o 'Informal')

                # Crear un subnodo para cada miembro de la familia predial con el tipo de predio
                familia_item = QTreeWidgetItem(familia_predial_item, [f"QR {tipo_predio}: {qr_familia}"])
                #familia_item = QTreeWidgetItem(familia_predial_item, [f"QR: {qr_familia} ({tipo_predio})"])

                # Agregar subnodos con los detalles del terreno
                QTreeWidgetItem(familia_item, [f"T_ID Terreno: {t_id_terreno}"])
                QTreeWidgetItem(familia_item, [f"Área Terreno: {area_terreno} m²"])

            predio_item2.setExpanded(True)




            # Ejecutar la nueva consulta para obtener las áreas formales e informales
            sql_area_remanente = f"""
                SELECT
                    pd.qr_operacion_definitivo AS "QR DERIVADO CONSULTADO",
                    pd.qr_operacion AS "QR MATRIZ O QR CONTENEDOR",
                    ter.t_id AS "T_ID TERRENO",
                    ROUND(ST_Area(ST_Transform(ter.geometria, 9377))::numeric, 2) AS "AREA TERRENO",
                    CASE
                        WHEN drtp.ilicode = 'Dominio' THEN 'Formal'
                        ELSE 'Informal'
                    END AS "TIPO_PREDIO"
                FROM {esquema}.cca_predio pd
                JOIN {esquema}.cca_predio sub ON sub.qr_operacion = pd.qr_operacion
                JOIN {esquema}.cca_terreno ter ON sub.terreno = ter.t_id
                JOIN {esquema}.cca_derecho der ON sub.t_id = der.predio
                LEFT JOIN {esquema}.cca_derechotipo drtp ON der.tipo = drtp.t_id
                WHERE {where_clause};
            """


            # Ejecutar la nueva consulta para obtener las áreas formales e informales
            cursor.execute(sql_area_remanente)
            area_resultados = cursor.fetchall()

            # Variables para almacenar el área total de Informales y el área del Formal
            area_formal = 0
            area_informal_total = 0

            # Crear el nodo "Área Remanente" bajo "Predio"
            area_remanente_item = QTreeWidgetItem(predio_item, ["Área Remanente"])

            # Iterar sobre los resultados para clasificar las áreas formales e informales
            for resultado in area_resultados:
                qr_derivado = resultado[0]  # QR derivado consultado
                t_id_terreno = resultado[2]  # T_ID del terreno
                area_terreno = float(resultado[3])  # Área del terreno
                tipo_predio = resultado[4]  # Tipo de predio (Formal o Informal)

                # Agregar cada terreno a la lista correspondiente
                if tipo_predio == "Formal":
                    area_formal = area_terreno  # Guardar el área del terreno formal
                else:
                    area_informal_total += area_terreno  # Sumar las áreas de los terrenos informales

            # Crear un nodo para mostrar solo el área del Formal
            area_formal_item = QTreeWidgetItem(area_remanente_item, [f"Área del Formal: {area_formal:.2f} m²"])
            area_formal_item.setFont(0, self.bold_font())  # Negrilla para el área del formal

            # Crear un nodo para mostrar la sumatoria de las áreas informales
            area_informales_item = QTreeWidgetItem(area_remanente_item, [f"Sumatoria de Áreas Informales: {area_informal_total:.2f} m²"])

            # Calcular el área remanente (área formal - sumatoria de áreas informales)
            area_remanente = area_formal - area_informal_total

            # Crear un nodo para mostrar el área remanente
            area_remanente_final_item = QTreeWidgetItem(area_remanente_item, [f"Área Remanente: {area_remanente:.2f} m²"])
            area_remanente_final_item.setFont(0, self.bold_font())  # Negrilla para el área remanente

            # Expander el nodo principal para que se vea inmediatamente
            area_remanente_item.setExpanded(False)





            sql_query_interesados = f"""
                SELECT pd.t_id, pd.qr_operacion, pd.qr_operacion_definitivo, der.t_id, drtp.ilicode as tipo_derecho,
                intertp.ilicode as tipo_interesado, interdmt.ilicode as tipo_documento, inter.documento_identidad, 
                CASE 
                    WHEN interdmt.ilicode='NIT' THEN inter.razon_social
                    ELSE CONCAT(inter.primer_nombre,' ',inter.segundo_nombre,' ',inter.primer_apellido,' ',inter.segundo_apellido) 
                END as nombre_interesado,
                sex.ilicode as sexo, ec.ilicode as estado_civil, 
                CASE
                    WHEN inter.reside_predio = TRUE THEN 'SI'
                    WHEN inter.reside_predio = FALSE THEN 'NO'
                    ELSE 'SIN DILIGENCIAR' 
                END as interesado_reside_predio,
                CASE
                    WHEN inter.acepta_ospr = TRUE THEN 'SI'
                    WHEN inter.acepta_ospr = FALSE THEN 'NO'
                    ELSE 'SIN DILIGENCIAR' 
                END as acepta_ospr,
                CASE
                    WHEN inter.interesado_victima_conflicto = TRUE THEN 'SI'
                    WHEN inter.interesado_victima_conflicto = FALSE THEN 'NO'
                    ELSE 'SIN DILIGENCIAR' 
                END as victima_conflicto   
                FROM {esquema}.cca_predio pd 
                JOIN {esquema}.cca_derecho der ON pd.t_id = der.predio
                LEFT JOIN {esquema}.cca_derechotipo drtp ON der.tipo = drtp.t_id
                JOIN {esquema}.cca_interesado inter ON der.t_id = inter.derecho
                LEFT JOIN {esquema}.cca_interesadotipo intertp ON inter.tipo = intertp.t_id
                LEFT JOIN {esquema}.cca_interesadodocumentotipo interdmt ON inter.tipo_documento = interdmt.t_id
                LEFT JOIN {esquema}.cca_sexotipo sex ON inter.sexo = sex.t_id
                LEFT JOIN {esquema}.cca_estadociviltipo ec ON inter.estado_civil = ec.t_id
                WHERE {where_clause};
            """

            cursor.execute(sql_query_interesados)
            interesados_resultados = cursor.fetchall()

            # Verificar si se encontraron interesados
            if interesados_resultados:
                # Contar el número de interesados
                total_interesados = len(interesados_resultados)

                # Crear el nodo "Interesados" bajo "Predio" y mostrar el total
                interesados_item = QTreeWidgetItem(derecho_item, [f"Interesados ({total_interesados})"])

                # Iterar sobre los interesados y crear subnodos
                for interesado in interesados_resultados:
                    tipo_interesado = interesado[5]  # Tipo de interesado
                    tipo_documento = interesado[6]  # Tipo de documento
                    documento_identidad = interesado[7]  # Documento de identidad
                    nombre_interesado = interesado[8]  # Nombre del interesado
                    sexo = interesado[9]  # Sexo
                    estado_civil = interesado[10]  # Estado civil
                    reside_predio = interesado[11]  # Reside en el predio
                    acepta_ospr = interesado[12]  # Acepta OSPR
                    victima_conflicto = interesado[13]  # Víctima del conflicto

                    # Crear un nodo para cada interesado con su nombre en el título
                    interesado_item = QTreeWidgetItem(interesados_item, [f"{nombre_interesado}"])

                    # Agregar subnodos con la información del interesado
                    QTreeWidgetItem(interesado_item, [f"Tipo de Interesado: {tipo_interesado}"])
                    QTreeWidgetItem(interesado_item, [f"Tipo de Documento: {tipo_documento}"])
                    QTreeWidgetItem(interesado_item, [f"Documento de Identidad: {documento_identidad}"])
                    QTreeWidgetItem(interesado_item, [f"Sexo: {sexo}"])
                    QTreeWidgetItem(interesado_item, [f"Estado Civil: {estado_civil}"])
                    QTreeWidgetItem(interesado_item, [f"Reside en el Predio: {reside_predio}"])
                    QTreeWidgetItem(interesado_item, [f"Acepta OSPR: {acepta_ospr}"])
                    QTreeWidgetItem(interesado_item, [f"Víctima del Conflicto: {victima_conflicto}"])








        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", f"Error al ejecutar la consulta: {e}")



    def zoom_to_geometry(self):
        try:
            esquema = QSettings().value("JM_TOOLS/esquema")  # Obtener el esquema dinámico

            # Verificar si hay resultados y si la geometría está presente
            if self.resultados and self.resultados.get('geometria'):
                wkb_geometry = self.resultados['geometria']

                # Validar la geometría antes de procesar
                if not wkb_geometry:
                    raise ValueError("La geometría está vacía o no es válida.")
                
                # Convertir WKB a binario y luego crear la geometría usando QgsGeometry.fromWkb
                geometry = QgsGeometry()
                geometry.fromWkb(bytes.fromhex(wkb_geometry))

                if geometry and not geometry.isEmpty():
                    # Crear un bounding box de la geometría y hacer zoom
                    canvas = self.iface.mapCanvas()
                    extent = geometry.boundingBox()
                    canvas.setExtent(extent)
                    canvas.refresh()

                    # Seleccionar la geometría en la capa
                    capas = QgsProject.instance().mapLayersByName(f"{esquema}.cca_terreno")
                    if not capas:
                        raise ValueError(f"No se pudo encontrar la capa '{esquema}.cca_terreno'.")

                    layer = capas[0]  # Obtener la capa

                    # Limpiar la selección anterior
                    layer.removeSelection()

                    # Seleccionar el predio basado en la geometría
                    feature_ids = []
                    for feature in layer.getFeatures():
                        if feature.geometry().equals(geometry):
                            feature_ids.append(feature.id())

                    if feature_ids:
                        layer.selectByIds(feature_ids)

                        # Resaltar la geometría con QgsHighlight
                        highlight = QgsHighlight(canvas, geometry, layer)
                        highlight.setColor(QColor(255, 0, 0))  # Resaltar en rojo
                        highlight.setWidth(2)  # Ajustar el ancho del borde

                        # Mantener el resaltado durante 2 segundos y luego deshabilitarlo
                        QTimer.singleShot(2000, highlight.hide)

                        # Refrescar el canvas para que la selección sea visible
                        canvas.refresh()
                else:
                    raise ValueError("No se encontró una geometría válida para el valor proporcionado.")
            else:
                raise ValueError("No se encontró geometría para el valor proporcionado.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al intentar realizar el zoom: {e}")






    def identificar_terreno(self):
        """
        Habilitar la herramienta de selección de QGIS para seleccionar un terreno y obtener el t_id.
        """
        try:
            # Obtener la capa de terreno
            esquema = QSettings().value("JM_TOOLS/esquema")
            vlayer = QgsProject.instance().mapLayersByName(f"{esquema}.cca_terreno")

            # Crear la herramienta de selección de QGIS
            self.selection_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
            self.selection_tool.canvasClicked.connect(self.on_terreno_seleccionado)

            # Habilitar la herramienta de selección
            self.iface.mapCanvas().setMapTool(self.selection_tool)

            QMessageBox.information(self, "Identificar Terreno", "Selecciona un predio en el mapa.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al intentar habilitar la selección: {e}")







    def on_terreno_seleccionado(self, point):
        """
        Método que se ejecuta cuando se selecciona un predio en el mapa.
        Obtiene todas las características en la ubicación seleccionada y permite al usuario elegir una.
        """
        try:
            # Obtener el esquema de los settings
            esquema = QSettings().value("JM_TOOLS/esquema")

            # Obtener la capa de terreno usando el esquema
            vlayer = QgsProject.instance().mapLayersByName(f"{esquema}.cca_terreno")[0]

            # Asegurarse de que el punto esté en el mismo CRS que la capa
            crs_layer = vlayer.crs()
            crs_canvas = self.iface.mapCanvas().mapSettings().destinationCrs()
            if crs_canvas != crs_layer:
                transform = QgsCoordinateTransform(crs_canvas, crs_layer, QgsProject.instance())
                point = transform.transform(point)

            # Convertir el punto a una geometría con un pequeño buffer para asegurar la selección
            point_geom = QgsGeometry.fromPointXY(point).buffer(1, 5)

            # Crear una lista de las características que intersectan con el punto seleccionado
            selected_features = []
            for feature in vlayer.getFeatures():
                if feature.geometry().intersects(point_geom):
                    selected_features.append(feature)

            if not selected_features:
                QMessageBox.warning(self, "Advertencia", "No se seleccionó ningún terreno.")
                return

            # Crear una lista de opciones para el usuario, mostrando el t_id, el qr_operacion_definitivo y el tipo_predio
            opciones = []
            for feature in selected_features:
                t_id = feature['t_id']
                qr_operacion_definitivo, tipo_predio = self.obtener_qr_operacion_definitivo(t_id)
                opciones.append(f"t_id: {t_id}, QR: {qr_operacion_definitivo}, Tipo: {tipo_predio}")

            # Mostrar un cuadro de diálogo para que el usuario elija el polígono que desea identificar
            opcion_seleccionada, ok = QInputDialog.getItem(self, "Seleccionar Terreno", "Selecciona el terreno que deseas consultar:", opciones, 0, False)

            if ok and opcion_seleccionada:
                # Obtener el t_id del polígono seleccionado
                t_id_seleccionado = int(opcion_seleccionada.split(",")[0].split(":")[1].strip())

                # Colocar el qr_operacion_definitivo en el campo de búsqueda
                qr_operacion_definitivo_seleccionado, _ = self.obtener_qr_operacion_definitivo(t_id_seleccionado)
                self.valor_line.setText(qr_operacion_definitivo_seleccionado)

                # Ejecutar la consulta como si el usuario hubiera ingresado ese valor manualmente
                self.realizar_consulta()

            # Desactivar la herramienta de selección después de usarla
            self.iface.mapCanvas().unsetMapTool(self.selection_tool)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al identificar el terreno: {e}")




    def obtener_qr_operacion_definitivo(self, t_id):
        """
        Realiza una consulta SQL para obtener el qr_operacion_definitivo y tipo_predio basado en el t_id del terreno.
        """
        try:
            settings = QSettings()
            esquema = settings.value("JM_TOOLS/esquema")  # Esquema dinámico
            base_datos = settings.value("JM_TOOLS/base_datos")
            host = settings.value("JM_TOOLS/host", "localhost")
            port = settings.value("JM_TOOLS/port", "5432")
            usuario = settings.value("JM_TOOLS/usuario", "postgres")
            contraseña = settings.value("JM_TOOLS/password", "")

            with psycopg2.connect(host=host, port=port, database=base_datos, user=usuario, password=contraseña) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT pd.qr_operacion_definitivo,
                        CASE WHEN drtp.ilicode = 'Dominio' THEN 'Formal' ELSE 'Informal' END as tipo_predio
                    FROM {esquema}.cca_predio pd
                    JOIN {esquema}.cca_terreno ter ON pd.terreno = ter.t_id
                    JOIN {esquema}.cca_derecho der ON pd.t_id = der.predio
                    LEFT JOIN {esquema}.cca_derechotipo drtp ON der.tipo = drtp.t_id
                    WHERE ter.t_id = %s;
                """, (t_id,))

                resultado = cursor.fetchone()

                if resultado:
                    qr_operacion_definitivo, tipo_predio = resultado
                    return qr_operacion_definitivo, tipo_predio
                else:
                    return "No disponible", "No disponible"

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener qr_operacion_definitivo y tipo_predio: {e}")
            return "Error", "Error"






    def cargar_unidades_construccion(self):
        """
        Carga las geometrías de las unidades de construcción junto con los atributos correspondientes.
        """
        try:
            settings = QSettings()
            esquema = settings.value("JM_TOOLS/esquema")
            base_datos = settings.value("JM_TOOLS/base_datos")
            host = settings.value("JM_TOOLS/host", "localhost")
            port = settings.value("JM_TOOLS/port", "5432")
            usuario = settings.value("JM_TOOLS/usuario", "postgres")
            contraseña = settings.value("JM_TOOLS/password", "")

            # Realizar la consulta SQL para obtener las geometrías y atributos de las unidades de construcción
            with psycopg2.connect(host=host, port=port, database=base_datos, user=usuario, password=contraseña) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT pd.qr_operacion_definitivo, uc.t_id, uc.planta_ubicacion, cuc.identificador, 
                        ST_AsBinary(ST_Transform(uc.geometria, 9377)) AS geometria
                    FROM {esquema}.cca_predio pd
                    JOIN {esquema}.cca_caracteristicasunidadconstruccion cuc ON pd.t_id = cuc.predio
                    JOIN {esquema}.cca_unidadconstruccion uc ON cuc.t_id = uc.caracteristicasunidadconstruccion;
                """)

                resultados = cursor.fetchall()

            if not resultados:
                QMessageBox.warning(self, "Advertencia", "No se encontraron unidades de construcción.")
                return

            # Crear una nueva capa de tipo memoria para almacenar las geometrías de las unidades de construcción
            campos = QgsFields()
            campos.append(QgsField("qr_operacion_definitivo", QVariant.String))
            campos.append(QgsField("t_id", QVariant.Int))
            campos.append(QgsField("planta_ubicacion", QVariant.String))
            campos.append(QgsField("identificador", QVariant.String))

            # Crear la capa de tipo polígono (o multipolígono dependiendo de la geometría de las unidades)
            crs = QgsCoordinateReferenceSystem(9377)  # EPSG:9377
            capa_unidades = QgsVectorLayer("Polygon?crs=EPSG:9377", "Unidades de Construcción", "memory")
            capa_unidades.dataProvider().addAttributes(campos)
            capa_unidades.updateFields()

            # Agregar las geometrías a la capa
            for resultado in resultados:
                qr_operacion_definitivo = resultado[0]
                t_id = resultado[1]
                planta_ubicacion = resultado[2]
                identificador = resultado[3]
                geometria_wkb = resultado[4]

                # Crear una nueva característica (feature)
                feature = QgsFeature()
                feature.setFields(capa_unidades.fields())

                # Configurar los atributos
                feature.setAttribute("qr_operacion_definitivo", qr_operacion_definitivo)
                feature.setAttribute("t_id", t_id)
                feature.setAttribute("planta_ubicacion", planta_ubicacion)
                feature.setAttribute("identificador", identificador)

                # Establecer la geometría a partir del WKB
                geometry = QgsGeometry()
                geometry.fromWkb(bytes(geometria_wkb))
                feature.setGeometry(geometry)

                # Añadir la característica a la capa
                capa_unidades.dataProvider().addFeature(feature)

            # Actualizar la capa para reflejar los cambios
            capa_unidades.updateExtents()


            # Crear el símbolo de relleno
            fill_symbol = QgsFillSymbol.createSimple({
                'color': '#ffa500',  # Color de relleno
                'outline_color': '#db7e4f',  # Color del borde
                'outline_width': '0.3'  # Ancho del borde en milímetros
            })

            # Configurar la opacidad del relleno y el borde de manera independiente
            for layer in fill_symbol.symbolLayers():
                if isinstance(layer, QgsSimpleFillSymbolLayer):  # Ajustar la opacidad del relleno
                    layer.setBrushStyle(Qt.SolidPattern)
                    layer.setColor(QColor(255, 165, 0, int(255 * 0.5)))  # 50% opacidad para el relleno
                elif isinstance(layer, QgsLineSymbolLayer):  # Ajustar la opacidad del borde
                    layer.setColor(QColor(0, 0, 0, int(255 * 0.5)))  # 50% opacidad para el borde

            # Aplicar el símbolo a la capa
            capa_unidades.renderer().setSymbol(fill_symbol)

            # Añadir la capa al proyecto de QGIS
            QgsProject.instance().addMapLayer(capa_unidades)

            # Añadir la capa al proyecto de QGIS
            QgsProject.instance().addMapLayer(capa_unidades)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar unidades de construcción: {e}")




 