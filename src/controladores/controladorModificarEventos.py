import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets

# Preparo la ruta para poder importar las interfaces .py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventos import Ui_EventosGestion
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeEvento import Ui_EventosListado
from controladorEditarEvento import controladorEditarEvento


class controladorModificarEventos:
    
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosGestion, parent_controller):
        # Guardo la ventana de esta pantalla y el controlador padre (Home)
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller
        
        self.editar_window = None
        self.siguiente_window = None

        self.conectar_botones()

        # Al abrir esta pantalla cargo los eventos en la tabla
        self.cargar_eventos()
    
    def showEvent(self, event):
        """Cuando se muestra la ventana, recargo la tabla de eventos."""
        self.cargar_eventos()
        super().showEvent(event) if hasattr(super(), 'showEvent') else None
        
    def conectar_botones(self):
        # Botón para abrir la ventana de edición
        self.ui.btnEditar.clicked.connect(self.abrir_editar_evento)
        # Botón para volver al Home
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_principal)
        
        # Búsqueda en tiempo real por texto
        try:
            self.ui.leBuscar.textChanged.connect(self.buscar_eventos)
        except Exception:
            pass
        # Botón para exportar el listado a CSV
        try:
            self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        except Exception:
            pass
        # Botón para eliminar el evento seleccionado
        try:
            self.ui.btnEliminar.clicked.connect(self.eliminar_evento)
        except Exception:
            pass

    def cargar_eventos(self):
        """Rellena la tabla con todos los eventos que tiene el Home."""
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
        """Filtra los eventos según el texto que se escribe en el buscador."""
        texto_busqueda = self.ui.leBuscar.text().strip().lower()
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return
        
        eventos = getattr(self.parent_controller, 'eventos', [])
        
        # Si no se escribe nada, vuelvo a mostrar todos los eventos
        if not texto_busqueda:
            self.cargar_eventos()
            return
        
        # Me quedo solo con los eventos que coinciden con el texto
        eventos_filtrados = []
        for ev in eventos:
            if (
                texto_busqueda in getattr(ev, 'nombre', '').lower() or
                texto_busqueda in getattr(ev, 'fecha', '').lower() or
                texto_busqueda in getattr(ev, 'cliente', '').lower() or
                texto_busqueda in getattr(ev, 'telefono', '').lower()
            ):
                eventos_filtrados.append(ev)
        
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

    def abrir_editar_evento(self):
        """Abre la ventana para editar el evento seleccionado en la tabla."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        fila = tabla.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Editar', 'Selecciona un evento')
            return

        # Recupero el evento de la lista global del Home
        eventos = getattr(self.parent_controller, 'eventos', [])
        if fila >= len(eventos):
            QtWidgets.QMessageBox.warning(self.main_window, 'Editar', 'Índice de evento no válido')
            return

        evento_seleccionado = eventos[fila]

        # Creo la ventana de edición y su interfaz
        self.editar_window = QMainWindow() 
        editar_ui = Ui_EventoEditar() 
        editar_ui.setupUi(self.editar_window)
      
        # Creo el controlador de edición y le paso este como padre
        self.editar_controller = controladorEditarEvento(
            self.editar_window,
            editar_ui,
            self
        )

        # Le paso el evento al controlador y cargo los datos en el formulario
        self.editar_controller.evento = evento_seleccionado
        self.editar_controller.cargar_datos_evento()
        
        self.editar_window.show()
        self.main_window.hide()

    def volver_ventana_principal(self):
        """Vuelve al Home recargando antes la tabla de eventos."""
        self.cargar_eventos()
        self.parent_controller.main_window.show()
        self.main_window.hide()
    
    def mostrar_ventana(self):
        """Muestra esta ventana y recarga los eventos por si han cambiado."""
        self.cargar_eventos()
        self.main_window.show()
    
    def obtener_eventos_visibles(self):
        """Devuelve la lista de eventos que deberían mostrarse según el filtro."""
        texto_busqueda = getattr(self.ui, 'leBuscar', None)
        eventos = getattr(self.parent_controller, 'eventos', [])
        if texto_busqueda is None:
            return list(eventos)
        txt = texto_busqueda.text().strip().lower()
        if not txt:
            return list(eventos)
        visibles = []
        for ev in eventos:
            if (
                txt in getattr(ev, 'nombre', '').lower() or
                txt in getattr(ev, 'fecha', '').lower() or
                txt in getattr(ev, 'cliente', '').lower() or
                txt in getattr(ev, 'telefono', '').lower()
            ):
                visibles.append(ev)
        return visibles

    def exportar_csv(self):
        """Exporta a CSV lo que se ve en la tabla de eventos."""
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
                # Cabeceras de la tabla
                cabecera = []
                for col in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(col)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                # Filas tal y como se ven en la tabla
                for row in range(tabla.rowCount()):
                    datos = []
                    for col in range(tabla.columnCount()):
                        item = tabla.item(row, col)
                        datos.append(item.text() if item is not None else '')
                    writer.writerow(datos)

            QtWidgets.QMessageBox.information(
                self.main_window,
                'Exportar CSV',
                f'CSV exportado correctamente a:\n{filename}'
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.main_window,
                'Exportar CSV',
                f'Error al exportar CSV:\n{e}'
            )

    def eliminar_evento(self):
        """Elimina el evento seleccionado, teniendo en cuenta el filtro de búsqueda."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        fila = tabla.currentRow()
        if fila < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Eliminar', 'Selecciona un evento')
            return

        # Busco el evento real a partir de la lista filtrada
        eventos_visibles = self.obtener_eventos_visibles()
        if fila >= len(eventos_visibles):
            QtWidgets.QMessageBox.warning(self.main_window, 'Eliminar', 'Selección no válida')
            return

        evento_obj = eventos_visibles[fila]
        nombre = getattr(evento_obj, 'nombre', 'evento')

        resp = QtWidgets.QMessageBox.question(
            self.main_window,
            'Confirmar eliminación',
            f'¿Seguro que deseas eliminar el evento "{nombre}"?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if resp != QtWidgets.QMessageBox.Yes:
            return

        # Intento eliminar el evento usando la misma referencia
        eventos_globales = getattr(self.parent_controller, 'eventos', [])
        try:
            idx = next(i for i, ev in enumerate(eventos_globales) if ev is evento_obj)
            eventos_globales.pop(idx)
        except StopIteration:
            # Si no lo encuentro por referencia, pruebo a compararlo por campos básicos
            for i, ev in enumerate(eventos_globales):
                if (
                    getattr(ev, 'nombre', None) == getattr(evento_obj, 'nombre', None) and
                    getattr(ev, 'fecha', None) == getattr(evento_obj, 'fecha', None) and
                    getattr(ev, 'cliente', None) == getattr(evento_obj, 'cliente', None) and
                    getattr(ev, 'telefono', None) == getattr(evento_obj, 'telefono', None)
                ):
                    eventos_globales.pop(i)
                    break

        # Actualizo la tabla con el filtro actual
        self.buscar_eventos()
        QtWidgets.QMessageBox.information(self.main_window, 'Eliminar', 'Evento eliminado correctamente')
