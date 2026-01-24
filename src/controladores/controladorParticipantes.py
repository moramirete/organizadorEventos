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
        # Sincronizamos con la nube para asegurar el guardado
        self.sincronizar_nube()
        QtWidgets.QMessageBox.information(self.main_window, 'Guardar', 'Participantes guardados en la nube')

    def sincronizar_nube(self):
        """Sincroniza el estado actual del evento (participantes y mesas) con Supabase"""
        evento = getattr(self, 'evento', None) or getattr(self.parent_controller, 'evento', None)
        if evento is None or not getattr(evento, 'id', None):
            print("No se puede sincronizar: evento no guardado en DB aún")
            return

        try:
            from config.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Preparamos el objeto distribucion JSONB
            # IMPORTANTE: Incluimos la configuracion para no borrarla al sincronizar invitados
            distribucion = {
                "configuracion": {
                    "num_mesas": getattr(evento, 'num_mesas', 0),
                    "inv_por_mesa": getattr(evento, 'inv_por_mesa', 0)
                },
                "lista_participantes": [
                    {"nombre": p.nombre, "prefiere": p.prefiere, "no_prefiere": p.no_prefiere}
                    for p in evento.participantes
                ],
                "asignaciones_mesas": evento.asignaciones_mesas
            }
            
            # Solo actualizamos la columna distribucion y num_participantes
            supabase.table("eventos").update({
                "distribucion": distribucion,
                "num_participantes": len(evento.participantes)
            }).eq("id", evento.id).execute()
            
            print(f"Sincronizado con éxito: {len(evento.participantes)} invitados.")
        except Exception as e:
            print(f"Error sincronizando con la nube: {e}")

    def crear_participante(self):
        # ... (código anterior igual)
        nombre = self.ui.leNombreParticipante.text().strip()
        prefiere = self.ui.lePrefiereCon.text().strip()
        no_prefiere = self.ui.leNoPrefiereCon.text().strip()

        if not nombre:
            QtWidgets.QMessageBox.warning(self.main_window, 'Validación', 'El nombre es obligatorio')
            return

        evento = getattr(self, 'evento', None)
        if evento is not None:
            for p_existente in evento.participantes:
                if p_existente.nombre.lower() == nombre.lower():
                    QtWidgets.QMessageBox.warning(self.main_window, 'Duplicado', 'Ya existe un participante con ese nombre')
                    return
            
            if evento.contar_participantes() >= evento.capacidad_total():
                QtWidgets.QMessageBox.warning(self.main_window, 'Límite', 'No hay espacio')
                return

        p = Participante(nombre, prefiere, no_prefiere)
        if evento is not None:
            evento.agregar_participante(p)
        
        self.refrescar_tabla()
        self.sincronizar_nube() # Sincronizar después de añadir

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
        self.sincronizar_nube() # Sincronizar después de eliminar

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
                
                # --- MEJORA: Mapeo inteligente de columnas ---
                idx_nombre = 0
                idx_prefiere = 1
                idx_no_prefiere = 2
                
                rows_for_analysis = []
                try:
                    # Leemos unas cuantas filas para analizar el contenido real
                    for _ in range(5):
                        r = next(reader, None)
                        if r: rows_for_analysis.append(r)
                except Exception:
                    pass
                
                # Volvemos al inicio para procesar de verdad
                f.seek(0)
                reader = csv.reader(f, dialect)
                
                first_row = rows_for_analysis[0] if rows_for_analysis else None
                if first_row:
                    # Palabras clave para cabeceras
                    cabecera_keywords = ['id', 'nombre', 'name', 'usuario', 'username', 'participante', 'prefiere', 'no_prefiere']
                    es_cabecera = any(k in str(cell).lower() for cell in first_row for k in cabecera_keywords)
                    
                    if es_cabecera or has_header:
                        print("Cabecera detectada. Analizando estructura...")
                        next(reader, None) # Saltar la cabecera en el reader real
                        
                        # Mapeamos los índices según los nombres de las columnas
                        for i, cell in enumerate(first_row):
                            txt = cell.lower().strip()
                            # Si la columna contiene "nombre" o similar, es nuestra candidata principal
                            if any(k in txt for k in ['nombre', 'name', 'usuario', 'username', 'participante']):
                                if 'id' not in txt or len(txt) > 2: # Evitar "id" a secas
                                    idx_nombre = i
                            elif any(k in txt for k in ['prefiere', 'deseado', 'prefer', 'gustar']) and 'no' not in txt:
                                idx_prefiere = i
                            elif any(k in txt for k in ['no prefiere', 'no deseado', 'no prefer', 'no gustar', 'enemigo']):
                                idx_no_prefiere = i
                        
                        # HEURÍSTICA: Si idx_nombre sigue siendo 0 pero la primera columna de los DATOS es numérica
                        # y la segunda es texto, probablemente la primera sea un ID.
                        if idx_nombre == 0 and len(rows_for_analysis) > 1:
                            data_sample = rows_for_analysis[1] # Primera fila de datos tras cabecera
                            if len(data_sample) > 1:
                                val0 = data_sample[0].strip()
                                val1 = data_sample[1].strip()
                                # Si col 0 es número y col 1 no lo es, col 1 es el nombre
                                if val0.isdigit() and not val1.isdigit():
                                    idx_nombre = 1
                                    print(f"Heurística aplicada: Cambiando columna nombre de 0 a 1 (Col 0 parece ser ID numérico)")

                    else:
                        print("No se detectó cabecera. Usando heurística de contenido...")
                        # Si no hay cabecera, comprobamos si la primera columna es un ID numérico
                        if len(first_row) > 1:
                            if first_row[0].strip().isdigit() and not first_row[1].strip().isdigit():
                                idx_nombre = 1
                                idx_prefiere = 2
                                idx_no_prefiere = 3
                
                existentes = {p.nombre.strip().lower() for p in evento.participantes}

                for row in reader:
                    try:
                        if not row:
                            continue
                        
                        nombre = (row[idx_nombre] if len(row) > idx_nombre else '').strip()
                        prefiere = (row[idx_prefiere] if len(row) > idx_prefiere else '').strip()
                        no_prefiere = (row[idx_no_prefiere] if len(row) > idx_no_prefiere else '').strip()

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
            self.sincronizar_nube() # Sincronizar importación
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
