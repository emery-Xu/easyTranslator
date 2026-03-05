import sys
import time
import threading
import pyperclip
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QPoint

from config import Config
from database import Database
from translator import create_translator


def _get_selected_text_via_clipboard() -> str:
    """Send Ctrl+C and read clipboard to obtain currently selected text."""
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""
    try:
        pyperclip.copy("")
    except Exception:
        pass

    # Simulate Ctrl+C using pynput (no admin rights needed on Windows)
    from pynput.keyboard import Controller as KbController, Key
    kb = KbController()
    kb.press(Key.ctrl)
    kb.press("c")
    kb.release("c")
    kb.release(Key.ctrl)

    time.sleep(0.08)  # Wait for clipboard to be populated

    try:
        selected = pyperclip.paste()
    except Exception:
        selected = ""

    try:
        pyperclip.copy(original)
    except Exception:
        pass

    return (selected or "").strip()


def main():
    # 1. Load config
    config = Config("config.json")
    cfg = config.load_config()

    # 2. Start PyQt6 application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 3. Initialize backend modules
    db = Database("data/words.db")
    translator = create_translator(cfg)

    # 4. Initialize tray
    from ui.tray import TrayIcon
    tray = TrayIcon(cfg, config, db, translator, app)
    tray.show()

    # 5. Show startup notification (delayed so tray is fully visible first)
    backend = cfg.get("backend", "deepl")
    backend_label = "DeepL" if backend == "deepl" else f"Ollama ({cfg.get('ollama_model', 'qwen2.5:7b')})"
    QTimer.singleShot(800, lambda: tray.notify("EasyTranslator 已启动", f"后端：{backend_label}"))

    # 6. Setup SelectionButton
    from ui.selection_button import SelectionButton

    _popup_ref = []  # Keep popup references alive (prevent GC)

    def show_popup(text: str, result: str):
        from ui.popup import PopupWindow
        popup = PopupWindow(text, result, db)
        _popup_ref.clear()
        _popup_ref.append(popup)
        popup.show()

    def on_translate_requested(text: str):
        if not text:
            return
        try:
            result = tray.translator.translate(text)
        except Exception as e:
            from PyQt6.QtWidgets import QSystemTrayIcon
            tray.notify("翻译失败", str(e), QSystemTrayIcon.MessageIcon.Warning)
            return
        show_popup(text, result)

    sel_btn = SelectionButton(on_translate=on_translate_requested)

    # 7. Setup pynput mouse listener in a background thread
    # Detect left-button release → grab selected text → show SelectionButton
    _mouse_btn_down = threading.Event()

    def _on_mouse_click(x, y, button, pressed):
        from pynput.mouse import Button
        if button != Button.left:
            return
        if pressed:
            _mouse_btn_down.set()
        else:
            # Left button released — attempt to grab selection
            _mouse_btn_down.clear()
            pos_x, pos_y = x, y

            def _worker():
                text = _get_selected_text_via_clipboard()
                if text:
                    QTimer.singleShot(0, lambda: sel_btn.show_near_cursor(text, QPoint(pos_x, pos_y)))

            threading.Thread(target=_worker, daemon=True).start()

    from pynput.mouse import Listener as MouseListener
    mouse_listener = MouseListener(on_click=_on_mouse_click)
    mouse_listener.daemon = True
    mouse_listener.start()

    # 8. If using DeepL with no API key, open settings immediately
    if cfg.get("backend", "deepl") == "deepl" and not cfg.get("deepl_api_key"):
        QTimer.singleShot(500, tray.show_settings)

    # 9. Enter event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
