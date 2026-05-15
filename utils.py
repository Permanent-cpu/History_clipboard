from datetime import datetime, timedelta


def format_time(timestamp: str) -> str:
    dt = datetime.fromisoformat(timestamp)
    now = datetime.now()
    delta = now - dt

    if delta < timedelta(minutes=1):
        return "刚刚"
    elif delta < timedelta(hours=1):
        m = int(delta.total_seconds() // 60)
        return f"{m} 分钟前"
    elif delta < timedelta(days=1):
        h = int(delta.total_seconds() // 3600)
        return f"{h} 小时前"
    elif delta < timedelta(days=7):
        d = delta.days
        return f"{d} 天前"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def make_preview(content: str, content_type: str, max_len: int = 100) -> str:
    if content_type == "image":
        return "[图片]"
    elif content_type == "files":
        return f"[文件: {content}]"
    else:
        text = content.replace("\n", " ").replace("\r", " ").strip()
        return text[:max_len] + "…" if len(text) > max_len else text
