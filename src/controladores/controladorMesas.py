import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets

# Configurar la ruta para importar las interfaces
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosAsignacionInvitados import Ui_AsignacionesInvitados


class ControladorMesas:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        
        self.conectar_botones()
        
    def conectar_botones(self):
        # Conectar el botón Volver
        self.ui.btnVolver.clicked.connect(self.volver_a_home)
        
        
        self.ui.btnGuardar.clicked.connect(self.guardar_asignacion)

    def volver_a_home(self):
       #Para voler al menu principal home 
        home_controller = self.parent_controller.parent_controller.parent_controller
        
        
        home_controller.main_window.show()
        self.main_window.hide()
    
    def guardar_asignacion(self):
        respuesta = QtWidgets.QMessageBox.question(
            self.main_window,
            'Guardar',
            '¿Guardar la asignación de mesas?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        # Si presiona Sí, mostrar mensaje de éxito
        if respuesta == QtWidgets.QMessageBox.Yes:
            QtWidgets.QMessageBox.information(
                self.main_window,
                'Éxito',
                'Asignación guardada correctamente.'
            )
