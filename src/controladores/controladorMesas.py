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

    def reiniciar_asignaciones(self):
        # vaciar asignaciones y llenar lista de invitados
        for m in self.mesas:
            m['invitados'] = []
        self.refresh_ui()

    def refresh_ui(self):
        # actualizar tabla de mesas
        tabla = self.ui.tablaAsignaciones
        tabla.setRowCount(len(self.mesas))
        for i, m in enumerate(self.mesas):
            tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(str(m['id'])))
            tabla.setItem(i, 1, QtWidgets.QTableWidgetItem(', '.join([p for p in m['invitados']])))

        # lista de invitados sin asignar
        lista = self.ui.listaInvitados
        lista.clear()
        participantes = [p.nombre for p in (self.evento.participantes if self.evento else [])]
        asignados = []
        for m in self.mesas:
            asignados.extend(m['invitados'])
        for nombre in participantes:
            if nombre not in asignados:
                lista.addItem(nombre)

    def asignacion_automatica(self):
        # Si existe el algoritmo, usarlo; sino fallback al reparto simple
        if asignar_mesas_optimizando is None or AlgPersona is None:
            # fallback simple: reparto equitativo
            if not self.mesas or not self.evento:
                QtWidgets.QMessageBox.warning(self.main_window, 'Error', 'No hay mesas o evento')
                return
            for m in self.mesas:
                m['invitados'] = []
            participantes = [p.nombre for p in self.evento.participantes]
            mesa_index = 0
            for nombre in participantes:
                placed = False
                for _ in range(len(self.mesas)):
                    m = self.mesas[mesa_index]
                    if len(m['invitados']) < m['capacidad']:
                        m['invitados'].append(nombre)
                        placed = True
                        mesa_index = (mesa_index + 1) % len(self.mesas)
                        break
                    mesa_index = (mesa_index + 1) % len(self.mesas)
                if not placed:
                    QtWidgets.QMessageBox.warning(self.main_window, 'Límite', f'No hay espacio para {nombre}')
            self.refresh_ui()
            return

        # Preparar participantes para el algoritmo
        participantes_obj = []
        for p in (self.evento.participantes if self.evento else []):
            amistades = []
            enemistades = []
            # las cadenas de 'prefiere' y 'no_prefiere' pueden llevar comas
            if getattr(p, 'prefiere', ''):
                amistades = [s.strip() for s in p.prefiere.split(',') if s.strip()]
            if getattr(p, 'no_prefiere', ''):
                enemistades = [s.strip() for s in p.no_prefiere.split(',') if s.strip()]
            participantes_obj.append(AlgPersona(p.nombre, amistades=amistades, enemistades=enemistades))

        tamano_mesa = int(self.evento.inv_por_mesa) if self.evento else 4
        solucion, excluidos = asignar_mesas_optimizando(participantes_obj, tamano_mesa)

        if solucion is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'No factible', 'No se pudo asignar mesas con el algoritmo.')
            return

        # Reconstruir mesas según solución
        num_mesas_needed = max(solucion.values()) + 1 if solucion else (self.evento.num_mesas if self.evento else len(self.mesas))
        self.mesas = []
        for i in range(num_mesas_needed):
            capacidad = int(self.evento.inv_por_mesa) if self.evento else 4
            self.mesas.append({'id': i+1, 'capacidad': capacidad, 'invitados': []})

        for nombre, mesa_idx in solucion.items():
            if 0 <= mesa_idx < len(self.mesas):
                self.mesas[mesa_idx]['invitados'].append(nombre)

        if excluidos:
            QtWidgets.QMessageBox.information(self.main_window, 'Excluidos', 'No se pudo ubicar a: ' + ', '.join(excluidos))

        self.refresh_ui()

    def asignar_seleccionado(self):
        lista = self.ui.listaInvitados
        item = lista.currentItem()
        if item is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Asignar', 'Selecciona un invitado')
            return
        nombre = item.text()
        fila = self.ui.tablaAsignaciones.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Asignar', 'Selecciona una mesa')
            return
        m = self.mesas[fila]
        if len(m['invitados']) >= m['capacidad']:
            QtWidgets.QMessageBox.warning(self.main_window, 'Asignar', 'La mesa está llena')
            return
        m['invitados'].append(nombre)
        # quitar de la lista
        lista.takeItem(lista.currentRow())
        self.refresh_ui()

    def quitar_seleccionado(self):
        fila = self.ui.tablaAsignaciones.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Quitar', 'Selecciona una mesa')
            return
        m = self.mesas[fila]
        # tomar último invitado
        if not m['invitados']:
            QtWidgets.QMessageBox.warning(self.main_window, 'Quitar', 'No hay invitados en esa mesa')
            return
        nombre = m['invitados'].pop()
        # añadir a lista de invitados
        self.ui.listaInvitados.addItem(nombre)
        self.refresh_ui()
