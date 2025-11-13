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
# Asegurar que podemos importar los modelos
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorMesas import ControladorMesas
from interfazHomeModificarListadoEventosAsignacionInvitados import Ui_AsignacionesInvitados
from modelos.participantes import Participante
from PyQt5 import QtWidgets

class ControladorParticipantes:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        self.mesas_window = None
        # evento será pasado desde Nuevo/Editar evento
        self.evento = getattr(self, 'evento', None)

        self.conectar_botones()
        # Cargar participantes si el evento ya tiene algunos
        self.refrescar_tabla()
        
    def conectar_botones(self):
        # Botones de la UI de participantes
        try:
            self.ui.btnCrear.clicked.connect(self.crear_participante)
        except Exception:
            pass

        try:
            self.ui.btnEliminar.clicked.connect(self.eliminar_participante)
        except Exception:
            pass

        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

        try:
            self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        except Exception:
            pass

        try:
            self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)
        except Exception:
            pass

    def ir_siguiente_interfaz(self):
        # Antes de abrir Mesas, pasar el evento actual
        self.mesas_window = QMainWindow()
        mesas_ui = Ui_AsignacionesInvitados()
        mesas_ui.setupUi(self.mesas_window)

        self.mesas_controller = ControladorMesas(self.mesas_window, mesas_ui, self)
        # pasar evento
        self.mesas_controller.evento = getattr(self, 'evento', None)
        # iniciar controlador de mesas para crear estructura
        try:
            self.mesas_controller.iniciar()
        except Exception:
            pass

        self.mesas_window.show()
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Recargar tabla en el controlador padre si tiene el método
        if hasattr(self.parent_controller, 'cargar_datos_evento'):
            self.parent_controller.cargar_datos_evento()
        
        # Mostrar ventana anterior
        self.parent_controller.main_window.show()
        
        # Ocultar ventana actual
        self.main_window.hide()

    def crear_participante(self):
        # Crear participante simple desde los campos
        nombre = self.ui.leNombreParticipante.text().strip()
        prefiere = self.ui.lePrefiereCon.text().strip()
        no_prefiere = self.ui.leNoPrefiereCon.text().strip()

        if not nombre:
            QtWidgets.QMessageBox.warning(self.main_window, 'Validación', 'El nombre es obligatorio')
            return

        # Verificar que el nombre no esté duplicado
        evento = getattr(self, 'evento', None)
        if evento is not None:
            # Verificar duplicados
            for p_existente in evento.participantes:
                if p_existente.nombre.lower() == nombre.lower():
                    QtWidgets.QMessageBox.warning(self.main_window, 'Duplicado', 'Ya existe un participante con ese nombre')
                    return
            
            # Comprobar límite de capacidad total
            capacidad_actual = evento.contar_participantes()
            capacidad_maxima = evento.capacidad_total()
            if capacidad_actual >= capacidad_maxima:
                QtWidgets.QMessageBox.warning(
                    self.main_window, 
                    'Límite alcanzado', 
                    f'No caben más invitados.\n\n'
                    f'Participantes actuales: {capacidad_actual}\n'
                    f'Capacidad máxima: {capacidad_maxima}\n'
                    f'(Mesas: {evento.num_mesas} × Capacidad: {evento.inv_por_mesa})\n\n'
                    f'Para agregar más participantes, vuelve atrás y aumenta el número de mesas o la capacidad por mesa.'
                )
                return

        p = Participante(nombre, prefiere, no_prefiere)
        # si hay evento, añadirlo allí
        if evento is not None:
            evento.agregar_participante(p)
        else:
            # guardar temporal en el controlador padre si existe
            lst = getattr(self.parent_controller, 'evento', None)
            if lst is not None:
                lst.agregar_participante(p)

        self.refrescar_tabla()

    def eliminar_participante(self):
        tabla = self.ui.tablaParticipantes
        fila = tabla.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Eliminar', 'Selecciona un participante')
            return

        evento = getattr(self, 'evento', None) or getattr(self.parent_controller, 'evento', None)
        if evento is not None:
            evento.eliminar_participante(fila)

        self.refrescar_tabla()

    def refrescar_tabla(self):
        tabla = self.ui.tablaParticipantes
        tabla.clearContents()
        evento = getattr(self, 'evento', None) or getattr(self.parent_controller, 'evento', None)
        participantes = evento.participantes if evento is not None else []
        tabla.setRowCount(len(participantes) if participantes else 0)
        for i, p in enumerate(participantes):
            tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(p.nombre))
            tabla.setItem(i, 1, QtWidgets.QTableWidgetItem(p.prefiere))
            tabla.setItem(i, 2, QtWidgets.QTableWidgetItem(p.no_prefiere))

    def guardar_cambios(self):
        # Para simplicidad, guardar ya está hecho al añadir; aquí solo confirmamos
        QtWidgets.QMessageBox.information(self.main_window, 'Guardar', 'Participantes guardados')