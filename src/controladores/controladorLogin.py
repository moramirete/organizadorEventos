from PyQt5.QtWidgets import QMainWindow, QMessageBox
from interfazLogin import Ui_LoginWindow
from controladorHome import ControladorHome
from interfazHome import Ui_MainWindow

class ControladorLogin:
    def __init__(self, main_window: QMainWindow, ui: Ui_LoginWindow):
        self.main_window = main_window
        self.ui = ui
        self.is_login_mode = True 

        self.ui.btnAction.clicked.connect(self.ejecutar_accion)
        self.ui.btnToggleMode.clicked.connect(self.cambiar_modo)

    def cambiar_modo(self):
        self.is_login_mode = not self.is_login_mode
        
        # Cambiamos visibilidad (Replica MainActivity.kt)
        self.ui.lblUser.setVisible(not self.is_login_mode)
        self.ui.etUsername.setVisible(not self.is_login_mode)
        self.ui.lblConfirm.setVisible(not self.is_login_mode)
        self.ui.etConfirmPassword.setVisible(not self.is_login_mode)

        if self.is_login_mode:
            self.ui.tvFormTitle.setText("Iniciar Sesión")
            self.ui.btnAction.setText("Iniciar Sesión")
            self.ui.lblEmail.setText("Email o Nombre de Usuario")
            self.ui.btnToggleMode.setText("¿No tienes cuenta? Regístrate")
        else:
            self.ui.tvFormTitle.setText("Regístrate")
            self.ui.btnAction.setText("Registrarse")
            self.ui.lblEmail.setText("Email")
            self.ui.btnToggleMode.setText("¿Ya tienes cuenta? Inicia Sesión")

    def ejecutar_accion(self):
        if self.is_login_mode:
            # Lógica de login similar a activity_main.xml -> HomeActivity
            self.abrir_home()
        else:
            # Lógica de registro similar a activity_main.xml -> VerificacionEmailActivity
            self.cambiar_modo()

    def abrir_home(self):
        self.home_window = QMainWindow()
        self.home_ui = Ui_MainWindow()
        self.home_ui.setupUi(self.home_window)
        self.home_controller = ControladorHome(self.home_window, self.home_ui)
        self.home_window.show()
        self.main_window.close()