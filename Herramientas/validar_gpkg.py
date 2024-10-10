import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QProgressBar, QComboBox, QFileDialog, QTextEdit, QLineEdit
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from qgis.core import QgsProject, QgsVectorLayer
import xlsxwriter
from unidecode import unidecode
from PyQt5.QtCore import QDate, QDateTime,Qt
from datetime import datetime, timedelta

class validar_gpkg(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Validar Datos GPKG")
        self.resize(700, 600)

        # Layout principal
        layout = QVBoxLayout()

        # ComboBox para seleccionar la capa
        self.layer_combo = QComboBox()
        layout.addWidget(QLabel("Seleccionar capa para validar:"))
        layout.addWidget(self.layer_combo)

        # Campo para seleccionar la ruta de guardado del archivo Excel
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Ruta de guardado del reporte...")
        layout.addWidget(self.path_input)

        # Botón para seleccionar la ruta de guardado
        self.browse_button = QPushButton("Explorar")
        layout.addWidget(self.browse_button)

        # Botón para validar
        self.validate_button = QPushButton("Validar")
        layout.addWidget(self.validate_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Cuadro de texto para mostrar el progreso de la validación
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        # Label para mostrar el mensaje final con el enlace
        self.result_label = QLabel("")
        self.result_label.setOpenExternalLinks(True)  # Permitir enlaces clicables
        layout.addWidget(self.result_label)


        # Conectar eventos a funciones
        self.browse_button.clicked.connect(self.select_save_path)
        self.validate_button.clicked.connect(self.run_validation)

        # Cargar capas cargadas en QGIS
        self.load_layers()

        self.setLayout(layout)


    def show_success_message(self, save_path):
        """Mostrar un mensaje de éxito con un enlace clicable a la ruta del archivo."""
        message = f"Validación realizada y reporte guardado en: <a href=\"file:///{save_path}\">{save_path}</a>"
        self.result_label.setText(message)

    def load_layers(self):
        """Cargar las capas vectoriales de QGIS en el comboBox."""
        self.layer_combo.clear()
        layers = [layer for layer in QgsProject.instance().mapLayers().values() if isinstance(layer, QgsVectorLayer)]
        for layer in layers:
            self.layer_combo.addItem(layer.name())

    def select_save_path(self):
        """Abrir un diálogo para seleccionar la ruta de guardado del archivo Excel."""
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar reporte de validación", "", "Excel Files (*.xlsx)")
        if save_path:
            self.path_input.setText(save_path)

    def run_validation(self):
        """Función principal para ejecutar la validación y generar el reporte en Excel."""
        selected_layer_name = self.layer_combo.currentText()
        layers = QgsProject.instance().mapLayersByName(selected_layer_name)
        if not layers:
            self.iface.messageBar().pushWarning("Advertencia", "No se encontró la capa seleccionada.")
            return

        layer = layers[0]  # Obtener la capa seleccionada

        save_path = self.path_input.text()
        if not save_path:
            self.iface.messageBar().pushWarning("Advertencia", "Por favor selecciona la ruta de guardado del archivo.")
            return

        # Configurar Excel
        try:
            workbook = xlsxwriter.Workbook(save_path)
        except Exception as e:
            self.iface.messageBar().pushWarning("Error", f"No se pudo crear el archivo Excel: {str(e)}")
            return

        worksheet = workbook.add_worksheet()

        # Escribir los encabezados
        headers = ["QR", "QR_CONTENEDOR", "DTO", "MUNI", "UIT", "TIPO_DERECHO", "FORMAL_INFORMAL", "NATURALEZA","COD_DANE",
                   "F_LEV", "F_REPOR", "AREA_M2", "AREA_HA","OBS", "VALIDACION_DERECHO_TIPO", "VALIDACION_COINCIDENCIA_QRs",
                   "VALIDACION_NATURALEZA", "VALIDACION_NATURALEZA_FAMILIA"]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Barra de progreso
        self.progress_bar.setMaximum(layer.featureCount())

        row = 1
        qr_contenedor_groups = {}
        for i, feature in enumerate(layer.getFeatures()):
            tipo_derecho = unidecode(str(feature["TIPO_DERECHO"]).strip().lower()) if feature["TIPO_DERECHO"] else ""
            formal_informal = unidecode(str(feature["FORMAL_INFORMAL"]).strip().lower()) if feature["FORMAL_INFORMAL"] else ""
            naturaleza = unidecode(str(feature["NATURALEZA"]).strip().lower()) if feature["NATURALEZA"] else ""

           
            validation_result = ""
            error_list = []

            # Validación NATURALEZA
            if not naturaleza and not tipo_derecho:
                error_list.append('FALTA DILIGENCIAR NATURALEZA Y TIPO_DERECHO')
            elif not naturaleza:
                error_list.append('FALTA DILIGENCIAR NATURALEZA')
            elif not tipo_derecho:
                error_list.append('FALTA DILIGENCIAR TIPO_DERECHO')

            if naturaleza == "privado" and tipo_derecho not in ["posesion", "dominio"]:
                error_list.append('ERROR: PRIVADO SOLO PERMITE POSESION O DOMINIO')
            elif naturaleza == "publico" and tipo_derecho not in ["ocupacion", "dominio"]:
                error_list.append('ERROR: PUBLICO SOLO PERMITE OCUPACION O DOMINIO')

            naturaleza_result = "; ".join(error_list) if error_list else "OK"


             # Validación de TIPO_DERECHO y FORMAL_INFORMAL

            # Regla 1: Si TIPO_DERECHO es 'dominio' y FORMAL_INFORMAL es 'informal'
            if tipo_derecho in ['dominio'] and formal_informal in ['informal']:
                validation_result = 'ERROR, UN DOMINIO NO PUEDE SER INFORMAL'
            
            # Regla 2: Si TIPO_DERECHO es posesión u ocupación y FORMAL_INFORMAL es 'formal'
            elif tipo_derecho in ['ocupacion', 'posesion'] and formal_informal in ['formal', 'bien_uso_publico', 
                    'formal ospr', 'formal_ospr', 'formal_con_remanente', 'formal_remanente', 'formal_sin_remanente']:
                validation_result = 'ERROR, POSESION/OCUPACION NO PUEDE SER FORMAL'
            
            # Regla 3: Si TIPO_DERECHO está vacío o nulo
            elif not tipo_derecho or tipo_derecho == 0 or tipo_derecho.strip() == "":
                validation_result = 'FALTA DILIGENCIAR TIPO_DERECHO'
            
            # Regla 4: Si FORMAL_INFORMAL está vacío o nulo
            elif not formal_informal or formal_informal == 0 or formal_informal.strip() == "":
                validation_result = 'FALTA DILIGENCIAR FORMAL_INFORMAL (CONDICION DEL PREDIO)'
            
            # Regla 5: Si TIPO_DERECHO es posesión u ocupación e INFORMAL está bien
            elif tipo_derecho in ['ocupacion', 'posesion'] and formal_informal in ['informal']:
                validation_result = 'OK_INFORMAL'
            
            # Regla 6: Si TIPO_DERECHO es dominio y FORMAL está bien
            elif tipo_derecho in ['dominio'] and formal_informal in ['formal', 'bien_uso_publico', 'formal ospr', 
                    'formal_con_remanente', 'formal_remanente', 'formal_sin_remanente']:
                validation_result = 'OK_FORMAL'
            
            # Si ninguna regla aplica
            else:
                validation_result = 'VERIFICAR MANUALMENTE QUE PASA'

            # Validación de coincidencia de QR y QR_CONTENEDOR
            qr = feature["QR"]
            qr_contenedor = feature["QR_CONTENEDOR"]
            coincidencia_qr_result = ""

            if qr == qr_contenedor:
                coincidencia_qr_result = 'DEBERÍA SER FORMAL'
            elif qr != qr_contenedor:
                coincidencia_qr_result = 'DEBERÍA SER INFORMAL'
            elif qr is None:
                coincidencia_qr_result = 'FALTA QR'
            elif qr_contenedor is None or qr_contenedor == 0:
                coincidencia_qr_result = 'FALTA QR MATRIZ'

            # Agrupar los QR asociados a cada QR_CONTENEDOR para la validación de familia predial
            if qr_contenedor:
                qr_contenedor_groups.setdefault(str(qr_contenedor), []).append((row, tipo_derecho, naturaleza))

            # Convertir el valor de F_LEV a formato dd/mm/yyyy
            f_lev = self.format_date(feature["F_LEV"])

            # Convertir el valor de F_REPOR a formato dd/mm/yyyy
            f_repor = self.format_date(feature["F_REPOR"])

            # Calcular el área en hectáreas (dividir AREA_M2 por 10,000) y redondear a 2 decimales
            area_m2 = float(feature["AREA_M2"]) if feature["AREA_M2"] else 0
            area_ha = round(area_m2 / 10000, 4)

            # Escribir los resultados en el archivo Excel y manejar valores nulos
            worksheet.write(row, 0, self.safe_write(feature["QR"]))
            worksheet.write(row, 1, self.safe_write(feature["QR_CONTENEDOR"]))
            worksheet.write(row, 2, self.safe_write(feature["DTO"]))
            worksheet.write(row, 3, self.safe_write(feature["MUNI"]))
            worksheet.write(row, 4, self.safe_write(feature["UIT"]))
            worksheet.write(row, 5, self.safe_write(tipo_derecho))
            worksheet.write(row, 6, self.safe_write(formal_informal))
            worksheet.write(row, 7, self.safe_write(feature["NATURALEZA"]))
            worksheet.write(row, 8, self.safe_write(feature["COD_DANE"]))
            worksheet.write(row, 9, self.safe_write(f_lev))
            worksheet.write(row, 10, self.safe_write(f_repor)) 
            worksheet.write(row, 11, self.safe_write(feature["AREA_M2"]))
            worksheet.write(row, 12, self.safe_write(area_ha))
            worksheet.write(row, 13, self.safe_write(feature["OBS"]))
            worksheet.write(row, 14, validation_result)
            worksheet.write(row, 15, coincidencia_qr_result)
            worksheet.write(row, 16, naturaleza_result) 

            # Actualizar el cuadro de progreso y el log
            self.progress_bar.setValue(i + 1)
            validation_details = "; ".join([validation_result, coincidencia_qr_result, naturaleza_result])
            self.log_text.append(f"Validando QR: {feature['QR']} -> {validation_details}")

            row += 1

        # Validación de la familia predial


        # Validación de la familia predial
        for qr_cont, groups in qr_contenedor_groups.items():
            tipo_derecho_naturaleza_set = set((tipo_derecho, naturaleza) for _, tipo_derecho, naturaleza in groups)
            # Estandarizar `QR` y `QR_CONTENEDOR` a texto sin espacios antes de la comparación
            qr_cont = str(qr_cont).strip()
            
            # Identificar si hay un QR que es matriz real (cuando QR y QR_CONTENEDOR son iguales y el tipo de derecho es dominio)
            matriz_dominio = next(
                (g for g in groups if str(layer.getFeature(g[0])["QR"]).strip() == qr_cont and g[1].lower() == "dominio"),
                None
            )
            
            # Variable para el resultado final y los detalles del análisis
            naturaleza_familia_result = "OK"
            detalles = []

            # 1. Si existe un QR MATRIZ REAL
            if matriz_dominio:
                # Extraer los detalles del QR matriz
                qr_matriz = str(layer.getFeature(matriz_dominio[0])["QR"]).strip()  # Asegurarnos de usar el valor correcto de QR MATRIZ
                tipo_derecho_matriz = matriz_dominio[1]
                naturaleza_matriz = matriz_dominio[2]
                
                # Si solo hay un QR matriz y ningún derivado, es "OK"
                if len(groups) == 1:
                    naturaleza_familia_result = "OK_FORMAL_UNICO"
                else:
                    # Verificar si todos los derivados tienen naturaleza vacía o nula
                    todas_naturalezas_vacias = all(
                        not nat for row, _, nat in groups if str(layer.getFeature(row)["QR"]).strip() != qr_matriz
                    )

                    if todas_naturalezas_vacias:
                        # Verificar el tipo de derecho de los QR derivados
                        tipos_derivados = set(tipo for _, tipo, _ in groups if tipo in ["posesion", "ocupacion"])

                        if "posesion" in tipos_derivados and "ocupacion" not in tipos_derivados:
                            naturaleza_familia_result = (
                                "FALTA DILIGENCIAR NATURALEZA (PPRIV): Todos los QR derivados asociados al QR_CONTENEDOR {} no tienen naturaleza diligenciada y son de tipo posesión.".format(qr_cont)
                            )
                        elif "ocupacion" in tipos_derivados and "posesion" not in tipos_derivados:
                            naturaleza_familia_result = (
                                "FALTA DILIGENCIAR NATURALEZA (PPUB): Todos los QR derivados asociados al QR_CONTENEDOR {} no tienen naturaleza diligenciada y son de tipo ocupación.".format(qr_cont)
                            )
                        else:
                            naturaleza_familia_result = (
                                "FALTA DILIGENCIAR NATURALEZA: Todos los QR derivados asociados al QR_CONTENEDOR {} no tienen naturaleza diligenciada.".format(qr_cont)
                            )
                    else:

                        # Verificar si hay diferencias de naturaleza
                        inconsistencias_naturaleza = []
                        verificar_segregado_dominio = False
                        qr_derivados_con_dominio = []

                        for row, tipo, nat in groups:
                            qr_derivado = str(layer.getFeature(row)["QR"]).strip()
                            descripcion_qr = "QR {} está como {}".format(qr_derivado, tipo)
                            
                            if not nat:
                                descripcion_qr += " y falta diligenciar la naturaleza"
                            else:
                                descripcion_qr += " y naturaleza {}".format(nat)

                            # Verificar diferencias de naturaleza con el QR matriz
                            if nat != naturaleza_matriz:
                                inconsistencias_naturaleza.append(descripcion_qr)
                            
                            # Verificar si hay otro dominio entre los derivados
                            if tipo == "dominio" and qr_derivado != qr_matriz:
                                verificar_segregado_dominio = True
                                qr_derivados_con_dominio.append(qr_derivado)

                        # Generar los mensajes de inconsistencias según los casos encontrados
                        if inconsistencias_naturaleza:
                            naturaleza_familia_result = (
                                "INCONSISTENCIA NATURALEZA MATRIZ/DERIVADOS: El QR MATRIZ {} ({}) tiene derivados con naturalezas diferentes. Detalles: {}".format(
                                    qr_matriz, naturaleza_matriz if naturaleza_matriz else "sin naturaleza", ", ".join(inconsistencias_naturaleza)
                                )
                            )
                        elif verificar_segregado_dominio:
                            naturaleza_familia_result = (
                                "VERIFICAR MATRIZ/SEGREGADO DOMINIO: Se ha encontrado un QR matriz {} con dominio, "
                                "pero también otros registros con derecho de dominio bajo el mismo QR_CONTENEDOR {}. "
                                "Los QR derivados con dominio son: {}".format(
                                    qr_matriz, qr_cont, ", ".join(qr_derivados_con_dominio)
                                )
                            )

            # 2. Si no existe un QR MATRIZ REAL
            else:
                # Verificar si hay un dominio entre los derivados
                existe_dominio = any(tipo == "dominio" for _, tipo, _ in groups)
                
                if existe_dominio:
                    detalles.append(
                        "SIN REGISTRO DOMINIO, POSIBLE EXISTENCIA DERIVADO: Se han encontrado registros con derecho de dominio bajo el QR_CONTENEDOR {} sin un QR matriz formal. Detalles: {}".format(
                            qr_cont, ", ".join(["QR {} está como {}".format(layer.getFeature(row)["QR"], tipo) for row, tipo, _ in groups])
                        )
                    )
                
                # Verificar si hay inconsistencias entre los derivados
                elif len(tipo_derecho_naturaleza_set) > 1:
                    detalles.append(
                        "INCONSISTENCIA FAMILIA: Los QR asociados al QR_CONTENEDOR {} tienen diferentes valores. Detalles: {}".format(
                            qr_cont, ", ".join(["QR {} está como {}".format(layer.getFeature(row)["QR"], tipo) for row, tipo, _ in groups])
                        )
                    )
            
            # 3. Construir el mensaje final
            if detalles:
                naturaleza_familia_result = "; ".join(detalles)

                # Agregar el resultado de la validación al log_text
                self.log_text.append(f"Validación de QR_CONTENEDOR {qr_cont}: {naturaleza_familia_result}")
            # Escribir el resultado en la columna correspondiente
            for row_idx, _, _ in groups:
                worksheet.write(row_idx, 17, naturaleza_familia_result)







        # Guardar y cerrar el archivo Excel
        workbook.close()

        # Mostrar mensaje de éxito con la ruta clicable
        self.show_success_message(save_path)




    def format_date(self, date_value):
        """Función para formatear la fecha en formato dd/mm/yyyy."""
        try:
            if isinstance(date_value, QDate):
                return date_value.toString('dd/MM/yyyy')
            elif isinstance(date_value, QDateTime):
                return date_value.date().toString('dd/MM/yyyy')
            elif isinstance(date_value, str):
                return datetime.strptime(date_value.strip(), '%Y-%m-%d').strftime('%d/%m/%Y')
            elif isinstance(date_value, (int, float)):
                origin = datetime(1900, 1, 1)
                return (origin + timedelta(days=int(date_value))).strftime('%d/%m/%Y')
        except Exception:
            return date_value

    def safe_write(self, value):
        """Función para evitar errores al escribir valores no válidos en Excel."""
        if value is None or str(value).strip() == "":
            return ""
        return str(value)
