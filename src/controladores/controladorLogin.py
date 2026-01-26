import sys
import os
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from supabase import create_client, Client

from config.supabase_client import get_supabase_client

class ControladorLogin:
    def __init__(self, main_window: QMainWindow, ui):
        self.main_window = main_window
        self.ui = ui
        self.is_login_mode = True 
        
        # Conexión al cliente
        try:
            self.supabase = get_supabase_client()
        except Exception as e:
            print(f"Error conexión: {e}")

        # Conectar botones
        self.ui.btnAction.clicked.connect(self.ejecutar_accion)
        self.ui.btnToggleMode.clicked.connect(self.cambiar_modo)

    def ejecutar_accion(self):
        if self.is_login_mode:
            self.login_supabase()
        else:
            self.registrar_supabase()

    def registrar_supabase(self):
        """Registro usando metadata para el nombre (sin modificar la DB externa)"""
        nombre = self.ui.etUsername.text().strip()
        email = self.ui.etEmail.text().strip()
        password = self.ui.etPassword.text().strip()
        confirm_pass = self.ui.etConfirmPassword.text().strip()

        # Validaciones básicas
        if not nombre or not email or not password:
            QMessageBox.warning(self.main_window, "Validación", "Por favor, rellena todos los campos.")
            return
        
        if password != confirm_pass:
            QMessageBox.warning(self.main_window, "Error", "Las contraseñas no coinciden.")
            return

        if len(password) < 6:
            QMessageBox.warning(self.main_window, "Error", "La contraseña debe tener al menos 6 caracteres.")
            return

        try:
            # Registro en Supabase Auth con metadatos de usuario
            # Esto guarda la información en la tabla interna auth.users
            res = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": nombre
                    }
                }
            })
            
            if res.user:
                # --- SINCRONIZACIÓN AUTOMÁTICA DE PERFIL ---
                # Insertamos/Actualizamos el perfil en 'usuarios' para evitar errores de Foreign Key
                self.sincronizar_perfil(res.user.id, nombre, email)
                
                QMessageBox.information(
                    self.main_window, 
                    "Éxito", 
                    f"¡Cuenta creada con éxito para {nombre}!\nYa puedes iniciar sesión."
                )
                self.cambiar_modo()
            else:
                # Casos donde no hay error pero no devuelve usuario (ej. confirmación de email pendiente)
                QMessageBox.information(
                    self.main_window, 
                    "Verificación enviada", 
                    "Se ha enviado un correo de confirmación. Por favor, verifica tu cuenta para continuar."
                )
                self.cambiar_modo()

        except Exception as e:
            # Capturamos errores de Supabase (email ya registrado, formato inválido, etc)
            error_msg = str(e)
            if "User already registered" in error_msg:
                QMessageBox.critical(self.main_window, "Error de Registro", "Este correo electrónico ya está registrado.")
            else:
                QMessageBox.critical(self.main_window, "Error", f"No se pudo completar el registro: {error_msg}")

    def login_supabase(self):
        """Login recuperando el nombre de metadata (admite email o username)"""
        credencial = self.ui.etEmail.text().strip()
        password = self.ui.etPassword.text().strip()

        if not credencial or not password:
            QMessageBox.warning(self.main_window, "Validación", "Por favor, introduce tus credenciales.")
            return

        email = credencial
        # Si no parece un email (no tiene @), buscamos el username en la DB
        if "@" not in credencial:
            try:
                res_user = self.supabase.table("usuarios").select("email").eq("username", credencial).execute()
                if res_user.data and len(res_user.data) > 0:
                    email = res_user.data[0].get("email")
                else:
                    QMessageBox.critical(self.main_window, "Error", f"No se encontró ningún usuario con el nombre: {credencial}")
                    return
            except Exception as e:
                print(f"Error buscando username: {e}")
                QMessageBox.critical(self.main_window, "Error", "Error al conectar con la base de datos.")
                return

        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                # Extraemos el nombre guardado en el registro
                metadata = res.user.user_metadata if res.user.user_metadata else {}
                nombre_usuario = metadata.get("full_name", "Usuario")
                
                # --- SINCRONIZACIÓN AUTOMÁTICA DE PERFIL ---
                self.sincronizar_perfil(res.user.id, nombre_usuario, email)
                
                # Pasamos ID, Nombre y Email al Home
                self.abrir_home(res.user.id, nombre_usuario, email)
        except Exception:
            QMessageBox.critical(self.main_window, "Error", "Credenciales incorrectas.")

    def abrir_home(self, user_id, nombre, email):
        from controladorHome import ControladorHome
        from interfazHome import Ui_MainWindow
        
        self.home_win = QMainWindow()
        self.home_ui = Ui_MainWindow()
        self.home_ui.setupUi(self.home_win)
        
        # Pasamos los datos al controlador del Home
        self.home_controller = ControladorHome(self.home_win, self.home_ui)
        self.home_controller.set_user_data(user_id, nombre, email)
        
        self.home_win.show()
        self.main_window.close()

    def cambiar_modo(self):
        self.is_login_mode = not self.is_login_mode
        self.ui.lblUser.setVisible(not self.is_login_mode)
        self.ui.etUsername.setVisible(not self.is_login_mode)
        self.ui.lblConfirm.setVisible(not self.is_login_mode)
        self.ui.etConfirmPassword.setVisible(not self.is_login_mode)
        
        texto_boton = "Iniciar Sesión" if self.is_login_mode else "Registrarse"
        self.ui.btnAction.setText(texto_boton)
        self.ui.tvFormTitle.setText(texto_boton)
        
        # Actualizamos el placeholder para indicar que se admite username
        if self.is_login_mode:
            self.ui.etEmail.setPlaceholderText("Correo o nombre de usuario")
        else:
            self.ui.etEmail.setPlaceholderText("Correo electrónico")

    def sincronizar_perfil(self, user_id, nombre, email):
        """Asegura que el usuario existe en la tabla 'usuarios' para cumplir con FKs"""
        try:
            # Según la imagen, la tabla 'usuarios' usa 'username' y 'email'
            self.supabase.table("usuarios").upsert({
                "id": user_id,
                "username": nombre,
                "email": email
            }).execute()
        except Exception as e:
            print(f"Error sincronizando perfil: {e}")