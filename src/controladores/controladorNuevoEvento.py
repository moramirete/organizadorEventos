import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore

# Preparo la ruta para poder importar las interfaces .py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes

# Añado src al path para poder importar los modelos
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from modelos.evento import Evento


class controladorNuevoEvento:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        # Referencia al controlador principal (Home)
        self.parent_controller = parent_controller
        self.siguiente_window = None

        # Evento que se rellena con los datos del formulario
        self.evento = Evento()
        # Para saber si se han guardado los cambios
        self.cambios_guardados = False

        self.conectar_botones()
        
    def conectar_botones(self):
        # Botón para pasar a la pantalla de participantes/mesas
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Botón para guardar el evento
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

        # Botón para volver al menú principal
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    def ir_siguiente_interfaz(self):
        # Solo dejo continuar si antes se han guardado los cambios
        if not self.cambios_guardados:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Guardar Cambios',
                'Debes guardar los cambios antes de continuar.'
            )
            return

        # Creo la ventana para gestionar participantes y mesas
        self.siguiente_window = QMainWindow()
        siguiente_ui = Ui_ParticipantsManager()
        siguiente_ui.setupUi(self.siguiente_window)
        
        # Creo el controlador de participantes y le paso este como padre
        self.participantes_controller = ControladorParticipantes(
            self.siguiente_window,
            siguiente_ui,
            self
        )

        # Paso el evento al controlador de participantes
        self.participantes_controller.evento = self.evento
        
        # Muestro la nueva ventana y oculto la actual
        self.siguiente_window.show()
        self.main_window.hide()

    def guardar_cambios(self):
        # Cojo los datos escritos en el formulario
        nombre = self.ui.leNombre.text().strip()
        num_mesas = int(self.ui.sbMesas.value())
        inv_por_mesa = int(self.ui.sbInvPorMesa.value())
        fecha = self.ui.deFecha.date().toString('yyyy-MM-dd')
        cliente = self.ui.leCliente.text().strip()
        telefono = self.ui.leTelefono.text().strip()

        # Compruebo que al menos haya nombre
        if not nombre:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Validación',
                'El nombre del evento es obligatorio.'
            )
            return

        # Guardo los datos en el objeto Evento
        self.evento = Evento(nombre, num_mesas, inv_por_mesa, fecha, cliente, telefono)
        self.cambios_guardados = True

        # Añado el evento a la lista general del Home si aún no está
        if self.evento not in self.parent_controller.eventos:
            self.parent_controller.eventos.append(self.evento)

        QtWidgets.QMessageBox.information(
            self.main_window,
            'Guardar',
            'Evento guardado correctamente.'
        )
    
    def volver_ventana_anterior(self):
        # Vuelvo a mostrar la ventana principal
        self.parent_controller.main_window.show()
        # Oculto la ventana de nuevo evento
        self.main_window.hide()
