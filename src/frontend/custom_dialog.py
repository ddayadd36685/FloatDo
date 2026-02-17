from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QColor
from src.frontend.theme import theme_manager

class CustomInputDialog(QDialog):
    def __init__(self, parent=None, title="Input", label="Enter value:"):
        super().__init__(parent)
        # Use Dialog + Frameless to ensure proper modality and taskbar handling if needed
        # WindowStaysOnTopHint ensures it stays above other windows
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(300, 180)
        
        self.text_value = None
        self.lost_focus = False  # Track if dialog was closed due to focus loss
        self.setup_ui(title, label)
        
        # Apply theme
        self.update_style(theme_manager.get_theme())

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                # If window loses focus (e.g. user clicks desktop), close it
                self.lost_focus = True
                self.reject()
        super().changeEvent(event)

    def showEvent(self, event):
        # Center on parent or screen
        if self.parent():
            parent_geo = self.parent().geometry()
            geo = self.geometry()
            geo.moveCenter(parent_geo.center())
            self.setGeometry(geo)
        super().showEvent(event)
        self.activateWindow()
        self.line_edit.setFocus()

    def setup_ui(self, title_text, label_text):
        # Outer layout for shadow
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("DialogContainer")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("DialogTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Input Label
        self.input_label = QLabel(label_text)
        layout.addWidget(self.input_label)
        
        # Input Field
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("...")
        # Enable Enter key to trigger accept_input
        self.line_edit.returnPressed.connect(self.accept_input)
        layout.addWidget(self.line_edit)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self.accept_input)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        
        layout.addLayout(btn_layout)
        
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)

    def accept_input(self):
        self.text_value = self.line_edit.text()
        self.accept()

    def update_style(self, theme):
        self.container.setStyleSheet(f"""
            QFrame#DialogContainer {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: 12px;
            }}
        """)
        
        style = f"color: {theme.text};"
        self.title_label.setStyleSheet(style + "font-size: 16px; font-weight: bold;")
        self.input_label.setStyleSheet(style)
        
        self.line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.bg};
                color: {theme.text};
                border: 1px solid {theme.border};
                border-radius: 6px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.accent};
            }}
        """)
        
        btn_style = f"""
            QPushButton {{
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
            }}
        """
        
        self.cancel_btn.setStyleSheet(btn_style + f"""
            background-color: transparent;
            color: {theme.secondary_text};
            border: 1px solid {theme.border};
        """)
        
        self.ok_btn.setStyleSheet(btn_style + f"""
            background-color: {theme.accent};
            color: white;
            border: none;
        """)

    @staticmethod
    def get_text(parent, title, label):
        dialog = CustomInputDialog(parent, title, label)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.text_value, True
        return "", False

class CustomConfirmDialog(QDialog):
    def __init__(self, parent=None, title="Confirm", message="Are you sure?"):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(320, 160)
        
        self.setup_ui(title, message)
        self.update_style(theme_manager.get_theme())
        
    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                self.reject()
        super().changeEvent(event)

    def showEvent(self, event):
        if self.parent():
            parent_geo = self.parent().geometry()
            geo = self.geometry()
            geo.moveCenter(parent_geo.center())
            self.setGeometry(geo)
        super().showEvent(event)
        self.activateWindow()

    def setup_ui(self, title_text, message_text):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("DialogContainer")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("DialogTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # Message
        self.message_label = QLabel(message_text)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        
        layout.addLayout(btn_layout)
        
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)

    def update_style(self, theme):
        self.container.setStyleSheet(f"""
            QFrame#DialogContainer {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: 12px;
            }}
        """)
        
        style = f"color: {theme.text};"
        self.title_label.setStyleSheet(style + "font-size: 16px; font-weight: bold;")
        self.message_label.setStyleSheet(style)
        
        btn_style = f"""
            QPushButton {{
                border-radius: 6px;
                padding: 6px 15px;
                font-weight: bold;
            }}
        """
        
        self.cancel_btn.setStyleSheet(btn_style + f"""
            background-color: transparent;
            color: {theme.secondary_text};
            border: 1px solid {theme.border};
        """)
        
        self.ok_btn.setStyleSheet(btn_style + f"""
            background-color: #FF7675; /* Red for destructive action */
            color: white;
            border: none;
        """)

    @staticmethod
    def confirm(parent, title, message):
        dialog = CustomConfirmDialog(parent, title, message)
        return dialog.exec() == QDialog.DialogCode.Accepted
