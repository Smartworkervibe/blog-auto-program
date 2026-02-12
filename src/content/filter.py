"""
🐟 금칙어 필터 모듈
네이버 AI 검열을 피하는 필터입니다!
"""

import re
from typing import List, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import BANNED_WORDS


class ContentFilter:
    """콘텐츠 금칙어 필터"""
    
    def __init__(self):
        self.banned_words = BANNED_WORDS
        
        # 카테고리별 금칙어
        self.category_banned = {
            "금융": ["대출", "보험", "투자", "수익률", "이자율", "원금", "납입"],
            "의료": ["치료", "처방", "약", "병원", "의사", "진단", "수술"],
            "도박": ["도박", "카지노", "베팅", "배팅", "잭팟"],
            "광고": ["최저가", "업계 1위", "100% 보장", "무조건", "단독", "파격"],
        }
        
        # 대체어 사전
        self.replacements = {
            "대출": "자금 지원",
            "보험": "보장 서비스",
            "투자": "자산 운용",
            "최저가": "합리적인 가격",
            "업계 1위": "많은 분들이 선택한",
            "100% 보장": "높은 만족도",
            "무조건": "대부분의 경우",
        }
    
    def check_content(self, content: str) -> Tuple[bool, List[str]]:
        """
        콘텐츠 금칙어 검사
        
        Args:
            content: 검사할 콘텐츠
            
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 발견된 금칙어 목록)
        """
        found_words = []
        
        for word in self.banned_words:
            if word in content:
                found_words.append(word)
        
        is_safe = len(found_words) == 0
        return is_safe, found_words
    
    def filter_content(self, content: str) -> str:
        """
        금칙어 필터링 (대체어로 변환)
        
        Args:
            content: 원본 콘텐츠
            
        Returns:
            str: 필터링된 콘텐츠
        """
        result = content
        
        for word, replacement in self.replacements.items():
            if word in result:
                result = result.replace(word, replacement)
                print(f"🔄 금칙어 변환: '{word}' → '{replacement}'")
        
        # 대체어 없는 금칙어는 첫 글자만 남기고 마스킹
        for word in self.banned_words:
            if word in result and word not in self.replacements:
                masked = f"{word[0]}**"
                result = result.replace(word, masked)
                print(f"🔒 금칙어 마스킹: '{word}' → '{masked}'")
        
        return result
    
    def check_keyword_density(self, content: str, keyword: str, max_density: float = 0.03) -> Tuple[bool, float]:
        """
        키워드 밀도 검사 (과도한 반복 방지)
        
        Args:
            content: 검사할 콘텐츠
            keyword: 타겟 키워드
            max_density: 최대 허용 밀도 (기본 3%)
            
        Returns:
            Tuple[bool, float]: (통과 여부, 현재 밀도)
        """
        total_words = len(content.split())
        keyword_count = content.lower().count(keyword.lower())
        
        if total_words == 0:
            return True, 0.0
        
        density = keyword_count / total_words
        is_ok = density <= max_density
        
        if not is_ok:
            print(f"⚠️ 키워드 과다 반복! '{keyword}' 밀도: {density:.1%} (최대: {max_density:.1%})")
        
        return is_ok, density
    
    def reduce_keyword_density(self, content: str, keyword: str, target_count: int = 5) -> str:
        """
        키워드 반복 횟수 줄이기
        
        Args:
            content: 원본 콘텐츠
            keyword: 줄일 키워드
            target_count: 목표 반복 횟수
            
        Returns:
            str: 키워드 줄인 콘텐츠
        """
        current_count = content.lower().count(keyword.lower())
        
        if current_count <= target_count:
            return content
        
        # 키워드를 동의어나 대명사로 일부 대체
        synonyms = ["해당 제품", "이 서비스", "그것", "이것"]
        
        result = content
        reduce_count = current_count - target_count
        
        for _ in range(reduce_count):
            synonym = synonyms[_ % len(synonyms)]
            # 문장 중간의 키워드만 대체 (제목이나 첫 언급 유지)
            pattern = rf'(?<=[가-힣\s]){re.escape(keyword)}(?=[을를이가은는])'
            result = re.sub(pattern, synonym, result, count=1)
        
        print(f"📉 키워드 밀도 조정: {current_count}회 → {target_count}회")
        return result
    
    def get_content_score(self, content: str, keyword: str) -> dict:
        """
        콘텐츠 품질 점수 산출
        
        Args:
            content: 검사할 콘텐츠
            keyword: 타겟 키워드
            
        Returns:
            dict: 점수 상세
        """
        scores = {
            "total": 0,
            "details": {}
        }
        
        # 1. 금칙어 검사 (30점)
        is_safe, found = self.check_content(content)
        ban_score = 30 if is_safe else max(0, 30 - len(found) * 5)
        scores["details"]["금칙어"] = {"score": ban_score, "max": 30, "issues": found}
        
        # 2. 키워드 밀도 (20점)
        density_ok, density = self.check_keyword_density(content, keyword)
        density_score = 20 if density_ok else 10
        scores["details"]["키워드밀도"] = {"score": density_score, "max": 20, "density": f"{density:.1%}"}
        
        # 3. 글자 수 (20점)
        length = len(content)
        if length >= 1500:
            length_score = 20
        elif length >= 1000:
            length_score = 15
        else:
            length_score = 10
        scores["details"]["글자수"] = {"score": length_score, "max": 20, "length": length}
        
        # 4. 구조화 (15점) - 소제목, 목록 등
        has_headers = bool(re.search(r'^#+\s', content, re.MULTILINE))
        has_lists = bool(re.search(r'^[\-\*]\s', content, re.MULTILINE))
        has_qa = "Q." in content or "Q:" in content
        structure_score = sum([
            5 if has_headers else 0,
            5 if has_lists else 0,
            5 if has_qa else 0,
        ])
        scores["details"]["구조화"] = {"score": structure_score, "max": 15}
        
        # 5. 휴먼터치 (15점)
        human_phrases = ["저도", "제가", "개인적으로", "솔직히", "경험상"]
        has_human = any(phrase in content for phrase in human_phrases)
        has_emoji = bool(re.search(r'[\U0001F300-\U0001F9FF]', content))
        human_score = sum([
            10 if has_human else 0,
            5 if has_emoji else 0,
        ])
        scores["details"]["휴먼터치"] = {"score": human_score, "max": 15}
        
        # 총점
        scores["total"] = sum(d["score"] for d in scores["details"].values())
        
        return scores


# 테스트 코드
if __name__ == "__main__":
    filter = ContentFilter()
    
    test_content = """
# 복합기 렌탈 최저가 추천

안녕하세요! 오늘은 복합기 렌탈에 대해 알려드릴게요.
저도 처음엔 대출 받아서 구매할까 고민했는데, 렌탈이 훨씬 경제적이더라고요 😊

## Q. 렌탈 비용은?
A. 월 3만원대부터 시작해요!

업계 1위 서비스를 추천드립니다. 100% 만족 보장!
    """
    
    # 금칙어 검사
    is_safe, found = filter.check_content(test_content)
    print(f"금칙어 검사: {'통과' if is_safe else '실패'}")
    print(f"발견된 금칙어: {found}")
    
    # 필터링
    filtered = filter.filter_content(test_content)
    print("\n필터링 결과:")
    print(filtered)
    
    # 품질 점수
    scores = filter.get_content_score(test_content, "복합기 렌탈")
    print(f"\n품질 점수: {scores['total']}/100")
