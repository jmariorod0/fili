import os
import subprocess
import psycopg2
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton

from PyQt5.QtWidgets import QProgressBar, QLabel
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QToolButton,QSizePolicy,
    QComboBox, QCheckBox, QInputDialog, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import QSettings,Qt
from PyQt5.QtGui import QIcon,QPixmap

def obtener_ruta_java():
    # Obtener la ruta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir la ruta esperada para java.exe dentro de la carpeta "JM_TOOLS/Herramientas/java-portable/bin/"
    java_path = os.path.join(current_dir,  'java-portable', 'bin', 'java.exe')
    
    # Verificar si la ruta existe
    if os.path.exists(java_path):
        return java_path
    else:
        raise FileNotFoundError(f"No se encontró 'java.exe' en la ruta: {java_path}")

# Usar la función para obtener la ruta a java.exe
try:
    java_path = obtener_ruta_java()
    print(f"Ruta a java.exe: {java_path}")
except FileNotFoundError as e:
    print(e)

class config_conexion(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Configurar Conexión a la Base de Datos")
        self.setMinimumWidth(400)
        self.conexion = None

        # Layout principal
        main_layout = QVBoxLayout()

        # Group 1: Conexión a la base de datos
        db_groupbox = QVBoxLayout()

        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("Host de la base de datos:")
        self.entry_host = QLineEdit()
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.entry_host)
        db_groupbox.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("Puerto de la base de datos:")
        self.entry_port = QLineEdit()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.entry_port)
        db_groupbox.addLayout(port_layout)

        # Usuario
        user_layout = QHBoxLayout()
        user_label = QLabel("Usuario de la base de datos:")
        self.entry_usuario = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.entry_usuario)
        db_groupbox.addLayout(user_layout)

        # Contraseña
        password_layout = QHBoxLayout()
        password_label = QLabel("Contraseña de la base de datos:")
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.entry_password)
        db_groupbox.addLayout(password_layout)

        # Conectar button
        connect_button_layout = QHBoxLayout()
        self.boton_conectar = QPushButton("Conectar")
        self.boton_conectar.clicked.connect(self.conectar_y_obtener_esquemas)
        connect_button_layout.addWidget(self.boton_conectar)
        db_groupbox.addLayout(connect_button_layout)

        # Nombre de la base de datos
        db_name_layout = QHBoxLayout()
        db_label = QLabel("Nombre de la base de datos:")
        self.db_menu = QComboBox()
        self.db_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        db_name_layout.addWidget(db_label)
        db_name_layout.addWidget(self.db_menu)

        # "+" button for creating a new database
        create_db_button = QPushButton("+")
        create_db_button.setFixedWidth(30)  # Hacer más pequeño el botón
        create_db_button.clicked.connect(self.crear_base_datos)
        db_name_layout.addWidget(create_db_button)
        db_groupbox.addLayout(db_name_layout)





        # Esquema
        schema_layout = QHBoxLayout()
        schema_label = QLabel("Seleccione el esquema:")
        self.esquema_menu = QComboBox()
        self.esquema_menu.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        schema_layout.addWidget(schema_label)
        schema_layout.addWidget(self.esquema_menu)

        # "+" button for creating a new schema
        create_schema_button = QPushButton("+")
        create_schema_button.setFixedWidth(30)  # Hacer más pequeño el botón
        create_schema_button.clicked.connect(self.crear_esquema)
        schema_layout.addWidget(create_schema_button)
        db_groupbox.addLayout(schema_layout)


        # Añadir todo al layout principal
        main_layout.addLayout(db_groupbox)
        self.setLayout(main_layout)


        # Botón para importar XTF
        self.boton_importar_xtf = QPushButton("Importar XTF")
        self.boton_importar_xtf.setEnabled(False)  # Lo habilitamos solo si la conexión es exitosa
        self.boton_importar_xtf.clicked.connect(self.importar_xtf)

        # Añadir el nuevo botón al layout principal
        main_layout.addWidget(self.boton_importar_xtf)




        # Botón para generar el modelo físico (deshabilitado por defecto)
        self.boton_generar_modelo = QPushButton("Generar Modelo Físico")
        self.boton_generar_modelo.setEnabled(False)
        self.boton_generar_modelo.clicked.connect(self.generar_modelo_fisico_para_esquema)

        # Checkbox para seleccionar si es "Palmira"
        self.checkbox_palmira = QCheckBox("Palmira")
        self.checkbox_palmira.setChecked(False)  # Desmarcado por defecto

        # Asegurarse de que ambos elementos tengan el tamaño adecuado
        self.boton_generar_modelo.setMinimumWidth(150)  # Ajustar el tamaño mínimo del botón
        self.checkbox_palmira.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Layout para el botón y el checkbox (orden cambiado)
        checkbox_button_layout = QHBoxLayout()
        checkbox_button_layout.addWidget(self.boton_generar_modelo)  # Añadir el botón primero
        checkbox_button_layout.addWidget(self.checkbox_palmira)  # Añadir el checkbox después

        # Añadir un poco de margen
        checkbox_button_layout.setContentsMargins(10, 0, 10, 0)

        # Añadir el layout al layout principal
        main_layout.addLayout(checkbox_button_layout)







        # Botón "OK" para guardar la configuración
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.guardar_configuracion_conexion)  # Guardar configuración y cerrar diálogo
        button_layout.addWidget(self.ok_button)
        
        # Botón "Cancelar"
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Dentro de la clase 'config_conexion', en el constructor __init__
        self.progress_bar_xtf = QProgressBar(self)
        self.progress_bar_xtf.setValue(0)  # Inicializa el valor de la barra en 0
        self.progress_bar_xtf.setVisible(False)  # Ocultar la barra de progreso hasta que empiece la importación

        self.label_archivo_actual = QLabel("Archivo actual: Ninguno", self)
        self.label_archivo_actual.setVisible(False)  # Ocultar la etiqueta hasta que empiece la importación

        # Añadir la barra de progreso y la etiqueta al layout principal
        main_layout.addWidget(self.label_archivo_actual)
        main_layout.addWidget(self.progress_bar_xtf)

        # Cargar configuraciones previas
        self.cargar_configuracion_conexion()

        # Conectar botón "Conectar"
        self.boton_conectar.clicked.connect(self.conectar_y_obtener_esquemas)




    def guardar_configuracion_conexion(self):
        """
        Guarda la configuración de conexión a la base de datos en QGIS para su uso posterior y cierra el cuadro de diálogo.
        """
        settings = QSettings()

        # Guardar los valores
        settings.setValue("JM_TOOLS/host", self.entry_host.text())
        settings.setValue("JM_TOOLS/port", self.entry_port.text())
        settings.setValue("JM_TOOLS/usuario", self.entry_usuario.text())
        settings.setValue("JM_TOOLS/password", self.entry_password.text())
        settings.setValue("JM_TOOLS/base_datos", self.db_menu.currentText())  # Guardar la base de datos seleccionada
        settings.setValue("JM_TOOLS/esquema", self.esquema_menu.currentText())  # Guardar el esquema seleccionado

        # Cerrar el cuadro de diálogo sin mostrar mensajes
        self.accept()  # Cierra el cuadro de diálogo



    def cargar_configuracion_conexion(self):
        """
        Carga la última configuración de la base de datos desde QGIS.
        """
        settings = QSettings()

        self.entry_host.setText(settings.value("JM_TOOLS/host", "localhost"))
        self.entry_port.setText(settings.value("JM_TOOLS/port", "5432"))
        self.entry_usuario.setText(settings.value("JM_TOOLS/usuario", "postgres"))
        self.entry_password.setText(settings.value("JM_TOOLS/password", ""))

        # Cargar la base de datos previamente seleccionada
        base_datos_guardada = settings.value("JM_TOOLS/base_datos", "")
        if base_datos_guardada:
            self.db_menu.addItem(base_datos_guardada)  # Añadimos manualmente el valor guardado para que sea seleccionado
            self.db_menu.setCurrentText(base_datos_guardada)  # Establecer el texto actual a la base de datos guardada

        # Cargar el esquema previamente seleccionado
        esquema_guardado = settings.value("JM_TOOLS/esquema", "")
        if esquema_guardado:
            self.esquema_menu.addItem(esquema_guardado)  # Añadimos manualmente el valor guardado
            self.esquema_menu.setCurrentText(esquema_guardado)  # Establecer el esquema guardado



    def conectar_y_obtener_esquemas(self):
        host = self.entry_host.text()
        port = self.entry_port.text()
        usuario = self.entry_usuario.text()
        contraseña = self.entry_password.text()

        try:
            self.conexion = psycopg2.connect(
                host=host,
                port=port,
                user=usuario,
                password=contraseña
            )
            cursor = self.conexion.cursor()

            # Listar todas las bases de datos
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            databases = cursor.fetchall()
            self.db_menu.clear()
            self.db_menu.addItems([db[0] for db in databases])

            # Guardar la configuración en QSettings
            #self.guardar_configuracion_conexion()  # LLamar sin pasar argumentos

            # Asociar el evento de selección de base de datos al combobox
            self.db_menu.currentIndexChanged.connect(self.obtener_esquemas)
            self.boton_importar_xtf.setEnabled(True)


        except psycopg2.OperationalError as e:
            # Mantener solo el mensaje de error
            QMessageBox.critical(self, "Error", f"Error al conectar a la base de datos: {e}")



    def obtener_esquemas(self):
        nombre_base_datos = self.db_menu.currentText()
        try:
            self.conexion.close()
            self.conexion = psycopg2.connect(
                host=self.entry_host.text(),
                port=self.entry_port.text(),
                database=nombre_base_datos,
                user=self.entry_usuario.text(),
                password=self.entry_password.text()
            )
            cursor = self.conexion.cursor()

            cursor.execute("SELECT schema_name FROM information_schema.schemata;")
            esquemas = cursor.fetchall()

            self.esquema_menu.clear()
            if esquemas:
                self.esquema_menu.addItems([esquema[0] for esquema in esquemas])

           
           
        except psycopg2.OperationalError as e:
            QMessageBox.critical(self, "Error", f"Error al conectar a la base de datos: {e}")







    def crear_base_datos(self):
        nombre_base_datos, ok = QInputDialog.getText(self, "Crear Base de Datos", "Ingrese el nombre de la nueva base de datos:")

        if ok and nombre_base_datos:
            try:
                nueva_conexion = psycopg2.connect(
                    host=self.entry_host.text(),
                    port=self.entry_port.text(),
                    user=self.entry_usuario.text(),
                    password=self.entry_password.text()
                )
                nueva_conexion.autocommit = True
                cursor = nueva_conexion.cursor()

                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{nombre_base_datos}';")
                if cursor.fetchone():
                    QMessageBox.warning(self, "Advertencia", f"La base de datos '{nombre_base_datos}' ya existe.")
                    return

                cursor.execute(f"CREATE DATABASE {nombre_base_datos};")
                nueva_conexion.close()

                nueva_conexion_bd = psycopg2.connect(
                    host=self.entry_host.text(),
                    port=self.entry_port.text(),
                    database=nombre_base_datos,
                    user=self.entry_usuario.text(),
                    password=self.entry_password.text()
                )
                nueva_conexion_bd.autocommit = True
                cursor = nueva_conexion_bd.cursor()

                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
                cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")

                # Insertar el sistema de coordenadas EPSG:9377 si no existe
                cursor.execute("""
                    INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
                    VALUES (
                        9377, 
                        'EPSG', 
                        9377, 
                        '+proj=tmerc +lat_0=4.0 +lon_0=-73.0 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
                        'PROJCRS["MAGNA-SIRGAS / Origen-Nacional", BASEGEOGCRS["MAGNA-SIRGAS", DATUM["Marco Geocentrico Nacional de Referencia", ELLIPSOID["GRS 1980",6378137,298.257222101, LENGTHUNIT["metre",1]]], PRIMEM["Greenwich",0, ANGLEUNIT["degree",0.0174532925199433]], ID["EPSG",4686]], CONVERSION["Colombia Transverse Mercator", METHOD["Transverse Mercator", ID["EPSG",9807]], PARAMETER["Latitude of natural origin",4, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8801]], PARAMETER["Longitude of natural origin",-73, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8802]], PARAMETER["Scale factor at natural origin",0.9992, SCALEUNIT["unity",1], ID["EPSG",8805]], PARAMETER["False easting",5000000, LENGTHUNIT["metre",1], ID["EPSG",8806]], PARAMETER["False northing",2000000, LENGTHUNIT["metre",1], ID["EPSG",8807]]], CS[Cartesian,2], AXIS["northing (N)",north, ORDER[1], LENGTHUNIT["metre",1]], AXIS["easting (E)",east, ORDER[2], LENGTHUNIT["metre",1]], USAGE[ SCOPE["unknown"], AREA["Colombia"], BBOX[-4.23,-84.77,15.51,-66.87]], ID["EPSG",9377]]'
                    ) 
                    ON CONFLICT (srid) DO NOTHING;
                """)

                nueva_conexion_bd.close()

                QMessageBox.information(self, "Éxito", f"La base de datos '{nombre_base_datos}' fue creada exitosamente.")
                self.conectar_y_obtener_esquemas()

            except psycopg2.Error as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la base de datos: {e}")



    def crear_esquema(self):
        nombre_esquema, ok = QInputDialog.getText(self, "Crear Esquema", "Ingrese el nombre del nuevo esquema:")

        if ok and nombre_esquema:
            try:
                cursor = self.conexion.cursor()
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {nombre_esquema};")
                self.conexion.commit()
                self.obtener_esquemas()  # Refrescamos los esquemas para que aparezca el nuevo
                QMessageBox.information(self, "Éxito", f"El esquema '{nombre_esquema}' fue creado exitosamente.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear el esquema: {e}")





    def obtener_esquemas(self):
        nombre_base_datos = self.db_menu.currentText()
        try:
            self.conexion.close()
            self.conexion = psycopg2.connect(
                host=self.entry_host.text(),
                port=self.entry_port.text(),
                database=nombre_base_datos,
                user=self.entry_usuario.text(),
                password=self.entry_password.text()
            )
            cursor = self.conexion.cursor()
            cursor.execute("SELECT schema_name FROM information_schema.schemata;")
            esquemas = cursor.fetchall()
            self.esquema_menu.clear()
            self.esquema_menu.addItems([esquema[0] for esquema in esquemas])

            # Asociar el evento de selección del esquema
            self.esquema_menu.currentIndexChanged.connect(self.verificar_tablas_en_esquema)

        except psycopg2.OperationalError as e:
            QMessageBox.critical(self, "Error", f"Error al conectar a la base de datos: {e}")

    def verificar_tablas_en_esquema(self):
        nombre_esquema = self.esquema_menu.currentText()
        cursor = self.conexion.cursor()
        # Verificar cuántas tablas hay en el esquema seleccionado
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{nombre_esquema}';")
        num_tablas = cursor.fetchone()[0]

        # Si el esquema tiene menos de 109 tablas, habilitar el botón de generar modelo físico
        if num_tablas < 109:
            self.boton_generar_modelo.setEnabled(True)
        else:
            self.boton_generar_modelo.setEnabled(False)



    def generar_modelo_fisico_para_esquema(self):
        nombre_esquema = self.esquema_menu.currentText()

        # Verificar si el checkbox está seleccionado para elegir la ruta
        if self.checkbox_palmira.isChecked():
            modelos_ili_path = self.obtener_ruta_modelos_ili("Palmira")  # Usar la ruta de "Palmira"
        else:
            modelos_ili_path = self.obtener_ruta_modelos_ili("Demás municipios")  # Usar la ruta de "Demás municipios"
        
        modelo_ili_path = self.seleccionar_archivo_ili(modelos_ili_path)

        try:
            self.generar_modelo_fisico(nombre_esquema, modelo_ili_path, modelos_ili_path)  # Pasa los tres argumentos
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el modelo físico: {e}")





    def obtener_ruta_modelos_ili(self, seleccion):
        """
        Obtiene la ruta a la carpeta que contiene los modelos .ili dentro de la estructura del proyecto.
        
        :param seleccion: Determina si se usa la ruta para "Palmira" o "Demás municipios".
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if seleccion == "Palmira":
            modelos_ili_path = os.path.join(current_dir, "modelos2")
        else:
            modelos_ili_path = os.path.join(current_dir, "modelos")
        
        # Imprimir las rutas para verificar
        print(f"Ruta actual: {current_dir}")
        print(f"Ruta de modelos ILI: {modelos_ili_path}")
        
        if not os.path.exists(modelos_ili_path):
            raise FileNotFoundError(f"No se encontró la carpeta de modelos .ili en la ruta esperada: {modelos_ili_path}")
        
        return modelos_ili_path





    def seleccionar_archivo_ili(self, modelos_ili_path):
        """
        Lógica para seleccionar un archivo ILI dentro de la carpeta especificada.
        En este ejemplo, se seleccionará el primer archivo .ili encontrado.
        """
        for file_name in os.listdir(modelos_ili_path):
            if file_name.endswith(".ili"):
                return os.path.join(modelos_ili_path, file_name)
        raise FileNotFoundError(f"No se encontró ningún archivo .ili en la carpeta: {modelos_ili_path}")
    






    def generar_modelo_fisico(self, esquema, modelo_ili_path, modelos_ili_path):
        try:
            ili2pg_path = self.obtener_ruta_ili2pg()
            modelos = self.obtener_modelos_desde_ili(modelos_ili_path)
            


            comando = [
                java_path,
                "-jar", ili2pg_path,
                "--schemaimport",
                "--dbhost", self.entry_host.text(),
                "--dbport", self.entry_port.text(),
                "--dbusr", self.entry_usuario.text(),
                "--dbpwd", self.entry_password.text(),
                "--dbdatabase", self.db_menu.currentText(),
                "--dbschema", esquema,
                "--coalesceCatalogueRef", #estructuras
                "--createNumChecks", #creacion de restrucciones
                "--createUnique", #creacion de restrucciones
                "--createFk", #creacion de restrucciones
                "--createFkIdx", #creacion de indices
                "--coalesceMultiSurface", #estructuras
                "--coalesceMultiLine", #estructuras
                #"--coalesceMultiPoint",
                #"--coalesceArray",
                "--beautifyEnumDispName", #enumeracion
                "--createGeomIdx", #creacion de indices
                "--createMetaInfo", #metainformacion adicional
                #"--expandMultilingual",
                #"--createTypeConstraint",
                "--createEnumTabsWithId", #enumeracion
                #"--createTidCol",
                "--smart2Inheritance", #herencia
                "--strokeArcs", #geometria
                #"--createBasketCol",
                "--defaultSrsAuth", "EPSG", #geometria
                "--defaultSrsCode", "9377",#geometria
                "--models", modelos,
                "--setupPgExt", #adjustments
                #"--iliMetaAttrs", "NULL",
                modelo_ili_path
            ]

            resultado = subprocess.run(comando, capture_output=True, text=True)

            if resultado.returncode == 0:
                QMessageBox.information(self, "Éxito", f"La generación del modelo físico para FILI fue generada exitosamente en el esquema '{esquema}'.", QMessageBox.Ok)

            else:
                QMessageBox.critical(self, "Error", f"Error al generar el modelo físico ILI: {resultado.stderr}", QMessageBox.Ok)

        except Exception as e:
            import traceback
            error_message = traceback.format_exc()
            QMessageBox.critical(self, "Error", f"Error al intentar generar el modelo físico ILI:\n{error_message}", QMessageBox.Ok)




    def verificar_o_insertar_crs(self):
        """
        Verificar si el CRS EPSG:9377 está presente en la base de datos y si no lo está, insertarlo.
        """
        try:
            # Conectarse a la base de datos seleccionada
            conexion = psycopg2.connect(
                host=self.entry_host.text(),
                port=self.entry_port.text(),
                database=self.db_menu.currentText(),
                user=self.entry_usuario.text(),
                password=self.entry_password.text()
            )
            conexion.autocommit = True
            cursor = conexion.cursor()

            # Verificar si EPSG:9377 ya está presente en spatial_ref_sys
            cursor.execute("SELECT COUNT(*) FROM spatial_ref_sys WHERE srid = 9377;")
            count = cursor.fetchone()[0]

            if count == 0:
                # Insertar EPSG:9377 si no existe
                cursor.execute("""
                    INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) 
                    VALUES (
                        9377, 
                        'EPSG', 
                        9377, 
                        '+proj=tmerc +lat_0=4.0 +lon_0=-73.0 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
                        'PROJCRS["MAGNA-SIRGAS / Origen-Nacional", BASEGEOGCRS["MAGNA-SIRGAS", DATUM["Marco Geocentrico Nacional de Referencia", ELLIPSOID["GRS 1980",6378137,298.257222101, LENGTHUNIT["metre",1]]], PRIMEM["Greenwich",0, ANGLEUNIT["degree",0.0174532925199433]], ID["EPSG",4686]], CONVERSION["Colombia Transverse Mercator", METHOD["Transverse Mercator", ID["EPSG",9807]], PARAMETER["Latitude of natural origin",4, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8801]], PARAMETER["Longitude of natural origin",-73, ANGLEUNIT["degree",0.0174532925199433], ID["EPSG",8802]], PARAMETER["Scale factor at natural origin",0.9992, SCALEUNIT["unity",1], ID["EPSG",8805]], PARAMETER["False easting",5000000, LENGTHUNIT["metre",1], ID["EPSG",8806]], PARAMETER["False northing",2000000, LENGTHUNIT["metre",1], ID["EPSG",8807]]], CS[Cartesian,2], AXIS["northing (N)",north, ORDER[1], LENGTHUNIT["metre",1]], AXIS["easting (E)",east, ORDER[2], LENGTHUNIT["metre",1]], USAGE[ SCOPE["unknown"], AREA["Colombia"], BBOX[-4.23,-84.77,15.51,-66.87]], ID["EPSG",9377]]'
                    ) ON CONFLICT (srid) DO NOTHING;
                """)
                QMessageBox.information(self, "Info", "El CRS EPSG:9377 ha sido insertado en la base de datos.")
            else:
                print("El CRS EPSG:9377 ya está presente en la base de datos.")
            
            conexion.close()

        except psycopg2.Error as e:
            QMessageBox.critical(self, "Error", f"Error al verificar o insertar el CRS: {e}")





    def obtener_ruta_ili2pg(self):
        """
        Obtiene la ruta al archivo ili2pg-5.1.0.jar dentro de la estructura del proyecto.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ili2pg_path = os.path.join(current_dir, "ilidb", "ili2pg-5.1.0.jar")
        
        if not os.path.exists(ili2pg_path):
            raise FileNotFoundError(f"No se encontró ili2pg en la ruta esperada: {ili2pg_path}")
        
        return ili2pg_path

    def obtener_modelos_desde_ili(self, modelos_ili_path):
        """
        Obtiene la lista de modelos a partir de los archivos .ili en la carpeta especificada.
        
        :param modelos_ili_path: Ruta a la carpeta que contiene los archivos .ili.
        :return: Una cadena con los nombres de los modelos separados por punto y coma.
        """
        modelos = []
        for file_name in os.listdir(modelos_ili_path):
            if file_name.endswith(".ili"):
                modelo = os.path.splitext(file_name)[0]
                modelos.append(modelo)
        
        return ";".join(modelos)
    





    def importar_xtf(self):
        """
        Permite seleccionar una carpeta con archivos XTF o un solo archivo XTF.
        """
        # Crear el diálogo de mensaje personalizado
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Seleccionar Modo de Importación")
        msg_box.setText("¿Desea seleccionar un archivo XTF individual o una carpeta?")
        
        # Añadir botones personalizados
        individual_button = msg_box.addButton("Individual", QMessageBox.ActionRole)
        carpeta_button = msg_box.addButton("Carpeta", QMessageBox.ActionRole)

        # Mostrar el cuadro de diálogo y esperar la respuesta del usuario
        msg_box.exec_()

        # Si el usuario cerró el cuadro de diálogo con "X", salir de la función
        if msg_box.clickedButton() is None:
            return

        # Determinar qué botón fue seleccionado
        if msg_box.clickedButton() == individual_button:
            # Seleccionar un solo archivo XTF
            file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo XTF", "", "XTF Files (*.xtf)")
            if not file_path:
                QMessageBox.warning(self, "Error", "No se seleccionó ningún archivo.")
                return
            input_path = file_path  # En este caso es un archivo individual
        elif msg_box.clickedButton() == carpeta_button:
            # Seleccionar una carpeta con múltiples archivos XTF
            folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta con Archivos XTF")
            if not folder_path:
                QMessageBox.warning(self, "Error", "No se seleccionó ninguna carpeta.")
                return
            input_path = folder_path  # En este caso es una carpeta
        else:
            # Si no se seleccionó ningún botón válido, salir de la función
            return

        # Obtener los parámetros de conexión
        host = self.entry_host.text()
        port = self.entry_port.text()
        nombre_base_datos = self.db_menu.currentText()
        usuario = self.entry_usuario.text()
        contraseña = self.entry_password.text()
        esquema = self.esquema_menu.currentText()  # Obtener el esquema seleccionado

        # Verificar si se seleccionó el checkbox de "Palmira"
        seleccion = "Palmira" if self.checkbox_palmira.isChecked() else "Demás municipios"

        try:
            # Importar XTF(s) - si es un archivo o una carpeta
            self.importar_xtfs_bd(host, port, nombre_base_datos, usuario, contraseña, input_path, esquema)
            QMessageBox.information(self, "Éxito", f"La importación de los archivos XTF en el esquema '{esquema}' se completó con éxito.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la importación: {e}")






    def importar_xtfs_bd(self, host, port, nombre_base_datos, usuario, contraseña, input_path, esquema):
        """
        Importa archivos XTF a la base de datos PostgreSQL usando ili2pg.
        Puede ser un solo archivo XTF o varios archivos en una carpeta.
        """
        # Determinar si se seleccionó un archivo o una carpeta
        if os.path.isfile(input_path) and input_path.endswith(".xtf"):
            # Es un archivo individual
            xtf_files = [input_path]
        elif os.path.isdir(input_path):
            # Es una carpeta, obtener todos los archivos XTF en la carpeta
            xtf_files = [f for f in os.listdir(input_path) if f.endswith(".xtf")]
            xtf_files = [os.path.join(input_path, f) for f in xtf_files]  # Asegurarse de que son rutas completas
        else:
            raise ValueError("La ruta seleccionada no es válida o no contiene archivos XTF.")

        if not xtf_files:
            raise ValueError("No se encontraron archivos XTF en la carpeta.")

        ili2pg_path = self.obtener_ruta_ili2pg()

        # Obtener la selección basada en el checkbox "Palmira"
        seleccion = "Palmira" if self.checkbox_palmira.isChecked() else "Demás municipios"
        
        # Aquí se pasa la selección como argumento
        modelos_ili_path = self.obtener_ruta_modelos_ili(seleccion)

        # Obtener los modelos desde los archivos .ili
        modelos = self.obtener_modelos_desde_ili(modelos_ili_path)
        if not modelos:
            raise ValueError("No se encontraron modelos .ili en la carpeta especificada.")

        total_files = len(xtf_files)

        # Mostrar la barra de progreso y la etiqueta
        self.progress_bar_xtf.setVisible(True)
        self.progress_bar_xtf.setValue(0)  # Inicializa en 0
        self.label_archivo_actual.setVisible(True)
        self.label_archivo_actual.setText("Archivo actual: Ninguno")

        for index, xtf_file in enumerate(xtf_files):
            xtf_path = os.path.normpath(xtf_file)

            # Comando para importar los archivos XTF usando ili2pg
            cmd = [
                java_path, "-jar", ili2pg_path,
                "--import",
                "--disableValidation",
                "--dbhost", host,
                "--dbport", port,
                "--dbusr", usuario,
                "--dbpwd", contraseña,
                "--dbdatabase", nombre_base_datos,
                "--dbschema", esquema,
                "--iliMetaAttrs", "NULL",
                "--models", modelos,
                xtf_path
            ]

            # Ejecutar el comando
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Manejo de errores de codificación
            if process.returncode != 0:
                try:
                    stderr_decoded = stderr.decode('utf-8-sig')
                except UnicodeDecodeError:
                    stderr_decoded = stderr.decode('latin-1', errors='ignore')

                raise Exception(f"Error al importar {xtf_file}: {stderr_decoded}")

            # Obtener solo el nombre del archivo sin la ruta
            archivo_actual = os.path.basename(xtf_file)

            # Actualizar la barra de progreso y la etiqueta del archivo actual
            progress_value = int(((index + 1) / total_files) * 100)
            self.progress_bar_xtf.setValue(progress_value)
            self.label_archivo_actual.setText(f"Archivo actual: {archivo_actual}")

        # Ocultar la barra de progreso y la etiqueta cuando termine
        self.progress_bar_xtf.setVisible(False)
        self.label_archivo_actual.setVisible(False)

        # Mostrar mensaje de éxito
        #QMessageBox.information(self, "Éxito", "La importación de los archivos XTF se completó con éxito.")
