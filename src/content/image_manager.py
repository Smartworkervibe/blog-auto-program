"""
🐟 이미지 생성/관리 모듈
키워드 기반으로 무료 이미지를 검색하고 블로그 글에 자동 삽입합니다.

지원 소스:
- Unsplash API (무료, API 키 필요)
- Pexels API (무료, API 키 필요)
- 로컬 이미지 관리
"""

import os
import re
import sys
import time
import shutil
import hashlib
import os
import re
import sys
import time
import shutil
import hashlib
import requests
import random
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

# 프로젝트 루트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from config.settings import APIConfig

# 이미지 저장 디렉토리
IMAGES_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "data" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 사용자 정의 이미지 프롬프트 (프린터/렌탈 관련)
CUSTOM_IMAGE_PROMPTS = [
    "Photorealistic image of a modern printer in a bright office, professional shot, 8k",
    "Close up shot of printer detailed interface, high tech feel",
    "Happy office workers using a copy machine, warm lighting, candid style",
    "Graph comparing printer speeds of different models, clean design",
    "Office space dedicated to printing, well-organized and efficient"
]

class ImageManager:
    """블로그용 이미지 검색/관리 및 AI 생성"""

    def __init__(self, unsplash_key: str = None, pexels_key: str = None, openai_key: str = None):
        """
        Args:
            unsplash_key: Unsplash API 키 (선택)
            pexels_key: Pexels API 키 (선택)
            openai_key: OpenAI API 키 (AI 생성용)
        """
        self.unsplash_key = unsplash_key or os.getenv("UNSPLASH_API_KEY", "")
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY", "")
        self.save_dir = IMAGES_DIR
        
        # OpenAI 클라이언트 초기화 (AI 이미지 생성용)
        self.openai_key = openai_key or APIConfig.OPENAI_API_KEY
        self.openai_client = None
        if self.openai_key and OpenAI:
            try:
                self.openai_client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                print(f"⚠️ OpenAI 클라이언트 초기화 실패 (이미지 생성 불가): {e}")

    # ============================================
    # 이미지 검색
    # ============================================
    def search_images(self, keyword: str, count: int = 3, source: str = "auto") -> List[dict]:
        """
        키워드로 무료 이미지 검색

        Args:
            keyword: 검색 키워드
            count: 가져올 이미지 수
            source: 'unsplash', 'pexels', 'auto'

        Returns:
            list: [{"url": str, "thumb": str, "alt": str, "source": str, "photographer": str}]
        """
        results = []

        if source in ("dalle", "ai") and self.openai_client:
            return self.generate_image_dalle(keyword, count)

        if source in ("auto", "pexels") and self.pexels_key:
            results = self._search_pexels(keyword, count)

        if not results and source in ("auto", "unsplash") and self.unsplash_key:
            results = self._search_unsplash(keyword, count)

        # API 키가 없으면 대체 이미지 사용
        if not results:
            results = self._get_placeholder_images(keyword, count)

        return results[:count]

    def _search_pexels(self, keyword: str, count: int = 3) -> List[dict]:
        """Pexels API로 이미지 검색"""
        try:
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": keyword,
                "per_page": count,
                "locale": "ko-KR"
            }
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers, params=params, timeout=10
            )
            r.raise_for_status()
            data = r.json()

            results = []
            for photo in data.get("photos", []):
                results.append({
                    "url": photo["src"]["large"],
                    "thumb": photo["src"]["medium"],
                    "alt": photo.get("alt", keyword),
                    "source": "pexels",
                    "photographer": photo.get("photographer", ""),
                    "source_url": photo.get("url", ""),
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0)
                })
            print(f"📸 Pexels에서 {len(results)}개 이미지 검색 완료!")
            return results

        except Exception as e:
            print(f"⚠️ Pexels 검색 실패: {e}")
            return []

    def _search_unsplash(self, keyword: str, count: int = 3) -> List[dict]:
        """Unsplash API로 이미지 검색"""
        try:
            params = {
                "query": keyword,
                "per_page": count,
                "client_id": self.unsplash_key
            }
            r = requests.get(
                "https://api.unsplash.com/search/photos",
                params=params, timeout=10
            )
            r.raise_for_status()
            data = r.json()

            results = []
            for photo in data.get("results", []):
                results.append({
                    "url": photo["urls"]["regular"],
                    "thumb": photo["urls"]["small"],
                    "alt": photo.get("alt_description", keyword),
                    "source": "unsplash",
                    "photographer": photo["user"]["name"],
                    "source_url": photo["links"]["html"],
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0)
                })
            print(f"📸 Unsplash에서 {len(results)}개 이미지 검색 완료!")
            return results

        except Exception as e:
            print(f"⚠️ Unsplash 검색 실패: {e}")
            return []

    def _get_placeholder_images(self, keyword: str, count: int = 3) -> List[dict]:
        """API 키 없을 때 플레이스홀더 이미지 생성"""
        results = []
        # 텍스트 기반 플레이스홀더 이미지 (picsum.photos 사용 - 무료, 키 불필요)
        for i in range(count):
            seed = hashlib.md5(f"{keyword}_{i}".encode()).hexdigest()[:8]
            results.append({
                "url": f"https://picsum.photos/seed/{seed}/800/500",
                "thumb": f"https://picsum.photos/seed/{seed}/400/250",
                "alt": f"{keyword} 관련 이미지 {i+1}",
                "source": "picsum",
                "photographer": "Lorem Picsum",
                "source_url": "https://picsum.photos",
                "width": 800,
                "height": 500
            })
        print(f"📸 플레이스홀더 이미지 {count}개 생성!")
        return results

    # ============================================
    # AI 이미지 생성 (DALL-E 3)
    # ============================================
    def generate_image_dalle(self, prompt: str = None, count: int = 1) -> List[dict]:
        """
        DALL-E 3로 이미지 생성

        Args:
            prompt: 이미지 생성 프롬프트 (None이면 기본 프롬프트 중 랜덤 선택)
            count: 생성할 이미지 수

        Returns:
            list: [{"url": str, "thumb": str, "alt": str, "source": "dalle", "local_path": str}]
        """
        if not self.openai_client:
            print("⚠️ OpenAI 클라이언트가 초기화되지 않아 이미지 생성을 건너뜁니다.")
            return []

        results = []
        try:
            # 프롬프트 최적화 로직
            final_prompt = prompt
            
            # 입력된 키워드가 프린터/복합기 관련이면 고품질 커스텀 프롬프트 적용
            if prompt:
                keywords = ["프린터", "복합기", "인쇄", "복사기", "렌탈", "printer", "copier"]
                if any(k in prompt for k in keywords):
                    print(f"💡 프린터 관련 키워드 감지! 고품질 전용 프롬프트를 적용합니다.")
                    final_prompt = random.choice(CUSTOM_IMAGE_PROMPTS)
            
            # 프롬프트가 없거나(None), 위 로직을 타지 않은 경우
            if not final_prompt:
                # 기본 랜덤 선택
                base_prompt = random.choice(CUSTOM_IMAGE_PROMPTS)
                final_prompt = f"{base_prompt}, high quality, detailed, {random.choice(['daylight', 'soft lighting', 'cinematic lighting'])}"
            
            print(f"🎨 AI 이미지 생성 시작 (DALL-E 3): {final_prompt}")

            # DALL-E 3는 한 번에 1장만 생성 가능하므로 루프 필요
            for _ in range(count):
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )

                image_url = response.data[0].url
                revised_prompt = response.data[0].revised_prompt
                
                # 이미지 다운로드 및 저장
                filename = f"dalle_{int(time.time())}_{random.randint(1000, 9999)}.png"
                local_path = self.save_dir / filename
                
                if self._download_file(image_url, local_path):
                    results.append({
                        "url": f"/images/{filename}", # 웹 접근 경로 (static)
                        "thumb": f"/images/{filename}",
                        "alt": revised_prompt or prompt,
                        "source": "dalle", # DALL-E 표시
                        "local_path": str(local_path)
                    })
                    print(f"✅ AI 이미지 생성 및 저장 완료: {filename}")

        except Exception as e:
            print(f"❌ DALL-E 이미지 생성 실패: {e}")

        return results
    
    def _download_file(self, url: str, save_path: Path) -> bool:
        """URL에서 파일 다운로드"""
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"⚠️ 파일 다운로드 실패: {e}")
        return False

    # ============================================
    # 이미지 다운로드
    # ============================================
    def download_image(self, url: str, filename: str = None) -> Optional[str]:
        """
        이미지 URL에서 다운로드하여 로컬에 저장

        Returns:
            str: 저장된 파일 경로 (실패 시 None)
        """
        try:
            if not filename:
                ext = url.split("?")[0].split(".")[-1][:4]
                if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
                    ext = "jpg"
                filename = f"{hashlib.md5(url.encode()).hexdigest()[:12]}.{ext}"

            filepath = self.save_dir / filename
            if filepath.exists():
                return str(filepath)

            r = requests.get(url, timeout=15, stream=True)
            r.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            print(f"💾 이미지 저장: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"⚠️ 이미지 다운로드 실패: {e}")
            return None

    def download_images(self, image_list: List[dict]) -> List[str]:
        """여러 이미지 다운로드"""
        paths = []
        for img in image_list:
            path = self.download_image(img["url"])
            if path:
                paths.append(path)
        return paths

    # ============================================
    # 블로그 글에 이미지 삽입
    # ============================================
    def insert_images_to_content(
        self,
        content: str,
        images: List[dict],
        mode: str = "distributed"
    ) -> str:
        """
        블로그 본문에 이미지 HTML 자동 삽입

        Args:
            content: 블로그 본문
            images: 이미지 목록
            mode: 'distributed'(분산배치), 'top'(상단), 'bottom'(하단)

        Returns:
            str: 이미지가 삽입된 본문
        """
        if not images:
            return content

        def _make_img_html(img: dict) -> str:
            alt = img.get("alt", "")
            url = img.get("url", "")
            photographer = img.get("photographer", "")
            source = img.get("source", "")
            credit = ""
            if photographer and source != "picsum":
                credit = f'\n<p style="text-align:center; font-size:0.85em; color:#888;">📷 {photographer} / {source.capitalize()}</p>'
            return f'''
<div style="text-align:center; margin:20px 0;">
<img src="{url}" alt="{alt}" style="max-width:100%; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.1);">{credit}
</div>'''

        if mode == "top":
            # 첫 번째 이미지만 상단에
            img_html = _make_img_html(images[0])
            return img_html + "\n\n" + content

        elif mode == "bottom":
            # 모든 이미지를 하단에
            imgs_html = "\n".join(_make_img_html(img) for img in images)
            return content + "\n\n" + imgs_html

        else:
            # distributed: 글의 단락 사이에 균등 배치
            paragraphs = re.split(r'\n{2,}', content)

            if len(paragraphs) <= 1:
                # 단락이 하나면 앞뒤에 배치
                img_top = _make_img_html(images[0]) if images else ""
                img_bottom = "\n".join(_make_img_html(img) for img in images[1:])
                return img_top + "\n\n" + content + "\n\n" + img_bottom

            # 이미지를 균등하게 배치할 위치 계산
            total = len(paragraphs)
            img_count = min(len(images), total - 1)
            interval = max(1, total // (img_count + 1))

            result_parts = []
            img_idx = 0

            for i, para in enumerate(paragraphs):
                result_parts.append(para)
                # 일정 간격마다 이미지 삽입
                if img_idx < img_count and (i + 1) % interval == 0 and i < total - 1:
                    result_parts.append(_make_img_html(images[img_idx]))
                    img_idx += 1

            return "\n\n".join(result_parts)

    # ============================================
    # 로컬 이미지 관리
    # ============================================
    def get_saved_images(self) -> List[dict]:
        """저장된 이미지 목록"""
        images = []
        for f in self.save_dir.iterdir():
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                images.append({
                    "filename": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime
                })
        return sorted(images, key=lambda x: x["modified"], reverse=True)

    def delete_image(self, filename: str) -> bool:
        """저장된 이미지 삭제"""
        filepath = self.save_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def cleanup_old_images(self, days: int = 30):
        """오래된 이미지 정리"""
        import time
        cutoff = time.time() - (days * 86400)
        count = 0
        for f in self.save_dir.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                count += 1
        if count:
            print(f"🗑️ {count}개 오래된 이미지 정리 완료!")


# 테스트
if __name__ == "__main__":
    mgr = ImageManager()

    # 플레이스홀더 이미지 테스트
    images = mgr.search_images("사무실 복합기", count=3)
    print(f"\n검색 결과: {len(images)}개")
    for img in images:
        print(f"  - {img['alt']} ({img['source']})")

    # 이미지 삽입 테스트
    test_content = """오늘은 사무실 복합기 선택 방법에 대해 알아보겠습니다.

복합기를 고를 때 가장 중요한 것은 출력 속도와 품질입니다.

월 출력량에 따라 적합한 기종이 달라집니다.

렌탈과 구매 중 어떤 것이 유리한지 비교해보겠습니다."""

    result = mgr.insert_images_to_content(test_content, images)
    print(f"\n삽입 결과 미리보기:\n{result[:500]}...")
