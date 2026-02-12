from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyperclip  # 클립보드 복사 모듈
import time
import random

# ==========================================
# 1. 사용자 정보 입력 (여기에 아이디/비번 입력)
# ==========================================
NAVER_ID = "cky4736"
NAVER_PW = "Dyaio218341@" 
# ==========================================

def start_stealth_driver():
    options = Options()
    
    # [핵심 1] 자동화 표시 제거 (네이버가 봇으로 인식 못하게 함)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # [핵심 2] 사용자 에이전트 위장 (일반 크롬 브라우저인 척)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 창 크기 설정
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    
    # [핵심 3] 자바스크립트 탐지 우회
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def naver_login(driver):
    print("🚀 네이버 로그인 시도 중...")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(random.uniform(2, 3)) # 로딩 대기

    # [핵심 4] 아이디 복사 붙여넣기 (키보드 타이핑 감지 우회)
    elem_id = driver.find_element(By.ID, 'id')
    elem_id.click()
    pyperclip.copy(NAVER_ID)
    elem_id.send_keys(Keys.CONTROL, 'v')
    time.sleep(random.uniform(1, 2))

    # [핵심 5] 비밀번호 복사 붙여넣기
    elem_pw = driver.find_element(By.ID, 'pw')
    elem_pw.click()
    pyperclip.copy(NAVER_PW)
    elem_pw.send_keys(Keys.CONTROL, 'v')
    time.sleep(random.uniform(1, 2))

    # 로그인 버튼 클릭
    driver.find_element(By.ID, "log.login").click()
    
    print("✅ 로그인 버튼 클릭 완료! 캡차 여부 확인 중...")
    time.sleep(5) # 로그인 완료 대기

# 실행
if __name__ == "__main__":
    print("🧩 모듈 로딩 테스트 시작...")
    try:
        from src.content.image_manager import ImageManager
        print("✅ ImageManager 모듈 로드 성공")
    except Exception as e:
        print(f"❌ ImageManager 로드 실패: {e}")

    try:
        from src.posting.neighbor_manager import NeighborManager
        print("✅ NeighborManager 모듈 로드 성공")
    except Exception as e:
        print(f"❌ NeighborManager 로드 실패: {e}")

    print("\n🚀 네이버 로그인 테스트 시작...")
    driver = start_stealth_driver()
    try:
        naver_login(driver)
        print("🎉 브라우저가 열려있습니다. 로그인이 성공했는지 확인하세요.")
        input("종료하려면 엔터키를 누르세요...")
    except Exception as e:
        print(f"❌ 로그인 테스트 실패: {e}")
    finally:
        driver.quit()