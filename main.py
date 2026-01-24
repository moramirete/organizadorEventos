import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# --- CORRECCIÓN DE RUTAS GENERAL PARA TODO EL PROYECTO ---
# Se asume que este archivo está en la raíz del proyecto.
project_root = os.path.dirname(os.path.abspath(__file__))

# Rutas a añadir:
interface_path = os.path.join(project_root, 'interfazes', 'python')
controladores_path = os.path.join(project_root, 'src', 'controladores')
src_path = os.path.join(project_root, 'src')

# Añadir las rutas al sistema:
if interface_path not in sys.path:
    sys.path.append(interface_path)

if controladores_path not in sys.path:
    sys.path.append(controladores_path)

if src_path not in sys.path:
    sys.path.append(src_path)
# --------------------------------------------------------

# Importar las clases controladoras e interfaces
from controladorLogin import ControladorLogin
from interfazLogin import Ui_LoginWindow


def run_application():
    """Función principal para inicializar y ejecutar la aplicación."""
    app = QApplication(sys.argv)
    
    LoginWindow = QMainWindow()
    ui = Ui_LoginWindow()
    ui.setupUi(LoginWindow)
    
    # Inicializa el ControladorLogin, que gestionará el flujo inicial
    controller = ControladorLogin(LoginWindow, ui)
    
    LoginWindow.show()
    
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