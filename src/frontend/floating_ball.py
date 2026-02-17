from PyQt6.QtWidgets import QWidget, QApplication, QGraphicsDropShadowEffect, QMenu
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush, QCursor, QRadialGradient, QFont, QAction, QPen
from src.frontend.settings_window import SettingsWindow

class Ripple:
    def __init__(self, center, max_radius=60):
        self.center = center
        self.radius = 0
        self.max_radius = max_radius
        self.opacity = 1.0
        self.active = True

    def update(self):
        self.radius += 2
        self.opacity -= 0.04
        if self.opacity <= 0:
            self.active = False

class FloatingBall(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(100, 100) # Larger size for glow/ripple
        self.setStyleSheet("background: transparent;")
        
        self.dragging = False
        self.offset = QPoint()
        self.start_pos = QPoint()
        
        # Connect click signal to parent or handler
        self.clicked_callback = None
        
        # Animation for snapping
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
        # Breathing Animation
        self._breath_factor = 0.0
        self.breath_timer = QTimer(self)
        self.breath_timer.timeout.connect(self.update_breath)
        self.breath_timer.start(50) # ~20fps
        self.breath_direction = 1
        
        # Ripples
        self.ripples = []
        self.ripple_timer = QTimer(self)
        self.ripple_timer.timeout.connect(self.update_ripples)
        
        # Scale
        self._scale = 1.0
        self.scale_animation = QPropertyAnimation(self, b"scale")
        self.scale_animation.setDuration(200)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.settings_window = None

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, scale):
        self._scale = scale
        self.update()

    def update_breath(self):
        # Sine wave breathing 0.0 to 1.0
        step = 0.05
        self._breath_factor += step * self.breath_direction
        if self._breath_factor >= 1.0:
            self._breath_factor = 1.0
            self.breath_direction = -1
        elif self._breath_factor <= 0.0:
            self._breath_factor = 0.0
            self.breath_direction = 1
        self.update()

    def update_ripples(self):
        active_ripples = []
        for r in self.ripples:
            r.update()
            if r.active:
                active_ripples.append(r)
        self.ripples = active_ripples
        if not self.ripples:
            self.ripple_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPointF(self.width() / 2, self.height() / 2)
        base_radius = 28 * self._scale
        
        # 1. Draw Halo/Glow (Behind)
        # Breathing effect affects opacity/size of glow
        glow_radius = base_radius + 5 + (4 * self._breath_factor)
        glow = QRadialGradient(center, glow_radius)
        glow.setColorAt(0.0, QColor(108, 92, 231, 150)) # Purple Core
        glow.setColorAt(0.6, QColor(0, 168, 255, 100))  # Blue Mid
        glow.setColorAt(1.0, QColor(0, 168, 255, 0))    # Fade out
        
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, glow_radius, glow_radius)
        
        # 2. Draw Ripples
        for r in self.ripples:
            ripple_color = QColor(255, 255, 255, int(100 * r.opacity))
            painter.setPen(QPen(ripple_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, base_radius + r.radius, base_radius + r.radius)

        # 3. Draw Glass Sphere
        sphere_rect = QRectF(center.x() - base_radius, center.y() - base_radius, 
                             base_radius * 2, base_radius * 2)
        
        # Main Gradient (Deep semi-transparent body)
        sphere_grad = QRadialGradient(sphere_rect.topLeft(), base_radius * 2)
        sphere_grad.setColorAt(0.0, QColor(255, 255, 255, 180)) # Top-Left Highlight
        sphere_grad.setColorAt(0.3, QColor(100, 100, 255, 40))  # Tinted transparency
        sphere_grad.setColorAt(1.0, QColor(20, 20, 50, 200))    # Darker rim
        
        painter.setBrush(QBrush(sphere_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, base_radius, base_radius)
        
        # 4. Rim Light (Fresnel) - simulated with thin stroke or inner gradient
        # Let's use a subtle stroke
        rim_pen = QPen(QColor(255, 255, 255, 150), 1.5)
        painter.setPen(rim_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, base_radius - 1, base_radius - 1)
        
        # 5. Shine/Reflection
        highlight_rect = QRectF(center.x() - base_radius * 0.5, center.y() - base_radius * 0.6,
                                base_radius * 0.6, base_radius * 0.4)
        highlight_grad = QRadialGradient(highlight_rect.center(), highlight_rect.width())
        highlight_grad.setColorAt(0.0, QColor(255, 255, 255, 220))
        highlight_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(highlight_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            self.start_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
            self.scale_animation.setStartValue(self._scale)
            self.scale_animation.setEndValue(0.9)
            self.scale_animation.start()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.mapToGlobal(event.pos()) - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
            self.scale_animation.setStartValue(self._scale)
            self.scale_animation.setEndValue(1.0)
            if self.rect().contains(event.pos()):
                self.scale_animation.setEndValue(1.1)
            else:
                self.scale_animation.setEndValue(1.0)
            self.scale_animation.start()
            
            end_pos = event.globalPosition().toPoint()
            distance = (end_pos - self.start_pos).manhattanLength()
            
            if distance < 5:
                # Trigger Ripple
                self.ripples.append(Ripple(QPoint(self.width()//2, self.height()//2)))
                if not self.ripple_timer.isActive():
                    self.ripple_timer.start(16)
                
                if self.clicked_callback:
                    self.clicked_callback()
            else:
                self.snap_to_edge()

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setCursor(Qt.CursorShape.PointingHandCursor)
        # Use simple style, ThemeManager could be used here too
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #DFE6E9;
                border-radius: 8px;
                padding: 6px;
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                font-size: 13px;
                color: #2D3436;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 6px;
                background-color: transparent;
                color: #2D3436;
            }
            QMenu::item:selected {
                background-color: #6C5CE7;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background: #DFE6E9;
                margin: 4px 0px;
            }
        """)
        
        settings_action = QAction("设置 (Settings)", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)
        
        shadow = QGraphicsDropShadowEffect(menu)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        menu.setGraphicsEffect(shadow)
        
        menu.exec(pos)

    def open_settings(self):
        if not self.settings_window:
            self.settings_window = SettingsWindow()
        self.settings_window.show()
        self.settings_window.activateWindow()

    def snap_to_edge(self):
        screen = QApplication.primaryScreen().availableGeometry()
        pos = self.pos()
        x = pos.x()
        y = pos.y()
        w = self.width()
        h = self.height()
        
        dist_left = x - screen.left()
        dist_right = screen.right() - (x + w)
        
        target_x = x
        if dist_left < dist_right:
            target_x = screen.left()
        else:
            target_x = screen.right() - w
            
        target_y = max(screen.top(), min(y, screen.bottom() - h))
        
        self.animation.setStartValue(QRectF(x, y, w, h))
        self.animation.setEndValue(QRectF(target_x, target_y, w, h))
        self.animation.start()

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.1)
        self.scale_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.scale_animation.setStartValue(self._scale)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()
        super().leaveEvent(event)
