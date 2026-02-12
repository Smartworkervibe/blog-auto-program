"""
🐟 렌탈 업체 전용 템플릿
사무기기 렌탈 블로그 글에 특화된 템플릿입니다!
"""


class RentalTemplate:
    """렌탈 업체 전용 블로그 템플릿"""
    
    @staticmethod
    def get_spec_table(product: str, specs: dict) -> str:
        """
        제품 스펙 테이블 생성
        
        Args:
            product: 제품명
            specs: 스펙 딕셔너리
            
        Returns:
            str: 마크다운 테이블
        """
        default_specs = {
            "월 렌탈료": "3만원대~",
            "설치비": "무료",
            "A/S": "무상 출장 수리",
            "약정": "12개월 / 24개월 / 36개월",
        }
        
        merged = {**default_specs, **specs}
        
        table = f"""
📋 **[{product} 렌탈 핵심 정보]**
"""
        for key, value in merged.items():
            table += f"• **{key}:** {value}\n"
        
        return table
    
    @staticmethod
    def get_qa_section(product: str, custom_qa: list = None) -> str:
        """
        Q&A 섹션 생성
        
        Args:
            product: 제품명
            custom_qa: 커스텀 Q&A 리스트 [{"q": "질문", "a": "답변"}, ...]
            
        Returns:
            str: Q&A 섹션
        """
        default_qa = [
            {
                "q": f"{product} 렌탈 비용은 얼마인가요?",
                "a": "월 3만원대부터 시작하며, 기종과 약정 기간에 따라 달라집니다."
            },
            {
                "q": "당일 설치가 가능한가요?",
                "a": "네, 오전 문의 시 당일 설치 가능합니다. (지역에 따라 다를 수 있음)"
            },
            {
                "q": "중도 해지 시 위약금이 있나요?",
                "a": "잔여 약정 기간에 따라 위약금이 발생할 수 있습니다. 자세한 사항은 상담 시 안내드려요."
            },
            {
                "q": "토너/잉크 교체는 어떻게 하나요?",
                "a": "무상 교체 서비스가 포함되어 있습니다. 전화 한 통이면 배송해드려요!"
            },
            {
                "q": "고장 시 A/S는 어떻게 받나요?",
                "a": "무상 출장 수리 서비스가 기본 포함입니다. 보통 1~2일 내 방문합니다."
            },
        ]
        
        qa_list = custom_qa if custom_qa else default_qa
        
        section = """
## ❓ 자주 묻는 질문 (FAQ)

"""
        for item in qa_list:
            section += f"""**Q. {item['q']}**
> A. {item['a']}

"""
        
        return section
    
    @staticmethod
    def get_comparison_table(products: list) -> str:
        """
        제품 비교 테이블 생성
        
        Args:
            products: 제품 리스트 [{"name": "제품명", "price": "가격", "speed": "속도", ...}, ...]
            
        Returns:
            str: 비교 테이블
        """
        if not products:
            products = [
                {"name": "캐논 C3525", "price": "4만원대", "speed": "분당 25매", "recommend": "중소기업"},
                {"name": "삼성 SL-X4300", "price": "5만원대", "speed": "분당 30매", "recommend": "디자인 업체"},
                {"name": "HP LaserJet", "price": "3만원대", "speed": "분당 20매", "recommend": "소규모 사무실"},
            ]
        
        table = """
## 📊 제품별 비교표

| 모델명 | 월 렌탈료 | 인쇄 속도 | 추천 대상 |
|--------|----------|----------|----------|
"""
        for p in products:
            table += f"| {p['name']} | {p['price']} | {p['speed']} | {p['recommend']} |\n"
        
        return table
    
    @staticmethod
    def get_checklist() -> str:
        """렌탈 체크리스트 (저장 유도 콘텐츠)"""
        return """
## ✅ 복합기 렌탈 체크리스트 (저장해두세요!)

렌탈 계약 전 꼭 확인해야 할 사항들이에요:

- [ ] 월 렌탈료 및 포함 매수 확인
- [ ] 초과 인쇄 비용 (매당 단가)
- [ ] 약정 기간 및 중도 해지 조건
- [ ] 설치비 무료 여부
- [ ] 토너/잉크 무상 제공 여부
- [ ] A/S 범위 및 출장 비용
- [ ] 컬러/흑백 인쇄 비율
- [ ] 스캔, 팩스 기능 필요 여부

💡 **꿀팁:** 2~3곳 견적을 비교해보시면 최적의 조건을 찾을 수 있어요!
"""
    
    @staticmethod
    def get_region_info(region: str, company_name: str, contact: str) -> str:
        """
        지역 맞춤 정보 섹션
        
        Args:
            region: 지역명
            company_name: 회사명
            contact: 연락처
            
        Returns:
            str: 지역 정보 섹션
        """
        return f"""
## 📍 {region} 지역 렌탈 서비스

**{company_name}**은 {region} 전 지역에 서비스를 제공하고 있습니다!

✅ **서비스 지역:** {region} 전체 (인근 지역 상담 가능)
✅ **당일 설치:** 오전 문의 시 당일 방문 설치 가능
✅ **긴급 A/S:** 평일 기준 1~2일 내 출장 수리
✅ **무료 상담:** {contact}

[이미지: {region} 사무실 복합기 설치 현장 사진]
"""
    
    @staticmethod
    def get_full_template(
        product: str,
        region: str,
        company_name: str,
        contact: str,
        specs: dict = None,
        custom_qa: list = None
    ) -> str:
        """
        전체 렌탈 블로그 글 템플릿
        
        Args:
            product: 제품명
            region: 지역명
            company_name: 회사명
            contact: 연락처
            specs: 제품 스펙
            custom_qa: 커스텀 Q&A
            
        Returns:
            str: 완성된 블로그 글 템플릿
        """
        template = f"""# {region} {product} 렌탈 비용 & 추천 업체 완벽 가이드 📋

안녕하세요! 오늘은 **{region}**에서 **{product} 렌탈**을 고민하시는 분들을 위해 꼭 알아야 할 정보들을 정리해봤어요 😊

저도 사무실 차릴 때 복합기 구매할지 렌탈할지 진짜 고민 많이 했거든요. 결론부터 말씀드리면, **렌탈이 훨씬 경제적**이었어요!

왜 그런지, 어떤 업체가 좋은지 하나씩 알려드릴게요 👇

---

{RentalTemplate.get_spec_table(product, specs or {})}

---

## 💰 렌탈 vs 구매, 뭐가 더 이득일까? 🤔

솔직히 저도 처음엔 "그냥 사는 게 낫지 않나?" 생각했어요.
근데 계산해보니까...

| 구분 | 구매 | 렌탈 |
|------|------|------|
| 초기 비용 | 200~500만원 | 0원 |
| 월 유지비 | 토너, A/S 별도 | 올인원 포함 |
| 고장 시 | 자비 수리 | 무상 출장 |
| 업그레이드 | 새로 구매 | 계약 갱신 시 교체 |

**결론:** 3년 TCO(총소유비용) 기준으로 렌탈이 30~40% 절감! 💸

---

{RentalTemplate.get_qa_section(product, custom_qa)}

---

{RentalTemplate.get_comparison_table(None)}

---

{RentalTemplate.get_region_info(region, company_name, contact)}

---

{RentalTemplate.get_checklist()}

---

## 마무리 ✨

{region}에서 {product} 렌탈 고민 중이시라면, 제가 정리한 정보가 도움이 되셨으면 좋겠어요!

궁금한 점 있으시면 댓글로 편하게 물어봐 주세요 😊
도움이 되셨다면 **저장**이나 **공감** 부탁드려요! 

다음에 더 유용한 정보로 돌아올게요~! 👋
"""
        return template


# 테스트 코드
if __name__ == "__main__":
    template = RentalTemplate.get_full_template(
        product="복합기",
        region="강남",
        company_name="테스트렌탈",
        contact="1588-0000"
    )
    
    print(template)
