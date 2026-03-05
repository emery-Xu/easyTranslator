import sys
import time
import keyboard
import pyperclip
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from config import Config
from database import Database
from translator import create_translator


def get_selected_text() -> str:
    """模拟 Ctrl+C 获取当前选中的文字"""
    original = pyperclip.paste()
    pyperclip.copy("")
    keyboard.send("ctrl+c")
    time.sleep(0.05)
    selected = pyperclip.paste()
    pyperclip.copy(original)
    return selected.strip()


def main():
    # 1. 加载配置
    config = Config("config.json")
    cfg = config.load_config()

    # 2. 启动 PyQt6 应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，保持托盘运行

    # 3. 初始化后端模块
    db = Database("data/words.db")
    translator = create_translator(cfg)

    # 4. 初始化托盘
    from ui.tray import TrayIcon
    tray = TrayIcon(cfg, config, db, translator, app)
    tray.show()

    # 5. 注册全局热键
    _popup_ref = []  # 保持弹窗引用，防止被 GC 回收

    def show_popup(text: str, result: str):
        from ui.popup import PopupWindow
        popup = PopupWindow(text, result, db)
        _popup_ref.clear()
        _popup_ref.append(popup)
        popup.show()

    def on_hotkey():
        text = get_selected_text()
        if not text:
            return
        try:
            result = tray.translator.translate(text)
        except Exception:
            return
        # keyboard 回调在子线程，切回主线程再操作 Qt 控件
        QTimer.singleShot(0, lambda: show_popup(text, result))

    keyboard.add_hotkey(cfg["hotkey"], on_hotkey)

    # 6. 若使用 DeepL 且 API Key 为空，弹出设置窗口
    if cfg.get("backend", "deepl") == "deepl" and not cfg.get("deepl_api_key"):
        QTimer.singleShot(500, tray.show_settings)

    # 7. 进入事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
