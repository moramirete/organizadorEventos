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
