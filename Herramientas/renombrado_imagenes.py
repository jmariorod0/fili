from PyQt5.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QLabel, QLineEdit, QPushButton, QDialog, QTextEdit
from PyQt5.QtCore import QSettings
import psycopg2
import os
from reportlab.pdfgen import canvas
from PIL import Image

class renombrado_imagenes(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Renombrado de Imágenes y Generación de PDF")
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        """
        Configuración de la interfaz.
        """
        # Campo para mostrar y seleccionar la carpeta de imágenes
        self.ruta_label = QLabel("Ruta de la Carpeta de Imágenes:")
        self.ruta_texto = QLineEdit(self)
        self.ruta_texto.setReadOnly(True)

        # Botón para seleccionar carpeta
        self.boton_seleccionar = QPushButton('Seleccionar Carpeta de Imágenes', self)
        self.boton_seleccionar.clicked.connect(self.seleccionar_carpeta)

        # Botón para ejecutar el renombrado y generación de PDFs
        self.boton_renombrar = QPushButton('Renombrar Imágenes y Generar PDFs', self)
        self.boton_renombrar.setEnabled(False)
        self.boton_renombrar.clicked.connect(self.renombrar_y_generar_pdf)

        # Área de texto para mostrar el progreso del renombrado
        self.area_progreso = QTextEdit(self)
        self.area_progreso.setReadOnly(True)

        # Layouts y diseño de la ventana
        layout = QVBoxLayout(self)
        layout.addWidget(self.ruta_label)
        layout.addWidget(self.ruta_texto)
        layout.addWidget(self.boton_seleccionar)
        layout.addWidget(self.boton_renombrar)
        layout.addWidget(self.area_progreso)

    def seleccionar_carpeta(self):
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directorio:
            self.ruta_texto.setText(directorio)
            self.boton_renombrar.setEnabled(True)

    def renombrar_y_generar_pdf(self):
        # Conectar a la base de datos
        settings = QSettings()
        esquema = settings.value("JM_TOOLS/esquema", "")
        base_datos = settings.value("JM_TOOLS/base_datos", "")
        host = settings.value("JM_TOOLS/host", "localhost")
        port = settings.value("JM_TOOLS/port", "5432")
        usuario = settings.value("JM_TOOLS/usuario", "postgres")
        contraseña = settings.value("JM_TOOLS/password", "")

        directorio = self.ruta_texto.text()
        if not directorio:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un directorio.")
            return

        try:
            conexion = psycopg2.connect(
                host=host,
                port=port,
                database=base_datos,
                user=usuario,
                password=contraseña
            )
            cursor = conexion.cursor()

            # Listar todas las imágenes en la carpeta
            imagenes_carpeta = [f.replace(".jpg", "") for f in os.listdir(directorio) if f.endswith(".jpg")]

            imagenes_procesadas = []  # Para llevar el registro de todas las imágenes que se procesan

            # -------------------------------------------
            # Renombrar imágenes (Primera consulta)
            # -------------------------------------------
            sql_query_renombrar = f"""
            SELECT adj.archivo, adj.procedencia, pd.qr_operacion_definitivo, 
                   substring(adj.archivo FROM '.*/([^/]+)\\.jpg') AS nombre_imagen,
                   CASE
                        WHEN adj.procedencia = 'lote' THEN CONCAT(pd.qr_operacion_definitivo, '_LOTE')
                   END AS nombre_archivo
            FROM {esquema}.cca_adjunto adj
            JOIN {esquema}.cca_predio pd ON adj.cca_predio_adjunto = pd.t_id;
            """
            cursor.execute(sql_query_renombrar)
            resultados_renombrar = cursor.fetchall()

            renombradas = 0
            omitidas_renombrar = []

            # Renombrar imágenes según la primera consulta
            for fila in resultados_renombrar:
                nombre_imagen = fila[3]
                nombre_archivo = fila[4]
                if nombre_imagen and nombre_archivo:
                    img_path = os.path.join(directorio, f"{nombre_imagen}.jpg")
                    new_img_path = os.path.join(directorio, f"{nombre_archivo}.jpg")
                    if os.path.exists(img_path):
                        os.rename(img_path, new_img_path)
                        renombradas += 1
                        imagenes_procesadas.append(nombre_imagen)
                        self.area_progreso.append(f"Imagen '{nombre_imagen}.jpg' renombrada a '{nombre_archivo}.jpg'")
                    else:
                        omitidas_renombrar.append(nombre_imagen)

            self.area_progreso.append(f"\nRenombradas {renombradas} imágenes de {len(resultados_renombrar)}.")






            # -------------------------------------------
            # Renombrar imágenes (Cuarta consulta)
            # -------------------------------------------
            sql_query_renombrar_cuarta = f"""
            SELECT adj.archivo, adj.procedencia, pd.qr_operacion_definitivo, 
                   substring(adj.archivo FROM '.*/([^/]+)\\.jpg') AS nombre_imagen,
                   CASE
                        WHEN adj.procedencia = 'fachada' THEN CONCAT(pd.qr_operacion_definitivo, '_FAC')
                        WHEN adj.procedencia = 'estructura' THEN CONCAT(pd.qr_operacion_definitivo, '_EST')
                        WHEN adj.procedencia = 'banos' THEN CONCAT(pd.qr_operacion_definitivo, '_BAN')    
                        WHEN adj.procedencia = 'cocina' THEN CONCAT(pd.qr_operacion_definitivo, '_COC')
                        WHEN adj.procedencia = 'cerchas' THEN CONCAT(pd.qr_operacion_definitivo, '_CER')
                        WHEN adj.procedencia = 'acabados' THEN CONCAT(pd.qr_operacion_definitivo, '_ACA')
                        WHEN adj.procedencia = 'unidadnoconvencional' THEN CONCAT(pd.qr_operacion_definitivo, '_NC')
                   END AS nombre_archivo
            FROM {esquema}.cca_adjunto adj
            JOIN {esquema}.cca_unidadconstruccion uc ON adj.cca_unidadconstruccion_adjunto = uc.t_id
            JOIN {esquema}.cca_caracteristicasunidadconstruccion cuc ON uc.caracteristicasunidadconstruccion = cuc.t_id
            JOIN {esquema}.cca_predio pd ON cuc.predio = pd.t_id
            WHERE adj.procedencia IN ('fachada', 'estructura', 'banos', 'cocina', 'cerchas', 'acabados', 'unidadnoconvencional');
            """
            cursor.execute(sql_query_renombrar_cuarta)
            resultados_renombrar_cuarta = cursor.fetchall()

            renombradas_cuarta = 0
            omitidas_renombrar_cuarta = []

            # Renombrar imágenes según la cuarta consulta
            for fila in resultados_renombrar_cuarta:
                nombre_imagen = fila[3]
                nombre_archivo = fila[4]
                if nombre_imagen and nombre_archivo:
                    img_path = os.path.join(directorio, f"{nombre_imagen}.jpg")
                    new_img_path = os.path.join(directorio, f"{nombre_archivo}.jpg")
                    if os.path.exists(img_path):
                        os.rename(img_path, new_img_path)
                        renombradas_cuarta += 1
                        imagenes_procesadas.append(nombre_imagen)
                        self.area_progreso.append(f"Imagen '{nombre_imagen}.jpg' renombrada a '{nombre_archivo}.jpg'")
                    else:
                        omitidas_renombrar_cuarta.append(nombre_imagen)

            self.area_progreso.append(f"\nRenombradas {renombradas_cuarta} imágenes de {len(resultados_renombrar_cuarta)}.")


            # -------------------------------------------
            # Generación de PDFs (Segunda consulta)
            # -------------------------------------------
            sql_query_pdf_segunda = f"""
            SELECT adj.archivo, adj.procedencia, inter.t_id AS id_interesado, 
                   pd.qr_operacion_definitivo, 
                   substring(adj.archivo FROM '.*/([^/]+)\\.jpg') AS nombre_imagen,
                   CASE
                        WHEN adj.procedencia = 'cedulacafetera' THEN CONCAT(pd.qr_operacion_definitivo, '_CCF')
                        WHEN adj.procedencia = 'cedulacampesina' THEN CONCAT(pd.qr_operacion_definitivo, '_CCP')
                        WHEN adj.procedencia = 'cedulasolicitante' THEN CONCAT(pd.qr_operacion_definitivo, '_CCS')
                        WHEN adj.procedencia = 'cedulaconyuge' THEN CONCAT(pd.qr_operacion_definitivo, '_CCC')
                        WHEN adj.procedencia = 'cedulaapoderado' THEN CONCAT(pd.qr_operacion_definitivo, '_CCA')
                        WHEN adj.procedencia = 'libretamilitar' THEN CONCAT(pd.qr_operacion_definitivo, '_LM')
                        WHEN adj.procedencia = 'tarjetaidentidad' THEN CONCAT(pd.qr_operacion_definitivo, '_TI')
                   END AS nombre_archivo
            FROM {esquema}.cca_adjunto adj
            JOIN {esquema}.cca_interesado inter ON adj.cca_interesado_adjunto = inter.t_id
            JOIN {esquema}.cca_derecho der ON inter.derecho = der.t_id
            JOIN {esquema}.cca_predio pd ON der.predio = pd.t_id
            WHERE adj.procedencia IN ('cedulacafetera', 'cedulacampesina', 'cedulasolicitante', 'cedulaconyuge', 
                                      'cedulaapoderado', 'libretamilitar', 'tarjetaidentidad');
            """
            cursor.execute(sql_query_pdf_segunda)
            resultados_pdf_segunda = cursor.fetchall()

            grupos_segunda = {}
            for fila in resultados_pdf_segunda:
                id_interesado = fila[2]
                qr_operacion_definitivo = fila[3]
                nombre_archivo = fila[5]
                nombre_imagen = fila[4]

                key = (id_interesado, qr_operacion_definitivo, nombre_archivo)
                if key not in grupos_segunda:
                    grupos_segunda[key] = []
                grupos_segunda[key].append(nombre_imagen)

            omitidos_pdf_segunda = []
            for key, imagenes in grupos_segunda.items():
                pdf_path = os.path.join(directorio, f"{key[2]}.pdf")
                try:
                    c = canvas.Canvas(pdf_path)
                    self.area_progreso.append(f"Generando PDF '{key[2]}.pdf' con las imágenes:")
                    for img in imagenes:
                        img_path = os.path.join(directorio, f"{img}.jpg")
                        if os.path.exists(img_path):
                            # Obtener tamaño y ajustar orientación con PIL
                            with Image.open(img_path) as image:
                                width, height = image.size
                                if width > height:  # Imagen horizontal
                                    c.setPageSize((width, height))
                                else:  # Imagen vertical
                                    c.setPageSize((height, width))
                                c.drawImage(img_path, 0, 0, width=width, height=height)
                                c.showPage()
                            self.area_progreso.append(f" - Imagen '{img}.jpg' añadida al PDF.")
                            imagenes_procesadas.append(img)
                        else:
                            omitidos_pdf_segunda.append(img)
                    c.save()
                except Exception as e:
                    omitidos_pdf_segunda.append(key[2])
                    print(f"Error al generar PDF {key[2]}: {e}")

            # -------------------------------------------
            # Generación de PDFs (Tercera consulta)
            # -------------------------------------------
            sql_query_pdf_tercera = f"""
            SELECT adj.archivo, adj.procedencia, fad.t_id AS id_fuenteadm, 
                   pd.qr_operacion_definitivo, 
                   substring(adj.archivo FROM '.*/([^/]+)\\.jpg') AS nombre_imagen,
                   CASE
                        WHEN adj.procedencia = 'actoadministrativo' THEN CONCAT(pd.qr_operacion_definitivo, '_AD')
                        WHEN adj.procedencia = 'escriturapublica' THEN CONCAT(pd.qr_operacion_definitivo, '_EP')
                        WHEN adj.procedencia = 'sentenciajudicial' THEN CONCAT(pd.qr_operacion_definitivo, '_SJ')    
                        WHEN adj.procedencia = 'contratocompravent' THEN CONCAT(pd.qr_operacion_definitivo, '_DPCC')
                        WHEN adj.procedencia = 'contratootorgamiento' THEN CONCAT(pd.qr_operacion_definitivo, '_DPCO')
                        WHEN adj.procedencia = 'documentodonacion' THEN CONCAT(pd.qr_operacion_definitivo, '_DOD')
                        WHEN adj.procedencia = 'cesion' THEN CONCAT(pd.qr_operacion_definitivo, '_DPC')
                        WHEN adj.procedencia = 'hererencial' THEN CONCAT(pd.qr_operacion_definitivo, '_DPH')
                   END AS nombre_archivo
            FROM {esquema}.cca_adjunto adj
            JOIN {esquema}.cca_fuenteadministrativa fad ON adj.cca_fuenteadminstrtiva_adjunto = fad.t_id
            JOIN {esquema}.cca_derecho der ON fad.derecho = der.t_id
            JOIN {esquema}.cca_predio pd ON der.predio = pd.t_id
            WHERE adj.procedencia IN ('actoadministrativo', 'escriturapublica', 'sentenciajudicial', 
                                      'contratocompravent', 'contratootorgamiento', 'documentodonacion', 
                                      'cesion', 'hererencial');
            """
            cursor.execute(sql_query_pdf_tercera)
            resultados_pdf_tercera = cursor.fetchall()

            grupos_tercera = {}
            for fila in resultados_pdf_tercera:
                id_fuenteadm = fila[2]
                qr_operacion_definitivo = fila[3]
                nombre_archivo = fila[5]
                nombre_imagen = fila[4]

                key = (id_fuenteadm, qr_operacion_definitivo, nombre_archivo)
                if key not in grupos_tercera:
                    grupos_tercera[key] = []
                grupos_tercera[key].append(nombre_imagen)

            omitidos_pdf_tercera = []
            for key, imagenes in grupos_tercera.items():
                pdf_path = os.path.join(directorio, f"{key[2]}.pdf")
                try:
                    c = canvas.Canvas(pdf_path)
                    self.area_progreso.append(f"Generando PDF '{key[2]}.pdf' con las imágenes:")
                    for img in imagenes:
                        img_path = os.path.join(directorio, f"{img}.jpg")
                        if os.path.exists(img_path):
                            # Obtener tamaño y ajustar orientación con PIL
                            with Image.open(img_path) as image:
                                width, height = image.size
                                if width > height:  # Imagen horizontal
                                    c.setPageSize((width, height))
                                else:  # Imagen vertical
                                    c.setPageSize((height, width))
                                c.drawImage(img_path, 0, 0, width=width, height=height)
                                c.showPage()
                            self.area_progreso.append(f" - Imagen '{img}.jpg' añadida al PDF.")
                            imagenes_procesadas.append(img)
                        else:
                            omitidos_pdf_tercera.append(img)
                    c.save()
                except Exception as e:
                    omitidos_pdf_tercera.append(key[2])
                    print(f"Error al generar PDF {key[2]}: {e}")

            # Determinar imágenes omitidas en general
            omitidas_final = set(imagenes_carpeta) - set(imagenes_procesadas)

            # Mensaje final sobre PDFs generados y omitidos
            self.area_progreso.append(f"\nPDFs generados: {len(grupos_segunda) + len(grupos_tercera) - len(omitidos_pdf_segunda) - len(omitidos_pdf_tercera)}.")
            if omitidas_final:
                self.area_progreso.append(f"Imágenes omitidas en general: {', '.join(omitidas_final)}")

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", f"Error al ejecutar la consulta: {e}")
        finally:
            if conexion:
                conexion.close()
