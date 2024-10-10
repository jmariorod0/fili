import os
import pandas as pd
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QProgressBar, QFileDialog, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

class r1r2(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Procesar Archivos R1 y R2")
        self.setMinimumSize(600, 400)

        # Variables para almacenar rutas
        self.ruta_r1 = ""
        self.ruta_r2 = ""
        self.carpeta_salida = ""

        # Layout principal
        layout = QVBoxLayout()

        # Selección del archivo R1
        r1_layout = QHBoxLayout()
        r1_label = QLabel("Archivo R1:")
        self.ruta_r1_entry = QLineEdit()
        boton_r1 = QPushButton("Seleccionar")
        boton_r1.clicked.connect(self.seleccionar_r1)
        r1_layout.addWidget(r1_label)
        r1_layout.addWidget(self.ruta_r1_entry)
        r1_layout.addWidget(boton_r1)
        layout.addLayout(r1_layout)

        # Selección del archivo R2
        r2_layout = QHBoxLayout()
        r2_label = QLabel("Archivo R2:")
        self.ruta_r2_entry = QLineEdit()
        boton_r2 = QPushButton("Seleccionar")
        boton_r2.clicked.connect(self.seleccionar_r2)
        r2_layout.addWidget(r2_label)
        r2_layout.addWidget(self.ruta_r2_entry)
        r2_layout.addWidget(boton_r2)
        layout.addLayout(r2_layout)

        # Selección de la carpeta de salida
        carpeta_salida_layout = QHBoxLayout()
        carpeta_salida_label = QLabel("Carpeta de salida:")
        self.carpeta_salida_entry = QLineEdit()
        boton_carpeta_salida = QPushButton("Seleccionar")
        boton_carpeta_salida.clicked.connect(self.seleccionar_carpeta_salida)
        carpeta_salida_layout.addWidget(carpeta_salida_label)
        carpeta_salida_layout.addWidget(self.carpeta_salida_entry)
        carpeta_salida_layout.addWidget(boton_carpeta_salida)
        layout.addLayout(carpeta_salida_layout)

        # Botón para procesar los archivos
        boton_procesar = QPushButton("Procesar")
        boton_procesar.clicked.connect(self.procesar_archivos)
        layout.addWidget(boton_procesar)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Aplicar el layout
        self.setLayout(layout)

    # Función para seleccionar el archivo R1
    def seleccionar_r1(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo R1", "", "Archivos de texto (*.txt *.lst)")
        if ruta:
            self.ruta_r1_entry.setText(ruta)
            self.ruta_r1 = ruta

    # Función para seleccionar el archivo R2
    def seleccionar_r2(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo R2", "", "Archivos de texto (*.txt *.lst)")
        if ruta:
            self.ruta_r2_entry.setText(ruta)
            self.ruta_r2 = ruta

    # Función para seleccionar la carpeta de salida
    def seleccionar_carpeta_salida(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_salida_entry.setText(carpeta)
            self.carpeta_salida = carpeta

    # Función para procesar los archivos
    def procesar_archivos(self):
        try:
            if not self.ruta_r1.endswith(('.txt', '.TXT', '.lst')) or not self.ruta_r2.endswith(('.txt', '.TXT', '.lst')):
                QMessageBox.critical(self, "Error", "Solo se permiten archivos de entrada con extensión .txt o .lst")
                return

            # Actualizar barra de progreso
            self.progress_bar.setValue(10)

            # Procesar archivo R1
            df_r1 = procesar_r1(self.ruta_r1)
            self.progress_bar.setValue(30)

            # Procesar archivo R2
            df_r2 = procesar_r2(self.ruta_r2)
            self.progress_bar.setValue(60)

            # Guardar en un único archivo Excel con dos pestañas
            ruta_salida_excel = os.path.join(self.carpeta_salida, 'R1R2.xlsx')
            with pd.ExcelWriter(ruta_salida_excel, engine='openpyxl') as writer:
                df_r1.to_excel(writer, sheet_name='R1', index=False)
                df_r2.to_excel(writer, sheet_name='R2', index=False)

            # Actualizar barra de progreso
            self.progress_bar.setValue(100)

            # Mensaje de éxito con enlace clicable
            mensaje = (f"<p>Archivo procesado correctamente: "
                    f"<a href='file:///{ruta_salida_excel}'>{ruta_salida_excel}</a></p>")
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Éxito")
            msg_box.setTextFormat(Qt.RichText)
            msg_box.setText(mensaje)
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # Conectar la acción para abrir el archivo cuando se haga clic en el enlace
            msg_box.buttonClicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(ruta_salida_excel)))

            msg_box.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}")


# Funciones de procesamiento (sin modificar la lógica)

def procesar_r1(ruta_txt):
    departamento_list = []
    municipio_list = []
    numero_del_predio_list = []
    tipo_del_registro_list = []
    numero_de_orden_list = []
    total_registros_list = []
    nombre_list = []
    estado_civil_list = []
    tipo_documento_list = []
    numero_documento_list = []
    direccion_list = []
    comuna_list = []
    destino_economico_list = []
    area_terreno_list = []
    area_construida_list = []
    avaluo_list = []
    vigencia_list = []
    numero_predial_anterior_list = []

    with open(ruta_txt, 'r', encoding='latin-1') as file:
        for line in file:
            departamento = line[0:2].strip()
            municipio = line[2:5].strip()
            numero_del_predio = line[5:30].strip()
            tipo_del_registro = line[30:31].strip()
            numero_de_orden = line[31:34].strip()
            total_registros = line[34:37].strip()
            nombre = line[37:137].strip()
            estado_civil = line[137:138].strip()
            tipo_documento = line[138:139].strip()
            numero_documento = line[139:151].strip()
            direccion = line[151:251].strip()
            comuna = line[251:252].strip()
            destino_economico = line[252:253].strip()
            area_terreno = line[253:268].strip()
            area_construida = line[268:274].strip()
            avaluo = line[274:289].strip()
            vigencia = line[289:297].strip()
            numero_predial_anterior = line[297:312].strip()

            departamento_list.append(departamento)
            municipio_list.append(municipio)
            numero_del_predio_list.append(numero_del_predio)
            tipo_del_registro_list.append(tipo_del_registro)
            numero_de_orden_list.append(numero_de_orden)
            total_registros_list.append(total_registros)
            nombre_list.append(nombre)
            estado_civil_list.append(estado_civil)
            tipo_documento_list.append(tipo_documento)
            numero_documento_list.append(numero_documento)
            direccion_list.append(direccion)
            comuna_list.append(comuna)
            destino_economico_list.append(destino_economico)
            area_terreno_list.append(area_terreno)
            area_construida_list.append(area_construida)
            avaluo_list.append(avaluo)
            vigencia_list.append(vigencia)
            numero_predial_anterior_list.append(numero_predial_anterior)

    df_r1 = pd.DataFrame({
        'DEPARTAMENTO': departamento_list,
        'MUNICIPIO': municipio_list,
        'NUMERO_DEL_PREDIO': numero_del_predio_list,
        'TIPO_DEL_REGISTRO': tipo_del_registro_list,
        'NUMERO_DE_ORDEN': numero_de_orden_list,
        'TOTAL_REGISTROS': total_registros_list,
        'NOMBRE': nombre_list,
        'ESTADO_CIVIL': estado_civil_list,
        'TIPO_DOCUMENTO': tipo_documento_list,
        'NUMERO_DOCUMENTO': numero_documento_list,
        'DIRECCION': direccion_list,
        'COMUNA': comuna_list,
        'DESTINO_ECONOMICO': destino_economico_list,
        'AREA_TERRENO': area_terreno_list,
        'AREA_CONSTRUIDA': area_construida_list,
        'AVALUO': avaluo_list,
        'VIGENCIA': vigencia_list,
        'NUMERO_PREDIAL_ANTERIOR': numero_predial_anterior_list
    })

    df_r1['NUMERO_PREDIAL'] = df_r1['DEPARTAMENTO'] + df_r1['MUNICIPIO'] + df_r1['NUMERO_DEL_PREDIO']
    df_r1['NUMERO_PREDIAL_ANTERIOR'] = df_r1['DEPARTAMENTO'] + df_r1['MUNICIPIO'] + df_r1['NUMERO_PREDIAL_ANTERIOR']

    return df_r1


# Función para procesar el archivo R2 y devolver el DataFrame
def procesar_r2(ruta_txt):
    departamento_list = []
    municipio_list = []
    numero_del_predio_list = []
    tipo_de_registro_list = []
    numero_de_orden_list = []
    total_registros_list = []
    matricula_inmobiliaria_list = []
    espacio_1_list = []
    zona_fisica_1_list = []
    zona_economica_1_list = []
    area_terreno_1_list = []
    espacio_2_list = []
    zona_fisica_2_list = []
    zona_economica_2_list = []
    area_terreno_2_list = []
    espacio_3_list = []
    habitaciones_1_list = []
    banos_1_list = []
    locales_1_list = []
    pisos_1_list = []
    estrato_1_list = []
    uso_1_list = []
    puntaje_1_list = []
    area_construida_1_list = []
    espacio_4_list = []
    habitaciones_2_list = []
    banos_2_list = []
    locales_2_list = []
    pisos_2_list = []
    estrato_2_list = []
    uso_2_list = []
    puntaje_2_list = []
    area_construida_2_list = []
    espacio_5_list = []
    habitaciones_3_list = []
    banos_3_list = []
    locales_3_list = []
    pisos_3_list = []
    estrato_3_list = []
    uso_3_list = []
    puntaje_3_list = []
    area_construida_3_list = []
    espacio_6_list = []
    vigencia_list = []
    numero_predial_anterior_list = []

    with open(ruta_txt, 'r', encoding='latin-1') as file:
        for line in file:
            departamento = line[0:2].strip()
            municipio = line[2:5].strip()
            numero_del_predio = line[5:30].strip()
            tipo_de_registro = line[30:31].strip()
            numero_de_orden = line[31:34].strip()
            total_registros = line[34:37].strip()
            matricula_inmobiliaria = line[37:55].strip()
            espacio_1 = line[55:77].strip()
            zona_fisica_1 = line[77:80].strip()
            zona_economica_1 = line[80:83].strip()
            area_terreno_1 = line[83:98].strip()
            espacio_2 = line[98:120].strip()
            zona_fisica_2 = line[120:123].strip()
            zona_economica_2 = line[123:126].strip()
            area_terreno_2 = line[126:141].strip()
            espacio_3 = line[141:163].strip()
            habitaciones_1 = line[163:167].strip()
            banos_1 = line[167:171].strip()
            locales_1 = line[171:175].strip()
            pisos_1 = line[175:177].strip()
            estrato_1 = line[177:178].strip()
            uso_1 = line[178:181].strip()
            puntaje_1 = line[181:183].strip()
            area_construida_1 = line[183:189].strip()
            espacio_4 = line[189:211].strip()
            habitaciones_2 = line[211:215].strip()
            banos_2 = line[215:219].strip()
            locales_2 = line[219:223].strip()
            pisos_2 = line[223:225].strip()
            estrato_2 = line[225:226].strip()
            uso_2 = line[226:229].strip()
            puntaje_2 = line[229:231].strip()
            area_construida_2 = line[231:237].strip()
            espacio_5 = line[237:259].strip()
            habitaciones_3 = line[259:263].strip()
            banos_3 = line[263:267].strip()
            locales_3 = line[267:271].strip()
            pisos_3 = line[271:273].strip()
            estrato_3 = line[273:274].strip()
            uso_3 = line[274:277].strip()
            puntaje_3 = line[277:279].strip()
            area_construida_3 = line[279:285].strip()
            espacio_6 = line[285:307].strip()
            vigencia = line[307:315].strip()
            numero_predial_anterior = line[315:330].strip()

            departamento_list.append(departamento)
            municipio_list.append(municipio)
            numero_del_predio_list.append(numero_del_predio)
            tipo_de_registro_list.append(tipo_de_registro)
            numero_de_orden_list.append(numero_de_orden)
            total_registros_list.append(total_registros)
            matricula_inmobiliaria_list.append(matricula_inmobiliaria)
            espacio_1_list.append(espacio_1)
            zona_fisica_1_list.append(zona_fisica_1)
            zona_economica_1_list.append(zona_economica_1)
            area_terreno_1_list.append(area_terreno_1)
            espacio_2_list.append(espacio_2)
            zona_fisica_2_list.append(zona_fisica_2)
            zona_economica_2_list.append(zona_economica_2)
            area_terreno_2_list.append(area_terreno_2)
            espacio_3_list.append(espacio_3)
            habitaciones_1_list.append(habitaciones_1)
            banos_1_list.append(banos_1)
            locales_1_list.append(locales_1)
            pisos_1_list.append(pisos_1)
            estrato_1_list.append(estrato_1)
            uso_1_list.append(uso_1)
            puntaje_1_list.append(puntaje_1)
            area_construida_1_list.append(area_construida_1)
            espacio_4_list.append(espacio_4)
            habitaciones_2_list.append(habitaciones_2)
            banos_2_list.append(banos_2)
            locales_2_list.append(locales_2)
            pisos_2_list.append(pisos_2)
            estrato_2_list.append(estrato_2)
            uso_2_list.append(uso_2)
            puntaje_2_list.append(puntaje_2)
            area_construida_2_list.append(area_construida_2)
            espacio_5_list.append(espacio_5)
            habitaciones_3_list.append(habitaciones_3)
            banos_3_list.append(banos_3)
            locales_3_list.append(locales_3)
            pisos_3_list.append(pisos_3)
            estrato_3_list.append(estrato_3)
            uso_3_list.append(uso_3)
            puntaje_3_list.append(puntaje_3)
            area_construida_3_list.append(area_construida_3)
            espacio_6_list.append(espacio_6)
            vigencia_list.append(vigencia)
            numero_predial_anterior_list.append(numero_predial_anterior)

    df_r2 = pd.DataFrame({
        'DEPARTAMENTO': departamento_list,
        'MUNICIPIO': municipio_list,
        'NUMERO_DEL_PREDIO': numero_del_predio_list,
        'TIPO_DE_REGISTRO': tipo_de_registro_list,
        'NUMERO_DE_ORDEN': numero_de_orden_list,
        'TOTAL_REGISTROS': total_registros_list,
        'MATRICULA_INMOBILIARIA': matricula_inmobiliaria_list,
        'ESPACIO_1': espacio_1_list,
        'ZONA_FISICA_1': zona_fisica_1_list,
        'ZONA_ECONOMICA_1': zona_economica_1_list,
        'AREA_TERRENO_1': area_terreno_1_list,
        'ESPACIO_2': espacio_2_list,
        'ZONA_FISICA_2': zona_fisica_2_list,
        'ZONA_ECONOMICA_2': zona_economica_2_list,
        'AREA_TERRENO_2': area_terreno_2_list,
        'ESPACIO_3': espacio_3_list,
        'HABITACIONES_1': habitaciones_1_list,
        'BANOS_1': banos_1_list,
        'LOCALES_1': locales_1_list,
        'PISOS_1': pisos_1_list,
        'ESTRATO_1': estrato_1_list,
        'USO_1': uso_1_list,
        'PUNTAJE_1': puntaje_1_list,
        'AREA_CONSTRUIDA_1': area_construida_1_list,
        'ESPACIO_4': espacio_4_list,
        'HABITACIONES_2': habitaciones_2_list,
        'BANOS_2': banos_2_list,
        'LOCALES_2': locales_2_list,
        'PISOS_2': pisos_2_list,
        'ESTRATO_2': estrato_2_list,
        'USO_2': uso_2_list,
        'PUNTAJE_2': puntaje_2_list,
        'AREA_CONSTRUIDA_2': area_construida_2_list,
        'ESPACIO_5': espacio_5_list,
        'HABITACIONES_3': habitaciones_3_list,
        'BANOS_3': banos_3_list,
        'LOCALES_3': locales_3_list,
        'PISOS_3': pisos_3_list,
        'ESTRATO_3': estrato_3_list,
        'USO_3': uso_3_list,
        'PUNTAJE_3': puntaje_3_list,
        'AREA_CONSTRUIDA_3': area_construida_3_list,
        'ESPACIO_6': espacio_6_list,
        'VIGENCIA': vigencia_list,
        'NUMERO_PREDIAL_ANTERIOR': numero_predial_anterior_list
    })

    df_r2['NUMERO_PREDIAL'] = df_r2['DEPARTAMENTO'] + df_r2['MUNICIPIO'] + df_r2['NUMERO_DEL_PREDIO']
    df_r2['NUMERO_PREDIAL_ANTERIOR'] = df_r2['DEPARTAMENTO'] + df_r2['MUNICIPIO'] + df_r2['NUMERO_PREDIAL_ANTERIOR']

    return df_r2

