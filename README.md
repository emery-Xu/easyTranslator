# EasyTranslator

> 鼠标划词即翻译，一键存词，内置闪卡复习 | Select text, instant translation, save words, flashcard review

---

## 简介 / Overview

**EasyTranslator** 是一款运行在系统托盘的轻量桌面翻译工具。

- 鼠标选中文字后按下全局热键，自动弹出翻译浮窗
- 翻译结果可一键保存到本地词库（SQLite）
- 内置词库管理界面与闪卡复习功能，帮助记忆词汇
- 支持两种翻译后端：**DeepL API**（云端，高质量）和 **Ollama**（本地大模型，离线可用）

**EasyTranslator** is a lightweight desktop translation tool that runs in the system tray.

- Select any text and press a global hotkey → a translation popup appears near your cursor
- Save translations to a local word book (SQLite) with one click
- Built-in word book manager and flashcard review to help you memorize vocabulary
- Supports two translation backends: **DeepL API** (cloud, high quality) and **Ollama** (local LLM, offline)

---

## 功能特性 / Features

| 功能 | 说明 |
|------|------|
| 划词翻译 | 选中文字 → 按 `Ctrl+T` → 浮窗显示译文 |
| 保存词条 | 浮窗内一键保存到本地词库 |
| 词库管理 | 搜索、浏览、删除词条 |
| 闪卡练习 | 按复习次数加权随机抽卡，认识 +1，不认识归零 |
| 系统托盘 | 后台常驻，右键菜单快速访问所有功能 |
| 双后端支持 | DeepL API 或本地 Ollama 模型，可在设置中切换 |

| Feature | Description |
|---------|-------------|
| Hotkey Translation | Select text → press `Ctrl+T` → popup with translation |
| Save to Word Book | One-click save from the popup window |
| Word Book Manager | Search, browse, and delete saved entries |
| Flashcard Review | Weighted random cards; correct → +1, incorrect → reset |
| System Tray | Runs in background; right-click for all features |
| Dual Backend | DeepL API or local Ollama model, switchable in settings |

---

## 截图 / Screenshots

```
翻译浮窗 / Translation Popup:
┌────────────────────────────────┐
│  ephemeral                     │
│  ──────────────────────────    │
│  短暂的；瞬息的                │
│                  [保存到词库]  │
└────────────────────────────────┘

词库管理 / Word Book:
┌─────────────────────────────────────────┐
│  我的词库   [搜索____________]           │
│─────────────────────────────────────────│
│  原文          译文         操作         │
│  ephemeral     短暂的       [删除]       │
│  serendipity   意外发现     [删除]       │
│─────────────────────────────────────────│
│  共 42 个词条          [开始闪卡练习]   │
└─────────────────────────────────────────┘
```

---

## 环境要求 / Requirements

- Python 3.11+
- Windows（全局热键依赖 `keyboard` 库，Linux/macOS 可能需要额外权限）

---

## 安装 / Installation

```bash
# 克隆仓库
git clone https://github.com/yourusername/easyTranslator.git
cd easyTranslator

# 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

---

## 配置 / Configuration

首次运行时程序会自动生成 `config.json`，也可以手动复制示例配置：

On first run, `config.json` is created automatically. You can also copy the example:

```bash
cp config.example.json config.json
```

### DeepL 后端（默认）/ DeepL Backend (default)

编辑 `config.json`：

```json
{
    "backend": "deepl",
    "deepl_api_key": "your-deepl-api-key-here",
    "hotkey": "ctrl+t",
    "target_lang": "ZH"
}
```

> DeepL 免费版每月提供 50 万字符额度，个人日常使用完全够用。
> 免费版 API Key 末尾带 `:fx` 后缀。
> Free tier provides 500,000 characters/month. Free tier keys end with `:fx`.

### Ollama 后端（本地离线）/ Ollama Backend (offline)

确保本地已安装并运行 [Ollama](https://ollama.com)，然后修改配置：

Make sure [Ollama](https://ollama.com) is installed and running locally, then update config:

```json
{
    "backend": "ollama",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "qwen2.5:7b",
    "hotkey": "ctrl+t",
    "target_lang": "ZH"
}
```

也可以在程序「设置」窗口中切换后端，无需手动编辑文件。

You can also switch backends through the app's Settings window without editing the file manually.

---

## 运行 / Run

```bash
python main.py
```

程序启动后会最小化到系统托盘，右键托盘图标访问所有功能。
若使用 DeepL 且未配置 API Key，启动时会自动弹出设置窗口。

The app starts minimized to the system tray. Right-click the tray icon to access all features.
If using DeepL without an API key, the Settings window opens automatically on launch.

---

## 项目结构 / Project Structure

```
easyTranslator/
├── main.py              # 入口 / Entry point
├── translator.py        # DeepL & Ollama 翻译封装 / Translation backends
├── database.py          # SQLite 词库 CRUD / Word book database
├── config.py            # 配置读写 / Config management
├── config.example.json  # 示例配置 / Example config
├── requirements.txt
├── ui/
│   ├── tray.py          # 系统托盘 / System tray
│   ├── popup.py         # 翻译浮窗 / Translation popup
│   ├── wordbook.py      # 词库管理窗口 / Word book window
│   └── flashcard.py     # 闪卡窗口 / Flashcard window
├── assets/
│   └── icon.png         # 托盘图标 / Tray icon
└── data/
    └── words.db         # SQLite 数据库（运行时自动创建）/ Auto-created on run
```

---

## 打包为可执行文件 / Package as Executable

使用 PyInstaller 打包为 Windows 单文件 `.exe`：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=assets/icon.png main.py
```

生成文件位于 `dist/main.exe`，可直接运行，无需 Python 环境。

The output `dist/main.exe` runs standalone without a Python installation.

---

## 注意事项 / Notes

- **Windows 权限**：`keyboard` 库在某些系统上可能需要以管理员权限运行才能监听全局热键。
  **Windows permissions**: The `keyboard` library may require administrator privileges to capture global hotkeys.

- **热键冲突**：如果 `Ctrl+T` 与其他软件冲突，可在设置中修改热键。
  **Hotkey conflict**: If `Ctrl+T` conflicts with other apps, change it in Settings.

- **Ollama 模型**：首次使用需先拉取模型，例如 `ollama pull qwen2.5:7b`。
  **Ollama model**: Pull the model first, e.g. `ollama pull qwen2.5:7b`.

---

## 依赖 / Dependencies

| 库 | 用途 |
|----|------|
| PyQt6 | GUI 框架 / GUI framework |
| deepl | DeepL 翻译 API / DeepL translation API |
| keyboard | 全局热键监听 / Global hotkey capture |
| pyperclip | 剪贴板操作 / Clipboard access |
| requests | Ollama HTTP 请求 / Ollama HTTP requests |

---

## License

MIT
