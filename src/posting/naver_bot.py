"""
🐟 네이버 블로그 자동 포스팅 모듈
코다리 부장의 핵심 자동화 엔진입니다!
Selenium 기반으로 안전하게 포스팅합니다.
다중 사용자 지원: 런타임에 ID/PW를 입력받아 사용합니다.
"""

import os
import sys
import time
import random
import pyperclip
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import SafetyConfig


class NaverBlogBot:
    """네이버 블로그 자동 포스팅 봇 (다중 사용자 지원)"""

    def __init__(self, naver_id: str = None, naver_pw: str = None, blog_id: str = None):
        """
        Args:
            naver_id: 네이버 아이디 (None이면 설정에서 가져옴)
            naver_pw: 네이버 비밀번호
            blog_id: 블로그 아이디 (기본값: naver_id와 동일)
        """
        self.driver = None
        self.is_logged_in = False

        if naver_id and naver_pw:
            # 런타임 입력 (다중 사용자)
            self.naver_id = naver_id
            self.naver_pw = naver_pw
            self.blog_id = blog_id or naver_id
        else:
            # .env 설정에서 가져오기 (기존 호환)
            from config.settings import NaverConfig
            self.naver_id = NaverConfig.ID
            self.naver_pw = NaverConfig.PASSWORD
            self.blog_id = NaverConfig.BLOG_ID

    def _init_driver(self):
        """Selenium WebDriver 초기화"""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # User-Agent 설정
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # 자동화 감지 우회
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("🌐 브라우저 초기화 완료!")

    def _random_delay(self, min_sec: float = None, max_sec: float = None):
        """랜덤 대기 (봇 감지 회피)"""
        min_sec = min_sec or SafetyConfig.MIN_DELAY
        max_sec = max_sec or SafetyConfig.MAX_DELAY
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def login(self) -> bool:
        """
        네이버 로그인

        Returns:
            bool: 로그인 성공 여부
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        if not self.driver:
            self._init_driver()

        print("🔐 네이버 로그인 시도 중...")

        try:
            # 네이버 로그인 페이지 접속
            self.driver.get("https://nid.naver.com/nidlogin.login")
            self._random_delay(2, 3)

            # 아이디 입력 (클립보드 방식)
            id_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "id"))
            )
            pyperclip.copy(self.naver_id)
            id_input.click()
            self._random_delay(0.3, 0.5)
            id_input.send_keys(Keys.CONTROL, 'v')
            self._random_delay(0.5, 1)

            # 비밀번호 입력 (클립보드 방식)
            pw_input = self.driver.find_element(By.ID, "pw")
            pyperclip.copy(self.naver_pw)
            pw_input.click()
            self._random_delay(0.3, 0.5)
            pw_input.send_keys(Keys.CONTROL, 'v')
            self._random_delay(0.5, 1)

            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.ID, "log.login")
            login_btn.click()
            self._random_delay(3, 5)

            # 로그인 확인
            if "nid.naver.com" not in self.driver.current_url:
                self.is_logged_in = True
                print("✅ 네이버 로그인 성공!")
                return True
            else:
                print("❌ 로그인 실패 - 캡차 또는 2차 인증 필요")
                return False

        except Exception as e:
            print(f"❌ 로그인 중 오류 발생: {e}")
            return False

    def write_post(
        self,
        title: str,
        content: str,
        tags: list = None,
        category: str = None,
        mode: str = "publish"
    ) -> bool:
        """
        블로그 글 작성 (ActionChains 적용으로 안정성 강화)

        Args:
            title: 글 제목
            content: 글 본문 (HTML 또는 텍스트)
            tags: 태그 리스트
            category: 카테고리명 (미구현)
            mode: 발행 모드 - "publish"(즉시발행), "draft"(임시저장), "schedule"(예약발행)
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains

        if not self.is_logged_in:
            if not self.login():
                return False

        print(f"✍️ 글 작성 시작... 제목: {title[:30]}... (모드: {mode})")

        try:
            # 블로그 글쓰기 페이지 접속
            write_url = f"https://blog.naver.com/{self.blog_id}/postwrite"
            self.driver.get(write_url)
            self._random_delay(3, 5)

            # 팝업 닫기 (이전 글 불러오기 등)
            try:
                popup_cancel = self.driver.find_elements(By.CSS_SELECTOR, ".se-popup-button-cancel")
                if popup_cancel:
                    popup_cancel[0].click()
                    self._random_delay(0.5, 1)
            except:
                pass

            # 스마트에디터 로딩 대기
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".se-main-container"))
                )
            except Exception as e:
                print(f"⚠️ 에디터 로딩 타임아웃, 계속 진행: {e}")

            actions = ActionChains(self.driver)

            # 1. 제목 입력
            try:
                print("📝 제목 입력 시도...")
                # 제목 영역 찾기 (여러 선택자 시도)
                title_selectors = [
                    ".se-document-title", 
                    ".se-title-text", 
                    ".se-ff-nanumgothic", 
                    "//span[contains(text(), '제목')]/.."
                ]
                
                title_elem = None
                for selector in title_selectors:
                    try:
                        if selector.startswith("//"):
                            elems = self.driver.find_elements(By.XPATH, selector)
                        else:
                            elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if elems and elems[0].is_displayed():
                            title_elem = elems[0]
                            break
                    except:
                        continue
                
                if title_elem:
                    actions.move_to_element(title_elem).click().perform()
                    self._random_delay(0.5, 1)
                    pyperclip.copy(title)
                    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                    self._random_delay(1, 2)
                    print("✅ 제목 입력 완료")
                else:
                    print("⚠️ 제목 입력란을 찾을 수 없습니다.")

            except Exception as e:
                print(f"⚠️ 제목 입력 실패: {e}")

            # 2. 본문 입력
            try:
                print("📝 본문 입력 시도...")
                # 본문 영역 찾기
                content_selectors = [
                    ".se-main-container",
                    ".se-component-text",
                    ".se-text-paragraph"
                ]
                
                content_elem = None
                for selector in content_selectors:
                    try:
                        elems = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elems and elems[0].is_displayed():
                            content_elem = elems[0]
                            break
                    except:
                        continue

                if content_elem:
                    # 본문 클릭 (포커스)
                    actions.move_to_element(content_elem).click().perform()
                    self._random_delay(0.5, 1)

                    # 본문을 청크로 나눠서 입력
                    chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                    for chunk in chunks:
                        pyperclip.copy(chunk)
                        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                        self._random_delay(0.2, 0.5)
                        
                        # 엔터키 입력 (줄바꿈)
                        actions.send_keys(Keys.ENTER).perform()
                        self._random_delay(0.1, 0.2)
                    
                    print("✅ 본문 입력 완료")
                else:
                    print("⚠️ 본문 입력란을 찾을 수 없습니다.")

            except Exception as e:
                print(f"⚠️ 본문 입력 실패: {e}")

            self._random_delay(1, 2)

            # 3. 태그 입력
            if tags:
                try:
                    # 태그 버튼 찾기
                    # 태그 버튼은 보통 하단에 있음, 스크롤 필요할 수도 있음
                    tag_input = None
                    try:
                        tag_input = self.driver.find_element(By.CSS_SELECTOR, ".se-tag-input")
                    except:
                        # 버튼을 눌러야 입력창이 나오는 경우
                        tag_btns = self.driver.find_elements(By.CSS_SELECTOR, ".button_tag")
                        if tag_btns:
                            tag_btns[0].click()
                            self._random_delay(0.5, 1)
                            tag_input = self.driver.find_element(By.CSS_SELECTOR, ".se-tag-input")
                    
                    if tag_input:
                        tag_input.click()
                        self._random_delay(0.5, 1)
                        for tag in tags[:10]:
                            pyperclip.copy(tag)
                            tag_input.send_keys(Keys.CONTROL, 'v')
                            tag_input.send_keys(Keys.ENTER)
                            self._random_delay(0.2, 0.4)
                        print("✅ 태그 입력 완료")
                except Exception as e:
                    print(f"⚠️ 태그 입력 중 오류 (무시): {e}")

            # 4. 발행 모드 처리
            self._random_delay(2, 3)

            if mode == "draft":
                return self._save_as_draft()
            elif mode == "schedule":
                return self._save_as_draft() # 예약발행 로직은 추후 구현, 일단 저장
            else:
                return self._publish_post()

        except Exception as e:
            print(f"❌ 글 작성 중 오류: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_as_draft(self) -> bool:
        """네이버 블로그에 임시저장 (단축키 및 버튼 클릭)"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains

        try:
            print("💾 임시저장 시도 중...")
            
            # 방법 1: 상단 '저장' 버튼 클릭
            try:
                # '저장' 텍스트를 가진 버튼 찾기
                save_btns = self.driver.find_elements(By.XPATH, "//button[contains(span, '저장')] | //span[contains(text(), '저장')]/..")
                
                clicked = False
                for btn in save_btns:
                    if btn.is_displayed():
                        btn.click()
                        self._random_delay(1, 2)
                        clicked = True
                        print("✅ '저장' 버튼 클릭 성공")
                        break
                
                if not clicked:
                    # 방법 2: 단축키 (Ctrl+S)
                    print("⚠️ 저장 버튼 못 찾음, 단축키 시도...")
                    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                    self._random_delay(2, 3)
            
            except Exception as e:
                print(f"⚠️ 저장 시도 1차 실패: {e}")
                
            # 임시저장 완료 확인 (선택 사항)
            return True

        except Exception as e:
            print(f"❌ 임시저장 중 오류: {e}")
            return False

    def _publish_post(self) -> bool:
        """글 발행"""
        from selenium.webdriver.common.by import By

        try:
            # 발행 버튼 클릭
            publish_btn = self.driver.find_element(By.CSS_SELECTOR, ".publish_btn__m9KHH")
            publish_btn.click()
            self._random_delay(2, 3)

            # 최종 발행 확인
            confirm_btn = self.driver.find_element(By.CSS_SELECTOR, ".confirm_btn")
            confirm_btn.click()
            self._random_delay(3, 5)

            print("✅ 글 발행 완료!")
            return True

        except Exception as e:
            print(f"❌ 발행 중 오류: {e}")
            return False

    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("🌐 브라우저 종료")


# 테스트 코드
if __name__ == "__main__":
    print("🐟 네이버 블로그 봇 테스트")
    print("⚠️ 실제 테스트는 네이버 계정 정보를 입력한 후 진행하세요!")

    # 예시 (다중 사용자 방식)
    # bot = NaverBlogBot(naver_id="myid", naver_pw="mypassword")
    # bot.login()
    # bot.write_post(
    #     title="테스트 포스트",
    #     content="테스트 내용입니다.",
    #     tags=["테스트", "자동화"],
    #     mode="publish"  # "draft", "schedule", "publish"
    # )
    # bot.close()
