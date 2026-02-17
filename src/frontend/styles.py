# Modern UI Stylesheet for TodoApp

# Color Palette
# Background: #FFFFFF (White) or #F5F7FA (Light Gray)
# Accent: #6C5CE7 (Soft Purple) or #0984E3 (Electron Blue)
# Text: #2D3436 (Dracula Orchid - Dark Gray)
# Secondary Text: #636E72 (American River - Gray)
# Card BG: #FFFFFF with Shadow
# Hover: #F1F2F6 (Anti-Flash White)

MAIN_STYLE = """
/* Global Reset */
QWidget {
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
    color: #2D3436;
}

/* Main Window Container */
#MainFrame {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #DFE6E9;
}

/* Title Bar */
#TitleBar {
    background-color: transparent;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

#TitleLabel {
    font-weight: bold;
    font-size: 16px;
    color: #6C5CE7;
    padding-left: 10px;
}

/* Input Field */
QLineEdit {
    border: 2px solid #DFE6E9;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #F8F9FA;
    selection-background-color: #6C5CE7;
    font-size: 14px;
}

QLineEdit:focus {
    border: 2px solid #6C5CE7;
    background-color: #FFFFFF;
}

/* Add Button */
QPushButton#AddButton {
    background-color: #6C5CE7;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    border: none;
}

QPushButton#AddButton:hover {
    background-color: #5849BE;
}

QPushButton#AddButton:pressed {
    background-color: #483D8B;
}

/* Section Headers */
QLabel#SectionHeader {
    font-weight: bold;
    color: #636E72;
    font-size: 13px;
    margin-top: 10px;
    margin-bottom: 5px;
    padding-left: 5px;
}

/* List Items */
QListWidget {
    background: transparent;
    border: none;
    outline: none;
}

QListWidget::item {
    background: #FFFFFF;
    border-radius: 8px;
    margin-bottom: 4px;
    padding: 0px;
    border: 1px solid transparent;
}

QListWidget::item:hover {
    background: #F1F2F6;
    border: 1px solid #DFE6E9;
}

QListWidget::item:selected {
    background: #F1F2F6;
    color: #2D3436; /* Keep text color same */
    border: 1px solid #6C5CE7;
}

/* Checkbox */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #B2BEC3;
    background: white;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #6C5CE7;
}

QCheckBox::indicator:checked {
    background-color: #6C5CE7;
    border-color: #6C5CE7;
    image: url(assets/check.png); /* Need to handle if image missing, maybe use pure CSS drawing or icon */
}

/* Delete Button */
QPushButton#DeleteButton {
    background-color: transparent;
    color: #FF7675;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    padding: 0px;
    min-width: 24px;
    min-height: 24px;
}

QPushButton#DeleteButton:hover {
    background-color: #FFEAA7;
}

/* Refresh Button */
QPushButton#RefreshButton {
    background-color: transparent;
    color: #636E72;
    border: 1px solid #DFE6E9;
    border-radius: 6px;
    padding: 5px;
    font-size: 12px;
}

QPushButton#RefreshButton:hover {
    background-color: #F1F2F6;
    color: #2D3436;
    border-color: #B2BEC3;
}

/* Scrollbar */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #DFE6E9;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #B2BEC3;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

