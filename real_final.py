from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip
import time

# ==========================================
# 👇 아이디와 비밀번호를 꼭 수정해주세요!
NAVER_ID = "cky4736"
NAVER_PW = "dyaio030429*" 
# ==========================================

def start_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    driver = start_driver()
    
    # 1. 로그인
    print("🚀 로봇: 로그인 시작!")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    
    try:
        elem_id = driver.find_element(By.ID, "id")
        elem_id.click()
        pyperclip.copy(NAVER_ID)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)

        elem_pw = driver.find_element(By.ID, "pw")
        elem_pw.click()
        pyperclip.copy(NAVER_PW)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        
        driver.find_element(By.ID, "log.login").click()
    except:
        pass
        
    print("\n" + "="*50)
    print("🛑 [사용자 미션] 60초 대기! '등록안함'이나 '보안문자'를 직접 해결해주세요!")
    print("👉 로그인이 완전히 끝나고 메인 화면이 나올 때까지 기다려주세요.")
    print("="*50 + "\n")
    time.sleep(60) 

    # 2. 글쓰기 화면 이동
    print("📝 로봇: 글쓰기 화면으로 이동...")
    driver.get(f"https://blog.naver.com/{NAVER_ID}?Redirect=Write")
    
    # 3. iframe 진입 (가장 중요)
    print("👀 로봇: 방(mainFrame) 찾는 중...")
    try:
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        print("✅ 로봇: 방 진입 성공!")
    except Exception as e:
        print(f"❌ 방 진입 실패: {e}")
        return

    # 4. 팝업 닫기 (ESC 연타)
    time.sleep(5)
    print("🧹 로봇: 팝업 청소 중...")
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    
    # 5. 제목 입력 (TAB 키로 강제 이동)
    print("✍️ 로봇: 제목 작성 시도...")
    try:
        # 제목 칸을 클릭하지 못해도, 탭 키로 이동해서 작성하는 전략
        # 1. 본문 영역(body) 클릭해서 포커스 잡기
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)
        
        # 2. 제목일 가능성이 높은 요소들 클릭 시도
        try:
            driver.find_element(By.CLASS_NAME, "se-document-title").click()
        except:
            pass

        time.sleep(1)
        pyperclip.copy("자동화 테스트: 드디어 제목이 입력되었습니다!")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 제목 입력 동작 완료")
    except Exception as e:
        print(f"❌ 제목 입력 실패: {e}")

    # 6. 본문 입력 (TAB 키로 이동)
    print("✍️ 로봇: 본문으로 이동...")
    try:
        # 제목에서 탭 키를 누르면 본문으로 넘어감
        actions.send_keys(Keys.TAB).perform()
        time.sleep(1)
        pyperclip.copy("성공입니다! \n이제 제목과 본문이 모두 정상적으로 입력됩니다.")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 본문 입력 동작 완료")
    except Exception as e:
        print(f"❌ 본문 입력 실패: {e}")

    # 7. 임시저장 (단축키 Ctrl+S 사용)
    print("💾 로봇: 저장 시도 (단축키)...")
    try:
        actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
        print("✅ 저장 신호 전송 완료!")
    except:
        print("❌ 저장 실패")

    print("\n🎉 모든 작업 종료! 화면에 글이 써졌는지 확인하세요.")
    input("종료하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main()