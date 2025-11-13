import sys
import os
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets

# Ajusto la ruta para poder importar las interfaces .py del proyecto
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeEventoMesas import Ui_EventoMesas

from controladorConsultar2 import ControladorConsultar2


class ControladorConsultar1:
    
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        # Ventana y ui de esta pantalla
        self.main_window = main_window 
        self.ui = ui
        # Guardo el controlador principal (Home)
        self.parent_controller = parent_controller
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None

        # Conecto los botones
        self.conectar_botones()

        # Cargo los eventos en la tabla al abrir esta ventana
        self.cargar_eventos()
        
    def conectar_botones(self):
        # Botón para ver el evento seleccionado
        self.ui.btnVerEvento.clicked.connect(self.abrir_consultar_eventos)
        # Botón para exportar la tabla a CSV (si existe)
        try:
            self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        except Exception:
            pass
        # Botón para volver a la ventana principal
        self.ui.btnVolver.clicked.connect(self.volver_ventana_principal)
        
        # Búsqueda en tiempo real por texto (si el lineEdit existe)
        try:
            self.ui.leBuscar.textChanged.connect(self.buscar_eventos)
        except Exception:
            pass

    def cargar_eventos(self):
        """Rellena la tabla con los eventos que tiene el controlador Home."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        eventos = getattr(self.parent_controller, 'eventos', [])
        tabla.setRowCount(len(eventos))

        for fila, ev in enumerate(eventos):
            # Datos en el mismo orden que las columnas de la tabla
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
        """Filtra los eventos de la tabla según el texto escrito en leBuscar."""
        texto_busqueda = self.ui.leBuscar.text().strip().lower()
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return
        
        eventos = getattr(self.parent_controller, 'eventos', [])
        
        # Si no hay texto, vuelvo a cargar todos los eventos
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
        
        # Pinto solo los eventos filtrados
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

    def abrir_consultar_eventos(self):
        """Abre la ventana de mesas del evento seleccionado en la tabla."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return
        
        fila_seleccionada = tabla.currentRow()
        if fila_seleccionada < 0:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Selección',
                'Por favor selecciona un evento de la lista.'
            )
            return
        
        # Creo la ventana donde se verán las mesas del evento
        self.consultar_window = QMainWindow() 
        consultar_ui = Ui_EventoMesas() 
        consultar_ui.setupUi(self.consultar_window)

        # Paso este controlador al siguiente para que tenga acceso al evento
        self.consultar_controller = ControladorConsultar2(
            self.consultar_window, 
            consultar_ui, 
            self  
        )
        
        self.consultar_window.show()
        # Oculto la ventana del listado
        self.main_window.hide()
    
    def volver_ventana_principal(self):
        """Vuelve a la ventana principal (Home) y oculta esta."""
        self.parent_controller.main_window.show()
        self.main_window.hide()

    def exportar_csv(self):
        """Exporta la tabla de eventos a un archivo CSV."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Exportar CSV',
                'No se encontró la tabla de eventos.'
            )
            return

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

                # Escribo la fila de cabeceras
                cabecera = []
                for columnas in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(columnas)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                # Escribo los datos de cada fila
                for filas in range(tabla.rowCount()):
                    datos_fila = []
                    for columnas in range(tabla.columnCount()):
                        item = tabla.item(filas, columnas)
                        datos_fila.append(item.text() if item is not None else '')
                    writer.writerow(datos_fila)

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
