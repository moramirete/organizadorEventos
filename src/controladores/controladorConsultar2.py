import sys
import os
import csv
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtWidgets

# --- INICIO: CORRECCIÓN DE RUTA DE IMPORTACIÓN PARA MODULOS ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)
# --- FIN: CORRECCIÓN DE RUTA DE IMPORTACIÓN ---

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeEventoMesas import Ui_EventoMesas


class ControladorConsultar2:
    
    # ACEPTA EL CONTROLADOR PADRE
    def __init__(self, main_window: QMainWindow, ui: Ui_EventosListado, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        self.parent_controller = parent_controller  # Almacenamos la referencia a ControladorHome
        
        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None
        self.evento_seleccionado = None

        self.conectar_botones()
        self.cargar_evento_seleccionado()
        
    def conectar_botones(self):
        self.ui.btnVolver.clicked.connect(self.volver_ventana_principal)
        self.ui.btnExportarCSV.clicked.connect(self.exportar_csv)
        # FALTA EL BOTON EXPORTARCSV

    # Método para abrir la ventana del evento con sus datos (la vista de mesas)
    
    
    def volver_ventana_principal(self):
        # 1. Usamos la referencia al ControladorHome para mostrar su ventana
        self.parent_controller.main_window.show()
        
        # 2. Ocultamos la ventana actual (Listado de Eventos)
        self.main_window.hide()

    def exportar_csv(self):
        
        # Exporta el contenido de la tabla `tablaEventos` a un archivo CSV.

        # Abre un diálogo para elegir la ruta de guardado y escribe las cabeceras y filas actuales de la QTableWidget.

        tabla = getattr(self.ui, 'tablaMesas', None)
        if tabla is None:
            QtWidgets.QMessageBox.warning(self.main_window, 'Exportar CSV', 'No se encontró la tabla de eventos.')
            return

        # Texto para seleccionar fichero
        # Tambien hace que los archivos que se guarden sea en formato .csv
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self.main_window,'Guardar CSV','','CSV Files (*.csv);;All Files (*)',options=options)
        if not filename:
            return

        # Aqui hago un try except por si ocurre un error, que el programa siga en ejecución.

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # Aqui lo que hace es recorrer cada columna para obtener el encabezado principal de los eventos (id, fecha,nombre, etc...)

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
    
    def cargar_evento_seleccionado(self):
        """Obtiene el evento seleccionado de la tabla del controlador padre y lo carga."""
        # Obtener la tabla del controlador padre
        tabla_eventos = getattr(self.parent_controller.ui, 'tablaEventos', None)
        if tabla_eventos is None:
            return
        
        # Obtener la fila seleccionada
        fila_seleccionada = tabla_eventos.currentRow()
        if fila_seleccionada < 0:
            QtWidgets.QMessageBox.warning(self.main_window, 'Selección', 'Por favor selecciona un evento de la lista.')
            return
        
        # Obtener el evento de la lista del Home
        eventos = getattr(self.parent_controller.parent_controller, 'eventos', [])
        if fila_seleccionada < len(eventos):
            self.evento_seleccionado = eventos[fila_seleccionada]
            self.mostrar_informacion_evento()
    
    def mostrar_informacion_evento(self):
        """Muestra las mesas y participantes del evento en la tabla."""
        if self.evento_seleccionado is None:
            return
        
        tabla = getattr(self.ui, 'tablaMesas', None)
        if tabla is None:
            return
        
        # Limpiar tabla
        tabla.clearContents()
        tabla.setRowCount(0)
        
        # Mostrar información de cada mesa
        num_mesas = int(getattr(self.evento_seleccionado, 'num_mesas', 0))
        inv_por_mesa = int(getattr(self.evento_seleccionado, 'inv_por_mesa', 0))
        
        if num_mesas == 0:
            QtWidgets.QMessageBox.information(self.main_window, 'Sin mesas', 'Este evento no tiene mesas configuradas.')
            return
        
        # Verificar si hay asignaciones guardadas
        asignaciones = getattr(self.evento_seleccionado, 'asignaciones_mesas', [])
        
        if asignaciones and len(asignaciones) > 0:
            # Mostrar asignaciones guardadas
            tabla.setRowCount(len(asignaciones))
            for i, mesa in enumerate(asignaciones):
                if not isinstance(mesa, dict):
                    continue
                    
                # Columna 0: Número de mesa
                mesa_id = mesa.get('id', i+1)
                tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(f"Mesa {mesa_id}"))
                
                # Columna 1: Invitados asignados (nombres)
                invitados = mesa.get('invitados', [])
                if invitados and len(invitados) > 0:
                    # Mostrar nombres de invitados
                    nombres_lista = [str(nombre) for nombre in invitados if nombre]
                    if nombres_lista:
                        nombres_texto = ', '.join(nombres_lista)
                        tabla.setItem(i, 1, QtWidgets.QTableWidgetItem(nombres_texto))
                    else:
                        tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))
                else:
                    tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))
        else:
            # Si no hay asignaciones, mostrar mesas vacías
            tabla.setRowCount(num_mesas)
            for i in range(num_mesas):
                tabla.setItem(i, 0, QtWidgets.QTableWidgetItem(f'Mesa {i+1}'))
                tabla.setItem(i, 1, QtWidgets.QTableWidgetItem('Sin asignar'))