import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore

# Configurar la ruta para importar las interfaces
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes

src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from modelos.evento import Evento


class controladorEditarEvento:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.siguiente_window = None
        self.evento = None   # se asignará desde fuera
        self.cambios_guardados = False

        self.conectar_botones()
        
    def conectar_botones(self):
        # Conectar botón Siguiente
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Conectar botón Cancelar
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

        # Botón guardar
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

    def cargar_datos_evento(self):
        """Rellena los campos de la UI con los datos del evento actual."""
        if self.evento is None:
            self.evento = Evento()
            return

        self.ui.leNombre.setText(self.evento.nombre)
        self.ui.sbMesas.setValue(int(self.evento.num_mesas))
        self.ui.sbInvPorMesa.setValue(int(self.evento.inv_por_mesa))
        self.ui.deFecha.setDate(QtCore.QDate.fromString(self.evento.fecha, 'yyyy-MM-dd'))
        self.ui.leCliente.setText(self.evento.cliente)
        self.ui.leTelefono.setText(self.evento.telefono)

    def ir_siguiente_interfaz(self):
        # Sólo permitir si guardado
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

        # Pasar evento
        self.participantes_controller.evento = self.evento

        # Mostrar ventana de participantes y ocultar la actual
        self.siguiente_window.show()
        self.main_window.hide()

    def guardar_cambios(self):
        nombre = self.ui.leNombre.text().strip()
        num_mesas = int(self.ui.sbMesas.value())
        inv_por_mesa = int(self.ui.sbInvPorMesa.value())
        fecha = self.ui.deFecha.date().toString('yyyy-MM-dd')
        cliente = self.ui.leCliente.text().strip()
        telefono = self.ui.leTelefono.text().strip()

        if not nombre:
            QtWidgets.QMessageBox.warning(self.main_window, 'Validación', 'Debes rellenar todos los campos.')
            return

        # 👉 ACTUALIZAR EL MISMO OBJETO, NO CREAR UNO NUEVO
        if self.evento is None:
            self.evento = Evento(nombre, num_mesas, inv_por_mesa, fecha, cliente, telefono)
        else:
            # Verificar si cambió el número de mesas o capacidad
            cambio_mesas = (self.evento.num_mesas != num_mesas or 
                           self.evento.inv_por_mesa != inv_por_mesa)
            
            self.evento.nombre = nombre
            self.evento.num_mesas = num_mesas
            self.evento.inv_por_mesa = inv_por_mesa
            self.evento.fecha = fecha
            self.evento.cliente = cliente
            self.evento.telefono = telefono
            
            # Si cambió la configuración de mesas, ajustar las asignaciones
            if cambio_mesas:
                asignaciones_antiguas = getattr(self.evento, 'asignaciones_mesas', [])
                
                # Crear nueva estructura de mesas
                nuevas_asignaciones = []
                for i in range(num_mesas):
                    # Intentar preservar invitados de mesas antiguas si existen
                    if i < len(asignaciones_antiguas):
                        # Mantener invitados de la mesa existente (pero limitados a nueva capacidad)
                        invitados_antiguos = asignaciones_antiguas[i].get('invitados', [])
                        invitados = invitados_antiguos[:inv_por_mesa]  # Limitar a nueva capacidad
                    else:
                        invitados = []
                    
                    nuevas_asignaciones.append({
                        'id': i + 1,
                        'capacidad': inv_por_mesa,
                        'invitados': invitados
                    })
                
                self.evento.asignaciones_mesas = nuevas_asignaciones

        self.cambios_guardados = True
        QtWidgets.QMessageBox.information(self.main_window, 'Guardar', 'Evento guardado correctamente.')
    
    def volver_ventana_anterior(self):
        # Recargar eventos en la ventana padre antes de mostrarla
        if hasattr(self.parent_controller, 'cargar_eventos'):
            self.parent_controller.cargar_eventos()
        
        # Mostramos la ventana anterior a través del controlador padre
        self.parent_controller.main_window.show()
        self.main_window.hide()
