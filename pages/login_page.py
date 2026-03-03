# -*- coding: utf-8 -*-
"""LoginPage — 카카오 로그인 플로우 Page Object

[근본 원인 분석]
Kakao SDK(2.x+)는 OAuth 인증에 Chrome Custom Tab을 사용한다.
Chrome Custom Tab은 Appium WEBVIEW_* 컨텍스트로 노출되지 않으며,
d.contexts 호출 시 Appium이 Chromedriver 세션 생성을 시도하다
"session not created" 오류를 발생시킨다.

[해결 전략]
WebView 컨텍스트 전환을 완전히 제거하고,
NATIVE_APP 컨텍스트(UiAutomator2)만으로 Kakao OAuth 화면과 상호작용한다.
Chrome Custom Tab의 웹 콘텐츠도 UiAutomator2로 텍스트 기반 접근이 가능하다.
"""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage


class LoginPage(BasePage):

    # ── 앱 로그인 화면 ────────────────────────────────────────────
    KAKAO_START_BUTTON = "//*[@text='카카오로 시작하기']"

    # ── Kakao OAuth 페이지 (Chrome Custom Tab, NATIVE 컨텍스트 접근) ──
    # Kakao OAuth 화면이 로드됐음을 감지하는 XPath
    # Custom Tab의 웹 콘텐츠는 android.view.View/@text 또는
    # android.widget.TextView/@text 로 UiAutomator2에서 읽힌다.
    KAKAO_OAUTH_READY = (
        "//*[@text='계속하기']"
        " | //*[@text='카카오계정으로 로그인']"
        " | //*[contains(@text,'로그인') and contains(@package,'kakao')]"
    )

    # '계속하기' 버튼 — 저장된 카카오 계정이 있을 때 노출
    KAKAO_CONTINUE_NATIVE = (
        "//*[@text='계속하기' or @text='Continue' or @text='동의']"
    )

    # 첫 번째 카카오 계정 항목
    # 계정 목록은 Android ListView 또는 web 렌더링 요소로 나타남
    KAKAO_FIRST_ACCOUNT_NATIVE = (
        "(//*[contains(@text,'@') or contains(@resource-id,'account')])[1]"
        " | (//android.widget.ListView//*[contains(@class,'Layout')])[1]"
    )

    # ── 홈 화면 고유 식별 요소 ────────────────────────────────────
    HOME_TAB     = "//*[@text='홈']"
    HOME_CONTENT = (
        "//*[contains(@text,'보험 종합진단')"
        " or contains(@text,'매월 내는 보험료')]"
    )
    BOTTOM_TABS  = ['홈', '진단', '상품', '건강', '보상']

    # ════════════════════════════════════════════════════════════
    # 로그인 화면
    # ════════════════════════════════════════════════════════════

    def ensure_login_screen(self, timeout: int = 10):
        """'카카오로 시작하기' 버튼이 표시될 때까지 대기한다.

        로그인된 상태에서 실행 시 버튼이 없어 AssertionError 발생.
        이 경우 대시보드 UI의 Skip 버튼으로 이 시나리오를 건너뛰세요.
        """
        try:
            self.wait_for_element(self.KAKAO_START_BUTTON, timeout=timeout)
            print("[OK] 로그인 화면 확인 ('카카오로 시작하기' 버튼 노출)")
        except Exception:
            raise AssertionError(
                f"로그인 화면이 {timeout}초 내에 표시되지 않았습니다.\n"
                "'카카오로 시작하기' 버튼을 찾을 수 없습니다.\n"
                "앱이 이미 로그인된 상태라면 대시보드 UI의 Skip 버튼으로 "
                "이 시나리오를 건너뛰세요."
            )

    def start_kakao_login(self):
        """권한 팝업 처리 후 '카카오로 시작하기' 버튼 클릭."""
        self.dismiss_any_permission_popup()
        self.click(self.KAKAO_START_BUTTON, "S2_Kakao_Start_Click")

    # ════════════════════════════════════════════════════════════
    # Kakao OAuth 화면 (NATIVE 컨텍스트 — Chrome Custom Tab)
    # ════════════════════════════════════════════════════════════

    def wait_for_kakao_oauth_ui(self, timeout: int = 15):
        """Kakao OAuth 페이지가 로드됐음을 NATIVE 컨텍스트에서 확인한다.

        WebView/Chromedriver 세션 생성 없이 UiAutomator2만 사용한다.
        KAKAO_OAUTH_READY XPath 요소가 나타나면 성공으로 간주한다.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_elements(AppiumBy.XPATH, self.KAKAO_OAUTH_READY)
            )
            print("[OK] Kakao OAuth 페이지 로드 확인 (NATIVE 컨텍스트)")
        except Exception:
            raise AssertionError(
                f"Kakao OAuth 페이지가 {timeout}초 내에 로드되지 않았습니다.\n"
                f"감지 XPath: {self.KAKAO_OAUTH_READY}\n"
                "조치: KAKAO_OAUTH_READY XPath를 실기기 요소에 맞게 조정하세요."
            )

    def click_kakao_continue(self):
        """Kakao OAuth 화면의 '계속하기' 버튼을 클릭한다.

        NATIVE 컨텍스트에서 텍스트 기반으로 시도하고,
        실패 시 비율 좌표로 폴백한다. WebView 전환 없음.
        """
        try:
            self.wait_for_element(self.KAKAO_CONTINUE_NATIVE, timeout=5)
            self.click(self.KAKAO_CONTINUE_NATIVE, "S2_Kakao_Continue_Click")
            print("[OK] '계속하기' 버튼 클릭 (NATIVE)")
        except Exception:
            print("[WARN] '계속하기' 버튼 미발견 — 좌표 폴백")
            self.tap_coordinate(0.5, 0.66, "S2_Kakao_Continue_Tap")

    def select_first_kakao_account(self):
        """Kakao OAuth 화면에서 첫 번째 계정을 선택한다.

        NATIVE 컨텍스트에서 계정 요소를 탐색하고,
        실패 시 비율 좌표로 폴백한다. WebView 전환 없음.
        """
        try:
            self.wait_for_element(self.KAKAO_FIRST_ACCOUNT_NATIVE, timeout=5)
            self.click(self.KAKAO_FIRST_ACCOUNT_NATIVE, "S2_Kakao_Account_Click")
            print("[OK] 첫 번째 카카오 계정 선택 (NATIVE)")
        except Exception:
            print("[WARN] 계정 목록 미발견 — 좌표 폴백")
            self.tap_coordinate(0.5, 0.35, "S2_Kakao_Account_Tap")

    # ════════════════════════════════════════════════════════════
    # 홈 화면 검증
    # ════════════════════════════════════════════════════════════

    def verify_home_screen(self, timeout: int = 20):
        """로그인 완료 후 홈 화면 진입 및 핵심 요소를 검증한다.

        성공 조건 (모두 만족해야 함):
          1. '홈' 탭(하단 탭바) 노출
          2. 홈 콘텐츠 영역(보험 종합진단 또는 매월 내는 보험료) 노출
          3. 하단 탭바 5개(홈·진단·상품·건강·보상) 노출
        """
        # 1. 홈 탭 진입 대기
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_elements(AppiumBy.XPATH, self.HOME_TAB)
            )
            print("[OK] 홈 탭 진입 확인")
        except Exception:
            raise AssertionError(
                f"카카오 로그인 후 {timeout}초 내에 홈 화면으로 이동하지 않았습니다.\n"
                "'홈' 탭이 표시되지 않습니다. 로그인 처리 중 오류가 발생했을 수 있습니다."
            )

        # 2. 홈 콘텐츠 영역 노출 확인
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_elements(AppiumBy.XPATH, self.HOME_CONTENT)
            )
            print("[OK] 홈 콘텐츠 영역 확인")
        except Exception:
            raise AssertionError(
                "홈 탭 진입 후 콘텐츠 영역(보험 종합진단/매월 내는 보험료)이 "
                "10초 내에 표시되지 않습니다."
            )

        # 3. 하단 탭바 5개 노출 확인
        for tab in self.BOTTOM_TABS:
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d, t=tab: d.find_elements(
                        AppiumBy.XPATH, f"//*[@text='{t}']"
                    )
                )
                print(f"[OK] 탭 '{tab}' 확인")
            except Exception:
                confirmed = self.BOTTOM_TABS[:self.BOTTOM_TABS.index(tab)]
                raise AssertionError(
                    f"하단 탭바에서 '{tab}' 탭이 표시되지 않습니다.\n"
                    f"확인된 탭: {confirmed if confirmed else '없음'}"
                )

        print("[OK] 홈 화면 진입 및 탭바 전체 검증 완료")

    # ════════════════════════════════════════════════════════════
    # 기존 호환 메서드
    # ════════════════════════════════════════════════════════════

    def verify_login_screen_visible(self):
        element = self.wait_for_element(self.KAKAO_START_BUTTON)
        if self.ss:
            self.ss("S2_LoginScreen_Visible")
        assert element.is_displayed()

    def verify_logged_in(self):
        """로그인 완료 후 하단 탭바 5개 노출 확인."""
        for tab in self.BOTTOM_TABS:
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d, t=tab: d.find_elements(
                        AppiumBy.XPATH, f"//*[@text='{t}']"
                    )
                )
                print(f"[OK] 탭 '{tab}' 확인")
            except Exception:
                raise AssertionError(f"로그인 후 하단 탭 '{tab}'이 표시되지 않습니다.")

    def _back_to_native(self):
        try:
            self.driver.switch_to.context('NATIVE_APP')
        except Exception:
            pass
