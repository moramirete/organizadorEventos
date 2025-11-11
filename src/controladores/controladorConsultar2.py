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

from interfazHomeEventoMesas import Ui_EventoMesas


class ControladorConsultar2:
    """Controlador mínimo para la ventana 'EventoMesas'.

    - Crea una QMainWindow con la UI de mesas.
    - Conecta el botón 'Volver' para cerrar esta ventana y mostrar la ventana padre.
    """
    def __init__(self, parent_window: QMainWindow = None):
        self.parent_window = parent_window
        self.window = QMainWindow()
        self.ui = Ui_EventoMesas()
        self.ui.setupUi(self.window)

        # Conectar botón Volver
        try:
            self.ui.btnVolver.clicked.connect(self._on_volver)
        except Exception:
            pass

        self.window.show()

    def _on_volver(self):
        # Cerrar la ventana actual y mostrar la ventana padre si existe
        try:
            self.window.close()
        except Exception:
            pass
        if self.parent_window is not None:
            try:
                self.parent_window.show()
            except Exception:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ctrl = ControladorConsultar2()
    sys.exit(app.exec_())
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