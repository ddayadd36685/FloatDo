from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QLineEdit, QPushButton, QListWidgetItem, QCheckBox, 
    QLabel, QMessageBox, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QScrollArea, QInputDialog, QDialog, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve, QTimer, QSize, QThread
from PyQt6.QtGui import QColor, QIcon, QFont, QPainter, QBrush, QPen, QAction
from src.frontend.api_client import ApiClient
from src.frontend.theme import theme_manager, Theme
import uuid

class ModernCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(24, 24)

class TaskCard(QFrame):
    status_changed = pyqtSignal(str, bool)
    delete_requested = pyqtSignal(str)

    def __init__(self, task_id, title, completed, theme: Theme):
        super().__init__()
        self.task_id = task_id
        self.theme = theme
        
        self.setObjectName("TaskCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Checkbox
        self.checkbox = ModernCheckBox()
        self.checkbox.setChecked(completed)
        self.checkbox.stateChanged.connect(self.on_check)
        
        # Label
        self.label = QLabel(title)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 11))
        
        # Right Arrow / Delete
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.clicked.connect(self.on_delete)
        self.delete_btn.setFlat(True)
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)
        self.update_style(theme, completed)

    def on_check(self, state):
        checked = self.checkbox.isChecked()
        self.update_style(self.theme, checked)
        self.status_changed.emit(self.task_id, checked)

    def on_delete(self):
        self.delete_requested.emit(self.task_id)

    def update_style(self, theme: Theme, completed: bool):
        self.theme = theme
        
        bg_color = theme.border if not completed else theme.hover
        text_color = theme.text if not completed else theme.secondary_text
        
        self.setStyleSheet(f"""
            QFrame#TaskCard {{
                background-color: {bg_color};
                border-radius: 16px;
            }}
            QLabel {{
                color: {text_color};
                font-weight: 500;
                border: none;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {theme.secondary_text};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme.accent};
                border-color: {theme.accent};
                image: none;
            }}
            QPushButton {{
                color: {theme.secondary_text};
                border: none;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }}
            QPushButton:hover {{
                color: #FF7675;
            }}
        """)
        
        f = self.label.font()
        f.setStrikeOut(completed)
        self.label.setFont(f)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.back_btn = QPushButton("←") 
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.setStyleSheet("border: none; font-size: 18px; font-weight: bold;")
        self.back_btn.clicked.connect(self.window().hide)
        
        self.title_label = QLabel("今日任务")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.menu_btn = QPushButton("···")
        self.menu_btn.setFixedSize(30, 30)
        self.menu_btn.setStyleSheet("border: none; font-size: 18px; font-weight: bold;")
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.show_menu)
        
        layout.addWidget(self.back_btn)
        layout.addWidget(self.title_label, 1)
        layout.addWidget(self.menu_btn)
        
        self.setLayout(layout)

    def show_menu(self):
        # Access TaskWindow instance
        task_window = self.window()
        if not task_window or not hasattr(task_window, 'api'):
            return

        menu = QMenu(self)
        menu.setCursor(Qt.CursorShape.PointingHandCursor)
        
        theme = theme_manager.get_theme()
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {theme.surface};
                border: 1px solid {theme.border};
                border-radius: 8px;
                padding: 6px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
                color: {theme.text};
            }}
            QMenu::item {{
                padding: 6px 24px;
                border-radius: 6px;
                background-color: transparent;
                color: {theme.text};
            }}
            QMenu::item:selected {{
                background-color: {theme.accent};
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background: {theme.border};
                margin: 4px 0px;
            }}
        """)
        
        # --- Lists Section ---
        lists = task_window.api.get_lists()
        
        # Header for lists (Disabled action as label)
        list_header = QAction("我的清单", self)
        list_header.setEnabled(False)
        menu.addAction(list_header)
        
        for lst in lists:
            action = QAction(lst['name'], self)
            # Mark current list
            if lst['id'] == task_window.current_list_id:
                action.setText(f"✓ {lst['name']}")
            
            # Use closure to capture list_id
            action.triggered.connect(lambda checked, l=lst: task_window.switch_list(l['id'], l['name']))
            menu.addAction(action)
            
        new_list_action = QAction("+ 新建清单", self)
        new_list_action.triggered.connect(task_window.create_new_list)
        menu.addAction(new_list_action)
        
        menu.addSeparator()
        
        # --- Settings & Exit ---
        settings_action = QAction("设置 (Settings)", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        pos = self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height()))
        menu.exec(pos)

    def open_settings(self):
        if not hasattr(self, 'settings_window') or self.settings_window is None:
            from src.frontend.settings_window import SettingsWindow
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.activateWindow()

    def update_style(self, theme: Theme):
        style = f"color: {theme.text}; background: transparent;"
        self.back_btn.setStyleSheet(style + "font-size: 20px;")
        self.title_label.setStyleSheet(style + "font-size: 16px; font-weight: 600;")
        self.menu_btn.setStyleSheet(style + "font-size: 20px; padding-bottom: 5px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window() 
            if hasattr(window, 'start_drag'):
                window.start_drag(event.globalPosition().toPoint())

class AddTaskThread(QThread):
    finished = pyqtSignal(bool, str)

    def __init__(self, api_client, task_id, title, list_id):
        super().__init__()
        self.api = api_client
        self.task_id = task_id
        self.title = title
        self.list_id = list_id

    def run(self):
        try:
            success = self.api.add_task(self.task_id, self.title, self.list_id)
            self.finished.emit(success, self.task_id if success else "Failed")
        except Exception as e:
            self.finished.emit(False, str(e))

class TaskWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(360, 600)
        
        self.api = ApiClient()
        self.drag_pos = QPoint()
        self.current_list_id = "default"
        self.current_list_name = "今日任务"
        
        self.setup_ui()
        
        self.apply_theme(theme_manager.get_theme())
        theme_manager.theme_changed.connect(self.apply_theme)
        
        self.refresh_tasks()
        
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tasks_silent)
        self.refresh_timer.start(2000)

    def setup_ui(self):
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.container = QFrame()
        self.container.setObjectName("Container")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        self.header_label = QLabel("今日任务")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(40, 40)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.clicked.connect(self.toggle_input)
        
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        
        layout.addWidget(header_widget)
        
        self.input_container = QWidget()
        self.input_container.setVisible(False)
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(20, 0, 20, 10)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("添加新任务...")
        self.task_input.setFixedHeight(40)
        self.task_input.returnPressed.connect(self.add_task)
        
        input_layout.addWidget(self.task_input)
        layout.addWidget(self.input_container)
        
        self.task_list = QListWidget()
        self.task_list.setFrameShape(QFrame.Shape.NoFrame)
        self.task_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.task_list.setStyleSheet("background: transparent; outline: none;")
        self.task_list.setSpacing(8)
        
        list_wrapper = QWidget()
        list_layout = QVBoxLayout(list_wrapper)
        list_layout.setContentsMargins(15, 0, 15, 15)
        list_layout.addWidget(self.task_list)
        
        layout.addWidget(list_wrapper, 1)
        
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)

    def apply_theme(self, theme: Theme):
        self.current_theme = theme
        
        self.container.setStyleSheet(f"""
            QFrame#Container {{
                background-color: {theme.bg};
                border-radius: 20px;
                border: 1px solid {theme.border};
            }}
        """)
        
        self.title_bar.update_style(theme)
        
        self.header_label.setStyleSheet(f"color: {theme.text}; font-size: 24px; font-weight: bold; border: none; background: transparent;")
        
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.border};
                color: {theme.text};
                border-radius: 20px;
                font-size: 24px;
                font-weight: 300;
            }}
            QPushButton:hover {{
                background-color: {theme.accent};
                color: white;
            }}
        """)
        
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.surface};
                color: {theme.text};
                border: 1px solid {theme.border};
                border-radius: 12px;
                padding: 0 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {theme.accent};
            }}
        """)
        
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget:
                widget.update_style(theme, widget.checkbox.isChecked())

    def toggle_input(self):
        self.input_container.setVisible(not self.input_container.isVisible())
        if self.input_container.isVisible():
            self.task_input.setFocus()

    def start_drag(self, global_pos):
        self.drag_pos = global_pos - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = QPoint()

    def add_item_to_list(self, task):
        item = QListWidgetItem(self.task_list)
        widget = TaskCard(task['id'], task['title'], task['completed'], self.current_theme)
        widget.status_changed.connect(self.on_task_status_change)
        widget.delete_requested.connect(self.on_task_delete)
        
        item.setSizeHint(QSize(0, 70))
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, widget)

    def refresh_tasks(self):
        self.task_list.clear()
        tasks = self.api.get_tasks(self.current_list_id)
        tasks.sort(key=lambda x: x['completed'])
        
        for t in tasks:
            self.add_item_to_list(t)

    def refresh_tasks_silent(self):
        try:
            current_tasks = self.api.get_tasks(self.current_list_id)
            current_tasks.sort(key=lambda x: x['completed'])
            
            if len(current_tasks) != self.task_list.count():
                self.refresh_tasks()
                return
                
            for i, t in enumerate(current_tasks):
                item = self.task_list.item(i)
                widget = self.task_list.itemWidget(item)
                if widget.task_id != t['id'] or widget.checkbox.isChecked() != t['completed']:
                    self.refresh_tasks()
                    return
        except:
            pass

    def add_task(self):
        title = self.task_input.text().strip()
        if not title: return
        
        self.task_input.setEnabled(False)
        self.add_btn.setEnabled(False)
        
        task_id = str(uuid.uuid4())
        
        self.add_thread = AddTaskThread(self.api, task_id, title, self.current_list_id)
        self.add_thread.finished.connect(self.on_add_finished)
        self.add_thread.start()

    def on_add_finished(self, success, message):
        self.task_input.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.task_input.setFocus()
        
        if success:
            self.task_input.clear()
            self.input_container.hide()
            self.refresh_tasks()
        else:
            QMessageBox.warning(self, "Error", f"Failed to add task: {message}")

    def on_task_status_change(self, task_id, completed):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            widget = self.task_list.itemWidget(item)
            if widget.task_id == task_id:
                if self.api.update_task(task_id, widget.label.text(), completed, self.current_list_id):
                    pass
                break

    def on_task_delete(self, task_id):
        if self.api.delete_task(task_id):
            self.refresh_tasks()

    def switch_list(self, list_id, list_name):
        self.current_list_id = list_id
        self.current_list_name = list_name
        
        # Update Titles
        self.title_bar.title_label.setText(list_name)
        self.header_label.setText(list_name)
        
        self.refresh_tasks()

    def create_new_list(self):
        from src.frontend.custom_dialog import CustomInputDialog
        # Manually create dialog to access lost_focus property
        dialog = CustomInputDialog(self, "新建清单", "请输入清单名称:")
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = dialog.text_value
            if text and text.strip():
                list_id = str(uuid.uuid4())
                if self.api.create_list(list_id, text.strip()):
                    self.switch_list(list_id, text.strip())
                else:
                    QMessageBox.warning(self, "错误", "创建清单失败")
        else:
            # If rejected (cancelled) AND lost focus (clicked outside), hide the panel
            # This implements the user request: "clean up (reject) then hide panel"
            if getattr(dialog, 'lost_focus', False):
                self.hide()
