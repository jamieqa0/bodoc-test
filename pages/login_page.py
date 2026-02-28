# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class LoginPage(BasePage):
    KAKAO_START_BUTTON = "//*[@text='카카오로 시작하기']"

    # ── 퍼블릭 액션 ──────────────────────────────────────────────
    def start_kakao_login(self):
        self.click(self.KAKAO_START_BUTTON, "Scenario1_06_LoginHome_KakaoClick")

    def wait_for_kakao_webview_ready(self, timeout=12):
        """WEBVIEW 컨텍스트에 클릭 가능한 콘텐츠가 로드될 때까지 대기.

        start_kakao_login() 이후, click_kakao_continue() 이전에 호출.
        Returns:
            True — 웹뷰 콘텐츠 로드 확인
            False — 타임아웃 또는 전환 실패
        """
        try:
            # 1단계: WEBVIEW 컨텍스트 자체가 등장할 때까지 대기
            WebDriverWait(self.driver, timeout).until(
                lambda d: any('WEBVIEW' in c for c in d.contexts)
            )
            # 2단계: 웹뷰로 전환 후 클릭 가능한 UI 요소 등장 대기
            if not self._switch_to_webview():
                return False
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button | //a | //input | //li")
                )
            )
            self._back_to_native()
            print("[OK] 카카오 웹뷰 콘텐츠 로드 완료")
            return True
        except Exception as e:
            print(f"[WARN] 웹뷰 콘텐츠 대기 타임아웃: {e}")
            self._back_to_native()
            return False

    def click_kakao_continue(self):
        """웹뷰 내 '계속하기' 버튼 클릭.

        웹뷰 텍스트로 먼저 탐색, 실패 시 좌표 폴백.
        """
        if self._click_in_webview(["계속하기", "Continue", "동의"]):
            return
        # 폴백: 기기 화면 비율 기반 좌표
        self.tap_coordinate(0.5, 0.66, "Scenario1_07_KakaoWebView_Continue_Tap")

    def verify_account_screen_visible(self, timeout=10):
        """'계속하기' 클릭 후 계정 선택 화면이 등장했는지 확인.

        웹뷰 내에 계정 목록(li) 또는 입력 폼이 나타나면 True.
        """
        if not self._switch_to_webview():
            return False
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//li | //input[@type='tel'] | //*[@role='listitem']")
                )
            )
            self._back_to_native()
            print("[OK] 카카오 계정 선택 화면 확인")
            return True
        except Exception:
            self._back_to_native()
            return False

    def select_first_kakao_account(self):
        """첫 번째 카카오 계정 선택.

        웹뷰 컨텍스트에서 계정 목록 첫 항목 탐색, 실패 시 좌표 폴백.
        """
        if self._click_in_webview_index(0):
            return
        # 폴백: 기기 화면 비율 기반 좌표
        self.tap_coordinate(0.5, 0.20, "Scenario1_08_KakaoWebView_Account_Select_Tap")

    def wait_for_auth_redirect(self, timeout=15):
        """계정 선택 후 OAuth 인증 처리 완료를 대기.

        웹뷰 컨텍스트가 사라지거나 홈 화면이 나타나면 인증 완료로 판단.
        Returns:
            True — 인증 완료 또는 리디렉션 확인
            False — 타임아웃
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: (
                    all('WEBVIEW' not in c for c in d.contexts)
                    or bool(d.find_elements(AppiumBy.XPATH, "//*[@text='홈']"))
                )
            )
            print("[OK] 카카오 인증 처리 완료 (웹뷰 종료 또는 홈 화면 감지)")
            return True
        except Exception:
            print("[WARN] 인증 완료 신호 미감지 (타임아웃)")
            return False

    def verify_login_screen_visible(self):
        element = self.wait_for_element(self.KAKAO_START_BUTTON)
        if self.ss:
            self.ss("Scenario1_05_LoginHome_Visible")
        assert element.is_displayed()

    # ── 웹뷰 헬퍼 ─────────────────────────────────────────────
    def _switch_to_webview(self):
        """WEBVIEW 컨텍스트로 전환. 성공 시 True."""
        try:
            contexts = self.driver.contexts
            webview = next((c for c in contexts if 'WEBVIEW' in c), None)
            if webview:
                self.driver.switch_to.context(webview)
                return True
        except Exception:
            pass
        return False

    def _back_to_native(self):
        try:
            self.driver.switch_to.context('NATIVE_APP')
        except Exception:
            pass

    def _click_in_webview(self, texts):
        """웹뷰에서 텍스트 목록 중 하나를 클릭. 성공 시 True."""
        if not self._switch_to_webview():
            return False
        try:
            xpath = " | ".join(
                f"//*[contains(text(),'{t}') or contains(@value,'{t}')]"
                for t in texts
            )
            el = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            el.click()
            self._back_to_native()
            return True
        except Exception as e:
            print(f"[WARN] 웹뷰 텍스트 클릭 실패: {e}")
            self._back_to_native()
            return False

    def _click_in_webview_index(self, index):
        """웹뷰에서 클릭 가능한 요소 중 index번째를 클릭. 성공 시 True."""
        if not self._switch_to_webview():
            return False
        try:
            els = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//li | //button | //a[@href]")
                )
            )
            if len(els) > index:
                els[index].click()
                self._back_to_native()
                return True
        except Exception as e:
            print(f"[WARN] 웹뷰 인덱스 클릭 실패: {e}")
            self._back_to_native()
        return False
