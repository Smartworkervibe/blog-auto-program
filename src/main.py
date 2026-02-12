"""
🐟 블로그 자동화 프로그램 - 메인 실행 파일
코다리 부장이 만든 통합 자동화 시스템입니다!

사용법:
    python main.py --help              # 도움말
    python main.py generate            # 글 생성
    python main.py post                # 작성 + 포스팅
    python main.py analyze <키워드>     # 키워드 분석
    python main.py rental              # 렌탈 전용 글 생성
"""

import argparse
import sys
import os

# 프로젝트 루트 경로 설정 (src 폴더의 상위 폴더)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from config.settings import (
    APIConfig, NaverConfig, ContentConfig, 
    SafetyConfig, RentalConfig
)


def check_config():
    """설정 확인"""
    print("🔍 설정 확인 중...")
    
    issues = []
    
    # API 키 확인
    if not APIConfig.OPENAI_API_KEY and not APIConfig.GEMINI_API_KEY:
        issues.append("⚠️ AI API 키가 설정되지 않았습니다. (.env 파일 확인)")
    
    # 네이버 계정 확인
    if not NaverConfig.ID or not NaverConfig.PASSWORD:
        issues.append("⚠️ 네이버 계정 정보가 설정되지 않았습니다. (.env 파일 확인)")
    
    if issues:
        print("\n".join(issues))
        print("\n💡 .env.example 파일을 참고해서 .env 파일을 생성해주세요!")
        return False
    
    print("✅ 설정 확인 완료!")
    return True


def cmd_generate(args):
    """글 생성 명령"""
    from src.content.generator import ContentGenerator
    from src.content.humanizer import Humanizer
    from src.content.filter import ContentFilter
    
    print(f"\n🐟 글 생성 시작!")
    print(f"📌 주제: {args.topic}")
    print(f"📌 키워드: {args.keyword}")
    
    # 1. AI 글 생성
    generator = ContentGenerator()
    result = generator.generate_blog_post(
        topic=args.topic,
        keyword=args.keyword,
        persona=args.persona
    )
    
    if not result["content"]:
        print("❌ 글 생성 실패!")
        return
    
    # 2. 휴먼터치 적용
    if args.humanize:
        humanizer = Humanizer()
        result["content"] = humanizer.humanize(result["content"])
        result["content"] = humanizer.add_personal_touch(result["content"], args.topic)
    
    # 3. 금칙어 필터링
    filter = ContentFilter()
    result["content"] = filter.filter_content(result["content"])
    
    # 4. 품질 점수
    scores = filter.get_content_score(result["content"], args.keyword)
    
    # 결과 출력
    print("\n" + "="*60)
    print(f"📌 제목: {result['title']}")
    print(f"🏷️ 태그: {', '.join(result['tags'])}")
    print(f"📊 품질 점수: {scores['total']}/100")
    print("="*60)
    print(result["content"][:1000] + "...")
    
    # 파일로 저장
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"# {result['title']}\n\n")
            f.write(result["content"])
        print(f"\n💾 파일 저장: {args.output}")


def cmd_rental(args):
    """렌탈 전용 글 생성"""
    from src.content.generator import ContentGenerator
    from src.content.templates.rental import RentalTemplate
    from src.content.filter import ContentFilter
    
    print(f"\n🏢 렌탈 글 생성 시작!")
    print(f"📌 제품: {args.product}")
    print(f"📌 지역: {args.region}")
    
    # 1. 렌탈 템플릿 기반 글 생성
    if args.template:
        # 템플릿 사용
        content = RentalTemplate.get_full_template(
            product=args.product,
            region=args.region,
            company_name=RentalConfig.COMPANY_NAME,
            contact=RentalConfig.CONTACT_NUMBER
        )
        title = f"{args.region} {args.product} 렌탈 비용 & 추천 업체 완벽 가이드"
        tags = [f"{args.region}{args.product}렌탈", f"{args.product}렌탈", args.region]
    else:
        # AI 생성
        generator = ContentGenerator()
        result = generator.generate_rental_post(
            product=args.product,
            region=args.region
        )
        content = result["content"]
        title = result["title"]
        tags = result["tags"]
    
    # 2. 금칙어 필터링
    filter = ContentFilter()
    content = filter.filter_content(content)
    scores = filter.get_content_score(content, f"{args.region} {args.product} 렌탈")
    
    # 결과 출력
    print("\n" + "="*60)
    print(f"📌 제목: {title}")
    print(f"🏷️ 태그: {', '.join(tags)}")
    print(f"📊 품질 점수: {scores['total']}/100")
    print("="*60)
    print(content[:1500] + "...")
    
    # 파일로 저장
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(content)
        print(f"\n💾 파일 저장: {args.output}")


def cmd_analyze(args):
    """키워드 분석"""
    from src.keyword.analyzer import KeywordAnalyzer
    
    print(f"\n🔍 키워드 분석: {args.keyword}")
    
    analyzer = KeywordAnalyzer()
    
    # 경쟁 분석
    competition = analyzer.analyze_competition(args.keyword)
    print(f"\n📊 경쟁 분석:")
    print(f"  - 블로그 문서 수: {competition['blog_count']:,}개")
    print(f"  - 경쟁 강도: {competition['competition_level']}")
    print(f"  - 💡 추천: {competition['recommendation']}")
    
    # 연관 키워드
    if args.related:
        related = analyzer.get_related_keywords(args.keyword)
        print(f"\n🔗 연관 키워드: {', '.join(related[:10])}")
    
    # 롱테일 키워드
    if args.longtail:
        longtails = analyzer.generate_longtail_keywords(args.keyword)
        print(f"\n📝 롱테일 키워드:")
        for kw in longtails[:10]:
            print(f"  - {kw}")


def cmd_post(args):
    """글 작성 + 포스팅"""
    from src.content.generator import ContentGenerator
    from src.content.humanizer import Humanizer
    from src.content.filter import ContentFilter
    from src.posting.naver_bot import NaverBlogBot
    
    print(f"\n🚀 자동 포스팅 시작!")
    
    # 1. 글 생성
    print("\n1️⃣ 글 생성 중...")
    generator = ContentGenerator()
    result = generator.generate_blog_post(
        topic=args.topic,
        keyword=args.keyword
    )
    
    if not result["content"]:
        print("❌ 글 생성 실패!")
        return
    
    # 2. 휴먼터치
    print("\n2️⃣ 휴먼터치 적용 중...")
    humanizer = Humanizer()
    result["content"] = humanizer.humanize(result["content"])
    
    # 3. 필터링
    print("\n3️⃣ 금칙어 필터링 중...")
    filter = ContentFilter()
    result["content"] = filter.filter_content(result["content"])
    
    # 4. 포스팅
    print("\n4️⃣ 네이버 블로그 포스팅 중...")
    bot = NaverBlogBot()
    
    try:
        success = bot.write_post(
            title=result["title"],
            content=result["content"],
            tags=result["tags"]
        )
        
        if success:
            print("\n✅ 포스팅 성공!")
        else:
            print("\n❌ 포스팅 실패!")
    finally:
        bot.close()


def main():
    parser = argparse.ArgumentParser(
        description="🐟 블로그 자동화 프로그램 - 코다리 부장",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="명령어")
    
    # generate 명령
    gen_parser = subparsers.add_parser("generate", help="블로그 글 생성")
    gen_parser.add_argument("--topic", "-t", required=True, help="글 주제")
    gen_parser.add_argument("--keyword", "-k", required=True, help="타겟 키워드")
    gen_parser.add_argument("--persona", "-p", default="lifestyle_blogger",
                           choices=["rental_expert", "lifestyle_blogger", "tech_reviewer"],
                           help="글쓰기 페르소나")
    gen_parser.add_argument("--humanize", "-H", action="store_true", help="휴먼터치 적용")
    gen_parser.add_argument("--output", "-o", help="출력 파일 경로")
    
    # rental 명령
    rental_parser = subparsers.add_parser("rental", help="렌탈 전용 글 생성")
    rental_parser.add_argument("--product", "-p", default="복합기", help="제품명")
    rental_parser.add_argument("--region", "-r", default="서울", help="타겟 지역")
    rental_parser.add_argument("--template", "-T", action="store_true", help="템플릿 사용")
    rental_parser.add_argument("--output", "-o", help="출력 파일 경로")
    
    # analyze 명령
    analyze_parser = subparsers.add_parser("analyze", help="키워드 분석")
    analyze_parser.add_argument("keyword", help="분석할 키워드")
    analyze_parser.add_argument("--related", "-r", action="store_true", help="연관 키워드 표시")
    analyze_parser.add_argument("--longtail", "-l", action="store_true", help="롱테일 키워드 표시")
    
    # post 명령
    post_parser = subparsers.add_parser("post", help="글 생성 + 포스팅")
    post_parser.add_argument("--topic", "-t", required=True, help="글 주제")
    post_parser.add_argument("--keyword", "-k", required=True, help="타겟 키워드")
    
    args = parser.parse_args()
    
    # 헤더 출력
    print("""
╔══════════════════════════════════════════════════════════╗
║  🐟 블로그 자동화 프로그램 v1.0                           ║
║  Made by 코다리 부장 | Connect AI LAB                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    if not args.command:
        parser.print_help()
        return
    
    # 설정 확인
    if not check_config() and args.command in ["generate", "post", "rental"]:
        return
    
    # 명령 실행
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "rental":
        cmd_rental(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "post":
        cmd_post(args)


if __name__ == "__main__":
    main()
