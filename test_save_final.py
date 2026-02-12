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
# 👇 아이디와 비밀번호를 '따옴표' 안에 적어주세요!
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
    
    # 3. iframe 진입
    print("👀 로봇: 방(mainFrame) 찾는 중...")
    try:
        WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        print("✅ 로봇: 방 진입 성공!")
    except Exception as e:
        print(f"❌ 방 진입 실패: {e}")
        return

    # 4. 팝업 닫기 (ESC + TAB 키 전략)
    time.sleep(5)
    print("🧹 로봇: 팝업 청소 및 위치 잡는 중...")
    
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)

    try:
        actions.move_by_offset(100, 200).click().perform()
    except:
        pass
    
    # 5. 제목 입력 (TAB 키로 이동)
    print("✍️ 로봇: 제목 작성 시도...")
    try:
        # 제목이라고 추정되는 곳을 클릭 시도
        possible_titles = ["se-document-title", "se-ff-tit", "se-document-title-container"]
        for class_name in possible_titles:
            try:
                elem = driver.find_element(By.CLASS_NAME, class_name)
                elem.click()
                break
            except:
                continue
        
        time.sleep(1)
        pyperclip.copy("최종 테스트: 제목이 입력되었습니다!")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 제목 입력 동작 완료")
    except Exception as e:
        print(f"❌ 제목 입력 실패: {e}")

    # 6. 본문 입력 (TAB 키로 본문으로 이동)
    print("✍️ 로봇: 본문으로 이동...")
    try:
        actions.send_keys(Keys.TAB).perform()
        time.sleep(1)
        pyperclip.copy("드디어 성공입니다! \n자동화 테스트 완료.")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 본문 입력 동작 완료")
    except Exception as e:
        print(f"❌ 본문 입력 실패: {e}")

    # 7. 임시저장
    print("💾 로봇: 저장 시도...")
    try:
        driver.find_element(By.CLASS_NAME, "se-tool-save-btn-save").click()
        print("✅ 저장 버튼 클릭 성공!")
    except:
        print("⚠️ 버튼 못 찾음 -> 단축키(Ctrl+S) 시도")
        actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()

    print("\n🎉 모든 작업 종료! 화면에 글이 써졌는지 확인하세요.")
    input("종료하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main()