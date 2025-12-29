from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(1024, 700)
        LoginWindow.setStyleSheet("background-color: #F2F4F7;")
        
        self.centralwidget = QtWidgets.QWidget(LoginWindow)
        self.layout_principal = QtWidgets.QVBoxLayout(self.centralwidget)
        self.layout_principal.setContentsMargins(0, 0, 0, 0)
        self.layout_principal.setSpacing(0)

        # Cabecera Azul (Se mantiene fija arriba)
        self.headerFrame = QtWidgets.QFrame()
        self.headerFrame.setFixedHeight(180) # Reducido un poco para dar aire al formulario
        self.headerFrame.setStyleSheet("background-color: #1E73E8;")
        header_layout = QtWidgets.QVBoxLayout(self.headerFrame)
        
        self.lblHeader = QtWidgets.QLabel("Gestor de Eventos\nLos Super Nenes")
        self.lblHeader.setStyleSheet("color: white; font-size: 26pt; font-weight: bold;")
        self.lblHeader.setAlignment(QtCore.Qt.AlignCenter)
        header_layout.addWidget(self.lblHeader)
        self.layout_principal.addWidget(self.headerFrame)

        # Contenedor central (Sustituye al ScrollArea)
        self.container_centro = QtWidgets.QWidget()
        self.layout_centro = QtWidgets.QHBoxLayout(self.container_centro)
        
        # Espaciadores laterales para centrar horizontalmente
        self.layout_centro.addStretch()
        
        # Tarjeta blanca (CardView)
        self.cardFrame = QtWidgets.QFrame()
        self.cardFrame.setFixedWidth(550) 
        self.cardFrame.setStyleSheet("""
            QFrame { background-color: white; border-radius: 20px; }
            QLineEdit { border: 1px solid #D3D3D3; border-radius: 8px; padding: 10px; font-size: 11pt; }
            QLabel { color: #5F6368; font-weight: bold; background: transparent; }
        """)
        
        self.formLayout = QtWidgets.QVBoxLayout(self.cardFrame)
        self.formLayout.setContentsMargins(40, 30, 40, 30)
        self.formLayout.setSpacing(12)

        self.tvFormTitle = QtWidgets.QLabel("Iniciar Sesión")
        self.tvFormTitle.setStyleSheet("font-size: 20pt; color: #202124; margin-bottom: 5px;")
        self.tvFormTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.addWidget(self.tvFormTitle)

        # Campos dinámicos (Username)
        self.lblUser = QtWidgets.QLabel("Nombre de Usuario")
        self.etUsername = QtWidgets.QLineEdit()
        self.etUsername.setPlaceholderText("Ej: SuperNene01")
        self.formLayout.addWidget(self.lblUser)
        self.formLayout.addWidget(self.etUsername)
        self.lblUser.setVisible(False)
        self.etUsername.setVisible(False)

        # Email
        self.lblEmail = QtWidgets.QLabel("Email o Nombre de Usuario")
        self.etEmail = QtWidgets.QLineEdit()
        self.etEmail.setPlaceholderText("tu@email.com")
        self.formLayout.addWidget(self.lblEmail)
        self.formLayout.addWidget(self.etEmail)

        # Contraseña
        self.formLayout.addWidget(QtWidgets.QLabel("Contraseña"))
        self.etPassword = QtWidgets.QLineEdit()
        self.etPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.addWidget(self.etPassword)

        # Campos dinámicos (Confirmar Password)
        self.lblConfirm = QtWidgets.QLabel("Confirmar Contraseña")
        self.etConfirmPassword = QtWidgets.QLineEdit()
        self.etConfirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.addWidget(self.lblConfirm)
        self.formLayout.addWidget(self.etConfirmPassword)
        self.lblConfirm.setVisible(False)
        self.etConfirmPassword.setVisible(False)

        # Botón Acción
        self.btnAction = QtWidgets.QPushButton("Iniciar Sesión")
        self.btnAction.setFixedHeight(50)
        self.btnAction.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnAction.setStyleSheet("""
            QPushButton { background-color: #202124; color: white; border-radius: 10px; font-weight: bold; font-size: 12pt; margin-top: 10px; }
            QPushButton:hover { background-color: #3c4043; }
        """)
        self.formLayout.addWidget(self.btnAction)

        # Toggle modo
        self.btnToggleMode = QtWidgets.QPushButton("¿No tienes cuenta? Regístrate")
        self.btnToggleMode.setCursor(QtCore.Qt.PointingHandCursor)
        self.btnToggleMode.setStyleSheet("color: #1E73E8; border: none; font-size: 10pt; background: transparent; padding: 5px;")
        self.formLayout.addWidget(self.btnToggleMode)

        self.layout_centro.addWidget(self.cardFrame)
        self.layout_centro.addStretch() # Centrado horizontal
        
        # Añadimos el contenedor al layout principal con espaciadores verticales
        self.layout_principal.addStretch() # Empuja hacia abajo
        self.layout_principal.addWidget(self.container_centro)
        self.layout_principal.addStretch() # Empuja hacia arriba
        
        LoginWindow.setCentralWidget(self.centralwidget)