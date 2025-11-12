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
from interfazHomeEventoMesas import Ui_EventoMesas

class ControladorHome:
    # Esto es para que se inice el controlador
    def __init__(self, main_window: QMainWindow, ui: Ui_MainWindow):
        self.main_window = main_window 
        self.ui = ui
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None

        self.conectar_botones()
        
    def conectar_botones(self):
         self.ui.btnConsultar.clicked.connect(self.abrir_consultar_eventos)
        #  self.ui.btnExportarCSV.clicked.connect(self.exportar_CSV)
         self.ui.btnModificar.clicked.connect(self.volver_ventana_principal)

    # Metodo para abrir la ventana del evento con sus datos

    # def abrir_consultar_evento_creado(self):
        # self.consultar_window = QMainWindow() 
        # consultar_ui = Ui_EventoMesas() 
        # consultar_ui.setupUi(self.consultar_window)
        
        # self.consultar_window.show()
        # self.main_window.hide()

    def abrir_consultar_eventos(self):
        self.consultar_window = QMainWindow() 
        consultar_ui = Ui_EventoMesas() 
        consultar_ui.setupUi(self.consultar_window)
        
        self.consultar_window.show()
        self.main_window.hide()

    # def exportar_CSV(self):
        # self.nuevo_window = QMainWindow() 
        # nuevo_ui = Ui_EventoEditar() 
        # nuevo_ui.setupUi(self.nuevo_window)
        
        # self.nuevo_window.show()
        # self.main_window.hide()
    
    def volver_ventana_principal(self):
        self.modificar_window = QMainWindow() 
        modificar_ui = Ui_MainWindow() 
        modificar_ui.setupUi(self.modificar_window)
        
        self.modificar_window.show()
        self.main_window.hide()

# Main

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    sys.exit(app.exec_())