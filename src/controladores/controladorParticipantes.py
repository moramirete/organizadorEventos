import sys
import os
import csv
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets

# Añado la ruta para poder importar las interfaces generadas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

# Añado src al path para poder usar los modelos
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorMesas import ControladorMesas
from interfazHomeModificarListadoEventosAsignacionInvitados import Ui_AsignacionesInvitados
from modelos.participantes import Participante


class ControladorParticipantes:
    
    def __init__(self, main_window, ui, parent_controller):
        # Ventana y UI de esta pantalla
        self.main_window = main_window
        self.ui = ui
        # Controlador anterior (Nuevo/Editar evento)
        self.parent_controller = parent_controller

        self.mesas_window = None
        # El evento se pasa desde el controlador padre
        self.evento = getattr(self, 'evento', None)

        self.conectar_botones()
        # Si el evento ya tiene participantes los cargamos en la tabla
        self.refrescar_tabla()
        
    def conectar_botones(self):
        # Botón para crear un participante nuevo
        try:
            self.ui.btnCrear.clicked.connect(self.crear_participante)
        except Exception:
            pass

        # Botón para eliminar el participante seleccionado
        try:
            self.ui.btnEliminar.clicked.connect(self.eliminar_participante)
        except Exception:
            pass

        # Botón "Guardar" (realmente solo muestra mensaje, los datos ya se van guardando)
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

        # Botón para importar participantes desde CSV
        try:
            self.ui.btnImportarCSV.clicked.connect(self.importar_csv)
        except Exception:
            pass

        # Botón para ir a la pantalla de mesas
        try:
            self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        except Exception:
            pass

        # Botón para volver a la pantalla anterior
        try:
            self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)
        except Exception:
            pass

    def ir_siguiente_interfaz(self):
        # Antes de abrir Mesas, preparo la ventana y le paso el evento actual
        self.mesas_window = QMainWindow()
        mesas_ui = Ui_AsignacionesInvitados()
        mesas_ui.setupUi(self.mesas_window)

        self.mesas_controller = ControladorMesas(self.mesas_window, mesas_ui, self)
        # Paso el evento al controlador de mesas
        self.mesas_controller.evento = getattr(self, 'evento', None)

        # Creo la estructura de mesas a partir del evento
        try:
            self.mesas_controller.iniciar()
        except Exception:
            pass

        self.mesas_window.show()
        self.main_window.hide()
    
    def volver_ventana_anterior(self):
        # Si el padre tiene método para recargar datos, lo uso
        if hasattr(self.parent_controller, 'cargar_datos_evento'):
            self.parent_controller.cargar_datos_evento()
        
        # Muestro la ventana anterior
        self.parent_controller.main_window.show()
        # Oculto esta ventana
        self.main_window.hide()

    def crear_participante(self):
        # Cojo los datos escritos en los campos
        nombre = self.ui.leNombreParticipante.text().strip()
        prefiere = self.ui.lePrefiereCon.text().strip()
        no_prefiere = self.ui.leNoPrefiereCon.text().strip()

        if not nombre:
            QtWidgets.QMessageBox.warning(self.main_window, 'Validación', 'El nombre es obligatorio')
            return

        evento = getattr(self, 'evento', None)
        if evento is not None:
            # Compruebo que no haya otro participante con el mismo nombre
            for p_existente in evento.participantes:
                if p_existente.nombre.lower() == nombre.lower():
                    QtWidgets.QMessageBox.warning(self.main_window, 'Duplicado', 'Ya existe un participante con ese nombre')
                    return
            
            # Compruebo si el evento ya está lleno
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

        # Creo el objeto participante
        p = Participante(nombre, prefiere, no_prefiere)
        # Si hay evento lo añado ahí
        if evento is not None:
            evento.agregar_participante(p)
        else:
            # Si no, intento añadirlo al evento que tenga el padre
            lst = getattr(self.parent_controller, 'evento', None)
            if lst is not None:
                lst.agregar_participante(p)

        self.refrescar_tabla()

    def eliminar_participante(self):
        # Elimino el participante de la fila seleccionada
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
        # Vuelvo a dibujar la tabla con la lista de participantes del evento
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
        # Los cambios ya se aplican al añadir/eliminar. Aquí solo confirmo.
        QtWidgets.QMessageBox.information(self.main_window, 'Guardar', 'Participantes guardados')

    def importar_csv(self):
        # Abro un diálogo para elegir el archivo CSV
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            'Importar CSV de participantes',
            '',
            'CSV Files (*.csv);;All Files (*)',
            options=options
        )
        if not filename:
            return

        evento = getattr(self, 'evento', None) or getattr(self.parent_controller, 'evento', None)
        if evento is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Importar CSV', 'No hay evento activo para importar participantes.')
            return

        agregados = 0
        duplicados = 0
        sin_nombre = 0
        sin_espacio = 0
        errores = 0

        try:
            with open(filename, 'r', encoding='utf-8-sig', newline='') as f:
                sample = f.read(2048)
                f.seek(0)
                # Intento detectar delimitador y si tiene cabecera
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t')
                except Exception:
                    dialect = csv.excel
                try:
                    has_header = csv.Sniffer().has_header(sample)
                except Exception:
                    has_header = False

                reader = csv.reader(f, dialect)
                if has_header:
                    next(reader, None)  # salta la cabecera

                existentes = {p.nombre.strip().lower() for p in evento.participantes}

                for row in reader:
                    try:
                        if not row:
                            continue
                        nombre = (row[0] if len(row) > 0 else '').strip()
                        prefiere = (row[1] if len(row) > 1 else '').strip()
                        no_prefiere = (row[2] if len(row) > 2 else '').strip()

                        if not nombre:
                            sin_nombre += 1
                            continue

                        if nombre.lower() in existentes:
                            duplicados += 1
                            continue

                        # Compruebo capacidad antes de añadir
                        if evento.contar_participantes() >= evento.capacidad_total():
                            sin_espacio += 1
                            continue

                        p = Participante(nombre, prefiere, no_prefiere)
                        evento.agregar_participante(p)
                        existentes.add(nombre.lower())
                        agregados += 1
                    except Exception:
                        errores += 1

            self.refrescar_tabla()
            QtWidgets.QMessageBox.information(
                self.main_window,
                'Importar CSV',
                'Importación finalizada.\n\n'
                f'Agregados: {agregados}\n'
                f'Duplicados omitidos: {duplicados}\n'
                f'Filas sin nombre: {sin_nombre}\n'
                f'Sin espacio (capacidad completa): {sin_espacio}\n'
                f'Errores de lectura: {errores}'
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, 'Importar CSV', f'Error al importar CSV:\n{e}')
