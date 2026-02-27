# -*- coding: utf-8 -*-
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class LoginPage(BasePage):
    KAKAO_START_BUTTON = "//*[@text='카카오로 시작하기']"

    def start_kakao_login(self):
        self.click(self.KAKAO_START_BUTTON, "Scenario1_06_LoginHome_KakaoClick")

    def click_kakao_continue(self):
        """웹뷰 내 '계속하기' 버튼.
        #4: 웹뷰 컨텍스트에서 텍스트로 먼저 탐색, 실패 시 좌표 폴백.
        """
        if self._click_in_webview(["계속하기", "Continue", "동의"]):
            return
        # 폴백: 기기 화면 비율 기반 좌표
        self.tap_coordinate(0.5, 0.66, "Scenario1_07_KakaoWebView_Continue_Tap")

    def select_first_kakao_account(self):
        """첫 번째 카카오 계정 선택.
        #4: 웹뷰 컨텍스트에서 계정 목록 첫 항목 탐색, 실패 시 좌표 폴백.
        """
        if self._click_in_webview_index(0):
            return
        # 폴백: 기기 화면 비율 기반 좌표
        self.tap_coordinate(0.5, 0.20, "Scenario1_08_KakaoWebView_Account_Select_Tap")

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
