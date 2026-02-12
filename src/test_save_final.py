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
# 👇 아이디와 비밀번호 입력
NAVER_ID = "cky4736"
NAVER_PW = "dyaio030429*" 
# ==========================================

def start_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080") # 화면을 넓게 써야 요소가 잘 보임
    
    driver = webdriver.Chrome(options=options)
    return driver

def main():
    driver = start_driver()
    
    # 1. 로그인
    print("🚀 로봇: 로그인 시작!")
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(2)
    
    # 아이디/비번 복사 붙여넣기
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
        
    # ==========================================================
    # 🛑 [사용자 미션] 60초 대기
    # ==========================================================
    print("\n" + "="*50)
    print("🛑 로봇: 60초 대기! '등록안함'이나 '로그인 유지' 등을 직접 눌러주세요!")
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

    # 4. [필살기] 팝업 닫기 및 제목 찾기 (ESC + TAB 키 전략)
    time.sleep(5) # 에디터 로딩 대기
    print("🧹 로봇: 팝업 청소 및 위치 잡는 중...")
    
    actions = ActionChains(driver)
    
    # (1) ESC 키를 연타해서 도움말 팝업 닫기
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)

    # (2) 본문 아무곳이나 한번 클릭해서 포커스 잡기 (좌표 클릭)
    try:
        # 화면 중앙쯤을 클릭해서 브라우저가 활성화되게 함
        actions.move_by_offset(100, 200).click().perform()
    except:
        pass
    
    # 5. 제목 입력 (TAB 키로 이동해서 작성)
    print("✍️ 로봇: 제목 작성 시도 (TAB 이동법)...")
    try:
        # 제목 칸을 직접 찾는게 아니라, 
        # 그냥 제목이라고 추정되는 곳을 클릭 시도하거나 
        # 제목 클래스의 변형들을 모두 시도
        title_found = False
        possible_titles = [
            "se-document-title", 
            "se-ff-tit", 
            "se-document-title-container"
        ]
        
        for class_name in possible_titles:
            try:
                elem = driver.find_element(By.CLASS_NAME, class_name)
                elem.click()
                title_found = True
                break
            except:
                continue
        
        if not title_found:
            # 못 찾았으면 그냥 맨 위를 클릭해봄
            print("⚠️ 제목 칸 못 찾음 -> 강제 좌표 클릭 시도")
            actions.move_to_element_with_offset(driver.find_element(By.TAG_NAME, "body"), 0, 100).click().perform()

        time.sleep(1)
        pyperclip.copy("최종 테스트: 제목이 입력되었습니다!")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 제목 입력 동작 완료")
    except Exception as e:
        print(f"❌ 제목 입력 실패: {e}")

    # 6. 본문 입력 (TAB 키로 본문으로 이동)
    print("✍️ 로봇: 본문으로 이동...")
    try:
        # 제목에서 탭 키를 누르면 본문으로 넘어감
        actions.send_keys(Keys.TAB).perform()
        time.sleep(1)
        
        pyperclip.copy("드디어 성공입니다! \n이 글이 보이면 이제 자동화 프로그램을 돌릴 수 있습니다.")
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        print("✅ 본문 입력 동작 완료")
    except Exception as e:
        print(f"❌ 본문 입력 실패: {e}")

    # 7. 임시저장 (단축키 사용)
    # 저장 버튼을 못 찾으면 단축키 (Ctrl + S) 시도
    print("💾 로봇: 저장 시도 (단축키 Ctrl+S)...")
    try:
        actions.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
        time.sleep(3)
        # 팝업이 뜨면 ESC로 닫기
        actions.send_keys(Keys.ESCAPE).perform()
        print("✅ 저장 신호 전송 완료!")
    except:
        print("❌ 저장 실패")

    print("\n🎉 모든 작업 종료! 화면에 글이 써졌는지 확인하세요.")
    input("종료하려면 엔터키를 누르세요...")

if __name__ == "__main__":
    main()