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

    time.sleep(0.15)  # Wait for clipboard to be populated

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

    # 5. Create and show main window
    from ui.main_window import MainWindow
    main_window = MainWindow(tray)
    tray.set_main_window(main_window)
    main_window.show()

    # 6. Show startup notification (delayed so tray is fully visible first)
    backend = cfg.get("backend", "deepl")
    backend_label = "DeepL" if backend == "deepl" else f"Ollama ({cfg.get('ollama_model', 'qwen2.5:7b')})"
    QTimer.singleShot(800, lambda: tray.notify("EasyTranslator 已启动", f"后端：{backend_label}"))

    # 7. Setup SelectionButton
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

    # 8. Setup pynput mouse listener in a background thread
    # Only trigger clipboard grab when mouse is dragged (not plain click)
    _MIN_DRAG_DISTANCE = 5  # pixels
    _press_pos = {}  # store press position: {thread_id: (x, y)}
    _ignore_next_release = False  # flag to skip release after clicking SelectionButton

    def _on_mouse_click(x, y, button, pressed):
        nonlocal _ignore_next_release
        from pynput.mouse import Button as MButton
        if button != MButton.left:
            return
        if pressed:
            _press_pos["pos"] = (x, y)
        else:
            press = _press_pos.pop("pos", None)
            if press is None:
                return

            # If we should ignore this release (e.g. after clicking SelectionButton)
            if _ignore_next_release:
                _ignore_next_release = False
                return

            # Check if the SelectionButton is visible and the click landed on it
            if sel_btn.isVisible():
                btn_geo = sel_btn.geometry()
                if btn_geo.contains(x, y):
                    _ignore_next_release = True
                    return

            # Only treat as drag-select if moved more than threshold
            dx = x - press[0]
            dy = y - press[1]
            if (dx * dx + dy * dy) < _MIN_DRAG_DISTANCE * _MIN_DRAG_DISTANCE:
                return

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

    # 9. If using DeepL with no API key, open settings immediately
    if cfg.get("backend", "deepl") == "deepl" and not cfg.get("deepl_api_key"):
        QTimer.singleShot(500, tray.show_settings)

    # 10. Enter event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
