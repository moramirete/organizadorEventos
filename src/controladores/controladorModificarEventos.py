import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets

current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)

from interfazHomeModificarListadoEventos import Ui_EventosGestion
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeEvento import Ui_EventosListado
from controladorEditarEvento import controladorEditarEvento


class controladorModificarEventos:
    
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosGestion, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        
        self.editar_window = None
        self.siguiente_window = None

        self.conectar_botones()

        # 👉 CARGAR LISTADO DE EVENTOS
        self.cargar_eventos()
    
    def showEvent(self, event):
        """Se llama automáticamente cuando se muestra la ventana"""
        self.cargar_eventos()
        super().showEvent(event) if hasattr(super(), 'showEvent') else None
        
    def conectar_botones(self):
        self.ui.btnEditar.clicked.connect(self.abrir_editar_evento)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_principal)
        
        # Conectar búsqueda en tiempo real
        try:
            self.ui.leBuscar.textChanged.connect(self.buscar_eventos)
        except Exception:
            pass
        # Exportar CSV del listado visible
        try:
            self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        except Exception:
            pass
        # Eliminar evento seleccionado (respetando el filtro de búsqueda)
        try:
            self.ui.btnEliminar.clicked.connect(self.eliminar_evento)
        except Exception:
            pass

    def cargar_eventos(self):
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        eventos = getattr(self.parent_controller, 'eventos', [])
        tabla.setRowCount(len(eventos))

        for fila, ev in enumerate(eventos):
            valores = [
                getattr(ev, 'nombre', ''),
                getattr(ev, 'fecha', ''),
                getattr(ev, 'cliente', ''),
                getattr(ev, 'telefono', ''),
                str(getattr(ev, 'num_mesas', '')),
                str(getattr(ev, 'inv_por_mesa', '')),
            ]

            for col in range(min(tabla.columnCount(), len(valores))):
                tabla.setItem(fila, col, QtWidgets.QTableWidgetItem(valores[col]))
    
    def buscar_eventos(self):
        """Filtra los eventos en la tabla según el texto de búsqueda."""
        texto_busqueda = self.ui.leBuscar.text().strip().lower()
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return
        
        eventos = getattr(self.parent_controller, 'eventos', [])
        
        if not texto_busqueda:
            # Si no hay texto de búsqueda, mostrar todos los eventos
            self.cargar_eventos()
            return
        
        # Filtrar eventos que coincidan con el texto de búsqueda
        eventos_filtrados = []
        for ev in eventos:
            # Buscar en nombre, fecha, cliente o teléfono
            if (texto_busqueda in getattr(ev, 'nombre', '').lower() or
                texto_busqueda in getattr(ev, 'fecha', '').lower() or
                texto_busqueda in getattr(ev, 'cliente', '').lower() or
                texto_busqueda in getattr(ev, 'telefono', '').lower()):
                eventos_filtrados.append(ev)
        
        # Mostrar eventos filtrados
        tabla.setRowCount(len(eventos_filtrados))
        for fila, ev in enumerate(eventos_filtrados):
            valores = [
                getattr(ev, 'nombre', ''),
                getattr(ev, 'fecha', ''),
                getattr(ev, 'cliente', ''),
                getattr(ev, 'telefono', ''),
                str(getattr(ev, 'num_mesas', '')),
                str(getattr(ev, 'inv_por_mesa', '')),
            ]
            for col in range(min(tabla.columnCount(), len(valores))):
                tabla.setItem(fila, col, QtWidgets.QTableWidgetItem(valores[col]))

    # Método para abrir la ventana de edición del evento
    def abrir_editar_evento(self):
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        fila = tabla.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Editar', 'Selecciona un evento')
            return

        # 👉 Recuperamos el evento de la lista global (Home)
        eventos = getattr(self.parent_controller, 'eventos', [])
        if fila >= len(eventos):
            QtWidgets.QMessageBox.warning(self.main_window, 'Editar', 'Índice de evento no válido')
            return

        evento_seleccionado = eventos[fila]

        self.editar_window = QMainWindow() 
        editar_ui = Ui_EventoEditar() 
        editar_ui.setupUi(self.editar_window)
      
        self.editar_controller = controladorEditarEvento(
            self.editar_window,
            editar_ui,
            self  # Pasamos la referencia a este controlador como padre
        )

        # Pasamos el evento al controlador de edición y cargamos datos
        self.editar_controller.evento = evento_seleccionado
        self.editar_controller.cargar_datos_evento()
        
        self.editar_window.show()
        self.main_window.hide()

    
    
    def volver_ventana_principal(self):
        # Recargar eventos antes de mostrar
        self.cargar_eventos()
        
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos para modificar)
        self.main_window.hide()
    
    def mostrar_ventana(self):
        """Método para mostrar la ventana y recargar eventos"""
        self.cargar_eventos()
        self.main_window.show()
    
    def obtener_eventos_visibles(self):
        texto_busqueda = getattr(self.ui, 'leBuscar', None)
        eventos = getattr(self.parent_controller, 'eventos', [])
        if texto_busqueda is None:
            return list(eventos)
        txt = texto_busqueda.text().strip().lower()
        if not txt:
            return list(eventos)
        visibles = []
        for ev in eventos:
            if (txt in getattr(ev, 'nombre', '').lower() or
                txt in getattr(ev, 'fecha', '').lower() or
                txt in getattr(ev, 'cliente', '').lower() or
                txt in getattr(ev, 'telefono', '').lower()):
                visibles.append(ev)
        return visibles

    def exportar_csv(self):
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Exportar CSV', 'No se encontró la tabla de eventos.')
            return

        import csv
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.main_window,
            'Guardar CSV',
            '',
            'CSV Files (*.csv);;All Files (*)',
            options=options
        )
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Cabeceras visibles en la tabla
                cabecera = []
                for col in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(col)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                # Filas visibles tal como se muestran
                for row in range(tabla.rowCount()):
                    datos = []
                    for col in range(tabla.columnCount()):
                        item = tabla.item(row, col)
                        datos.append(item.text() if item is not None else '')
                    writer.writerow(datos)

            QtWidgets.QMessageBox.information(self.main_window, 'Exportar CSV', f'CSV exportado correctamente a:\n{filename}')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, 'Exportar CSV', f'Error al exportar CSV:\n{e}')

    def eliminar_evento(self):
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        fila = tabla.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Eliminar', 'Selecciona un evento')
            return

        # Encontrar el evento real basado en la vista filtrada
        eventos_visibles = self.obtener_eventos_visibles()
        if fila >= len(eventos_visibles):
            QtWidgets.QMessageBox.warning(self.main_window, 'Eliminar', 'Selección no válida')
            return

        evento_obj = eventos_visibles[fila]
        nombre = getattr(evento_obj, 'nombre', '¿evento?')

        resp = QtWidgets.QMessageBox.question(
            self.main_window,
            'Confirmar eliminación',
            f'¿Seguro que deseas eliminar el evento "{nombre}"?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if resp != QtWidgets.QMessageBox.Yes:
            return

        # Eliminar por identidad del listado global
        eventos_globales = getattr(self.parent_controller, 'eventos', [])
        try:
            idx = next(i for i, ev in enumerate(eventos_globales) if ev is evento_obj)
            eventos_globales.pop(idx)
        except StopIteration:
            # Si no se encontró por identidad, intentar por coincidencia de atributos principales
            for i, ev in enumerate(eventos_globales):
                if (getattr(ev, 'nombre', None) == getattr(evento_obj, 'nombre', None) and
                    getattr(ev, 'fecha', None) == getattr(evento_obj, 'fecha', None) and
                    getattr(ev, 'cliente', None) == getattr(evento_obj, 'cliente', None) and
                    getattr(ev, 'telefono', None) == getattr(evento_obj, 'telefono', None)):
                    eventos_globales.pop(i)
                    break

        # Refrescar la vista según el filtro actual
        self.buscar_eventos()
        QtWidgets.QMessageBox.information(self.main_window, 'Eliminar', 'Evento eliminado correctamente')
