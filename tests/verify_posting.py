import sys
import os
import time

# 프로젝트 루트 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.posting.naver_bot import NaverBlogBot
from config.settings import NaverConfig

def test_draft_saving():
    print("🚀 임시저장 기능 테스트 시작...")
    
    # 설정값이 없으면 수동 로그인 유도
    naver_id = NaverConfig.ID or ""
    naver_pw = NaverConfig.PASSWORD or ""

    if not naver_id:
        print("ℹ️ 설정된 네이버 아이디가 없습니다. 브라우저가 열리면 직접 로그인해주세요.")

    try:
        bot = NaverBlogBot(naver_id=naver_id, naver_pw=naver_pw)
        
        print("1️⃣ 로그인 시도...")
        # 정보가 있으면 자동 로그인 시도, 없으면 그냥 브라우저 띄우기
        if naver_id and naver_pw:
            if not bot.login():
                print("⚠️ 자동 로그인 실패. 직접 로그인해주세요.")
                bot.driver.get("https://nid.naver.com/nidlogin.login")
        else:
            # 드라이버 초기화 및 로그인 페이지 이동
            bot._init_driver()
            bot.driver.get("https://nid.naver.com/nidlogin.login")
            print("🔐 네이버 로그인 페이지로 이동했습니다.")

        print("⏳ 로그인 대기 중... (60초)")
        # 사용자가 로그인할 시간을 줌
        time.sleep(60)
        
        # 로그인 여부 확인 (URL 변경 등)
        try:
            if "nid.naver.com" not in bot.driver.current_url:
                bot.is_logged_in = True
                print("✅ 로그인 감지됨!")
            else:
                print("⚠️ 아직 로그인 페이지인 것 같습니다. 계속 진행합니다.")
        except:
            print("⚠️ 브라우저 확인 중 오류. 닫혔을 수도 있습니다.")

        print("2️⃣ 글 작성 및 임시저장 시도...")
        title = f"자동화 테스트 글 {int(time.time())}"
        content = "이 글은 자동화 테스트에 의해 작성되었습니다.\\n임시저장 기능 확인 중입니다."
        
        success = bot.write_post(
            title=title,
            content=content,
            tags=["테스트", "자동화"],
            mode='draft'
        )
        
        if success:
            print("✅ 테스트 성공! 임시저장함 확인 부탁드립니다.")
        else:
            print("❌ 테스트 실패.")
            
        time.sleep(5)
        bot.close()
        
    except Exception as e:
        print(f"❌ 치명적 오류 발생: {e}")

if __name__ == "__main__":
    test_draft_saving()
