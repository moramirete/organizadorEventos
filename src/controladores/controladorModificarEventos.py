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

from interfazHomeModificarListadoEventos import Ui_EventosGestion
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeEvento import Ui_EventosListado
from controladorEditarEvento import controladorEditarEvento


class controladorModificarEventos:
    
    # ACEPTA EL CONTROLADOR PADRE
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosGestion, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller  # Almacenamos la referencia al controlador padre
        
        self.editar_window = None
        self.siguiente_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
        self.ui.btnEditar.clicked.connect(self.abrir_editar_evento)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_principal)

    # Método para abrir la ventana de edición del evento
    def abrir_editar_evento(self):
        self.editar_window = QMainWindow() 
        editar_ui = Ui_EventoEditar() 
        editar_ui.setupUi(self.editar_window)
        
        # Crear el controlador para el editor de evento
        self.editar_controller = controladorEditarEvento(
            self.editar_window,
            editar_ui,
            self  # Pasamos la referencia a este controlador como padre
        )
        
        self.editar_window.show()
        # Ocultamos la ventana actual (Listado de Eventos para modificar)
        self.main_window.hide()
    
    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos para modificar)
        self.main_window.hide()
