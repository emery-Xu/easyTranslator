from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal


class SelectionButton(QWidget):
    """Small floating 'Translate' button that appears near the cursor after text selection."""

    # Signal for cross-thread communication: (text, position)
    # Emitted from background threads; connected to show_near_cursor on the main thread.
    request_show = pyqtSignal(str, QPoint)

    def __init__(self, on_translate, parent=None):
        super().__init__(parent)
        self._on_translate = on_translate
        self._text = ""
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self.request_show.connect(self.show_near_cursor)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(90, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QWidget#sel_btn_container {
                background-color: rgba(40, 40, 40, 210);
                border-radius: 14px;
            }
            QLabel#sel_btn_label {
                color: #ffffff;
                font-size: 12px;
            }
        """)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("sel_btn_container")
        outer.addWidget(container)

        inner = QHBoxLayout(container)
        inner.setContentsMargins(8, 0, 8, 0)

        label = QLabel("Translate")
        label.setObjectName("sel_btn_label")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(label)

    def show_near_cursor(self, text: str, pos: QPoint):
        """Position near pos (below-right), store text, start 2.5s auto-dismiss timer."""
        self._text = text
        self._timer.stop()

        # Offset below the release point so it doesn't cover selected text
        x = pos.x() + 4
        y = pos.y() + 16

        # Keep within screen bounds
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = min(x, geo.right() - self.width() - 4)
            y = min(y, geo.bottom() - self.height() - 4)

        self.move(QPoint(x, y))
        self.show()
        self.raise_()
        self._timer.start(2500)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._timer.stop()
            text = self._text
            self.hide()
            self._on_translate(text)
        else:
            super().mousePressEvent(event)
