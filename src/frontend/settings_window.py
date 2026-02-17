from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QRadioButton, QHBoxLayout, QFrame, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
from src.frontend.theme import theme_manager

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Use Dialog + Frameless to match custom dialog style and ensure proper window behavior
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.resize(320, 240)
        
        self.setup_ui()
        self.update_style(theme_manager.get_theme())
        theme_manager.theme_changed.connect(self.update_style)

    def showEvent(self, event):
        # Center on screen or parent
        if self.parent():
            parent_geo = self.parent().geometry()
            geo = self.geometry()
            geo.moveCenter(parent_geo.center())
            self.setGeometry(geo)
        else:
            # Center on active screen
            screen = self.screen().availableGeometry()
            geo = self.geometry()
            geo.moveCenter(screen.center())
            self.setGeometry(geo)
        super().showEvent(event)
        self.activateWindow()

    def setup_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("SettingsContainer")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title Bar (with Close button)
        title_layout = QHBoxLayout()
        title = QLabel("设置 (Settings)")
        title.setObjectName("SettingsTitle")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 20px; font-weight: bold;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addLayout(title_layout)
        
        # Theme Section
        theme_label = QLabel("主题 (Theme)")
        theme_label.setObjectName("SectionLabel")
        theme_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(theme_label)
        
        self.radio_light = QRadioButton("浅色 (Light)")
        self.radio_dark = QRadioButton("深色 (Dark)")
        
        # Set initial state
        if theme_manager.get_theme().name == "Light":
            self.radio_light.setChecked(True)
        else:
            self.radio_dark.setChecked(True)
            
        self.radio_light.toggled.connect(lambda: self.change_theme("light"))
        self.radio_dark.toggled.connect(lambda: self.change_theme("dark"))
        
        layout.addWidget(self.radio_light)
        layout.addWidget(self.radio_dark)
        layout.addStretch()
        
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)

    def change_theme(self, mode):
        if (mode == "light" and self.radio_light.isChecked()) or \
           (mode == "dark" and self.radio_dark.isChecked()):
            theme_manager.set_theme(mode)

    def update_style(self, theme):
        self.container.setStyleSheet(f"""
            QFrame#SettingsContainer {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: 12px;
            }}
        """)
        
        style = f"color: {theme.text}; font-family: 'Segoe UI', sans-serif;"
        self.setStyleSheet(style)
        
        # Radio Button Style
        radio_style = f"""
            QRadioButton {{
                spacing: 8px;
                color: {theme.text};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {theme.secondary_text};
                background: transparent;
            }}
            QRadioButton::indicator:checked {{
                background-color: {theme.accent};
                border-color: {theme.accent};
            }}
        """
        self.radio_light.setStyleSheet(radio_style)
        self.radio_dark.setStyleSheet(radio_style)

