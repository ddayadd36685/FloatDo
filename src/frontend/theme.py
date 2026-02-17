from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal

class Theme:
    def __init__(self, name, bg, surface, text, secondary_text, accent, border, hover):
        self.name = name
        self.bg = bg
        self.surface = surface
        self.text = text
        self.secondary_text = secondary_text
        self.accent = accent
        self.border = border
        self.hover = hover

LIGHT_THEME = Theme(
    name="Light",
    bg="#F5F7FA",
    surface="#FFFFFF",
    text="#2D3436",
    secondary_text="#636E72",
    accent="#6C5CE7",
    border="#DFE6E9",
    hover="#F1F2F6"
)

DARK_THEME = Theme(
    name="Dark",
    bg="#121212",
    surface="#1E1E2E",
    text="#FFFFFF",
    secondary_text="#A0A0A0",
    accent="#7F5AF0", # Soft Purple/Blue for Dark Mode
    border="#2A2A3C",
    hover="#252535"
)

class ThemeManager(QObject):
    theme_changed = pyqtSignal(Theme)

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance.current_theme = DARK_THEME # Default to Dark as per request
        return cls._instance

    def set_theme(self, mode: str):
        if mode.lower() == "light":
            self.current_theme = LIGHT_THEME
        else:
            self.current_theme = DARK_THEME
        self.theme_changed.emit(self.current_theme)

    def get_theme(self):
        return self.current_theme

theme_manager = ThemeManager()
