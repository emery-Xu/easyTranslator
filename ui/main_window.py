import threading

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from database import Database


class MainWindow(QWidget):
    """Main window providing access to wordbook, flashcard, and settings."""

    def __init__(self, tray, parent=None):
        super().__init__(parent)
        self._tray = tray
        self._popup_ref = []
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("EasyTranslator")
        self.setFixedSize(320, 270)

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

        test_btn = QPushButton("测试翻译弹窗")
        test_btn.setStyleSheet(btn_style)
        test_btn.clicked.connect(self._test_popup)
        layout.addWidget(test_btn)

        hint = QLabel("选中文字后点击 Translate 按钮即可翻译")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

    def _test_popup(self):
        """Open a PopupWindow with hardcoded text — bypasses mouse selection for testing."""
        from ui.popup import PopupWindow
        test_text = "hello world"
        print(f"[test] opening popup for: {test_text!r}")
        popup = PopupWindow(test_text, self._tray.db)
        self._popup_ref.clear()
        self._popup_ref.append(popup)
        popup.show()

        def _do_translate():
            try:
                result = self._tray.translator.translate(test_text)
            except Exception as e:
                result = f"翻译失败：{e}"
            print(f"[test] result: {result!r}")
            popup.result_ready.emit(result)

        threading.Thread(target=_do_translate, daemon=True).start()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
