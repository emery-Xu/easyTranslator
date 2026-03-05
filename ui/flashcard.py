from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from database import Database


class FlashcardWindow(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self._current_card = None
        self._setup_ui()
        self._load_next_card()

    def _setup_ui(self):
        self.setWindowTitle("闪卡练习")
        self.resize(420, 300)

        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(24, 24, 24, 24)
        self.layout_.setSpacing(12)

        # Empty state label
        self.empty_label = QLabel("词库为空，请先保存一些词条！")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("font-size: 16px; color: gray;")
        self.layout_.addWidget(self.empty_label)

        # Front side: source word large
        self.front_widget = QWidget()
        front_layout = QVBoxLayout(self.front_widget)
        front_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.front_source_label = QLabel()
        self.front_source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.front_source_label.setWordWrap(True)
        self.front_source_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        front_layout.addWidget(self.front_source_label)
        front_layout.addSpacing(20)
        self.flip_btn = QPushButton("点击翻转")
        self.flip_btn.clicked.connect(self._show_back)
        front_layout.addWidget(self.flip_btn)
        self.layout_.addWidget(self.front_widget)

        # Back side: source small + divider + target large + two buttons
        self.back_widget = QWidget()
        back_layout = QVBoxLayout(self.back_widget)
        back_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_source_label = QLabel()
        self.back_source_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_source_label.setStyleSheet("font-size: 13px; color: gray;")
        back_layout.addWidget(self.back_source_label)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        back_layout.addWidget(line)
        self.back_target_label = QLabel()
        self.back_target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.back_target_label.setWordWrap(True)
        self.back_target_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        back_layout.addWidget(self.back_target_label)
        back_layout.addSpacing(16)
        btn_row = QHBoxLayout()
        self.forget_btn = QPushButton("不认识，再来")
        self.forget_btn.clicked.connect(self._on_forget)
        self.know_btn = QPushButton("认识，下一个")
        self.know_btn.clicked.connect(self._on_know)
        btn_row.addWidget(self.forget_btn)
        btn_row.addWidget(self.know_btn)
        back_layout.addLayout(btn_row)
        self.layout_.addWidget(self.back_widget)

    def _load_next_card(self):
        self._current_card = self.db.get_next_flashcard()
        if self._current_card is None:
            self.empty_label.setVisible(True)
            self.front_widget.setVisible(False)
            self.back_widget.setVisible(False)
        else:
            self.empty_label.setVisible(False)
            _, source, target, review_count, _ = self._current_card
            self.front_source_label.setText(source)
            self.back_source_label.setText(source)
            self.back_target_label.setText(target)
            self._show_front()

    def _show_front(self):
        self.front_widget.setVisible(True)
        self.back_widget.setVisible(False)

    def _show_back(self):
        self.front_widget.setVisible(False)
        self.back_widget.setVisible(True)

    def _on_know(self):
        if self._current_card:
            word_id, _, _, review_count, _ = self._current_card
            self.db.update_review_count(word_id, review_count + 1)
        self._load_next_card()

    def _on_forget(self):
        if self._current_card:
            word_id = self._current_card[0]
            self.db.update_review_count(word_id, 0)
        self._load_next_card()
