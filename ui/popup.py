from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QCursor

from database import Database


class PopupWindow(QWidget):
    # Emitted from background thread when translation is ready
    result_ready = pyqtSignal(str)

    def __init__(self, source: str, db: Database):
        super().__init__()
        self.source = source
        self.db = db
        self._setup_ui()
        self._position_near_cursor()
        self.result_ready.connect(self._apply_result)

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet("""
            QWidget#popup_container {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 10px;
            }
            QLabel#source_label {
                color: #aaaaaa;
                font-size: 12px;
            }
            QLabel#target_label {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#save_btn {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 12px;
            }
            QPushButton#save_btn:hover {
                background-color: #357abd;
            }
            QPushButton#save_btn:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("popup_container")
        outer.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        source_label = QLabel(self.source)
        source_label.setObjectName("source_label")
        source_label.setWordWrap(True)
        layout.addWidget(source_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #555555;")
        layout.addWidget(line)

        self._target_label = QLabel("翻译中…")
        self._target_label.setObjectName("target_label")
        self._target_label.setWordWrap(True)
        layout.addWidget(self._target_label)

        self.save_btn = QPushButton("保存到词库")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_word)
        layout.addWidget(self.save_btn)

        self.setFixedWidth(280)

    def _position_near_cursor(self):
        pos = QCursor.pos()
        screen = self.screen()
        if screen:
            geo = screen.availableGeometry()
            x = min(pos.x() + 10, geo.right() - self.sizeHint().width() - 10)
            y = min(pos.y() + 10, geo.bottom() - self.sizeHint().height() - 10)
            self.move(QPoint(x, y))
        else:
            self.move(pos.x() + 10, pos.y() + 10)

    def _apply_result(self, text: str):
        self._target_label.setText(text)
        self._result = text
        self.save_btn.setEnabled(True)
        self.adjustSize()

    def _save_word(self):
        self.db.add_word(self.source, getattr(self, "_result", self._target_label.text()))
        self.save_btn.setText("已保存")
        self.save_btn.setEnabled(False)
        self.close()

    def show(self):
        super().show()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Don't close if focus moved to a child widget (e.g. the save button)
        from PyQt6.QtWidgets import QApplication
        focused = QApplication.focusWidget()
        if focused and self.isAncestorOf(focused):
            return
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
