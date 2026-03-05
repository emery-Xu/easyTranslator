import sqlite3

class Database:
    def __init__(self, db_path: str):
        """连接数据库，并确保 words 表存在"""
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                source     TEXT NOT NULL,           -- 原文
                target     TEXT NOT NULL,           -- 译文（中文）
                review_count INTEGER DEFAULT 0,    -- 闪卡复习次数（认识 +1，不认识归零）
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_word(self, source: str, target: str):
        """添加一个词条到词库"""
        self.conn.execute(
            "INSERT INTO words (source, target) VALUES (?, ?)",
            (source, target)
        )
        self.conn.commit()

    def delete_word(self, word_id: int):
        """根据 id 删除一个词条"""
        self.conn.execute("DELETE FROM words WHERE id = ?", (word_id,))
        self.conn.commit()

    def search_words(self, keyword: str) -> list:
        """按关键词模糊搜索词条，返回所有匹配的行"""
        cursor = self.conn.execute(
            "SELECT * FROM words WHERE source LIKE ?",
            (f"%{keyword}%",)
        )
        return cursor.fetchall()

    def get_next_flashcard(self) -> dict | None:
        """按权重随机取一张闪卡（review_count 低的优先），词库为空返回 None"""
        cursor = self.conn.execute(
            "SELECT * FROM words ORDER BY review_count ASC, RANDOM() LIMIT 1"
        )
        return cursor.fetchone()
        

    def update_review_count(self, word_id: int, count: int):
        """更新指定词条的 review_count"""
        self.conn.execute(
            "UPDATE words SET review_count = ? WHERE id = ?",
            (count, word_id)
        )
        self.conn.commit()
