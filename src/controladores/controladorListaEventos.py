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

class controladorListaEventos:
    # ACEPTA EL CONTROLADOR PADRE
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller  # Almacenamos la referencia a ControladorHome
        
        self.conectar_botones()

    def conectar_botones(self):
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_principal)

    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos)
        self.main_window.hide()
