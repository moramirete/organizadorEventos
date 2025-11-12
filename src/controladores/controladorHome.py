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
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeModificarListadoEventos import Ui_EventosGestion
from controladorConsultar1 import ControladorConsultar1
from controladorModificarEventos import controladorModificarEventos 
from controladorInformacionEvento import controladorInformacionEvento

class ControladorHome:
    def __init__(self, main_window: QMainWindow, ui: Ui_MainWindow):
        self.main_window = main_window 
        self.ui = ui
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None
        self.consultar_controller = None

        self.conectar_senales()
        
    def conectar_senales(self):
        self.ui.btnConsultar.clicked.connect(self.abrir_consultar_eventos)
        self.ui.btnNuevo.clicked.connect(self.abrir_nuevo_evento)
        self.ui.btnModificar.clicked.connect(self.abrir_modificar_eventos)

    def abrir_consultar_eventos(self):
        self.consultar_window = QMainWindow() 
        consultar_ui = Ui_EventosListado() 
        consultar_ui.setupUi(self.consultar_window)
        
        # Se pasa 'self' (instancia de ControladorHome) como controlador padre
        self.consultar_controller = ControladorConsultar1(
            self.consultar_window, 
            consultar_ui, 
            self  
        )
        
        self.consultar_window.show()
        # self.main_window.hide() <--- Removido/Comentado
        

    def abrir_nuevo_evento(self):
        self.nuevo_window = QMainWindow() 
        nuevo_ui = Ui_EventoEditar() 
        nuevo_ui.setupUi(self.nuevo_window)

        self.nuevo_controler = ControladorConsultar1(
            self.consultar_window, 
            nuevo_ui, 
            self  
        )
        
        self.nuevo_window.show()
        # self.main_window.hide() <--- Removido/Comentado
    
    def abrir_modificar_eventos(self):
        self.modificar_window = QMainWindow() 
        modificar_ui = Ui_EventosGestion() 
        modificar_ui.setupUi(self.modificar_window)

        # Uso modificar_ui y modificar_window para el modificar controller,
        # y se almacena separado así no se sobreescribe consultar_controller.
        self.modificar_controller = controladorModificarEventos(
            self.modificar_window, 
            modificar_ui, 
            self  
        )
        
        self.modificar_window.show()
        # self.main_window.hide() <--- Removido/Comentado

# --- Bloque de ejecución principal para la aplicación (Main) ---

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    sys.exit(app.exec_())