import sys
import os
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets

# Ajusto la ruta para poder importar las interfaces del proyecto
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeEventoMesas import Ui_EventoMesas


class ControladorConsultar2:
    
    # Recibe la ventana, la interfaz y el controlador padre
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        # Controlador padre (ControladorConsultar1)
        self.parent_controller = parent_controller
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None
        self.evento_seleccionado = None

        self.conectar_botones()
        self.cargar_evento_seleccionado()
        
    def conectar_botones(self):
        self.ui.btnVolver.clicked.connect(self.volver_ventana_principal)
        self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        # Falta el botón ExportarCSV en el .ui si no existe

    def volver_ventana_principal(self):
        """Vuelve a la ventana anterior usando el controlador padre."""
        self.parent_controller.main_window.show()
        self.main_window.hide()

    def exportar_csv(self):
        """Exporta la tabla de mesas a un archivo CSV."""
        tabla = getattr(self.ui, 'tablaMesas', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Exportar CSV',
                'No se encontró la tabla de mesas.'
            )
            return

        # Cuadro de diálogo para elegir el fichero donde guardar
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

                # Escribo primero la fila de cabeceras
                cabecera = []
                for columnas in range(tabla.columnCount()):
                    item = tabla.horizontalHeaderItem(columnas)
                    cabecera.append(item.text() if item is not None else '')
                writer.writerow(cabecera)

                # Ahora recorro todas las filas de la tabla
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
    
    def cargar_evento_seleccionado(self):
        """Obtiene el evento seleccionado de la tabla del controlador padre y lo carga."""
        tabla_eventos = getattr(self.parent_controller.ui, 'tablaEventos', None)
        if tabla_eventos is None:
            return
        
        fila_seleccionada = tabla_eventos.currentRow()
        if fila_seleccionada < 0:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Selección',
                'Por favor selecciona un evento de la lista.'
            )
            return
        
        # Cojo el evento de la lista que mantiene el Home
        eventos = getattr(self.parent_controller.parent_controller, 'eventos', [])
        if fila_seleccionada < len(eventos):
            self.evento_seleccionado = eventos[fila_seleccionada]
            self.mostrar_informacion_evento()
    
    def mostrar_informacion_evento(self):
        """Muestra las mesas y sus invitados en la tabla."""
        if self.evento_seleccionado is None:
            return
        
        tabla = getattr(self.ui, 'tablaMesas', None)
        if tabla is None:
            return
        
        # Limpio la tabla antes de rellenarla
        tabla.clearContents()
        tabla.setRowCount(0)
        
        num_mesas = int(getattr(self.evento_seleccionado, 'num_mesas', 0))
        inv_por_mesa = int(getattr(self.evento_seleccionado, 'inv_por_mesa', 0))
        
        if num_mesas == 0:
            QtWidgets.QMessageBox.information(
                self.main_window,
                'Sin mesas',
                'Este evento no tiene mesas configuradas.'
            )
            return
        
        # Miro si el evento tiene asignaciones guardadas
        asignaciones = getattr(self.evento_seleccionado, 'asignaciones_mesas', [])
        
        if asignaciones and len(asignaciones) > 0:
            tabla.setRowCount(len(asignaciones))
            for i, mesa in enumerate(asignaciones):
                if not isinstance(mesa, dict):
                    continue
                    
                # Columna 0: número de mesa
                mesa_id = mesa.get('id', i + 1)
                tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(f"Mesa {mesa_id}"))
                
                # Columna 1: invitados asignados
                invitados = mesa.get('invitados', [])
                if invitados and len(invitados) > 0:
                    nombres_lista = [str(nombre) for nombre in invitados if nombre]
                    if nombres_lista:
                        nombres_texto = ', '.join(nombres_lista)
                        tabla.setItem(i, 1, QtWidgets.QTableWidgetItem(nombres_texto))
                    else:
                        tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))
                else:
                    tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))
        else:
            # Si no hay datos guardados, pongo las mesas vacías
            tabla.setRowCount(num_mesas)
            for i in range(num_mesas):
                tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(f'Mesa {i+1}'))
                tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))
