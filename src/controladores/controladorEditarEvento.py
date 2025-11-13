import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore

# Configuro la ruta para poder importar las interfaces .py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes

# Añado src para poder importar los modelos
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from modelos.evento import Evento


class controladorEditarEvento:
    
    def __init__(self, main_window, ui, parent_controller):
        # Guardo la ventana, la interfaz y el controlador padre
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller

        self.siguiente_window = None
        self.evento = None   # Aquí se asigna el evento que queremos editar
        self.cambios_guardados = False

        # Conecto los botones de la pantalla
        self.conectar_botones()
        
    def conectar_botones(self):
        # Botón para ir a la pantalla de participantes/mesas
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        # Botón para volver atrás
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)
        # Botón para guardar cambios del evento
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            # Por si en el .ui todavía no está el botón creado
            pass

    def cargar_datos_evento(self):
        """Carga en los campos de la interfaz los datos del evento actual."""
        if self.evento is None:
            # Si no viene ningún evento, creo uno vacío
            self.evento = Evento()
            return

        self.ui.leNombre.setText(self.evento.nombre)
        self.ui.sbMesas.setValue(int(self.evento.num_mesas))
        self.ui.sbInvPorMesa.setValue(int(self.evento.inv_por_mesa))
        self.ui.deFecha.setDate(QtCore.QDate.fromString(self.evento.fecha, 'yyyy-MM-dd'))
        self.ui.leCliente.setText(self.evento.cliente)
        self.ui.leTelefono.setText(self.evento.telefono)

    def ir_siguiente_interfaz(self):
        # Solo dejo pasar si antes se han guardado los cambios
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

        # Le paso el evento que estamos editando
        self.participantes_controller.evento = self.evento

        # Muestro la ventana de participantes y oculto la actual
        self.siguiente_window.show()
        self.main_window.hide()

    def guardar_cambios(self):
        # Cojo los valores de los campos de la interfaz
        nombre = self.ui.leNombre.text().strip()
        num_mesas = int(self.ui.sbMesas.value())
        inv_por_mesa = int(self.ui.sbInvPorMesa.value())
        fecha = self.ui.deFecha.date().toString('yyyy-MM-dd')
        cliente = self.ui.leCliente.text().strip()
        telefono = self.ui.leTelefono.text().strip()

        if not nombre:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Validación',
                'Debes rellenar todos los campos.'
            )
            return

        # Actualizo el mismo objeto evento para no perder la referencia
        if self.evento is None:
            self.evento = Evento(nombre, num_mesas, inv_por_mesa, fecha, cliente, telefono)
        else:
            # Compruebo si han cambiado el número de mesas o la capacidad por mesa
            cambio_mesas = (
                self.evento.num_mesas != num_mesas or 
                self.evento.inv_por_mesa != inv_por_mesa
            )
            
            # Actualizo los datos básicos del evento
            self.evento.nombre = nombre
            self.evento.num_mesas = num_mesas
            self.evento.inv_por_mesa = inv_por_mesa
            self.evento.fecha = fecha
            self.evento.cliente = cliente
            self.evento.telefono = telefono
            
            # Si cambia la configuración de mesas, reajusto las asignaciones
            if cambio_mesas:
                asignaciones_antiguas = getattr(self.evento, 'asignaciones_mesas', [])
                
                nuevas_asignaciones = []
                for i in range(num_mesas):
                    # Intento mantener a los invitados que ya estaban sentados
                    if i < len(asignaciones_antiguas):
                        invitados_antiguos = asignaciones_antiguas[i].get('invitados', [])
                        # Me quedo solo con los que caben en la nueva capacidad
                        invitados = invitados_antiguos[:inv_por_mesa]
                    else:
                        invitados = []
                    
                    nuevas_asignaciones.append({
                        'id': i + 1,
                        'capacidad': inv_por_mesa,
                        'invitados': invitados
                    })
                
                self.evento.asignaciones_mesas = nuevas_asignaciones

        self.cambios_guardados = True
        QtWidgets.QMessageBox.information(
            self.main_window,
            'Guardar',
            'Evento guardado correctamente.'
        )
    
    def volver_ventana_anterior(self):
        # Antes de volver, recargo los eventos en el controlador padre si tiene el método
        if hasattr(self.parent_controller, 'cargar_eventos'):
            self.parent_controller.cargar_eventos()
        
        # Muestro la ventana anterior (listado de eventos) y oculto esta
        self.parent_controller.main_window.show()
        self.main_window.hide()
