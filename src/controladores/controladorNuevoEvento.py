import sys
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore

# Preparo la ruta para poder importar las interfaces .py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
interfaces_path = os.path.join(project_root, 'interfazes', 'python')
if interfaces_path not in sys.path:
    sys.path.append(interfaces_path)

from interfazHomeModificarListadoEventosEvento import Ui_EventoEditar
from interfazHomeParticipantesMesas import Ui_ParticipantsManager
from controladorParticipantes import ControladorParticipantes

# Añado src al path para poder importar los modelos
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from modelos.evento import Evento


class controladorNuevoEvento:
    
    def __init__(self, main_window, ui, parent_controller):
        self.main_window = main_window 
        self.ui = ui
        # Referencia al controlador principal (Home)
        self.parent_controller = parent_controller
        self.siguiente_window = None

        # Evento que se rellena con los datos del formulario
        self.evento = Evento()
        # Para saber si se han guardado los cambios
        self.cambios_guardados = False

        self.conectar_botones()
        
    def conectar_botones(self):
        # Botón para pasar a la pantalla de participantes/mesas
        self.ui.btnSiguiente.clicked.connect(self.ir_siguiente_interfaz)
        
        # Botón para guardar el evento
        try:
            self.ui.btnGuardarCambios.clicked.connect(self.guardar_cambios)
        except Exception:
            pass

        # Botón para volver al menú principal
        self.ui.btnCancelar.clicked.connect(self.volver_ventana_anterior)

    def ir_siguiente_interfaz(self):
        # Solo dejo continuar si antes se han guardado los cambios
        if not self.cambios_guardados:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Guardar Cambios',
                'Debes guardar los cambios antes de continuar.'
            )
            return

        # Creo la ventana para gestionar participantes y mesas
        self.siguiente_window = QMainWindow()
        siguiente_ui = Ui_ParticipantsManager()
        siguiente_ui.setupUi(self.siguiente_window)
        
        # Creo el controlador de participantes y le paso este como padre
        self.participantes_controller = ControladorParticipantes(
            self.siguiente_window,
            siguiente_ui,
            self
        )

        # Paso el evento al controlador de participantes
        self.participantes_controller.evento = self.evento
        
        # Muestro la nueva ventana y oculto la actual
        self.siguiente_window.show()
        self.main_window.hide()

    def guardar_cambios(self):
        # Cojo los datos escritos en el formulario
        nombre = self.ui.leNombre.text().strip()
        num_mesas = int(self.ui.sbMesas.value())
        inv_por_mesa = int(self.ui.sbInvPorMesa.value())
        fecha = self.ui.deFecha.date().toString('yyyy-MM-dd')
        cliente = self.ui.leCliente.text().strip()
        telefono = self.ui.leTelefono.text().strip()

        # Compruebo que al menos haya nombre
        if not nombre:
            QtWidgets.QMessageBox.warning(
                self.main_window,
                'Validación',
                'El nombre del evento es obligatorio.'
            )
            return

        # Guardo los datos en el objeto Evento (localmente)
        if self.evento is None:
            self.evento = Evento(nombre, num_mesas, inv_por_mesa, fecha, cliente, telefono)
        else:
            self.evento.nombre = nombre
            self.evento.num_mesas = num_mesas
            self.evento.inv_por_mesa = inv_por_mesa
            self.evento.fecha = fecha
            self.evento.cliente = cliente
            self.evento.telefono = telefono
        
        # --- GUARDAR EN SUPABASE ---
        try:
            from config.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            
            # Obtenemos los datos del usuario actual desde el controlador padre (Home)
            usuario_id = self.parent_controller.current_user_id
            usuario_nombre = self.parent_controller.current_user_name
            usuario_email = getattr(self.parent_controller, 'current_user_email', None)
            
            # --- SALVAGUARDA: Sincronizar perfil antes de insertar evento ---
            # Esto asegura que el usuario_id existe en la tabla 'usuarios' (FK)
            try:
                supabase.table("usuarios").upsert({
                    "id": usuario_id,
                    "username": usuario_nombre,
                    "email": usuario_email
                }).execute()
            except Exception as e:
                print(f"Aviso: No se pudo auto-sincronizar perfil: {e}")

            # Preparamos los datos según la imagen de la tabla 'eventos' que me pasaste
            # Nota: 'distribucion' guardará tanto participantes como mesas como JSON
            # Nota: 'num_mesas' e 'inv_por_mesa' no están en la DB, van dentro de distribucion
            datos_evento = {
                "usuario_id": usuario_id,
                "nombre": nombre,
                "fecha": fecha,
                "ubicacion": cliente,
                "telefono": int(telefono) if telefono.isdigit() else 0,
                "num_participantes": len(self.evento.participantes),
                "distribucion": {
                    "configuracion": {
                        "num_mesas": num_mesas,
                        "inv_por_mesa": inv_por_mesa
                    },
                    "lista_participantes": [
                        {"nombre": p.nombre, "prefiere": p.prefiere, "no_prefiere": p.no_prefiere}
                        for p in self.evento.participantes
                    ],
                    "asignaciones_mesas": self.evento.asignaciones_mesas
                }
            }

            # Si ya tenemos ID, lo incluimos para que haga UPSERT (actualizar en vez de insertar)
            if getattr(self.evento, 'id', None):
                datos_evento["id"] = self.evento.id
            
            res = supabase.table("eventos").upsert(datos_evento).execute()
            
            if res.data:
                # GUARDAMOS EL ID RECUPERADO DE LA BASE DE DATOS PARA FUTURAS ACTUALIZACIONES
                self.evento.id = res.data[0].get("id")
                
                self.cambios_guardados = True
                # Añado el evento a la lista general del Home si aún no está
                if self.evento not in self.parent_controller.eventos:
                    self.parent_controller.eventos.append(self.evento)

                QtWidgets.QMessageBox.information(
                    self.main_window,
                    'Guardar',
                    'Evento guardado correctamente en la nube.'
                )
            else:
                raise Exception("No se recibieron datos tras el guardado.")

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.main_window,
                'Error al Guardar',
                f'No se pudo guardar el evento en la base de datos: {str(e)}'
            )
    
    def volver_ventana_anterior(self):
        # Vuelvo a mostrar la ventana principal
        self.parent_controller.main_window.show()
        # Oculto la ventana de nuevo evento
        self.main_window.hide()
