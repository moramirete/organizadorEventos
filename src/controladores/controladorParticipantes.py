import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets

# Configurar la ruta para importar las interfaces
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorMesas import ControladorMesas


class ControladorParticipantes:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.mesas_window = None
        
        self.conectar_botones()
        
    def conectar_botones(self):
        # Conectar el botón Siguiente
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Conectar el botón Cancelar (volver atrás)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    def ir_siguiente_interfaz(self):
        # Importar la interfaz de mesas
        from interfazHomeModificarListadoEventosAsignacionInvitados import Ui_AsignacionesInvitados
        
        # Crear ventana de mesas
        self.mesas_window = QMainWindow() 
        mesas_ui = Ui_AsignacionesInvitados() 
        mesas_ui.setupUi(self.mesas_window)

        # Crear controlador de mesas
        self.mesas_controller = ControladorMesas(self.mesas_window, mesas_ui, self)
        
        # Mostrar ventana de mesas y ocultar la actual
        self.mesas_window.show()
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Mostrar ventana anterior
        self.parent_controller.main_window.show()
        
        # Ocultar ventana actual
        self.main_window.hide()
