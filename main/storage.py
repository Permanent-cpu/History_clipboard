import sqlite3
import os
from datetime import datetime
from main.models import ClipItem
from main.utils import make_preview

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "history.db")
MAX_ITEMS = 500
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "images")


class Storage:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_type TEXT NOT NULL DEFAULT 'text',
                preview TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_item(self, content: str, content_type: str) -> ClipItem | None:
        # dedup: skip if same as last item
        last = self.get_last()
        if last and last.content == content and last.content_type == content_type:
            return None

        preview = make_preview(content, content_type)
        now = datetime.now().isoformat(sep=" ", timespec="seconds")

        cursor = self.conn.execute(
            "INSERT INTO clipboard_history (content, content_type, preview, created_at) VALUES (?, ?, ?, ?)",
            (content, content_type, preview, now),
        )
        self.conn.commit()

        # clean up image files for items about to be deleted
        old_rows = self.conn.execute(
            "SELECT id, content FROM clipboard_history WHERE content_type = 'image' AND id NOT IN (SELECT id FROM clipboard_history ORDER BY id DESC LIMIT ?)",
            (MAX_ITEMS,),
        ).fetchall()
        for row in old_rows:
            if os.path.isfile(row["content"]):
                try:
                    os.remove(row["content"])
                except OSError:
                    pass

        # enforce max items
        self.conn.execute(
            "DELETE FROM clipboard_history WHERE id NOT IN (SELECT id FROM clipboard_history ORDER BY id DESC LIMIT ?)",
            (MAX_ITEMS,),
        )
        self.conn.commit()

        return ClipItem(
            id=cursor.lastrowid,
            content=content,
            content_type=content_type,
            preview=preview,
            created_at=now,
        )

    def get_last(self) -> ClipItem | None:
        row = self.conn.execute(
            "SELECT * FROM clipboard_history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return self._row_to_item(row) if row else None

    def get_all(self, limit: int = 200) -> list[ClipItem]:
        rows = self.conn.execute(
            "SELECT * FROM clipboard_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._row_to_item(r) for r in rows]

    def delete_item(self, item_id: int):
        self._delete_image_file(item_id)
        self.conn.execute(
            "DELETE FROM clipboard_history WHERE id = ?", (item_id,)
        )
        self.conn.commit()

    def clear_all(self):
        rows = self.conn.execute(
            "SELECT id FROM clipboard_history WHERE content_type = 'image'"
        ).fetchall()
        for row in rows:
            self._delete_image_file(row["id"])
        self.conn.execute("DELETE FROM clipboard_history")
        self.conn.commit()

    def _delete_image_file(self, item_id: int):
        row = self.conn.execute(
            "SELECT content FROM clipboard_history WHERE id = ?", (item_id,)
        ).fetchone()
        if row and os.path.isfile(row["content"]):
            try:
                os.remove(row["content"])
            except OSError:
                pass

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM clipboard_history").fetchone()
        return row["cnt"] if row else 0

    def _row_to_item(self, row) -> ClipItem:
        return ClipItem(
            id=row["id"],
            content=row["content"],
            content_type=row["content_type"],
            preview=row["preview"],
            created_at=row["created_at"],
        )
