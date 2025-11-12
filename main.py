import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# --- INICIO: CORRECCIÓN DE RUTA DE IMPORTACIÓN PARA MÓDULOS ---
# 1. Determina la ruta absoluta del directorio actual (la raíz del proyecto).
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_script_dir 

# 2. Define las rutas de las interfaces y controladores.
interface_path = os.path.join(project_root, 'interfazes', 'python')
controladores_path = os.path.join(project_root, 'src', 'controladores')

# 3. Añade ambas rutas a sys.path para que Python pueda encontrar los módulos.
if interface_path not in sys.path:
    sys.path.append(interface_path)

if controladores_path not in sys.path:
    sys.path.append(controladores_path)
# --- FIN: CORRECCIÓN DE RUTA DE IMPORTACIÓN ---

from controladorHome import ControladorHome
from interfazHome import Ui_MainWindow


def run_application():
    """Función principal para inicializar y ejecutar la aplicación."""
    
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_application()