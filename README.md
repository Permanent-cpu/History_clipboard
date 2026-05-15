# History_pasteboard

A lightweight clipboard history manager for Windows. Runs in the system tray and automatically records every clipboard change.

## Features

- **Auto-record** — monitors clipboard and saves text, HTML, images, and file paths
- **Image support** — saves clipboard images as PNG and restores them on click
- **Instant paste** — click any entry to copy it back to the clipboard
- **Timestamps** — shows relative time (e.g. "2 min ago", "3 hours ago")
- **Delete & clear** — right-click to delete single items, button to clear all
- **System tray** — runs in the background, double-click to show window
- **Deduplication** — skips duplicate consecutive entries
- **Auto-cleanup** — keeps the latest 500 items, removes oldest automatically

## Requirements

- Windows 10/11
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
│   ├── storage.py                # SQLite database operations
│   ├── main_window.py            # Main window UI (list, delete, copy)
│   ├── tray_manager.py           # System tray icon & menu
│   ├── utils.py                  # Time formatting & preview helpers
│   └── models.py                 # ClipItem data model
├── requirements.txt              # PySide6 dependency
├── installer.iss                 # Inno Setup installer script
└── data/                         # Runtime data (SQLite DB, cached images)
```

## Build Installer

```bash
# Step 1: Build single exe with PyInstaller
pyinstaller --onefile --windowed --name History_pasteboard main.py

# Step 2: Compile installer with Inno Setup
# Open installer.iss in Inno Setup Compiler -> Build -> Compile
```

## License

MIT
