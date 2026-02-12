"""
🐟 네이버 블로그 이웃 관리 자동화 모듈
서로이웃 수락, 이웃 방문, 자동 공감 및 AI 댓글 기능을 수행합니다.
모바일 웹(m.blog.naver.com) 기반으로 작동하여 복잡한 iframe 문제를 최소화합니다.
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.posting.naver_bot import NaverBlogBot
from src.dashboard.app import get_content_generator # 앱 컨텍스트 의존성 주의 (순환 참조 방지 위해 내부 임포트 권장)

class NeighborManager(NaverBlogBot):
    """이웃 관리 자동화 클래스 (NaverBlogBot 상속)"""

    def __init__(self, naver_id, naver_pw, blog_id=None):
        super().__init__(naver_id, naver_pw, blog_id)
        self.generator = None

    def _get_generator(self):
        if not self.generator:
            try:
                # 순환 참조 방지를 위해 여기서 임포트
                from src.content.generator import ContentGenerator
                from src.dashboard.app import get_content_generator
                # app.py의 헬퍼 함수를 쓰거나 직접 생성 (API 키 필요)
                # 여기서는 세션 정보가 없으므로 API 키를 환경변수에서 가져오도록 유도하거나
                # ContentGenerator()를 직접 호출 (설정값 사용)
                self.generator = ContentGenerator() 
            except:
                print("⚠️ AI 생성기 초기화 실패. 댓글 기능이 제한될 수 있습니다.")

    def accept_neighbor_requests(self):
        """서로이웃 신청 자동 수락 (모바일 웹)"""
        if not self.driver:
            if not self.login():
                return False

        print("🤝 서로이웃 신청 목록 확인 중...")
        count = 0
        try:
            # 1. 모바일 서로이웃 신청 관리 페이지 이동
            self.driver.get("https://m.blog.naver.com/BuddyMeManage.naver")
            time.sleep(3)

            # 2. '받은 신청' 탭 확인 및 클릭
            # 보통 URL 파라미터나 탭 버튼으로 접근. 기본이 받은 신청일 수 있음.
            # 탭 버튼 찾기: "받은 신청" 텍스트 포함된 요소
            try:
                tabs = self.driver.find_elements(By.XPATH, "//a[contains(text(), '받은 신청')]")
                if tabs:
                    tabs[0].click()
                    time.sleep(2)
            except:
                pass

            # 3. 신청 목록 확인
            # 목록 아이템: .item_buddy 등
            items = self.driver.find_elements(By.CSS_SELECTOR, ".u_checkbox") 
            
            if not items:
                print("✅ 대기 중인 서로이웃 신청이 없습니다.")
                return True

            print(f"📋 발견된 신청 수: {len(items)}명 (화면에 보이는 만큼)")
            
            # 4. 전체 선택 (혹은 개별 수락)
            # '전체선택' 체크박스 찾기
            select_all = self.driver.find_elements(By.ID, "checkall")
            if select_all:
                # 라벨을 클릭해야 할 수도 있음
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "label[for='checkall']").click()
                except:
                    select_all[0].click()
                time.sleep(1)
                
                # 수락 버튼 클릭
                accept_btns = self.driver.find_elements(By.CSS_SELECTOR, ".btn_confirm") # 클래스명 추정
                # 실제 버튼: '수락' 텍스트 찾기
                if not accept_btns:
                    accept_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), '수락')] | //a[contains(text(), '수락')]")
                
                if accept_btns:
                    accept_btns[0].click()
                    time.sleep(1)
                    
                    # 확인 팝업 (alert) 처리
                    try:
                        WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                        alert = self.driver.switch_to.alert
                        alert.accept()
                        print("✅ 수락 확인 팝업 승인")
                    except:
                        pass
                        
                    count = len(items)
                    print(f"🎉 {count}명의 서로이웃 신청을 수락했습니다!")
                    return True
            
            print("⚠️ 수락 버튼을 찾지 못해 개별 처리를 시도합니다.")
            return False

        except Exception as e:
            print(f"❌ 서로이웃 수락 중 오류: {e}")
            return False

    def visit_and_like_neighbors(self, count=5, mode="like"):
        """
        이웃 새글 방문, 공감, 댓글 작성
        
        Args:
            count: 방문할 글 수
            mode: 'like' (공감만), 'like_comment' (공감+댓글)
        """
        if not self.driver:
            if not self.login():
                return False

        if mode == "like_comment":
            self._get_generator()

        print(f"❤️ 이웃 새글 {count}개 방문... (모드: {mode})")
        posts_visited = 0
        
        try:
            # 1. 모바일 이웃 새글 페이지 이동
            self.driver.get("https://m.blog.naver.com/FeedList.naver")
            time.sleep(3)
            
            # 스크롤해서 글 더 로딩
            for _ in range(2):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            # 2. 포스트 링크 수집
            # 모바일 피드 구조: .list_post .link 등
            post_links = []
            try:
                # 제목/이미지/내용을 감싸는 링크 찾기
                # 보통 class="link" 또는 구조적으로 접근
                # 안전하게: href에 'logNo'가 포함된 링크들
                elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logNo=']")
                for el in elements:
                    url = el.get_attribute("href")
                    if url and "blog.naver.com" in url and url not in post_links:
                        post_links.append(url)
            except:
                pass
            
            # 만약 못 찾으면 PC 버전으로 시도 (백업)
            if not post_links:
                print("⚠️ 모바일 피드 파싱 실패, PC 버전에서 링크 수집 시도...")
                self.driver.get("https://section.blog.naver.com/BlogHome.naver?directoryNo=0&currentPage=1&groupId=0")
                time.sleep(3)
                items = self.driver.find_elements(By.CSS_SELECTOR, ".info_post .title a")
                for item in items:
                    link = item.get_attribute("href")
                    if link:
                        post_links.append(link)

            print(f"📋 방문할 포스트: {len(post_links)}개 중 {count}개 선택")
            target_links = post_links[:count]

            # 3. 순차 방문
            for link in target_links:
                try:
                    # 모바일 버전으로 접속 강제 (댓글/공감 처리가 쉬움)
                    # PC 링크라면 모바일로 변환: blog.naver.com/{id}/{logNo} -> m.blog.naver.com/{id}/{logNo}
                    if "m.blog.naver.com" not in link:
                        link = link.replace("blog.naver.com", "m.blog.naver.com")
                    
                    print(f"➡️ 방문 중: {link}")
                    self.driver.get(link)
                    time.sleep(random.uniform(3, 5)) # 로딩 대기

                    # 스크롤 (읽는 척)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.5)")
                    self._random_delay(1, 2)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                    self._random_delay(1, 2)

                    # 공감 클릭
                    try:
                        # u_likeit_list_btn 클래스 (공통 공감 버튼)
                        # data-on="false" 인지 확인 필요 (u_likeit_on 클래스가 있으면 이미 누른 것)
                        like_btn = self.driver.find_element(By.CSS_SELECTOR, ".u_likeit_list_btn")
                        
                        # 이미 좋아요 눌렀는지 확인
                        is_liked = "on" in like_btn.get_attribute("class") or \
                                   (like_btn.get_attribute("aria-pressed") == "true")
                        
                        if not is_liked:
                            # 화면에 안 보이면 스크롤 조정
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_btn)
                            time.sleep(0.5)
                            like_btn.click()
                            print("   ❤️ 공감 클릭 완료!")
                            time.sleep(1)
                        else:
                            print("   ℹ️ 이미 공감한 글입니다.")
                    except Exception as e:
                        print(f"   ⚠️ 공감 버튼 찾기 실패: {e}")

                    # 댓글 작성 (옵션)
                    if mode == "like_comment" and self.generator:
                        try:
                            # 1. 글 본문 추출
                            # 모바일 본문: .se-main-container or .post_ct
                            content_text = ""
                            try:
                                body_elem = self.driver.find_element(By.CSS_SELECTOR, ".se-main-container")
                                content_text = body_elem.text
                            except:
                                try:
                                    body_elem = self.driver.find_element(By.CSS_SELECTOR, "#viewTypeSelector")
                                    content_text = body_elem.text
                                except:
                                    pass
                            
                            if len(content_text) > 50:
                                # 2. AI 댓글 생성
                                comment = self.generator.generate_comment(content_text)
                                print(f"   💬 생성된 댓글: {comment}")
                                
                                # 3. 댓글 버튼 클릭하여 입력창 열기 (있으면)
                                # 보통 하단에 바로 입력창이 있거나, 댓글 버튼을 눌러야 함
                                # 모바일 웹 댓글 입력창: .u_cbox_text
                                # 먼저 iframe 전환이 필요할 수 있음 (네이버 댓글은 별도 모듈)
                                # 하지만 모바일 웹은 보통 iframe 아님.
                                
                                # 댓글 영역이 보이도록 스크롤
                                # .u_cbox_area
                                
                                # 입력창 찾기
                                text_area = self.driver.find_element(By.CLASS_NAME, "u_cbox_text")
                                text_area.click()
                                time.sleep(0.5)
                                text_area.send_keys(comment)
                                time.sleep(1)
                                
                                # 등록 버튼
                                submit_btn = self.driver.find_element(By.CLASS_NAME, "u_cbox_btn_upload")
                                submit_btn.click()
                                print("   ✅ 댓글 등록 완료!")
                                time.sleep(2)
                            else:
                                print("   ⚠️ 본문 내용이 너무 짧아 댓글 생략")
                        except Exception as e:
                            print(f"   ⚠️ 댓글 작성 실패: {e}")

                    posts_visited += 1

                except Exception as e:
                    print(f"⚠️ 포스트 처리 중 오류: {e}")
                    continue

            print(f"✅ 총 {posts_visited}개 글에 흔적을 남겼습니다.")
            return posts_visited

        except Exception as e:
            print(f"❌ 이웃 방문 작업 중 오류: {e}")
            return posts_visited

# 테스트
if __name__ == "__main__":
    pass
