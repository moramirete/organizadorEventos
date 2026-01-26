import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication

# Ajusto la ruta para poder importar las interfaces .py del proyecto
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_script_dir, '..', '..'))
interface_path = os.path.join(project_root, 'interfazes', 'python')
if interface_path not in sys.path:
    sys.path.append(interface_path)

from interfazHome import Ui_MainWindow
from interfazHomeEvento import Ui_EventosListado
from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeModificarListadoEventos import Ui_EventosGestion
from controladorConsultar1 import ControladorConsultar1
from controladorModificarEventos import controladorModificarEventos
from controladorNuevoEvento import controladorNuevoEvento


class ControladorHome:
    def __init__(self, main_window: QMainWindow, ui: Ui_MainWindow):
        # Ventana principal y su interfaz
        self.main_window = main_window
        self.ui = ui
        
        # Lista donde se guardan todos los eventos de la aplicación
        self.eventos = []

        self.consultar_window = None
        self.nuevo_window = None
        self.modificar_window = None
        self.consultar_controller = None

        # Conecto los botones del menú principal
        self.conectar_senales()
        
    def set_user_data(self, user_id, nombre, email):
        """Recibe los datos del login y actualiza la interfaz"""
        self.current_user_id = user_id
        self.current_user_name = nombre
        self.current_user_email = email
        
        # --- CARGAR EVENTOS DESDE SUPABASE ---
        self.cargar_eventos_usuario(user_id)
        
        # Actualizamos el texto de bienvenida en la interfaz
        bienvenida_texto = (
            f"<html><head/><body><p align=\"center\">"
            f"<span style=\"font-size:18pt; font-weight:600; color:#333333;\">"
            f"¡Hola, {nombre}!</span><br/>"
            f"<span style=\"font-size:14pt; color:#666666;\">Bienvenido al Gestor de Eventos</span>"
            f"</p></body></html>"
        )
        self.ui.lblBienvenida.setText(bienvenida_texto)

    def cargar_eventos_usuario(self, user_id):
        """Consulta los eventos del usuario en Supabase y los carga en self.eventos"""
        try:
            from config.supabase_client import get_supabase_client
            from modelos.evento import Evento
            from modelos.participantes import Participante
            
            supabase = get_supabase_client()
            res = supabase.table("eventos").select("*").eq("usuario_id", user_id).execute()
            
            self.eventos = []
            for item in res.data:
                # Mapeamos los campos de la DB al objeto Evento
                # 'ubicacion' mapea a 'cliente' en nuestro modelo local
                ev = Evento(
                    nombre=item.get("nombre", ""),
                    num_mesas=item.get("num_mesas", 0),
                    inv_por_mesa=item.get("inv_por_mesa", 0),
                    fecha=item.get("fecha"),
                    cliente=item.get("ubicacion", ""),
                    telefono=str(item.get("telefono", "")),
                    id=item.get("id") # Guardamos el ID real de la DB
                )
                
                # --- RECONSTRUIR DATOS DESDE DISTRIBUCION (JSONB) ---
                dist = item.get("distribucion", [])
                if isinstance(dist, list):
                    # Nuevo formato: [ {numero, capacidad, participantes: [{nombre, prefiere, noPrefiere}] }, ... ]
                    
                    # Primero cargamos a todos los participantes para reconstruir ev.participantes
                    # Y guardamos las asignaciones de mesas
                    ev.participantes = []
                    ev.asignaciones_mesas = []
                    
                    # Buscamos la mesa 0 (invitados sin asignar) si existe para la lista general
                    # Y procesamos el resto de mesas
                    nombres_añadidos = set()
                    
                    for mesa in dist:
                        m_num = mesa.get("numero", 0)
                        m_cap = mesa.get("capacidad", 0)
                        m_parts = mesa.get("participantes", [])
                        
                        # Reconstruimos la lista local de participantes del evento (ev.participantes)
                        invitados_nombres_mesa = []
                        for p_data in m_parts:
                            nombre = p_data.get("nombre", "")
                            if nombre and nombre not in nombres_añadidos:
                                p = Participante(
                                    nombre=nombre,
                                    prefiere=p_data.get("prefiere", ""),
                                    # Soportamos ambos nombres de campo para transición suave
                                    no_prefiere=p_data.get("noPrefiere", p_data.get("no_prefiere", ""))
                                )
                                ev.participantes.append(p)
                                nombres_añadidos.add(nombre)
                            invitados_nombres_mesa.append(nombre)
                        
                        # Si es una mesa real (>0), la añadimos a asignaciones_mesas
                        if m_num > 0:
                            ev.asignaciones_mesas.append({
                                'id': m_num,
                                'capacidad': m_cap,
                                'invitados': invitados_nombres_mesa
                            })
                            # También intentamos actualizar num_mesas e inv_por_mesa del evento
                            ev.num_mesas = max(ev.num_mesas, m_num)
                            ev.inv_por_mesa = max(ev.inv_por_mesa, m_cap)

                elif isinstance(dist, dict):
                    # Formato antiguo (fallback)
                    config = dist.get("configuracion", {})
                    ev.num_mesas = config.get("num_mesas", ev.num_mesas)
                    ev.inv_por_mesa = config.get("inv_por_mesa", ev.inv_por_mesa)
                    
                    lista_p = dist.get("lista_participantes", [])
                    for p_data in lista_p:
                        if isinstance(p_data, dict):
                            p = Participante(
                                nombre=p_data.get("nombre", ""),
                                prefiere=p_data.get("prefiere", ""),
                                no_prefiere=p_data.get("no_prefiere", "")
                            )
                            ev.participantes.append(p)
                    
                    ev.asignaciones_mesas = dist.get("asignaciones_mesas", [])
                
                self.eventos.append(ev)
                
            print(f"Se han cargado {len(self.eventos)} eventos completos para el usuario.")
            
        except Exception as e:
            print(f"Error cargando eventos de la nube: {e}")




    def conectar_senales(self):
        # Botón para ir a consultar eventos
        self.ui.btnConsultar.clicked.connect(self.abrir_consultar_eventos)
        # Botón para crear un evento nuevo
        self.ui.btnNuevo.clicked.connect(self.abrir_nuevo_evento)
        # Botón para modificar/eliminar eventos
        self.ui.btnModificar.clicked.connect(self.abrir_modificar_eventos)

    def abrir_consultar_eventos(self):
        # Abro la ventana con el listado de eventos
        self.consultar_window = QMainWindow()
        consultar_ui = Ui_EventosListado()
        consultar_ui.setupUi(self.consultar_window)
        
        # Controlador de la pantalla de consulta, le paso este como padre
        self.consultar_controller = ControladorConsultar1(
            self.consultar_window,
            consultar_ui,
            self
        )
        
        self.consultar_window.show()
        # Si quisiera ocultar el home, descomento:
        # self.main_window.hide()

    def abrir_nuevo_evento(self):
        # Abro la ventana para crear un evento nuevo
        self.nuevo_window = QMainWindow()
        nuevo_ui = Ui_EventoEditar()
        nuevo_ui.setupUi(self.nuevo_window)

        # Controlador que gestiona la creación del evento
        self.nuevo_controller = controladorNuevoEvento(
            self.nuevo_window,
            nuevo_ui,
            self
        )
        
        self.nuevo_window.show()
        # self.main_window.hide()
    
    def abrir_modificar_eventos(self):
        # Abro la ventana para gestionar (modificar/borrar) eventos
        self.modificar_window = QMainWindow()
        modificar_ui = Ui_EventosGestion()
        modificar_ui.setupUi(self.modificar_window)

        # Controlador que maneja la parte de modificación
        self.modificar_controller = controladorModificarEventos(
            self.modificar_window,
            modificar_ui,
            self
        )
        
        self.modificar_window.show()
        # self.main_window.hide()


# Punto de entrada de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    controller = ControladorHome(MainWindow, ui)
    
    MainWindow.show()
    sys.exit(app.exec_())
