import sys
import os
import csv
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
        
    def conectar_botones(self):
        self.ui.btnEditar.clicked.connect(self.abrir_editar_evento)
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_principal)
        self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
    # Método para abrir la ventana de edición del evento
    def abrir_editar_evento(self):
        self.editar_window = QMainWindow() 
        editar_ui = Ui_EventoEditar() 
        editar_ui.setupUi(self.editar_window)
        
      
        self.editar_controller = controladorEditarEvento(
            self.editar_window,
            editar_ui,
            self  # Pasamos la referencia a este controlador como padre
        )
        
        self.editar_window.show()
        
        self.main_window.hide()
    
    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos para modificar)
        self.main_window.hide()

    def exportar_csv(self):
        # Exporta el contenido de la tabla `tablaEventos` a un archivo CSV.

        # Abre un diálogo para elegir la ruta de guardado y escribe las cabeceras y filas actuales de la QTableWidget.
        
        tabla = getattr(self.ui, 'tablaEventos', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Exportar CSV', 'No se encontró la tabla de eventos.')
            return

        # Texto para seleccionar fichero
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window,'Guardar CSV','','CSV Files (*.csv);;All Files (*)',options=options)
        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # Aqui lo que hace es recorrer cad columna para obtener el encabezado principal de cada evento
                cabecera = []
                for columnas in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(columnas)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                # Aqui lo mismo para las filas. Al final escribe el texto de cada linea en el CSV
                for filas in range(tabla.rowCount()):
                    datos_fila = []
                    for columnas in range(tabla.columnCount()):
                        item = tabla.item(filas, columnas)
                        datos_fila.append(item.text() if item is not None else '')
                    writer.writerow(datos_fila)

            QtWidgets.QMessageBox.information(self.main_window, 'Exportar CSV', f'CSV exportado correctamente a:\n{filename}')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.main_window, 'Exportar CSV', f'Error al exportar CSV:\n{e}')