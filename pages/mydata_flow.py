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
        self.click(self.CONNECT_40_BUTTON, "S10_Connect40_Click")

    def select_naver_cert(self):
        # '연결하기' 클릭 후 인증서 선택 화면 로드 대기
        self.wait_for_element(self.NAVER_CERT_BUTTON, timeout=10)
        self.click(self.NAVER_CERT_BUTTON, "S10_NaverCert_Select")

    def agree_and_continue(self):
        print("> 약관 동의 화면 스크롤 하단 이동...")
        self.scroll_down()
        self.click(self.AGREE_CONTINUE_BUTTON, "S10_Agree_Continue")

    def wait_for_connection(self, timeout=90):
        """마이데이터 수집 완료 대기.
        완료·확인·진단받기 텍스트가 나타날 때까지 최대 timeout 초 대기한다."""
        print(f"> 마이데이터 연결 대기 중 (최대 {timeout}초)...")

        def _done(d):
            d.execute_script('mobile: unlock')
            return d.find_elements(AppiumBy.XPATH, self.CONNECTION_DONE_XPATH)

        WebDriverWait(self.driver, timeout).until(_done)
        print("[OK] 마이데이터 연결 완료 감지")

    def click_final_confirms(self):
        """연결 완료 후 확인 버튼 처리.
        화면 구성에 따라 1~2회 나타날 수 있으므로 각 클릭은 독립적으로 시도한다."""
        for i, label in enumerate(("S10_Result_Confirm_1st", "S10_Result_Confirm_2nd"), start=1):
            try:
                self.click(self.CONFIRM_BUTTON, label)
                print(f"[OK] 확인 버튼 {i}번째 클릭")
            except Exception:
                print(f"[INFO] 확인 버튼 {i}번째 없음 — 계속 진행")
                break

    def dismiss_extra_agreements(self, max_attempts=5):
        """결과 확인 후 남아있는 추가 약관 동의 화면을 모두 처리"""
        print("> 추가 약관 동의 화면 처리 중...")
        for i in range(max_attempts):
            try:
                self.wait_for_element(self.AGREE_CONTINUE_BUTTON, timeout=3)
                print(f"  [추가동의 {i+1}] '동의하고 계속하기' 발견 → 클릭")
                self.scroll_down()
                self.click(self.AGREE_CONTINUE_BUTTON, f"S10_ExtraAgree_{i+1}")
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
        print("> '진단받기' 버튼 찾는 중 (스크롤 탐색)...")
        self.scroll_to_text("진단받기")
        self.click(self.GET_DIAGNOSIS_BUTTON, "S10_GetDiagnosis_Click")

    def close_chat(self):
        print("> 전문가 채팅 종료 시도 (X 버튼)...")
        try:
            self.click(self.CHAT_X_BUTTON, "S10_ChatClose_Click")
        except Exception:
            print("[WARN] 채팅 X 버튼 클릭 실패. 좌표 클릭 시도...")
            self.tap_coordinate(0.92, 0.05, "S10_ChatClose_Tap")
