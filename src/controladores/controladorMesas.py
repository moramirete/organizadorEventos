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

# Añadir src al path para importar el algoritmo
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Intentar importar el algoritmo de optimización
try:
    from algoritmos.algoritmo import Persona as AlgPersona, asignar_mesas_optimizando
except Exception:
    AlgPersona = None
    asignar_mesas_optimizando = None


class ControladorMesas:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.evento = None
        self.mesas = []  # lista de dicts: {'id':1,'capacidad':x,'invitados':[nombres]}
        
        self.conectar_botones()
        # no iniciamos todavía; el controlador padre debe pasar self.evento y llamar iniciar()
        
    def conectar_botones(self):
        # Conectar el botón Volver
        try:
            self.ui.btnVolver.clicked.connect(self.volver_a_home)
        except Exception:
            pass

        try:
            self.ui.btnGuardar.clicked.connect(self.guardar_asignacion)
        except Exception:
            pass

        try:
            self.ui.btnAuto.clicked.connect(self.asignacion_automatica)
        except Exception:
            pass

        try:
            self.ui.btnAsignar.clicked.connect(self.asignar_seleccionado)
        except Exception:
            pass

        try:
            self.ui.btnQuitar.clicked.connect(self.quitar_seleccionado)
        except Exception:
            pass

        try:
            self.ui.btnReiniciar.clicked.connect(self.reiniciar_asignaciones)
        except Exception:
            pass

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

    def iniciar(self):
        # Llamar después de asignar self.evento
        if self.evento is None:
            return
        # crear estructura de mesas
        self.mesas = []
        for i in range(max(0, int(self.evento.num_mesas))):
            self.mesas.append({'id': i+1, 'capacidad': int(self.evento.inv_por_mesa), 'invitados': []})

        self.reiniciar_asignaciones()