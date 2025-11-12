import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication


current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)


from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager


class controladorEditarEvento:
    
   
    def __init__(self, main_window: QMainWindow, ui: Ui_EventoEditar, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        
        self.siguiente_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    # Método para ir a la siguiente interfaz (interfazHomeParticipantesMesas)
    def ir_siguiente_interfaz(self):
        self.siguiente_window = QMainWindow() 
        siguiente_ui = Ui_ParticipantsManager() 
        siguiente_ui.setupUi(self.siguiente_window)
        
        self.siguiente_window.show()
        
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Mostramos la ventana anterior a través del controlador padre
        self.parent_controller.main_window.show()
        
        self.main_window.hide()
