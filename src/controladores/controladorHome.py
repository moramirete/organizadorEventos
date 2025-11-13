import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# Ajusto la ruta para poder importar las interfaces .py del proyecto
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeModificarListadoEventos import Ui_EventosGestion
from controladorConsultar1 import ControladorConsultar1
from controladorModificarEventos import controladorModificarEventos
from controladorNuevoEvento import controladorNuevoEvento


class ControladorHome:
    def __init__(self, main_window: QMainWindow, ui: Ui_MainWindow):
        # Ventana principal y su interfaz
        self.main_window = main_window
        self.ui = ui
        
        # Lista donde se guardan todos los eventos de la aplicación
        self.eventos = []

        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None
        self.consultar_controller = None

        # Conecto los botones del menú principal
        self.conectar_senales()
        
    def conectar_senales(self):
        # Botón para ir a consultar eventos
        self.ui.btnConsultar.clicked.connect(self.abrir_consultar_eventos)
        # Botón para crear un evento nuevo
        self.ui.btnNuevo.clicked.connect(self.abrir_nuevo_evento)
        # Botón para modificar/eliminar eventos
        self.ui.btnModificar.clicked.connect(self.abrir_modificar_eventos)

    def abrir_consultar_eventos(self):
        # Abro la ventana con el listado de eventos
        self.consultar_window = QMainWindow()
        consultar_ui = Ui_EventosListado()
        consultar_ui.setupUi(self.consultar_window)
        
        # Controlador de la pantalla de consulta, le paso este como padre
        self.consultar_controller = ControladorConsultar1(
            self.consultar_window,
            consultar_ui,
            self
        )
        
        self.consultar_window.show()
        # Si quisiera ocultar el home, descomento:
        # self.main_window.hide()

    def abrir_nuevo_evento(self):
        # Abro la ventana para crear un evento nuevo
        self.nuevo_window = QMainWindow()
        nuevo_ui = Ui_EventoEditar()
        nuevo_ui.setupUi(self.nuevo_window)

        # Controlador que gestiona la creación del evento
        self.nuevo_controller = controladorNuevoEvento(
            self.nuevo_window,
            nuevo_ui,
            self
        )
        
        self.nuevo_window.show()
        # self.main_window.hide()
    
    def abrir_modificar_eventos(self):
        # Abro la ventana para gestionar (modificar/borrar) eventos
        self.modificar_window = QMainWindow()
        modificar_ui = Ui_EventosGestion()
        modificar_ui.setupUi(self.modificar_window)

        # Controlador que maneja la parte de modificación
        self.modificar_controller = controladorModificarEventos(
            self.modificar_window,
            modificar_ui,
            self
        )
        
        self.modificar_window.show()
        # self.main_window.hide()


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    sys.exit(app.exec_())
