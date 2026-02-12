"""
🐟 발행 예약 스케줄러
백그라운드에서 예약된 글을 자동으로 발행합니다.
"""

import os
import sys
import time
import threading
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.database import DatabaseManager


class PublishScheduler:
    """백그라운드 발행 스케줄러"""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        self._running = False
        self._thread = None
        self._check_interval = 30  # 30초마다 체크
        # 사용자별 세션 비밀번호를 저장 (메모리에만 유지)
        self._user_credentials = {}

    def set_user_credentials(self, user_id: str, password: str, blog_id: str = None):
        """사용자 인증정보 등록 (메모리에만 저장)"""
        self._user_credentials[user_id] = {
            "password": password,
            "blog_id": blog_id or user_id
        }

    def remove_user_credentials(self, user_id: str):
        """사용자 인증정보 제거"""
        self._user_credentials.pop(user_id, None)

    def start(self):
        """스케줄러 시작"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("📅 발행 스케줄러 시작!")

    def stop(self):
        """스케줄러 중지"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("📅 발행 스케줄러 중지!")

    def _run_loop(self):
        """메인 루프"""
        while self._running:
            try:
                self._check_and_publish()
            except Exception as e:
                print(f"❌ 스케줄러 오류: {e}")
            time.sleep(self._check_interval)

    def _check_and_publish(self):
        """예약 시간 도래한 글 확인 및 발행"""
        pending_posts = self.db.get_pending_posts()

        for post in pending_posts:
            user_id = post["user_id"]
            creds = self._user_credentials.get(user_id)

            if not creds:
                print(f"⚠️ {user_id}의 인증정보 없음 - 발행 건너뜀")
                self.db.update_schedule_status(
                    post["id"], "failed",
                    "사용자 인증정보를 찾을 수 없습니다. 로그인 후 다시 시도해주세요."
                )
                continue

            print(f"⏰ 예약 발행 시작: {post['title'][:30]}... (사용자: {user_id})")

            try:
                from src.posting.naver_bot import NaverBlogBot

                bot = NaverBlogBot(
                    naver_id=user_id,
                    naver_pw=creds["password"],
                    blog_id=creds["blog_id"]
                )

                success = bot.write_post(
                    title=post["title"],
                    content=post["content"],
                    tags=post.get("tags", [])
                )

                if success:
                    self.db.update_schedule_status(post["id"], "published")
                    self.db.add_history(
                        user_id=user_id,
                        title=post["title"],
                        status="success",
                        content_preview=post["content"][:200],
                        source="scheduled"
                    )
                    print(f"✅ 예약 발행 성공: {post['title'][:30]}...")
                else:
                    self.db.update_schedule_status(post["id"], "failed", "포스팅 실패")
                    self.db.add_history(
                        user_id=user_id,
                        title=post["title"],
                        status="failed",
                        source="scheduled"
                    )

                bot.close()

            except Exception as e:
                error_msg = str(e)
                self.db.update_schedule_status(post["id"], "failed", error_msg)
                print(f"❌ 예약 발행 실패: {error_msg}")


# 전역 스케줄러 인스턴스
_scheduler_instance = None


def get_scheduler() -> PublishScheduler:
    """전역 스케줄러 인스턴스 반환"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = PublishScheduler()
    return _scheduler_instance
