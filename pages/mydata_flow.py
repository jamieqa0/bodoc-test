from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait


class MydataFlow(BasePage):
    # Locators
    CONNECT_40_BUTTON     = "//*[contains(@text, '연결하기')]"
    NAVER_CERT_BUTTON     = "//*[contains(@text, '네이버')]"
    AGREE_CONTINUE_BUTTON = "//*[contains(@text, '동의하고 계속하기')]"
    CONFIRM_BUTTON        = "//*[contains(@text, '확인')]"
    GET_DIAGNOSIS_BUTTON  = "//*[contains(@text, '진단받기')]"
    CHAT_X_BUTTON         = "//android.widget.ImageView[contains(@content-desc, '닫기')] | //*[@text='X']"
    # 연결 완료 후 나타나는 UI 요소들 (진단받기·완료·확인 등)
    CONNECTION_DONE_XPATH = (
        "//*[contains(@text,'연결 완료') or contains(@text,'수집 완료') "
        "or contains(@text,'완료되었습니다') or contains(@text,'진단받기') "
        "or contains(@text,'확인')]"
    )

    def click_connect_40(self):
        print("> 보험사 연결 화면 하단으로 스크롤 중...")
        self.scroll_to_text("연결하기")
        self.click(self.CONNECT_40_BUTTON, "S5_Connect40_Click")

    def select_naver_cert(self):
        self.click(self.NAVER_CERT_BUTTON, "S5_NaverCert_Select")

    def agree_and_continue(self, max_pages=6):
        """약관 동의 화면 전체 처리. 한 번 클릭 후 화면이 전환되면 반복한다.
        동의 페이지가 여러 장인 경우(보험사별 약관, 개인정보 동의 등) 모두 처리한다."""
        for i in range(max_pages):
            try:
                self.wait_for_element(self.AGREE_CONTINUE_BUTTON, timeout=5)
            except Exception:
                print(f"  [약관동의] 동의 화면 없음 — 총 {i}페이지 처리 완료")
                break
            print(f"  [약관동의 {i+1}] '동의하고 계속하기' 발견 → 스크롤 후 클릭")
            self.scroll_down()
            self.click(self.AGREE_CONTINUE_BUTTON, f"S10_Agree_Continue_{i+1}")
            # 동일 버튼이 사라질 때까지(=화면 전환) 대기 후 다음 라운드 확인
            try:
                WebDriverWait(self.driver, 8).until(
                    lambda d: not d.find_elements(
                        AppiumBy.XPATH, self.AGREE_CONTINUE_BUTTON
                    )
                )
            except Exception:
                # 사라지지 않으면 루프 탈출 (무한 반복 방지)
                print(f"  [약관동의] 버튼 변화 없음 — 루프 종료")
                break

    def wait_for_connection(self, timeout=90):
        """마이데이터 수집 완료 대기.
        완료·확인·진단받기 텍스트가 나타날 때까지 최대 timeout 초 대기한다."""
        print(f"> 마이데이터 연결 대기 중 (최대 {timeout}초)...")

        def _done(d):
            d.execute_script('mobile: unlock')
            return d.find_elements(AppiumBy.XPATH, self.CONNECTION_DONE_XPATH)

        WebDriverWait(self.driver, timeout).until(_done)
        print("[OK] 마이데이터 연결 완료 감지")

    def click_final_confirms(self, max_confirms=3):
        """연결 결과 화면의 확인/닫기 버튼을 모두 처리.
        버튼이 1개만 있거나 여러 개인 경우 모두 대응한다."""
        CLOSE_XPATH = (
            "//*[contains(@text,'확인') or contains(@text,'닫기') "
            "or contains(@text,'완료')]"
        )
        for i in range(max_confirms):
            try:
                self.wait_for_element(CLOSE_XPATH, timeout=5)
                self.click(CLOSE_XPATH, f"S10_Confirm_{i+1}")
                # 버튼 사라짐 대기
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda d: not d.find_elements(AppiumBy.XPATH, CLOSE_XPATH)
                    )
                except Exception:
                    break
            except Exception:
                print(f"  [최종확인] 더 이상 확인 화면 없음 (총 {i}회 처리)")
                break

    def dismiss_extra_agreements(self, max_attempts=5):
        """결과 확인 후 남아있는 추가 약관 동의 화면을 모두 처리"""
        print("> 추가 약관 동의 화면 처리 중...")
        for i in range(max_attempts):
            try:
                self.wait_for_element(self.AGREE_CONTINUE_BUTTON, timeout=3)
                print(f"  [추가동의 {i+1}] '동의하고 계속하기' 발견 → 클릭")
                self.scroll_down()
                self.click(self.AGREE_CONTINUE_BUTTON, f"S5_ExtraAgree_{i+1}")
                # 다음 약관 화면 또는 다음 단계 UI가 안정될 때까지 대기
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda d: not d.find_elements(
                            AppiumBy.XPATH, self.AGREE_CONTINUE_BUTTON
                        )
                    )
                except Exception:
                    pass
            except Exception:
                print(f"  [추가동의] 더 이상 동의 화면 없음 (총 {i}회 처리 완료)")
                break

    def get_insurance_diagnosis(self):
        print("> '진단받기' 버튼 찾는 중 (스크롤 후 클릭)...")
        self.scroll_down()
        self.click(self.GET_DIAGNOSIS_BUTTON, "S5_GetDiagnosis_Click")

    def close_chat(self):
        print("> 전문가 채팅 종료 시도 (X 버튼)...")
        try:
            self.click(self.CHAT_X_BUTTON, "S5_ChatClose_Click")
        except Exception:
            print("[WARN] 채팅 X 버튼 클릭 실패. 좌표 클릭 시도...")
            self.tap_coordinate(0.92, 0.05, "S5_ChatClose_Tap")
