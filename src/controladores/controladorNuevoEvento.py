import sys
import os
from PyQt5.QtWidgets import QMainWindow

# Configurar la ruta para importar las interfaces
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes


class controladorNuevoEvento:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.siguiente_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
        # Conectar botón Siguiente
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Conectar botón Cancelar
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    def ir_siguiente_interfaz(self):
        # Crear ventana de participantes
        self.siguiente_window = QMainWindow() 
        siguiente_ui = Ui_ParticipantsManager() 
        siguiente_ui.setupUi(self.siguiente_window)
        
        # Crear controlador de participantes
        self.participantes_controller = ControladorParticipantes(
            self.siguiente_window, 
            siguiente_ui, 
            self  
        )
        
        # Mostrar ventana de participantes y ocultar la actual
        self.siguiente_window.show()
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Mostrar ventana anterior (Home)
        self.parent_controller.main_window.show()
        
        # Ocultar ventana actual
        self.main_window.hide()
        self.parent_controller.main_window.show()
        
        self.main_window.hide()