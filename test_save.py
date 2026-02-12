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
# 👇 여기에 직접 아이디와 비밀번호를 적으세요!
NAVER_ID = "cky4736"     
NAVER_PW = "dyaio030429*"  
# ==========================================

def start_driver():
    options = Options()
    # "로봇 아님" 위장 설정
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    return driver

def clipboard_input(driver, xpath, text):
    try:
        elem = driver.find_element(By.XPATH, xpath)
        elem.click()
        pyperclip.copy(text)
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
    except:
        pass

def main():
    driver = start_driver()
    
    # 1. 로그인
    print("🚀 로봇: 로그인 하러 갑니다!")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    
    clipboard_input(driver, '//*[@id="id"]', NAVER_ID)
    clipboard_input(driver, '//*[@id="pw"]', NAVER_PW)
    
    try:
        driver.find_element(By.ID, "log.login").click()
    except:
        pass
        
    # ==========================================================
    # 🛑 [사용자 미션] 60초 동안 로그인을 완료해주세요!
    # ==========================================================
    print("\n" + "="*50)
    print("🛑 로봇: 60초 대기 중! '새로운 기기 등록'이나 '보안 문자'가 뜨면")
    print("👉 사용자님이 직접 마우스로 클릭해서 로그인을 끝내주세요!")
    print("👉 로그인이 완료되면 가만히 계세요.")
    print("="*50 + "\n")
    
    time.sleep(60) # 60초 대기

    # 2. 글쓰기 화면 이동
    print("📝 로봇: 글쓰기 화면으로 이동합니다...")
    driver.get(f"https://blog.naver.com/{NAVER_ID}?Redirect=Write")
    
    # 3. [중요] 확실하게 방(iframe) 안으로 들어가기
    print("👀 로봇: 글쓰기 방(mainFrame)을 찾는 중...")
    try:
        # 최대 20초까지 기다려서 'mainFrame'이 나오면 들어감
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        print("✅ 로봇: 방 안에 성공적으로 들어왔어요!")
    except Exception as e:
        print(f"❌ 로봇: 방에 못 들어갔어요... 오류: {e}")
        return # 방에 못 들어가면 여기서 종료

    # 팝업 닫기 (혹시 있으면)
    try:
        driver.find_element(By.CSS_SELECTOR, ".se-popup-button-cancel").click()
        time.sleep(1)
    except:
        pass

    # 4. 제목 입력
    print("✍️ 로봇: 제목 입력 시도...")
    try:
        # 제목 칸이 보일 때까지 10초 기다림
        title_area = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "se-document-title"))
        )
        title_area.click()
        pyperclip.copy("자동화 테스트: 성공적으로 작성된 제목입니다!")
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(1)
        print("✅ 제목 입력 완료")
    except Exception as e:
        print(f"❌ 제목 입력 실패: {e}")

    # 5. 본문 입력
    print("✍️ 로봇: 본문 입력 시도...")
    try:
        content_area = driver.find_element(By.CLASS_NAME, "se-main-container")
        content_area.click()
        pyperclip.copy("안녕하세요! 이 글은 로봇이 자동으로 쓴 글입니다. 임시저장 테스트 성공!")
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        time.sleep(2)
        print("✅ 본문 입력 완료")
    except Exception as e:
        print(f"❌ 본문 입력 실패: {e}")

    # 6. 임시저장 버튼 클릭
    print("💾 로봇: 저장 버튼을 찾습니다...")
    try:
        save_btn = driver.find_element(By.CLASS_NAME, "se-tool-save-btn-save")
        save_btn.click()
        print("🎉 대성공! 임시저장 버튼을 눌렀습니다!")
    except:
        print("❌ 저장 버튼을 못 찾겠어요.")

    print("\n테스트가 끝났습니다. 브라우저를 확인해보세요!")
    input("종료하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main()