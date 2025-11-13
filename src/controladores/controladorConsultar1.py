import sys
import os
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets

# --- INICIO: CORRECCIÓN DE RUTA DE IMPORTACIÓN PARA MODULOS ---

# Aqui lo que hace es modificar la ruta para que el controller se conecte
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)
# --- FIN: CORRECCIÓN DE RUTA DE IMPORTACIÓN ---

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeEventoMesas import Ui_EventoMesas

from controladorConsultar2 import ControladorConsultar2


class ControladorConsultar1:
    
    # ACEPTA EL CONTROLADOR PADRE
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller  # Almacenamos la referencia a ControladorHome
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None

        self.conectar_botones()

        # 👉 CARGAR LOS EVENTOS EN LA TABLA
        self.cargar_eventos()
        
    def conectar_botones(self):
        self.ui.btnVerEvento.clicked.connect(self.abrir_consultar_eventos)
        # Conectar exportar CSV
        try:
            self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        except Exception:
            pass
        self.ui.btnVolver.clicked.connect(self.volver_ventana_principal)
        
        # Conectar búsqueda en tiempo real
        try:
            self.ui.leBuscar.textChanged.connect(self.buscar_eventos)
        except Exception:
            pass

    def cargar_eventos(self):
        """Rellena tablaEventos con los eventos del Home."""
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return

        eventos = getattr(self.parent_controller, 'eventos', [])
        tabla.setRowCount(len(eventos))

        for fila, ev in enumerate(eventos):
            # Preparamos los valores en el orden que quieras
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

    # Método para abrir la ventana del evento con sus datos (la vista de mesas)
    def abrir_consultar_eventos(self):
        # Validar que haya una fila seleccionada
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            return
        
        fila_seleccionada = tabla.currentRow()
        if fila_seleccionada < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Selección', 'Por favor selecciona un evento de la lista.')
            return
        
        self.consultar_window = QMainWindow() 
        consultar_ui = Ui_EventoMesas() 
        consultar_ui.setupUi(self.consultar_window)

        self.consultar_controller = ControladorConsultar2(
            self.consultar_window, 
            consultar_ui, 
            self  
        )
        
        self.consultar_window.show()
        # Ocultamos la ventana actual (Listado de Eventos)
        self.main_window.hide()
    
    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos)
        self.main_window.hide()

    def exportar_csv(self):
        # Exporta el contenido de la tabla `tablaEventos` a un archivo CSV.

        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Exportar CSV', 'No se encontró la tabla de eventos.')
            return

        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window,'Guardar CSV','','CSV Files (*.csv);;All Files (*)',options=options)
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                cabecera = []
                for columnas in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(columnas)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                for filas in range(tabla.rowCount()):
                    datos_fila = []
                    for columnas in range(tabla.columnCount()):
                        item = tabla.item(filas, columnas)
                        datos_fila.append(item.text() if item is not None else '')
                    writer.writerow(datos_fila)

            QtWidgets.QMessageBox.information(self.main_window, 'Exportar CSV', f'CSV exportado correctamente a:\n{filename}')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, 'Exportar CSV', f'Error al exportar CSV:\n{e}')
