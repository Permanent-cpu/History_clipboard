# History_pasteboard

运行于 Windows 系统的轻量级剪贴板历史管理工具。

## 技术栈
- Python 3.13 + PySide6
- SQLite 存储剪贴板历史
- 定时轮询检测剪贴板变化（500ms）

## 运行方式
```
python main.py
```

## 项目结构
```
main.py              # 程序入口
clipboard_monitor.py # 剪贴板监听
storage.py           # SQLite 数据库操作
main_window.py       # 主窗口 UI
tray_manager.py      # 系统托盘
utils.py             # 工具函数
models.py            # ClipItem 数据模型
data/                # 数据库和图片缓存
```

## 功能
- 自动记录文本/HTML/图片/文件路径到历史
- 主窗口显示历史列表（预览 + 时间）
- 点击条目复制到剪贴板
- 右键删除单条 / 清空全部
- 系统托盘常驻后台
- 历史上限 500 条自动清理
