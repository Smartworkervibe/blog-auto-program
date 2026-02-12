# 🐟 블로그 자동화 프로그램 v1.0

> **Made by 코다리 부장** | Connect AI LAB 제이님 프롬프트 기반

AI 검열을 피하고, 사람이 쓴 것처럼 자연스러운 블로그 글을 자동으로 생성하고 포스팅하는 프로그램입니다!

---

## ✨ 주요 기능

### 1️⃣ AI 글 생성
- OpenAI GPT-4o / Google Gemini 지원
- 휴먼터치 자동 적용 (1인칭 서술, 경험담, 이모지)
- DB화 원고 구조 (요약박스, Q&A, 스펙표)

### 2️⃣ AI 검열 회피
- 금칙어 자동 필터링 및 대체
- 키워드 밀도 조절 (과도 반복 방지)
- 품질 점수 자동 산출

### 3️⃣ 렌탈 업체 특화
- 사무기기/복합기 전용 템플릿
- 지역 + 제품 키워드 자동 조합
- Q&A, 비교표, 체크리스트 자동 생성

### 4️⃣ 네이버 블로그 자동 포스팅
- Selenium 기반 자동화
- 랜덤 딜레이 (봇 감지 회피)
- 예약 발행 지원

---

## 🚀 설치 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
```bash
# .env.example을 복사해서 .env 파일 생성
copy .env.example .env

# .env 파일을 열어서 실제 API 키와 계정 정보 입력
```

### 3. 필수 API 키 발급
- **OpenAI API**: https://platform.openai.com/api-keys
- **Google Gemini**: https://aistudio.google.com/apikey
- **네이버 검색 API**: https://developers.naver.com/

---

## 📖 사용법

### 기본 글 생성
```bash
python src/main.py generate --topic "복합기 선택 가이드" --keyword "복합기 추천" --humanize
```

### 렌탈 전용 글 생성
```bash
# AI 생성
python src/main.py rental --product "복합기" --region "강남"

# 템플릿 사용
python src/main.py rental --product "복합기" --region "강남" --template
```

### 키워드 분석
```bash
python src/main.py analyze "복합기 렌탈" --related --longtail
```

### 자동 포스팅
```bash
python src/main.py post --topic "복합기 렌탈 가이드" --keyword "강남 복합기 렌탈"
```

---

## 📁 프로젝트 구조

```
블로그자동화 프로그램/
├── 📁 config/
│   ├── settings.py      # 설정
│   └── prompts.py       # AI 프롬프트
│
├── 📁 src/
│   ├── 📁 content/      # 콘텐츠 생성
│   │   ├── generator.py # AI 글 생성기
│   │   ├── humanizer.py # 휴먼터치 처리기
│   │   ├── filter.py    # 금칙어 필터
│   │   └── templates/   # 템플릿
│   │
│   ├── 📁 keyword/      # 키워드 분석
│   │   └── analyzer.py  # 키워드 분석기
│   │
│   ├── 📁 posting/      # 포스팅
│   │   └── naver_bot.py # 네이버 봇
│   │
│   └── main.py          # 메인 실행
│
├── .env.example         # 환경변수 예시
├── requirements.txt     # 의존성
└── README.md           # 사용 설명서
```

---

## ⚠️ 주의사항

1. **일일 발행량 제한**: 하루 3~5개 권장 (과도한 발행은 저품질 위험)
2. **계정 보안**: .env 파일은 절대 공유하지 마세요!
3. **네이버 정책**: 자동화 도구 사용에 따른 책임은 사용자에게 있습니다.

---

## 🐟 문의

이 프로그램은 **Connect AI LAB 제이**님의 프롬프트를 기반으로 **코다리 부장**이 제작했습니다.

---

**충성! 대표님의 블로그 자동화를 책임지겠습니다!** 🫡🚀
