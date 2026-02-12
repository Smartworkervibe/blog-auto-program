"""
🐟 키워드 분석 모듈
네이버 API를 활용한 키워드 분석기입니다!
"""

import os
import sys
import json
import requests
from typing import Optional
from urllib.parse import quote

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import APIConfig


class KeywordAnalyzer:
    """네이버 API 기반 키워드 분석기"""
    
    def __init__(self):
        self.client_id = APIConfig.NAVER_CLIENT_ID
        self.client_secret = APIConfig.NAVER_CLIENT_SECRET
        self.base_url = "https://openapi.naver.com/v1/search"
    
    def _request(self, endpoint: str, query: str, display: int = 10) -> dict:
        """네이버 API 요청"""
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        params = {
            "query": query,
            "display": display,
            "sort": "sim"  # 정확도순
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API 요청 실패: {e}")
            return {}
    
    def search_blog(self, keyword: str, count: int = 10) -> list:
        """
        네이버 블로그 검색
        
        Args:
            keyword: 검색 키워드
            count: 결과 개수
            
        Returns:
            list: 검색 결과 리스트
        """
        print(f"🔍 블로그 검색 중... 키워드: {keyword}")
        
        result = self._request("blog", keyword, count)
        
        if not result:
            return []
        
        items = result.get("items", [])
        
        blogs = []
        for item in items:
            blogs.append({
                "title": self._clean_html(item.get("title", "")),
                "description": self._clean_html(item.get("description", "")),
                "link": item.get("link", ""),
                "blogger_name": item.get("bloggername", ""),
                "post_date": item.get("postdate", "")
            })
        
        print(f"✅ {len(blogs)}개 블로그 검색 완료!")
        return blogs
    
    def analyze_competition(self, keyword: str) -> dict:
        """
        키워드 경쟁 강도 분석
        
        Args:
            keyword: 분석할 키워드
            
        Returns:
            dict: 경쟁 분석 결과
        """
        print(f"📊 경쟁 분석 중... 키워드: {keyword}")
        
        # 블로그 검색 결과
        blog_result = self._request("blog", keyword, 100)
        blog_total = blog_result.get("total", 0)
        
        # 웹 검색 결과
        web_result = self._request("webkr", keyword, 100)
        web_total = web_result.get("total", 0)
        
        # 경쟁 강도 계산
        if blog_total < 1000:
            competition_level = "낮음 🟢"
            recommendation = "진입하기 좋은 키워드입니다!"
        elif blog_total < 10000:
            competition_level = "보통 🟡"
            recommendation = "롱테일 키워드와 함께 공략하세요."
        elif blog_total < 100000:
            competition_level = "높음 🟠"
            recommendation = "차별화된 콘텐츠가 필요합니다."
        else:
            competition_level = "매우 높음 🔴"
            recommendation = "세부 키워드로 분리해서 공략하세요."
        
        result = {
            "keyword": keyword,
            "blog_count": blog_total,
            "web_count": web_total,
            "competition_level": competition_level,
            "recommendation": recommendation
        }
        
        print(f"✅ 분석 완료! 경쟁 강도: {competition_level}")
        return result
    
    def get_related_keywords(self, keyword: str) -> list:
        """
        연관 키워드 추출 (상위 블로그 분석)
        
        Args:
            keyword: 메인 키워드
            
        Returns:
            list: 연관 키워드 리스트
        """
        print(f"🔗 연관 키워드 분석 중... 키워드: {keyword}")
        
        blogs = self.search_blog(keyword, 20)
        
        # 제목과 설명에서 키워드 추출
        words = []
        for blog in blogs:
            title_words = blog["title"].split()
            desc_words = blog["description"].split()
            words.extend(title_words)
            words.extend(desc_words)
        
        # 빈도 계산
        word_count = {}
        for word in words:
            word = word.strip(".,!?\"'()[]{}:;")
            if len(word) >= 2 and word != keyword:
                word_count[word] = word_count.get(word, 0) + 1
        
        # 상위 키워드 추출
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        related = [word for word, count in sorted_words[:20] if count >= 2]
        
        print(f"✅ {len(related)}개 연관 키워드 발견!")
        return related
    
    def generate_longtail_keywords(self, keyword: str) -> list:
        """
        롱테일 키워드 생성
        
        Args:
            keyword: 메인 키워드
            
        Returns:
            list: 롱테일 키워드 리스트
        """
        suffixes = [
            "추천", "비교", "가격", "후기", "장단점",
            "사용법", "선택방법", "렌탈", "구매",
            "2026", "최신", "할인", "무료"
        ]
        
        prefixes = [
            "최고의", "가성비", "인기", "추천하는",
            "저렴한", "좋은"
        ]
        
        longtails = []
        
        # 접미사 조합
        for suffix in suffixes:
            longtails.append(f"{keyword} {suffix}")
        
        # 접두사 조합
        for prefix in prefixes:
            longtails.append(f"{prefix} {keyword}")
        
        return longtails[:15]
    
    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.replace("&quot;", '"')
        clean = clean.replace("&amp;", '&')
        clean = clean.replace("&lt;", '<')
        clean = clean.replace("&gt;", '>')
        return clean.strip()


class RentalKeywordGenerator:
    """렌탈 업체 전용 키워드 생성기"""
    
    def __init__(self):
        from config.settings import RentalConfig
        self.products = RentalConfig.PRODUCTS
        self.regions = RentalConfig.TARGET_REGIONS
    
    def generate_all_combinations(self) -> list:
        """
        지역 + 제품 조합 키워드 생성
        
        Returns:
            list: 키워드 리스트
        """
        keywords = []
        
        for region in self.regions:
            for product in self.products:
                keywords.extend([
                    f"{region} {product} 렌탈",
                    f"{region} {product} 임대",
                    f"{region} {product} 대여",
                    f"{region} {product} 렌탈 가격",
                    f"{region} {product} 렌탈 추천",
                ])
        
        return keywords
    
    def get_priority_keywords(self, limit: int = 20) -> list:
        """
        우선순위 키워드 추출
        
        Args:
            limit: 최대 개수
            
        Returns:
            list: 우선순위 키워드
        """
        all_keywords = self.generate_all_combinations()
        
        # 주요 지역과 제품 우선
        priority_regions = self.regions[:3]
        priority_products = self.products[:3]
        
        priority = []
        for region in priority_regions:
            for product in priority_products:
                priority.append(f"{region} {product} 렌탈")
        
        return priority[:limit]


# 테스트 코드
if __name__ == "__main__":
    analyzer = KeywordAnalyzer()
    
    # 경쟁 분석 테스트
    result = analyzer.analyze_competition("복합기 렌탈")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 연관 키워드 테스트
    related = analyzer.get_related_keywords("복합기 렌탈")
    print(f"연관 키워드: {related}")
    
    # 렌탈 키워드 생성 테스트
    rental_gen = RentalKeywordGenerator()
    keywords = rental_gen.get_priority_keywords(10)
    print(f"렌탈 키워드: {keywords}")
