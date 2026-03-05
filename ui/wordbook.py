from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtCore import Qt

from database import Database


class WordbookWindow(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._flashcard_window = None
        self._setup_ui()
        self._load_words()

    def _setup_ui(self):
        self.setWindowTitle("我的词库")
        self.resize(600, 450)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Top bar: title + search
        top = QHBoxLayout()
        title = QLabel("我的词库")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top.addWidget(title)
        top.addStretch()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索原文…")
        self.search_box.setFixedWidth(180)
        self.search_box.textChanged.connect(self._load_words)
        top.addWidget(self.search_box)
        layout.addLayout(top)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["原文", "译文", "添加时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        # Bottom bar: count + flashcard button
        bottom = QHBoxLayout()
        self.count_label = QLabel("共 0 条")
        bottom.addWidget(self.count_label)
        bottom.addStretch()
        flashcard_btn = QPushButton("开始闪卡练习")
        flashcard_btn.clicked.connect(self._open_flashcard)
        bottom.addWidget(flashcard_btn)
        layout.addLayout(bottom)

    def _load_words(self):
        keyword = self.search_box.text() if hasattr(self, "search_box") else ""
        rows = self.db.search_words(keyword)

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            word_id, source, target, review_count, created_at = row
            self.table.setItem(i, 0, QTableWidgetItem(source))
            self.table.setItem(i, 1, QTableWidgetItem(target))
            self.table.setItem(i, 2, QTableWidgetItem(str(created_at)))

            del_btn = QPushButton("删除")
            del_btn.clicked.connect(lambda _, wid=word_id: self._delete_word(wid))
            self.table.setCellWidget(i, 3, del_btn)

        self.count_label.setText(f"共 {len(rows)} 条")

    def _delete_word(self, word_id: int):
        self.db.delete_word(word_id)
        self._load_words()

    def _open_flashcard(self):
        from ui.flashcard import FlashcardWindow
        if self._flashcard_window is None or not self._flashcard_window.isVisible():
            self._flashcard_window = FlashcardWindow(self.db)
        self._flashcard_window.show()
        self._flashcard_window.raise_()
        self._flashcard_window.activateWindow()
