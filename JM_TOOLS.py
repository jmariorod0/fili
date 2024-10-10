from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSettings, Qt
import os
from .Herramientas.consultas import ConsultasDockWidget
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsApplication
from PyQt5.QtWidgets import QAction,QMessageBox
from PyQt5.QtGui import QDesktopServices
import os
import shutil
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QAction,QProgressBar
from PyQt5.QtWidgets import QMessageBox,QProgressBar
import requests
import zipfile
# Asegúrate de que estas importaciones estén en la parte superior de tu archivo
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QDialog, QProgressBar, QTextEdit, QPushButton, QMessageBox

# Importación necesaria

from PyQt5.QtCore import Qt, QCoreApplication




class JM_TOOLS:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = None  # Se inicializa el menú principal
        self.submenu_tools = None  # Submenú TOOLS
        self.submenu_analysis = None  # Submenú ANALYSIS
        self.toolbar = None  # Barra de herramientas
        self.consultas_dock = ConsultasDockWidget(self.iface) 

    def tr(self, message):
        return QCoreApplication.translate('GeoFILI SPO', message)


    def add_action(self, icon_path, text, callback, parent=None, submenu=None, add_to_toolbar=True):
        icon = QIcon(icon_path)
        
        # Si el parent no está definido, asignar la ventana principal del plugin como parent
        if parent is None:
            parent = self.iface.mainWindow()
        
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)

        # Agregar la acción al submenú si existe
        if submenu:
            submenu.addAction(action)
        else:
            self.iface.addPluginToMenu(self.menu, action)

        # Agregar la acción a la barra de herramientas SOLO si se especifica
        if add_to_toolbar and self.toolbar:
            self.toolbar.addAction(action)

        # Guardar la acción para referencia futura
        self.actions.append(action)

        return action

    def initGui(self):
        # Crear el menú principal si no existe
        self.menu = self.iface.mainWindow().menuBar().addMenu(self.tr(u'GeoFILI SPO'))

        # Crear los submenús TOOLS y FILI ANT dentro del menú principal
        self.submenu_tools = QMenu(self.tr(u'Tools'), self.iface.mainWindow())
        self.submenu_reporte = QMenu(self.tr(u'FILI ANT'), self.iface.mainWindow())
        self.submenu_documental = QMenu(self.tr(u'Documental'), self.iface.mainWindow())
        self.submenu_API = QMenu(self.tr(u'API'), self.iface.mainWindow())
        self.submenu_seguimiento = QMenu(self.tr(u'Seguimiento'), self.iface.mainWindow())

        # Agregar los submenús al menú principal
        self.menu.addMenu(self.submenu_tools)
        self.menu.addMenu(self.submenu_reporte)
        self.menu.addMenu(self.submenu_documental)
        self.menu.addMenu(self.submenu_API)
        self.menu.addMenu(self.submenu_seguimiento)

        # Crear la barra de herramientas
        self.toolbar = self.iface.addToolBar(u'JM_TOOLS')
        self.toolbar.setObjectName(u'JM_TOOLS')

        # Iconos para acciones

        icono_configura = QIcon(os.path.join(self.plugin_dir, "icons/configura3.png"))
        terreno_icono=os.path.join(self.plugin_dir, "icons/terreno.png")
        icono_stat = QgsApplication.getThemeIcon("/mActionCalculateField.svg")
        icono_xy = os.path.join(self.plugin_dir, "icons/objetivo.png")
        icono_query = os.path.join(self.plugin_dir, "icons/lupa.png")
        icono_load_layer = QgsApplication.getThemeIcon("/mActionAddLayer.svg")

        # Ruta para el ícono personalizado "ico.png" dentro de la carpeta icons del plugin
        icono_fili_ant = os.path.join(self.plugin_dir, "icons/formulario.png")
        icono_database = os.path.join(self.plugin_dir, "icons/ico.png")
        icono_tools = os.path.join(self.plugin_dir, "icons/tools.png")
        icono_topoint = os.path.join(self.plugin_dir, "icons/topounto.png")
        icono_vertice = os.path.join(self.plugin_dir, "icons/vertice.png")
        icono_documental = os.path.join(self.plugin_dir, "icons/documental.png")
        icono_documental2 = os.path.join(self.plugin_dir, "icons/carpeta.png")
        icono_API = os.path.join(self.plugin_dir, "icons/api1.png")
        icono_API2 = os.path.join(self.plugin_dir, "icons/api2.png")
        icono_depura = os.path.join(self.plugin_dir, "icons/depura.png")
        icono_lst = os.path.join(self.plugin_dir, "icons/lst.png")
        icono_derivado = os.path.join(self.plugin_dir, "icons/derivado.png")
        icono_acerca = QIcon(os.path.join(self.plugin_dir, "icons/acerca.png"))
        icono_seguimiento = QIcon(os.path.join(self.plugin_dir, "icons/seguir.png"))
        icono_estructura = os.path.join(self.plugin_dir, "icons/estructura.png")
        icono_datosgpkg = os.path.join(self.plugin_dir, "icons/datosgpkg.png")
        icono_validar = os.path.join(self.plugin_dir, "icons/validar.png")
        icono_esri = os.path.join(self.plugin_dir, "icons/formulario.png")

        # Agregar acciones al submenú TOOLS
        self.add_action(terreno_icono, self.tr(u'Terreno_LADM'), self.run_terreno, submenu=self.submenu_tools,add_to_toolbar=False)
        self.add_action(icono_topoint, self.tr(u'Feature To Point'), self.run_feature_to_point, submenu=self.submenu_tools,add_to_toolbar=False)
        self.add_action(icono_vertice, self.tr(u'Feature Vertices To Points'), self.run_feature_vertices_to_points, submenu=self.submenu_tools,add_to_toolbar=False)

        # Agregar acciones al submenú ANALYSIS (herramientas de análisis)
        self.add_action(icono_stat, self.tr(u'Estadísticas'), self.run_summary_statistics, submenu=self.submenu_tools,add_to_toolbar=False)
        self.add_action(icono_xy, self.tr(u'GO TO XY'), self.run_xy, submenu=self.submenu_tools,add_to_toolbar=False)

        # Agregar "Configurar Conexión" como acción directa al menú principal JM_TOOLS con el ícono de llave
        configurar_conexion_action = QAction(icono_configura, self.tr(u'Configurar Conexión'), self.iface.mainWindow())
        configurar_conexion_action.triggered.connect(self.run_configurar)
        self.menu.addAction(configurar_conexion_action)
        self.toolbar.addAction(configurar_conexion_action)







        # Función para mostrar el cuadro de diálogo "Acerca De" y abrir manuales
        def mostrar_acerca_de():
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Acerca De")

            docs_dir = os.path.join(self.plugin_dir, "documentos")
            manual1_path = os.path.join(docs_dir, "manual1.docx")
            manual2_path = os.path.join(docs_dir, "manual2.docx")
            manual3_path = os.path.join(docs_dir, "manual_api.docx")
            manual4_path = os.path.join(docs_dir, "manual_documental.docx")

            msg_box.setText(f'''<p><b>Herramienta de Estandarización, Validación y Consulta</b>, enfocado en los procesos misionales que lleva a cabo la Subdirección de Planeación Operativa de la Agencia Nacional de Tierras.</p>
                                        <p>Se cuenta con los siguientes manuales para los diferentes módulos:</p>
                                        <li>1. Módulo Consulta FILI: <a href="file:///{manual1_path}">Manual de Validación</a></li>
                                        <li>2. Módulo Herramientas Base de Datos: <a href="file:///{manual2_path}">Manual de Base de Datos</a></li>
                                        <li>3. Módulo API: <a href="file:///{manual3_path}">Manual API</a></li>
                                        <li>4. Módulo Documental: <a href="file:///{manual4_path}">Manual Documental</a></li>
                                    </ul>
                                    <ul>
                                    <p>By: 
                                    Ing. Mario Rodríguez - Ing. Carlos Rodríguez <br>
                                    Equipo SIG- SPO</p>
                                    ''')

            msg_box.setTextFormat(Qt.RichText)
            msg_box.setStandardButtons(QMessageBox.Ok)

            boton_librerias = QPushButton("Obtener Librerías Externas", msg_box)
            msg_box.addButton(boton_librerias, QMessageBox.ActionRole)
            boton_librerias.clicked.connect(obtener_librerias_externas)
            msg_box.exec_()




        def obtener_librerias_externas():
            drive_url_dependencias = "https://drive.google.com/uc?export=download&id=1EazXvwMAYfd4IlNSfZYIQQeOJvgtmRM5"
            drive_url_java_portable = "https://drive.usercontent.google.com/download?id=1tKBFFmKoCKSXDlFviU1asOIzVDkdoAsU&export=download&authuser=0&confirm=t&uuid=d3f46468-1032-4c9c-93c9-210e0da6287d"
            drive_url_ili2 = "https://drive.google.com/uc?export=download&id=1sAYgMMOlpPI91CQr7Xoe9_w40-5KzG04"
            drive_url_ilidb = "https://drive.usercontent.google.com/download?id=1sBZj180pfVg6NA2gPi8nnzx2kXgitPyV&export=download&authuser=0&confirm=t&uuid=6cacc1be-a7f1-4732-bc52-ff5c366dbebd&at=AN_67v1ouK2G-TqXimBUxWXA0IwV%3A1728238824718"
            
            temp_zip_dependencias = os.path.join(os.path.expanduser('~'), 'dependencias.zip')
            temp_zip_java_portable = os.path.join(os.path.expanduser('~'), 'java-portable.zip')
            temp_zip_ili2 = os.path.join(os.path.expanduser('~'), 'ili2.zip')
            temp_zip_ilidb = os.path.join(os.path.expanduser('~'), 'ilidb.zip')

            # Crear diálogo para mostrar el progreso
            progress_dialog = QDialog()
            progress_dialog.setWindowTitle("Progreso de Descarga")
            layout = QVBoxLayout()

            progress_bar = QProgressBar()
            layout.addWidget(progress_bar)

            progress_text = QTextEdit()
            progress_text.setReadOnly(True)
            layout.addWidget(progress_text)

            temp_path_label = QLabel(f"Ruta temporal: {os.path.expanduser('~')}")
            layout.addWidget(temp_path_label)

            progress_dialog.setLayout(layout)
            progress_dialog.setMinimumSize(600, 400)
            progress_dialog.show()

            # Descargar dependencias
            progress_text.append("Descargando dependencias...")
            descargar_y_extraer_zip(drive_url_dependencias, temp_zip_dependencias, os.path.expanduser('~'), progress_text, progress_bar, "Dependencias")

            # Copiar dependencias a AppData\Roaming\Python\Python39
            progress_text.append("Copiando dependencias a Python39...")
            copiar_dependencias(progress_text)

            # Descargar y copiar Java Portable
            progress_text.append("Descargando Java Portable...")
            descargar_y_extraer_zip(drive_url_java_portable, temp_zip_java_portable, os.path.expanduser('~'), progress_text, progress_bar, "Java Portable")

            progress_text.append("Copiando Java Portable a las carpetas destino...")
            copiar_java_portable(progress_text)

            # Descargar y copiar ili2
            progress_text.append("Descargando ili2...")
            descargar_y_extraer_zip(drive_url_ili2, temp_zip_ili2, os.path.expanduser('~'), progress_text, progress_bar, "ili2")

            progress_text.append("Copiando ili2 a la carpeta Herramientas...")
            copiar_ili2(progress_text)

            # Descargar y copiar ilidb
            progress_text.append("Descargando ilidb...")
            descargar_y_extraer_zip(drive_url_ilidb, temp_zip_ilidb, os.path.expanduser('~'), progress_text, progress_bar, "ilidb")

            progress_text.append("Copiando ilidb a la carpeta Herramientas...")
            copiar_ilidb(progress_text)

            # Mostrar mensaje final
            temp_path_label.setText("SE HA INSTALADO CORRECTAMENTE LAS LIBRERÍAS NECESARIAS!!")
            progress_dialog.exec_()





        # Función para copiar ili2 a la carpeta Herramientas y Herramientas/reportes/codigos
        def copiar_ili2(progress_text):
            # Definir las carpetas destino dentro de Herramientas
            herramientas_dir = os.path.join(self.plugin_dir, 'Herramientas')
            herramientas_reportes_codigos_dir = os.path.join(self.plugin_dir, 'Herramientas', 'reportes', 'codigos')

            # Definir las rutas de destino para la carpeta ili2
            ili2_dest_1 = os.path.join(herramientas_dir, 'ili2')  # Primera carpeta destino
            ili2_dest_2 = os.path.join(herramientas_reportes_codigos_dir, 'ili2')  # Segunda carpeta destino

            # Ruta temporal donde se extrajo el archivo de ili2
            ili2_src = os.path.join(os.path.expanduser('~'), 'ili2')

            if os.path.exists(ili2_src):
                progress_text.append("Copiando ili2 a las carpetas destino...")

                # Copiar a la primera ruta: Herramientas
                if os.path.exists(ili2_dest_1):
                    shutil.rmtree(ili2_dest_1)  # Eliminar solo la carpeta ili2 si ya existe
                shutil.copytree(ili2_src, ili2_dest_1)  # Copiar toda la carpeta
                progress_text.append(f"ili2 copiado exitosamente a {ili2_dest_1}.")

                # Copiar a la segunda ruta: Herramientas/reportes/codigos
                if not os.path.exists(herramientas_reportes_codigos_dir):
                    os.makedirs(herramientas_reportes_codigos_dir)  # Crear la estructura de carpetas si no existe
                if os.path.exists(ili2_dest_2):
                    shutil.rmtree(ili2_dest_2)  # Eliminar solo la carpeta ili2 si existe
                shutil.copytree(ili2_src, ili2_dest_2)
                progress_text.append(f"ili2 copiado exitosamente a {ili2_dest_2}.")
            else:
                progress_text.append(f"Error: La carpeta ili2 no fue encontrada en {ili2_src}.")

        # Función para copiar ilidb a la carpeta Herramientas y Herramientas/reportes/codigos
        def copiar_ilidb(progress_text):
            # Definir las carpetas destino dentro de Herramientas
            herramientas_dir = os.path.join(self.plugin_dir, 'Herramientas')
            herramientas_reportes_codigos_dir = os.path.join(self.plugin_dir, 'Herramientas', 'reportes', 'codigos')

            # Definir las rutas de destino para la carpeta ilidb
            ilidb_dest_1 = os.path.join(herramientas_dir, 'ilidb')  # Primera carpeta destino
            ilidb_dest_2 = os.path.join(herramientas_reportes_codigos_dir, 'ilidb')  # Segunda carpeta destino

            # Ruta temporal donde se extrajo el archivo de ilidb
            ilidb_src = os.path.join(os.path.expanduser('~'), 'ilidb')

            if os.path.exists(ilidb_src):
                progress_text.append("Copiando ilidb a las carpetas destino...")

                # Copiar a la primera ruta: Herramientas
                if os.path.exists(ilidb_dest_1):
                    shutil.rmtree(ilidb_dest_1)  # Eliminar solo la carpeta ilidb si ya existe
                shutil.copytree(ilidb_src, ilidb_dest_1)  # Copiar toda la carpeta
                progress_text.append(f"ilidb copiado exitosamente a {ilidb_dest_1}.")

                # Copiar a la segunda ruta: Herramientas/reportes/codigos
                if not os.path.exists(herramientas_reportes_codigos_dir):
                    os.makedirs(herramientas_reportes_codigos_dir)  # Crear la estructura de carpetas si no existe
                if os.path.exists(ilidb_dest_2):
                    shutil.rmtree(ilidb_dest_2)  # Eliminar solo la carpeta ilidb si existe
                shutil.copytree(ilidb_src, ilidb_dest_2)
                progress_text.append(f"ilidb copiado exitosamente a {ilidb_dest_2}.")
            else:
                progress_text.append(f"Error: La carpeta ilidb no fue encontrada en {ilidb_src}.")







        # Función para copiar dependencias a las rutas correspondientes
        def copiar_dependencias(progress_text):
            roaming_dir = os.path.expanduser('~\\AppData\\Roaming\\Python\\Python39')

            # Crear la carpeta Python39 si no existe
            if not os.path.exists(roaming_dir):
                os.makedirs(roaming_dir)

            # Crear o usar la carpeta Scripts
            scripts_dir = os.path.join(roaming_dir, 'Scripts')
            if not os.path.exists(scripts_dir):
                os.makedirs(scripts_dir)

            # Copiar los archivos de scripts desde el plugin
            plugin_scripts_dir = os.path.join(self.plugin_dir, 'dependencias', 'scripts')
            if os.path.exists(plugin_scripts_dir):
                progress_text.append("Copiando scripts...")
                for file_name in os.listdir(plugin_scripts_dir):
                    file_path = os.path.join(plugin_scripts_dir, file_name)
                    if file_name == "__pycache__":
                        continue
                    shutil.copy(file_path, scripts_dir)
                    progress_text.append(f"Copiado: {file_name}")

            # Crear o usar la carpeta site-packages
            site_packages_dir = os.path.join(roaming_dir, 'site-packages')
            if not os.path.exists(site_packages_dir):
                os.makedirs(site_packages_dir)

            # Copiar los archivos de site-packages desde el plugin
            plugin_site_packages_dir = os.path.join(self.plugin_dir, 'dependencias', 'site-packages')
            if os.path.exists(plugin_site_packages_dir):
                progress_text.append("Copiando site-packages...")
                for item in os.listdir(plugin_site_packages_dir):
                    src_path = os.path.join(plugin_site_packages_dir, item)
                    dest_path = os.path.join(site_packages_dir, item)

                    try:
                        if os.path.isdir(src_path):
                            if os.path.exists(dest_path):
                                for root, dirs, files in os.walk(src_path):
                                    for file in files:
                                        src_file = os.path.join(root, file)
                                        dest_file = os.path.join(dest_path, os.path.relpath(src_file, src_path))
                                        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                                        try:
                                            shutil.copy(src_file, dest_file)
                                            progress_text.append(f"Copiado: {file}")
                                        except PermissionError as e:
                                            progress_text.append(f"No se pudo copiar {file}: {e}")
                            else:
                                shutil.copytree(src_path, dest_path, ignore=shutil.ignore_patterns('__pycache__'))
                                progress_text.append(f"Copiada carpeta: {item}")
                        else:
                            try:
                                shutil.copy(src_path, dest_path)
                                progress_text.append(f"Copiado: {item}")
                            except PermissionError as e:
                                progress_text.append(f"No se pudo copiar {item}: {e}")
                    except PermissionError as e:
                        progress_text.append(f"No se pudo copiar {item}: {e}")

            progress_text.append("Dependencias copiadas exitosamente.")


        # Función para copiar la carpeta Java Portable a múltiples rutas sin afectar otros archivos

        def copiar_java_portable(progress_text):
            # Definir las carpetas destino dentro del plugin
            herramientas_dir = os.path.join(self.plugin_dir, 'Herramientas')
            herramientas_reportes_codigos_dir = os.path.join(self.plugin_dir, 'Herramientas', 'reportes', 'codigos')

            # Definir las rutas de destino para la carpeta java-portable
            java_portable_dest_1 = os.path.join(herramientas_dir, 'java-portable')  # Carpeta destino para java-portable en Herramientas
            java_portable_dest_2 = os.path.join(herramientas_reportes_codigos_dir, 'java-portable')  # Carpeta destino en Herramientas/reportes/codigos

            # Ruta temporal donde se extrajo el archivo de Java Portable
            java_portable_src = os.path.join(os.path.expanduser('~'), 'java-portable')

            if os.path.exists(java_portable_src):
                progress_text.append("Copiando Java Portable a las carpetas destino...")

                # Copiar a la primera ruta: Herramientas
                if os.path.exists(java_portable_dest_1):
                    shutil.rmtree(java_portable_dest_1)  # Eliminar solo la carpeta java-portable para evitar conflicto de archivos
                shutil.copytree(java_portable_src, java_portable_dest_1)
                progress_text.append(f"Java Portable copiado exitosamente a {java_portable_dest_1}.")

                # Copiar a la segunda ruta: Herramientas/reportes/codigos
                if not os.path.exists(herramientas_reportes_codigos_dir):
                    os.makedirs(herramientas_reportes_codigos_dir)  # Crear la estructura de carpetas si no existe
                if os.path.exists(java_portable_dest_2):
                    shutil.rmtree(java_portable_dest_2)  # Eliminar solo la carpeta java-portable si existe
                shutil.copytree(java_portable_src, java_portable_dest_2)
                progress_text.append(f"Java Portable copiado exitosamente a {java_portable_dest_2}.")
            else:
                progress_text.append(f"Error: La carpeta Java Portable no fue encontrada en {java_portable_src}.")







        # Función para descargar y extraer archivos ZIP con manejo de progreso
        def descargar_y_extraer_zip(url, temp_zip_path, extract_to, progress_text, progress_bar, item_name):
            try:
                # Añadir mensaje inicial de conexión
                progress_text.append(f"Conectando a {item_name} en {url}...")
                QCoreApplication.processEvents()  # Forzar la actualización de la interfaz

                with requests.get(url, stream=True) as r:
                    total_length = r.headers.get('content-length')

                    if total_length is None:
                        raise Exception("No se pudo obtener el tamaño del archivo.")

                    dl = 0
                    total_length = int(total_length)

                    # Abrir el archivo para escritura en modo binario
                    with open(temp_zip_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):  # Tamaño de chunk de 1MB
                            if chunk:
                                f.write(chunk)
                                dl += len(chunk)
                                progress_percentage = int(100 * dl / total_length)

                                # Actualizar barra de progreso y mensajes
                                progress_bar.setValue(progress_percentage)
                                progress_text.append(f"{item_name} descargado: {progress_percentage}% completado.")
                                
                                # Forzar actualización de la interfaz en cada iteración
                                QCoreApplication.processEvents()

                # Extraer el archivo ZIP
                progress_text.append(f"Extrayendo {item_name}...")
                QCoreApplication.processEvents()  # Forzar la actualización de la interfaz

                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)

                # Eliminar el archivo ZIP temporal
                os.remove(temp_zip_path)

                progress_text.append(f"{item_name} descargado y extraído exitosamente en {extract_to}.")
                QCoreApplication.processEvents()  # Forzar la actualización de la interfaz

            except zipfile.BadZipFile:
                progress_text.append(f"Error: {item_name} no es un archivo ZIP válido.")
                QMessageBox.critical(None, "Error", f"El archivo {item_name} descargado no es un archivo ZIP válido.")
            except Exception as e:
                progress_text.append(f"Error durante la descarga o extracción: {e}")
                QMessageBox.critical(None, "Error", f"Ocurrió un error durante la descarga o extracción de {item_name}: {e}")










        # Agregar "Acerca De" como acción directa al menú principal con el ícono
        acerca_de_action = QAction(icono_acerca, self.tr(u'Acerca De'), self.iface.mainWindow())
        acerca_de_action.triggered.connect(mostrar_acerca_de)
        self.menu.addAction(acerca_de_action)






        # Agregar "Herramientas BD" con el ícono de base de datos al submenú reporte
        self.add_action(icono_database, self.tr(u'Herramientas para Gestión BD FILI'), self.run_reportes, submenu=self.submenu_reporte,add_to_toolbar=True)
        self.add_action(icono_esri, self.tr(u'Load Data con Expresiones'), self.run_cargue_bd, submenu=self.submenu_reporte,add_to_toolbar=True)

        # Agregar "Cargar capas para consulta" y "Consultar" al submenú reporte
        self.add_action(icono_load_layer, self.tr(u'Cargar capas para consulta'), self.run_cargue, submenu=self.submenu_reporte,add_to_toolbar=True)
        self.add_action(icono_query, self.tr(u'Consultar'), self.run_consultas, submenu=self.submenu_reporte,add_to_toolbar=True)


        # Agregar el ícono personalizado "ico.png" al submenú FILI ANT
        self.submenu_reporte.setIcon(QIcon(icono_fili_ant))

        # Agregar el ícono personalizado "ico.png" al submenú FILI ANT
        self.submenu_tools.setIcon(QIcon(icono_tools))
        self.submenu_documental.setIcon(QIcon(icono_documental2))
        self.submenu_API.setIcon(QIcon(icono_API))
        self.submenu_seguimiento.setIcon(QIcon(icono_seguimiento))

        # Cargue masivo documental de 1 archivo version prueba
        self.add_action(icono_documental, self.tr(u'Cargue Masivo a Expedientes'), self.run_carguemasivo1, submenu=self.submenu_documental,add_to_toolbar=False)
        self.add_action(icono_documental, self.tr(u'Renombrado Adjuntos FILI (Requiere BD)'), self.run_renombrado, submenu=self.submenu_documental,add_to_toolbar=False)



        self.add_action(icono_API2, self.tr(u'R1R2 TXT IGAC'), self.run_r1r2, submenu=self.submenu_API,add_to_toolbar=False)
        self.add_action(icono_depura, self.tr(u'Depuración Espaciado SNR'), self.run_espaciossnr, submenu=self.submenu_API,add_to_toolbar=False)
        self.add_action(icono_lst, self.tr(u'Abrir .lst de Lindero/Complementación'), self.run_lst_lindero, submenu=self.submenu_API,add_to_toolbar=False)
        self.add_action(icono_derivado, self.tr(u'Cálculo Matriz/Derivado'), self.run_derivado, submenu=self.submenu_API,add_to_toolbar=False)


        self.add_action(icono_estructura, self.tr(u'Verificar Estructura GPKG'), self.run_verificarestructura, submenu=self.submenu_seguimiento,add_to_toolbar=False)
        self.add_action(icono_datosgpkg, self.tr(u'Cargar Datos a GPKG SEGUMIENTO'), self.run_cargueestructura, submenu=self.submenu_seguimiento,add_to_toolbar=False)
        self.add_action(icono_validar, self.tr(u'Validar Datos'), self.run_validargpkg, submenu=self.submenu_seguimiento,add_to_toolbar=False)




    def unload(self):
        # Eliminar todas las acciones y menús
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&JM_TOOLS'), action)
            self.iface.removeToolBarIcon(action)

        # Eliminar la barra de herramientas y el menú
        if self.toolbar:
            del self.toolbar
        if self.menu:
            self.iface.mainWindow().menuBar().removeAction(self.menu.menuAction())


    def run_carguemasivo1(self):
        from .Herramientas.carguemasivo1 import cargue_masivo
        dialog = cargue_masivo(self.iface)
        dialog.exec_()

    def run_renombrado(self):
        from .Herramientas.renombrado_imagenes import renombrado_imagenes
        dialog = renombrado_imagenes(self.iface)
        dialog.exec_()

    def run_verificarestructura(self):
        from .Herramientas.verificacion_estructura import verificacion_estructura
        dialog = verificacion_estructura(self.iface)
        dialog.exec_()

    def run_validargpkg(self):
        from .Herramientas.validar_gpkg import validar_gpkg
        dialog = validar_gpkg(self.iface)
        dialog.exec_()




    def run_cargueestructura(self):
        from .Herramientas.cargueestructura import cargue_estructura
        dialog = cargue_estructura(self.iface)
        dialog.exec_()

    def run_cargue_bd(self):
        from .Herramientas.cargue_bd import cargue_bd
        self.dialog = cargue_bd(self.iface)
        self.dialog.show() 


    def run_r1r2(self):
        from .Herramientas.r1r2 import r1r2
        dialog = r1r2(self.iface)
        dialog.exec_()

    def run_espaciossnr(self):
        from .Herramientas.espaciossnr import EspaciosSNRDialog
        dialog = EspaciosSNRDialog(self.iface)
        dialog.exec_()


    def run_lst_lindero(self):
        from .Herramientas.lst_lindero import ColumnAdjusterApp
        dialog = ColumnAdjusterApp(self.iface)
        dialog.exec_()



    def run_derivado(self):
        from .Herramientas.derivado import calculo_derivado
        dialog = calculo_derivado(self.iface)
        dialog.exec_()



    def run_feature_to_point(self):
        from .Herramientas.FeatureToPoint.FeatureToPoint import FeatureToPoint
        dialog = FeatureToPoint(self.iface)
        dialog.exec_()

    def run_feature_vertices_to_points(self):
        from .Herramientas.FeatureVerticesToPoints.FeatureVerticesToPoints import FeatureVerticesToPoints
        dialog = FeatureVerticesToPoints(self.iface)
        dialog.exec_()

    def run_summary_statistics(self):
        from .Herramientas.SummaryStatistics.SummaryStatistics import SummaryStatistics
        dialog = SummaryStatistics(self.iface)
        dialog.exec_()

    def run_terreno(self):
        from .Herramientas.Terreno.Terreno import CreateTerrenoLayer
        dialog = CreateTerrenoLayer(self.iface)
        dialog.exec_()

    def run_xy(self):
        from .Herramientas.xy.xy import XY
        dialog = XY(self.iface)
        dialog.exec_()

    def run_configurar(self):
        from .Herramientas.configurar_conexion import config_conexion
        dialog = config_conexion(self.iface)
        dialog.exec_()




    def run_consultas(self):
        # Si el DockWidget ya fue creado y sigue visible, solo enfócalo
        if hasattr(self, 'consultas_dock') and self.consultas_dock is not None:
            if self.consultas_dock.isVisible():
                self.consultas_dock.raise_()  # Trae el DockWidget al frente si está visible
                return
            else:
                # Si fue cerrado, elimínalo de la referencia para que pueda recrearse
                self.consultas_dock = None

        # Crear una nueva instancia si no está abierto o fue cerrado
        from .Herramientas.consultas import ConsultasDockWidget
        self.consultas_dock = ConsultasDockWidget(self.iface)

        # Conectar la señal 'visibilityChanged' del DockWidget para detectar el cierre
        self.consultas_dock.visibilityChanged.connect(self.on_consultas_dock_closed)

        # Añadir el DockWidget a la interfaz de QGIS
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.consultas_dock)


    def on_consultas_dock_closed(self, visible):
        """
        Se ejecuta cuando el DockWidget cambia su visibilidad.
        Si el DockWidget se cierra (se vuelve invisible), restablece la referencia.
        """
        if not visible:  # Si el DockWidget ya no es visible (se cerró)
            self.consultas_dock = None  # Restablecer la referencia



    def run_cargue(self):
        """
        Función que se invoca cuando presionas el botón para cargar capas y unidades de construcción.
        Llama a las funciones cargar_capa_terreno() y cargar_unidades_construccion() de la clase ConsultasDockWidget.
        """
        # Asegúrate de que el ConsultasDockWidget está inicializado
        if not hasattr(self, 'consultas_dock') or self.consultas_dock is None:
            self.consultas_dock = ConsultasDockWidget(self.iface)  # Si no está inicializado, crearlo
        
        # Llamar las funciones dentro de ConsultasDockWidget
        self.consultas_dock.cargar_capa_terreno()
        self.consultas_dock.cargar_unidades_construccion()



        

    def run_reportes(self):
        try:
            from .Herramientas.reportes.Reportes_BD import ReportGeneratorApp

            # Crear la ventana de reportes y mostrarla
            self.dialog = ReportGeneratorApp(self.iface)
            
            # Usar show() ya que es un QMainWindow
            self.dialog.show()

            # Mantener la ventana abierta y asegurar que el ciclo de eventos esté activo
            self.iface.mainWindow().show()

        except Exception as e:
            # Mostrar un mensaje de error en caso de que algo falle
            print(f"Error al crear la ventana de reportes: {e}")