# History_pasteboard

A lightweight clipboard history manager for Windows. Runs silently in the system tray and records every clipboard change — text, HTML, images, and file paths.

## Features

- **Auto-record** — polls the clipboard every 500ms, detects text / HTML / images / files
- **Glass UI** — frameless translucent window with rounded corners, minimal design
- **Image support** — saves clipboard images as PNG and restores them on click
- **One-click paste** — click any entry to copy it back to the clipboard
- **Smart dedup** — two-layer deduplication (MD5 polling + storage comparison), consecutive duplicates are skipped
- **Word-wrap** — long content wraps to multiple lines, no horizontal scrolling needed
- **Timestamps** — relative time display ("刚刚", "3 分钟前", "2 天前")
- **Auto-cleanup** — keeps the latest 500 items, prunes oldest automatically (images included)
- **System tray** — runs in background, double-click to show, right-click for menu
- **Delete & clear** — right-click to delete single items, button to clear all
- **Copy feedback** — green "✓ 已复制" confirmation on click
- **Installer** — Inno Setup script with desktop shortcut and auto-start option

## Requirements

- Windows 10 / 11
- Python 3.13+

## Quick Start

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Project Structure

```
History_pasteboard/
├── main.py                       # Entry point
├── main/                         # Core package
│   ├── clipboard_monitor.py      # Clipboard polling & change detection
│   ├── storage.py                # SQLite database (500-item cap, auto-prune)
│   ├── main_window.py            # Glass-morphism main window
│   ├── tray_manager.py           # System tray icon & context menu
│   ├── utils.py                  # Time formatting & preview helpers
│   └── models.py                 # ClipItem data model
├── requirements.txt              # PySide6
├── History_pasteboard.spec       # PyInstaller spec
├── installer.iss                 # Inno Setup installer script
└── data/                         # Runtime data (SQLite DB, cached images) — gitignored
```

## Build Installer

Requires Python 3.13+, PyInstaller, and [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bash
# Step 1: Build single exe
pyinstaller History_pasteboard.spec

# Step 2: Open installer.iss in Inno Setup Compiler → Build → Compile
```

The installer will be at `History_pasteboard_Setup_1.0.exe`.

## Deduplication Logic

Deduplication happens at **two layers** to prevent recording the same clipboard content consecutively:

| Layer | Location | Mechanism |
|---|---|---|
| **Monitor** | `clipboard_monitor.py` | MD5 hash of clipboard content, compared against `_last_hash` each poll cycle. If the hash hasn't changed, the change event is suppressed entirely. Hashes are type-specific: raw text for text/HTML, PNG bytes for images, concatenated file paths for files. |
| **Storage** | `storage.py` | Before inserting, `add_item()` fetches the most recent row and compares `content` + `content_type`. If both match, returns `None` — the item is discarded. This catches edge cases the hash layer might miss. |

If you copy the **same** content twice in a row, only the first copy is recorded. If you copy **different** content, both are saved.

## License

MIT
