"""
🐟 블로그 자동화 프로그램 설정
코다리 부장이 만든 설정 파일입니다!
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ============================================
# 🔑 API 설정
# ============================================
class APIConfig:
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # 네이버 API
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")
    
    # 사용할 AI (openai 또는 gemini)
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")


# ============================================
# 👤 네이버 계정 설정
# ============================================
class NaverConfig:
    ID = os.getenv("NAVER_ID", "")
    PASSWORD = os.getenv("NAVER_PASSWORD", "")
    BLOG_ID = os.getenv("NAVER_BLOG_ID", "")


# ============================================
# 📝 콘텐츠 생성 설정
# ============================================
class ContentConfig:
    # 글 생성 설정
    MIN_LENGTH = 1500  # 최소 글자 수
    MAX_LENGTH = 3000  # 최대 글자 수
    
    # 이미지 설정
    IMAGES_PER_POST = 3  # 포스트당 이미지 수
    
    # 키워드 설정
    MAX_KEYWORD_REPEAT = 5  # 키워드 최대 반복 횟수


# ============================================
# 🤖 자동화 안전 설정
# ============================================
class SafetyConfig:
    # 랜덤 대기 시간 (초)
    MIN_DELAY = 3
    MAX_DELAY = 10
    
    # 일일 발행량 제한
    DAILY_POST_LIMIT = 5
    
    # 포스팅 간격 (분)
    POST_INTERVAL_MINUTES = 60


# ============================================
# 🏢 렌탈 업체 설정
# ============================================
class RentalConfig:
    COMPANY_NAME = os.getenv("RENTAL_COMPANY_NAME", "렌탈전문업체")
    PRODUCTS = ["복합기", "프린터", "컴퓨터", "정수기", "공기청정기"]
    TARGET_REGIONS = ["서울", "강남", "송파", "마포", "영등포"]
    CONTACT_NUMBER = os.getenv("RENTAL_CONTACT", "1588-0000")


# ============================================
# 🚫 금칙어 목록 (AI 검열 회피)
# ============================================
BANNED_WORDS = [
    # 금융 관련
    "대출", "보험", "투자", "수익률", "이자율",
    # 의료 관련  
    "치료", "처방", "약", "병원",
    # 도박/성인
    "도박", "카지노", "성인",
    # 광고성 표현
    "최저가", "업계 1위", "100% 보장",
]


# ============================================
# 📁 경로 설정
# ============================================
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
LOGS_DIR = BASE_DIR / "logs"

# 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


# ============================================
# 🌐 Flask 대시보드 설정
# ============================================
class FlaskConfig:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "kodari-blog-auto-secret-key-2026")
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
