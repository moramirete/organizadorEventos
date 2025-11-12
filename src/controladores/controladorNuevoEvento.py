import sys
import os
from PyQt5.QtWidgets import QMainWindow

# Configurar la ruta para importar las interfaces
current_dir = os.path.dirname(os.path.abspath(_file_))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes

# Asegurar que podemos importar los modelos (src en sys.path)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from modelos.evento import Evento
from PyQt5 import QtWidgets, QtCore


class controladorNuevoEvento:
    
    def _init_(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.siguiente_window = None
        # Estado de guardado
        self.evento = Evento()
        self.cambios_guardados = False

        self.conectar_botones()
        
    def conectar_botones(self):
        # Conectar botón Siguiente
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Conectar botón Guardar
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

        # Conectar botón Cancelar
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    def ir_siguiente_interfaz(self):
        # Sólo dejar pasar si se han guardado los cambios en esta ventana
        if not self.cambios_guardados:
            QtWidgets.QMessageBox.warning(self.main_window, 'Guardar Cambios', 'Debes guardar los cambios antes de continuar.')
            return

        # Crear ventana de participantes
        self.siguiente_window = QMainWindow() 
        siguiente_ui = Ui_ParticipantsManager() 
        siguiente_ui.setupUi(self.siguiente_window)
        
        # Crear controlador de participantes
        self.participantes_controller = ControladorParticipantes(
            self.siguiente_window, 
            siguiente_ui, 
            self  
        )

        # Pasar el evento guardado al controlador de participantes
        self.participantes_controller.evento = self.evento
        
        # Mostrar ventana de participantes y ocultar la actual
        self.siguiente_window.show()
        self.main_window.hide()

    def guardar_cambios(self):
        # Leer campos y guardar en el POJO Evento
        nombre = self.ui.leNombre.text().strip()
        num_mesas = int(self.ui.sbMesas.value())
        inv_por_mesa = int(self.ui.sbInvPorMesa.value())
        fecha = self.ui.deFecha.date().toString('yyyy-MM-dd')
        cliente = self.ui.leCliente.text().strip()
        telefono = self.ui.leTelefono.text().strip()

        if not nombre or num_mesas or inv_por_mesa or fecha or cliente or telefono:
            QtWidgets.QMessageBox.warning(self.main_window, 'Validación', 'El nombre del evento es obligatorio.')
            return

        # Guardar en el objeto evento
        self.evento = Evento(nombre, num_mesas, inv_por_mesa, fecha, cliente, telefono)
        self.cambios_guardados = True

        QtWidgets.QMessageBox.information(self.main_window, 'Guardar', 'Evento guardado correctamente.')
    
    def volver_ventana_anterior(self):
        # Mostrar ventana anterior (Home)
        self.parent_controller.main_window.show()
        
        # Ocultar ventana actual
        self.main_window.hide()
        self.parent_controller.main_window.show()
        
        self.main_window.hide()