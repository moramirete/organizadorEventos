import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# --- INICIO: CORRECCIÓN DE RUTA DE IMPORTACIÓN PARA MODULOS ---
# 1. Determinar el directorio base del script actual (e.g., C:\organizadorEventos\src\controladores)
current_script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Subir dos niveles para llegar a la carpeta raíz del proyecto (e.g., C:\organizadorEventos)
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))

# 3. Definir la ruta completa donde se encuentran los archivos de interfaz (interfazes/python)
interface_path = os.path.join(project_root, 'interfazes', 'python')

# 4. Añadir la ruta al sistema de búsqueda de módulos de Python (sys.path)
if interface_path not in sys.path:
    sys.path.append(interface_path)
# --- FIN: CORRECCIÓN DE RUTA DE IMPORTACIÓN ---

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeModificarListadoEventos import Ui_EventosGestion

class ControladorHome:
    def __init__(self, main_window: QMainWindow, ui: Ui_MainWindow):
        self.main_window = main_window 
        self.ui = ui
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None

        self.conectar_senales()
        
    def conectar_senales(self):
        self.ui.btnConsultar.clicked.connect(self.abrir_consultar_eventos)
        self.ui.btnNuevo.clicked.connect(self.abrir_nuevo_evento)
        self.ui.btnModificar.clicked.connect(self.abrir_modificar_eventos)

    def abrir_consultar_eventos(self):
        self.consultar_window = QMainWindow() 
        consultar_ui = Ui_EventosListado() 
        consultar_ui.setupUi(self.consultar_window)
        
        self.consultar_window.show()
        self.main_window.hide()

    def abrir_nuevo_evento(self):
        self.nuevo_window = QMainWindow() 
        nuevo_ui = Ui_EventoEditar() 
        nuevo_ui.setupUi(self.nuevo_window)
        
        self.nuevo_window.show()
        self.main_window.hide()
    
    def abrir_modificar_eventos(self):
        self.modificar_window = QMainWindow() 
        modificar_ui = Ui_EventosGestion() 
        modificar_ui.setupUi(self.modificar_window)
        
        self.modificar_window.show()
        self.main_window.hide()



