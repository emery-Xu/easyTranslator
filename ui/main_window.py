from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class MainWindow(QWidget):
    """Main window providing access to wordbook, flashcard, and settings."""

    def __init__(self, tray, parent=None):
        super().__init__(parent)
        self._tray = tray
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("EasyTranslator")
        self.setFixedSize(320, 220)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("EasyTranslator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        btn_style = (
            "QPushButton { padding: 8px; font-size: 14px; }"
        )

        wordbook_btn = QPushButton("查看词库")
        wordbook_btn.setStyleSheet(btn_style)
        wordbook_btn.clicked.connect(self._tray.show_wordbook)
        layout.addWidget(wordbook_btn)

        flashcard_btn = QPushButton("开始闪卡")
        flashcard_btn.setStyleSheet(btn_style)
        flashcard_btn.clicked.connect(self._tray.show_flashcard)
        layout.addWidget(flashcard_btn)

        settings_btn = QPushButton("设置")
        settings_btn.setStyleSheet(btn_style)
        settings_btn.clicked.connect(self._tray.show_settings)
        layout.addWidget(settings_btn)

        hint = QLabel("选中文字后点击 Translate 按钮即可翻译")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
