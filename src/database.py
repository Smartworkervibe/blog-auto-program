"""
🐟 데이터베이스 관리 모듈
임시저장, 예약발행, 발행이력을 SQLite로 관리합니다.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, List
import pathlib

# DB 파일 경로
DB_DIR = pathlib.Path(__file__).parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "posts.db"


class DatabaseManager:
    """SQLite 데이터베이스 관리자"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._init_db()

    def _get_conn(self):
        """DB 연결"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """테이블 초기화"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # 임시저장 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                keyword TEXT DEFAULT '',
                persona TEXT DEFAULT 'lifestyle_blogger',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 예약 발행 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                draft_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (draft_id) REFERENCES drafts(id) ON DELETE SET NULL
            )
        """)

        # 발행 이력 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content_preview TEXT,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success',
                post_url TEXT,
                source TEXT DEFAULT 'direct'
            )
        """)

        conn.commit()
        conn.close()

    # ============================================
    # 💾 임시저장 (Drafts)
    # ============================================

    def save_draft(self, user_id: str, title: str, content: str,
                   tags: list = None, keyword: str = "", persona: str = "lifestyle_blogger") -> int:
        """임시저장 생성"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO drafts (user_id, title, content, tags, keyword, persona)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, content, json.dumps(tags or [], ensure_ascii=False), keyword, persona))
        draft_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return draft_id

    def update_draft(self, draft_id: int, user_id: str, title: str = None,
                     content: str = None, tags: list = None, keyword: str = None) -> bool:
        """임시저장 수정"""
        conn = self._get_conn()
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags, ensure_ascii=False))
        if keyword is not None:
            updates.append("keyword = ?")
            params.append(keyword)

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.extend([draft_id, user_id])

        cursor.execute(f"""
            UPDATE drafts SET {', '.join(updates)}
            WHERE id = ? AND user_id = ?
        """, params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_draft(self, draft_id: int, user_id: str) -> Optional[dict]:
        """임시저장 조회"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE id = ? AND user_id = ?", (draft_id, user_id))
        row = cursor.fetchone()
        conn.close()

        if row:
            d = dict(row)
            d['tags'] = json.loads(d['tags']) if d['tags'] else []
            return d
        return None

    def get_drafts(self, user_id: str) -> List[dict]:
        """사용자의 임시저장 목록"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drafts WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            d = dict(row)
            d['tags'] = json.loads(d['tags']) if d['tags'] else []
            result.append(d)
        return result

    def delete_draft(self, draft_id: int, user_id: str) -> bool:
        """임시저장 삭제"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drafts WHERE id = ? AND user_id = ?", (draft_id, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # ============================================
    # ⏰ 예약 발행 (Scheduled Posts)
    # ============================================

    def schedule_post(self, user_id: str, title: str, content: str,
                      scheduled_time: str, tags: list = None, draft_id: int = None) -> int:
        """예약 발행 추가"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scheduled_posts (user_id, draft_id, title, content, tags, scheduled_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, draft_id, title, content,
              json.dumps(tags or [], ensure_ascii=False), scheduled_time))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return post_id

    def get_scheduled_posts(self, user_id: str) -> List[dict]:
        """사용자의 예약 발행 목록"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scheduled_posts 
            WHERE user_id = ? 
            ORDER BY scheduled_time ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            d = dict(row)
            d['tags'] = json.loads(d['tags']) if d['tags'] else []
            result.append(d)
        return result

    def get_pending_posts(self) -> List[dict]:
        """발행 대기 중인 모든 예약 글 (시간 도래)"""
        conn = self._get_conn()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("""
            SELECT * FROM scheduled_posts 
            WHERE status = 'pending' AND scheduled_time <= ?
            ORDER BY scheduled_time ASC
        """, (now,))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            d = dict(row)
            d['tags'] = json.loads(d['tags']) if d['tags'] else []
            result.append(d)
        return result

    def update_schedule_status(self, post_id: int, status: str, error_message: str = None) -> bool:
        """예약 발행 상태 업데이트"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scheduled_posts SET status = ?, error_message = ?
            WHERE id = ?
        """, (status, error_message, post_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def cancel_schedule(self, post_id: int, user_id: str) -> bool:
        """예약 발행 취소"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM scheduled_posts 
            WHERE id = ? AND user_id = ? AND status = 'pending'
        """, (post_id, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # ============================================
    # 📊 발행 이력 (Post History)
    # ============================================

    def add_history(self, user_id: str, title: str, status: str = "success",
                    post_url: str = None, content_preview: str = None,
                    source: str = "direct") -> int:
        """발행 이력 추가"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO post_history (user_id, title, content_preview, status, post_url, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, title, content_preview, status, post_url, source))
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return history_id

    def get_history(self, user_id: str, limit: int = 20) -> List[dict]:
        """발행 이력 조회"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM post_history 
            WHERE user_id = ? 
            ORDER BY published_at DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_stats(self, user_id: str) -> dict:
        """사용자 통계"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # 임시저장 수
        cursor.execute("SELECT COUNT(*) FROM drafts WHERE user_id = ?", (user_id,))
        draft_count = cursor.fetchone()[0]

        # 예약 대기 수
        cursor.execute("SELECT COUNT(*) FROM scheduled_posts WHERE user_id = ? AND status = 'pending'", (user_id,))
        scheduled_count = cursor.fetchone()[0]

        # 총 발행 수
        cursor.execute("SELECT COUNT(*) FROM post_history WHERE user_id = ? AND status = 'success'", (user_id,))
        published_count = cursor.fetchone()[0]

        # 오늘 발행 수
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM post_history 
            WHERE user_id = ? AND status = 'success' AND DATE(published_at) = ?
        """, (user_id, today))
        today_count = cursor.fetchone()[0]

        conn.close()

        return {
            "draft_count": draft_count,
            "scheduled_count": scheduled_count,
            "published_count": published_count,
            "today_count": today_count,
        }
