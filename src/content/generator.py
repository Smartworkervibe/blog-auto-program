"""
🐟 AI 글 생성 모듈
코다리 부장의 핵심 엔진입니다!
OpenAI와 Gemini 둘 다 지원합니다.
"""

import os
import json
import sys
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.settings import APIConfig, ContentConfig, BANNED_WORDS
from config.prompts import BLOG_POST_PROMPT, RENTAL_POST_PROMPT, HUMANIZE_PROMPT, PERSONA_PROMPTS


class ContentGenerator:
    """AI 기반 블로그 콘텐츠 생성기"""
    
    def __init__(self, provider: str = None, api_key: str = None):
        """
        Args:
            provider: AI 프로바이더 ('openai' 또는 'gemini'). None이면 설정에서 가져옴
            api_key: API 키. None이면 설정에서 가져옴
        """
        self.provider = provider or APIConfig.AI_PROVIDER
        self._api_key = api_key  # 런타임 전달 키 우선
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """AI 클라이언트 초기화"""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                key = self._api_key or APIConfig.OPENAI_API_KEY
                if not key:
                    print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
                    return
                self.client = OpenAI(api_key=key)
                self.model = APIConfig.OPENAI_MODEL
                print("🤖 OpenAI 클라이언트 초기화 완료!")
            except Exception as e:
                print(f"⚠️ OpenAI 초기화 실패: {e}")
                
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                key = self._api_key or APIConfig.GEMINI_API_KEY
                if not key:
                    print("⚠️ Gemini API 키가 설정되지 않았습니다.")
                    return
                genai.configure(api_key=key)
                self.client = genai.GenerativeModel(APIConfig.GEMINI_MODEL)
                self.model = APIConfig.GEMINI_MODEL
                print("🤖 Gemini 클라이언트 초기화 완료!")
            except Exception as e:
                print(f"⚠️ Gemini 초기화 실패: {e}")
    
    def _call_ai(self, prompt: str) -> str:
        """AI API 호출 (재시도 로직 포함)"""
        if not self.client:
            raise RuntimeError(f"클라이언트가 초기화되지 않았습니다. {self.provider} API 키를 확인해주세요.")
        
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "당신은 전문 블로그 작가입니다."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8,
                        max_tokens=4000
                    )
                    return response.choices[0].message.content
                    
                elif self.provider == "gemini":
                    # 안전 설정 (필터링 완화)
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                    response = self.client.generate_content(prompt, safety_settings=safety_settings)
                    return response.text
            
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ AI 호출 실패 ({attempt+1}/{max_retries}): {error_msg}")
                
                # 429 Resource exhausted 에러 처리
                if "429" in error_msg or "Resource exhausted" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt) + random.uniform(0, 3)
                        print(f"⏳ 할당량 초과로 {wait_time:.1f}초 대기 후 재시도합니다...")
                        time.sleep(wait_time)
                        continue
                
                if attempt == max_retries - 1:
                    raise
    
    def generate_blog_post(
        self,
        topic: str,
        keyword: str,
        persona: str = "lifestyle_blogger",
        min_length: int = None,
        max_length: int = None
    ) -> dict:
        """
        블로그 글 생성
        
        Args:
            topic: 글 주제
            keyword: 타겟 키워드
            persona: 페르소나 유형
            min_length: 최소 글자 수
            max_length: 최대 글자 수
            
        Returns:
            dict: {"title": str, "content": str, "tags": list}
        """
        min_length = min_length or ContentConfig.MIN_LENGTH
        max_length = max_length or ContentConfig.MAX_LENGTH
        
        # 프롬프트 구성
        prompt = BLOG_POST_PROMPT.format(
            topic=topic,
            keyword=keyword,
            min_length=min_length,
            max_length=max_length,
            banned_words=", ".join(BANNED_WORDS[:10]),
            max_keyword_repeat=ContentConfig.MAX_KEYWORD_REPEAT,
            persona=PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["lifestyle_blogger"])
        )
        
        print(f"✍️ 글 생성 중... 키워드: {keyword}")
        content = self._call_ai(prompt)
        
        if not content:
            return {"title": "", "content": "", "tags": []}
        
        # 제목 추출 (첫 번째 줄 또는 # 이후)
        lines = content.strip().split("\n")
        title = ""
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                break
            elif line and not title:
                title = line
                break
        
        # 금칙어 필터링
        content = self._filter_banned_words(content)
        
        # 태그 생성
        tags = self._generate_tags(keyword, topic)
        
        print(f"✅ 글 생성 완료! 글자 수: {len(content)}")
        
        return {
            "title": title or f"{keyword} 완벽 정리",
            "content": content,
            "tags": tags
        }
    
    def generate_rental_post(
        self,
        product: str,
        region: str,
        keyword: str = None,
        company_name: str = None
    ) -> dict:
        """
        렌탈 업체 전용 블로그 글 생성
        
        Args:
            product: 제품명 (예: "복합기", "프린터")
            region: 타겟 지역 (예: "강남", "서울")
            keyword: 추가 키워드
            company_name: 회사명
            
        Returns:
            dict: {"title": str, "content": str, "tags": list}
        """
        from config.settings import RentalConfig
        
        keyword = keyword or f"{region} {product} 렌탈"
        company_name = company_name or RentalConfig.COMPANY_NAME
        
        prompt = RENTAL_POST_PROMPT.format(
            product=product,
            region=region,
            keyword=keyword,
            company_name=company_name,
            min_length=ContentConfig.MIN_LENGTH,
            max_length=ContentConfig.MAX_LENGTH
        )
        
        print(f"🏢 렌탈 글 생성 중... 제품: {product}, 지역: {region}")
        content = self._call_ai(prompt)
        
        if not content:
            return {"title": "", "content": "", "tags": []}
        
        # 제목 생성
        title = f"{region} {product} 렌탈 비용 및 추천 업체 완벽 가이드"
        
        # 금칙어 필터링
        content = self._filter_banned_words(content)
        
        # 태그 생성
        tags = [
            f"{region}{product}렌탈",
            f"{product}렌탈",
            f"{region}사무기기",
            f"{product}임대",
            company_name,
        ]
        
        print(f"✅ 렌탈 글 생성 완료! 글자 수: {len(content)}")
        
        return {
            "title": title,
            "content": content,
            "tags": tags
        }
    
    def humanize_content(self, content: str) -> str:
        """
        AI 글을 더 자연스럽게 변환 (휴먼터치)
        
        Args:
            content: 원본 글
            
        Returns:
            str: 자연스럽게 수정된 글
        """
        prompt = HUMANIZE_PROMPT.format(original_text=content)
        
        print("🧠 휴먼터치 적용 중...")
        humanized = self._call_ai(prompt)
        
        if humanized:
            print("✅ 휴먼터치 적용 완료!")
            return humanized
        return content
    
    def _filter_banned_words(self, content: str) -> str:
        """금칙어 필터링"""
        filtered = content
        for word in BANNED_WORDS:
            if word in filtered:
                # 금칙어를 부드러운 표현으로 대체
                filtered = filtered.replace(word, f"[{word[0]}**]")
        return filtered
    
    def generate_comment(self, post_content: str) -> str:
        """
        블로그 이웃 글에 달 댓글 생성 (평판 관리용)
        
        Args:
            post_content: 이웃 글 본문 (일부분)
            
        Returns:
            str: 생성된 댓글 (1-2문장)
        """
        prompt = f"""
        다음 블로그 글을 읽고, 작성자를 진심으로 응원하거나 내용에 공감하는 따뜻한 댓글을 1~2문장으로 짧게 작성해줘.
        광고성 느낌이 나지 않게, 친근한 이웃처럼 자연스럽게 작성해. 이모지를 1개만 사용해.
        반말은 하지 말고 해요체를 사용해.
        
        [블로그 글 본문]
        {post_content[:800]}
        """
        
        comment = self._call_ai(prompt).strip()
        # 따옴표 제거
        return comment.replace('"', '').replace("'", "")
    
    def _generate_tags(self, keyword: str, topic: str) -> list:
        """태그 생성"""
        tags = [keyword]
        
        # 키워드 분리해서 태그 추가
        for part in keyword.split():
            if len(part) >= 2 and part not in tags:
                tags.append(part)
        
        # 토픽에서 태그 추출
        for part in topic.split():
            if len(part) >= 2 and part not in tags and len(tags) < 10:
                tags.append(part)
        
        return tags[:10]  # 최대 10개


# 테스트 코드
if __name__ == "__main__":
    generator = ContentGenerator()
    
    # 일반 블로그 글 테스트
    result = generator.generate_blog_post(
        topic="사무실 복합기 선택 방법",
        keyword="복합기 추천",
        persona="tech_reviewer"
    )
    
    print("\n" + "="*50)
    print(f"📌 제목: {result['title']}")
    print(f"🏷️ 태그: {result['tags']}")
    print(f"📝 내용 미리보기:\n{result['content'][:500]}...")
