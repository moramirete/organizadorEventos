import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# --- INICIO: CORRECCIÓN DE RUTA DE IMPORTACIÓN PARA MODULOS ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)
# --- FIN: CORRECCIÓN DE RUTA DE IMPORTACIÓN ---

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeEventoMesas import Ui_EventoMesas


class ControladorConsultar2:
    
    # ACEPTA EL CONTROLADOR PADRE
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller  # Almacenamos la referencia a ControladorHome
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
        self.ui.btnVolver.clicked.connect(self.volver_ventana_principal)
        # FALTA EL BOTON EXPORTARCSV

    # Método para abrir la ventana del evento con sus datos (la vista de mesas)
    
    
    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos)
        self.main_window.hide()