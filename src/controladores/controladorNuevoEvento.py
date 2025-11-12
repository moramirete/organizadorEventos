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


# ¡ESTAS LÍNEAS ERAN LAS FALTANTES!
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager


class controladorNuevoEvento:
    
   
    # La pista de tipo Ui_EventoEditar ahora es reconocida
    def __init__(self, main_window: QMainWindow, ui: Ui_EventoEditar, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller # Almacenamos la referencia a ControladorHome
        
        self.siguiente_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
        # Asumiendo que Nuevo Evento tiene los mismos botones de navegación que Editar Evento
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)
        
        # Guardar Cambios para Nuevo Evento debería ser un 'Crear Evento'

    # Método para ir a la siguiente interfaz (interfazHomeParticipantesMesas)
    def ir_siguiente_interfaz(self):
        self.siguiente_window = QMainWindow() 
        siguiente_ui = Ui_ParticipantsManager() 
        siguiente_ui.setupUi(self.siguiente_window)
        
        # Aquí también deberías inicializar el controlador de la siguiente ventana
        # (p.ej., ControladorParticipantes) si existiera.
        
        self.siguiente_window.show()
        
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Mostramos la ventana anterior (ControladorHome)
        self.parent_controller.main_window.show()
        
        self.main_window.hide()