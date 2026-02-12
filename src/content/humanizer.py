"""
🐟 휴먼터치 처리기
AI가 쓴 티를 없애는 마법의 모듈입니다!
"""

import re
import random


class Humanizer:
    """AI 글을 자연스럽게 변환하는 휴먼터치 처리기"""
    
    def __init__(self):
        # 자연스러운 표현 변환 사전
        self.replacements = {
            # 딱딱한 표현 → 친근한 표현
            "~입니다.": ["~해요.", "~거든요.", "~죠.", "~답니다."],
            "~습니다.": ["~어요.", "~네요.", "~더라고요."],
            "것입니다": ["거예요", "건데요", "거랍니다"],
            "드립니다": ["드릴게요", "드려요"],
            "됩니다": ["돼요", "되더라고요", "되거든요"],
            
            # 기계적 표현 → 일상적 표현
            "첫째로": ["먼저", "우선"],
            "둘째로": ["그리고", "또"],
            "셋째로": ["마지막으로", "그리고 또"],
            "따라서": ["그래서", "그러니까"],
            "그러므로": ["그래서", "그러니"],
            "예를 들어": ["예를 들면", "가령"],
            "결론적으로": ["정리하면", "요약하면"],
            
            # 과도하게 공손한 표현 완화
            "권장드립니다": ["추천해요", "좋아요"],
            "추천드립니다": ["추천해요", "강추!"],
            "알려드립니다": ["알려드릴게요", "말씀드릴게요"],
        }
        
        # 1인칭 경험담 표현
        self.experience_phrases = [
            "제가 직접 써보니",
            "개인적으로 느끼기에",
            "저도 처음엔 고민했는데",
            "솔직히 말하면",
            "제 경험상",
            "직접 테스트해보니까",
            "몇 달 사용해본 결과",
        ]
        
        # 자연스러운 연결어
        self.connectors = [
            "그런데요,",
            "근데",
            "아,",
            "참고로",
            "솔직히",
            "사실",
            "진짜로",
        ]
        
        # 이모지 목록
        self.emojis = {
            "positive": ["😊", "👍", "✨", "🙌", "💯", "🎉", "❤️"],
            "thinking": ["🤔", "💭", "🧐"],
            "warning": ["⚠️", "❗", "📢"],
            "tips": ["💡", "✅", "📌", "🔥"],
            "question": ["❓", "🙋", "🤷"],
        }
    
    def humanize(self, content: str) -> str:
        """
        AI 글을 자연스럽게 변환
        
        Args:
            content: 원본 글
            
        Returns:
            str: 자연스럽게 변환된 글
        """
        result = content
        
        # 1. 표현 변환
        result = self._replace_formal_expressions(result)
        
        # 2. 경험담 표현 추가
        result = self._add_experience_phrases(result)
        
        # 3. 이모지 추가
        result = self._add_emojis(result)
        
        # 4. 문장 다양화
        result = self._diversify_sentences(result)
        
        return result
    
    def _replace_formal_expressions(self, content: str) -> str:
        """딱딱한 표현을 친근하게 변환"""
        result = content
        
        for formal, informal_list in self.replacements.items():
            if formal in result:
                # 모든 것을 바꾸지 않고 일부만 랜덤하게 변환
                count = result.count(formal)
                replace_count = max(1, count // 2)  # 절반 정도만 변환
                
                for _ in range(replace_count):
                    informal = random.choice(informal_list)
                    result = result.replace(formal, informal, 1)
        
        return result
    
    def _add_experience_phrases(self, content: str) -> str:
        """1인칭 경험담 표현 추가"""
        paragraphs = content.split("\n\n")
        
        # 2-3번째 문단에 경험담 추가
        for i in [1, 2]:
            if i < len(paragraphs) and len(paragraphs[i]) > 50:
                if not any(phrase in paragraphs[i] for phrase in self.experience_phrases):
                    phrase = random.choice(self.experience_phrases)
                    # 문단 시작 부분에 추가
                    paragraphs[i] = f"{phrase} {paragraphs[i]}"
        
        return "\n\n".join(paragraphs)
    
    def _add_emojis(self, content: str) -> str:
        """적절한 위치에 이모지 추가"""
        lines = content.split("\n")
        result_lines = []
        
        emoji_count = 0
        max_emojis = 5  # 글 전체에 최대 5개
        
        for line in lines:
            # 제목이나 소제목에 이모지 추가
            if line.startswith("#") and emoji_count < max_emojis:
                if "추천" in line or "좋은" in line:
                    emoji = random.choice(self.emojis["positive"])
                elif "주의" in line or "주요" in line:
                    emoji = random.choice(self.emojis["warning"])
                elif "팁" in line or "방법" in line:
                    emoji = random.choice(self.emojis["tips"])
                else:
                    emoji = random.choice(self.emojis["tips"])
                
                line = f"{line} {emoji}"
                emoji_count += 1
            
            result_lines.append(line)
        
        return "\n".join(result_lines)
    
    def _diversify_sentences(self, content: str) -> str:
        """문장 구조 다양화"""
        # "~입니다" 연속 사용 방지
        result = content
        
        # 연속되는 동일 어미 패턴 찾기
        patterns = [
            (r'(\.\s)입니다\.\s입니다\.', r'\1예요. 거든요.'),
            (r'(\.\s)합니다\.\s합니다\.', r'\1해요. 하거든요.'),
        ]
        
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def add_personal_touch(self, content: str, topic: str) -> str:
        """
        개인적인 터치 추가
        
        Args:
            content: 원본 글
            topic: 글 주제
            
        Returns:
            str: 개인적 터치가 추가된 글
        """
        # 도입부에 개인 경험 추가
        intro = random.choice([
            f"오늘은 {topic}에 대해 이야기해볼까 해요. 저도 예전에 이거 때문에 고민 많이 했거든요 😅",
            f"안녕하세요! 오늘 {topic} 관련해서 제가 직접 경험한 것들 공유해드릴게요 ✨",
            f"여러분도 {topic} 고민 중이시죠? 저도 그랬어요. 오늘 확실하게 정리해드릴게요! 💪",
        ])
        
        # 마무리에 친근한 인사 추가
        outro = random.choice([
            "\n\n도움이 되셨다면 댓글이나 공감 부탁드려요! 궁금한 점 있으시면 편하게 물어보세요 😊",
            "\n\n오늘도 읽어주셔서 감사해요! 다음에 더 좋은 정보로 돌아올게요 ✨",
            "\n\n저장해두시면 나중에 유용하게 쓰실 수 있을 거예요! 다른 궁금한 점 있으시면 댓글 남겨주세요 💬",
        ])
        
        return f"{intro}\n\n{content}{outro}"


# 테스트 코드
if __name__ == "__main__":
    humanizer = Humanizer()
    
    # 테스트 텍스트
    test_content = """
# 복합기 렌탈 추천

복합기를 선택하실 때 고려해야 할 점을 알려드립니다. 
첫째로 인쇄 속도를 확인하셔야 합니다.
둘째로 월 렌탈료를 비교하셔야 합니다.
따라서 여러 업체를 비교하시는 것을 권장드립니다.

결론적으로 복합기 렌탈은 구매보다 경제적입니다.
    """
    
    result = humanizer.humanize(test_content)
    result = humanizer.add_personal_touch(result, "복합기 렌탈")
    
    print("=" * 50)
    print("🔄 변환 결과:")
    print(result)
