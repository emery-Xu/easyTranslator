import os

from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QApplication,
    QComboBox, QGroupBox, QVBoxLayout, QWidget,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from config import Config
from database import Database
from translator import create_translator


class SettingsDialog(QDialog):
    def __init__(self, cfg: dict, config: Config, tray_icon, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.config = config
        self.tray_icon = tray_icon
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # Backend selector
        self.backend_combo = QComboBox()
        self.backend_combo.addItem("DeepL", "deepl")
        self.backend_combo.addItem("Ollama（本地）", "ollama")
        current_backend = self.cfg.get("backend", "deepl")
        idx = self.backend_combo.findData(current_backend)
        if idx >= 0:
            self.backend_combo.setCurrentIndex(idx)
        self.backend_combo.currentIndexChanged.connect(self._on_backend_changed)
        form.addRow("翻译后端：", self.backend_combo)

        # DeepL group
        self.deepl_group = QGroupBox("DeepL 设置")
        deepl_form = QFormLayout(self.deepl_group)
        self.api_key_edit = QLineEdit(self.cfg.get("deepl_api_key", ""))
        self.api_key_edit.setPlaceholderText("请输入 DeepL API Key")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        deepl_form.addRow("API Key：", self.api_key_edit)
        layout.addWidget(self.deepl_group)

        # Ollama group
        self.ollama_group = QGroupBox("Ollama 设置")
        ollama_form = QFormLayout(self.ollama_group)
        self.ollama_host_edit = QLineEdit(self.cfg.get("ollama_host", "http://localhost:11434"))
        self.ollama_model_edit = QLineEdit(self.cfg.get("ollama_model", "qwen2.5:7b"))
        ollama_form.addRow("Host：", self.ollama_host_edit)
        ollama_form.addRow("Model：", self.ollama_model_edit)
        layout.addWidget(self.ollama_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._update_group_visibility()

    def _on_backend_changed(self):
        self._update_group_visibility()

    def _update_group_visibility(self):
        is_ollama = self.backend_combo.currentData() == "ollama"
        self.deepl_group.setVisible(not is_ollama)
        self.ollama_group.setVisible(is_ollama)
        self.adjustSize()

    def _save(self):
        self.cfg["backend"] = self.backend_combo.currentData()
        self.cfg["deepl_api_key"] = self.api_key_edit.text().strip()
        self.cfg["ollama_host"] = self.ollama_host_edit.text().strip()
        self.cfg["ollama_model"] = self.ollama_model_edit.text().strip()
        self.config.save_config(self.cfg)
        # Re-initialize translator
        self.tray_icon.translator = create_translator(self.cfg)
        self.accept()


class TrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        cfg: dict,
        config: Config,
        db: Database,
        translator,
        app: QApplication,
    ):
        super().__init__()
        self.cfg = cfg
        self.config = config
        self.db = db
        self.translator = translator
        self.app = app

        self._wordbook_window = None
        self._flashcard_window = None
        self._settings_dialog = None

        self.setIcon(self._load_icon())
        self.setToolTip("EasyTranslator")

        self._build_menu()

    def _load_icon(self) -> QIcon:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        if os.path.isfile(icon_path):
            return QIcon(icon_path)
        style = self.app.style()
        pixmap = style.standardPixmap(style.StandardPixmap.SP_ComputerIcon)
        return QIcon(pixmap)

    def _build_menu(self):
        menu = QMenu()

        wordbook_action = menu.addAction("查看词库")
        wordbook_action.triggered.connect(self.show_wordbook)

        flashcard_action = menu.addAction("开始闪卡")
        flashcard_action.triggered.connect(self.show_flashcard)

        menu.addSeparator()

        settings_action = menu.addAction("设置")
        settings_action.triggered.connect(self.show_settings)

        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)

        self.setContextMenu(menu)

    def show_wordbook(self):
        from ui.wordbook import WordbookWindow
        if self._wordbook_window is None or not self._wordbook_window.isVisible():
            self._wordbook_window = WordbookWindow(self.db)
        self._wordbook_window.show()
        self._wordbook_window.raise_()
        self._wordbook_window.activateWindow()

    def show_flashcard(self):
        from ui.flashcard import FlashcardWindow
        if self._flashcard_window is None or not self._flashcard_window.isVisible():
            self._flashcard_window = FlashcardWindow(self.db)
        self._flashcard_window.show()
        self._flashcard_window.raise_()
        self._flashcard_window.activateWindow()

    def show_settings(self):
        dialog = SettingsDialog(self.cfg, self.config, self)
        dialog.exec()
