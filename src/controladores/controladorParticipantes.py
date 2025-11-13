import sys
import os
import csv
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

        try:
            self.ui.btnImportarCSV.clicked.connect(self.importar_csv)
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

        # comprobar límite de capacidad si existe evento
        evento = getattr(self, 'evento', None)
        if evento is not None:
            if evento.contar_participantes() >= evento.capacidad_total():
                QtWidgets.QMessageBox.warning(self.main_window, 'Límite', 'No caben más invitados según las mesas configuradas')
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

    def importar_csv(self):
        """
        Permite seleccionar un fichero CSV e importar participantes.
        Formato esperado por columna: Nombre, Prefiere, NoPrefiere
        Detecta delimitador (coma/;/tab) y salta cabecera si existe.
        """
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            'Seleccionar CSV',
            '',
            'CSV Files (*.csv);;All Files (*)',
            options=options
        )
        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8-sig', newline='') as f:
                    sample = f.read(2048)
                    f.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample, delimiters=',;|\t')
                        delimiter = dialect.delimiter
                    except Exception:
                        delimiter = ','

                    reader = csv.reader(f, delimiter=delimiter)
                    rows = list(reader)

            if not rows:
                QtWidgets.QMessageBox.warning(self.main_window, 'Importar CSV', 'El archivo está vacío.')
                return
            
        # Detectar si existe cabecera (buscando palabras clave)
            first = rows[0]
            header_lower = [c.strip().lower() for c in first]
            start_index = 0
            if any('nombre' in c for c in header_lower) or any('prefiere' in c for c in header_lower) or any('acompañ' in c for c in header_lower) or any('no' in c for c in header_lower):
                start_index = 1

            added = 0
            for row in rows[start_index:]:
                if not row or all(not cell.strip() for cell in row):
                    continue
                nombre = row[0].strip() if len(row) > 0 else ''
                prefiere = row[1].strip() if len(row) > 1 else ''
                no_prefiere = row[2].strip() if len(row) > 2 else ''
                if not nombre:
                    continue

                p = Participante(nombre, prefiere, no_prefiere)
                evento = getattr(self, 'evento', None)
                if evento is not None:
                    evento.agregar_participante(p)
                else:
                    lst = getattr(self.parent_controller, 'evento', None)
                    if lst is not None:
                        lst.agregar_participante(p)
                added += 1

            self.refrescar_tabla()
            QtWidgets.QMessageBox.information(self.main_window, 'Importar CSV', f'Importados {added} participantes.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, 'Importar CSV', f'Error al importar CSV:\n{e}')