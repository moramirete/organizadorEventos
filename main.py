import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# --- CORRECCIÓN DE RUTAS GENERAL PARA TODO EL PROYECTO ---
# Se asume que este archivo está en la raíz del proyecto.
project_root = os.path.dirname(os.path.abspath(__file__))

# Rutas a añadir:
interface_path = os.path.join(project_root, 'interfazes', 'python')
controladores_path = os.path.join(project_root, 'src', 'controladores')

# Añadir ambas rutas al sistema:
if interface_path not in sys.path:
    sys.path.append(interface_path)

if controladores_path not in sys.path:
    sys.path.append(controladores_path)
# --------------------------------------------------------

# Importar las clases controladoras e interfaces
from controladorHome import ControladorHome
from interfazHome import Ui_MainWindow


def run_application():
    """Función principal para inicializar y ejecutar la aplicación."""
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    # Inicializa el ControladorHome, que gestionará el flujo inicial
    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('Error en el bucle de la aplicación:', e)

if __name__ == "__main__":
    try:
        run_application()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('Error al iniciar la aplicación:', e)