# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.appiumby import AppiumBy


class DiagnosisPage(BasePage):
    DIAGNOSIS_TAB  = "//*[@text='진단']"
    PREMIUM_TAB    = "//*[contains(@text,'내 보험료') or contains(@text,'내보험료')]"
    PREMIUM_TITLE  = "//*[contains(@text,'매월 내는 보험료')]"
    PREMIUM_VALUE  = "//*[contains(@text,'원') and string-length(@text) > 2]"

    def go_diagnosis(self, ss_func=None, reporter=None):
        self.wait_for_home()
        self.click(self.DIAGNOSIS_TAB, "DiagnosisTabMove")
        # 탭 전환 후 진단 탭이 선택(활성화)될 때까지 대기
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_elements(AppiumBy.XPATH, self.DIAGNOSIS_TAB + "[@selected='true']")
        )
        if ss_func:
            shot = ss_func("S6_1_DiagnosisTabEntry")
            if reporter:
                reporter.step("진단탭 진입", "PASSED", shot)

    def verify_diagnosis_elements(self, ss_func=None, reporter=None):
        """진단 탭 주요 요소를 순차적으로 확인"""
        
        # 1️⃣ 진단 탭 네비게이션 확인
        self.wait_for_element(self.DIAGNOSIS_TAB, timeout=5)
        shot = ss_func("S6_2_DiagnosisTabNav") if ss_func else None
        if reporter:
            reporter.step("진단 탭 네비게이션 노출 확인", "PASSED", shot)
        print("[OK] 진단 탭 네비게이션 확인")

        # 2️⃣ 보험 진단 텍스트 요소 확인
        diagnosis_text_xpath = "//*[contains(@text,'진단') or contains(@text,'보험료') or contains(@text,'분석')]"
        self.wait_for_element(diagnosis_text_xpath, timeout=5)
        shot = ss_func("S6_3_DiagnosisTextCheck") if ss_func else None
        if reporter:
            reporter.step("보험 진단 관련 텍스트 노출 확인", "PASSED", shot)
        print("[OK] 보험 진단 관련 텍스트 확인")

    def scroll_to_bottom(self, ss_func=None, reporter=None):
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S6_4_ScrollDiagnosisMid")
            if reporter:
                reporter.step("진단 스크롤 (중간)", "PASSED", shot)
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S6_5_ScrollDiagnosisBottom")
            if reporter:
                reporter.step("진단 스크롤 (하단)", "PASSED", shot)

    def verify_insurance_premium(self, ss_func=None, reporter=None):
        """'내 보험료' 탭으로 이동하여 보험료 금액이 표시되는지 확인"""
        print("> '내 보험료' 탭 찾는 중 (상단)...")

        # 1️⃣ 상단 탭 영역으로 이동하기 위해 위로 스크롤 후 탭 등장 대기
        self.scroll_up(3)
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_elements(AppiumBy.XPATH, self.PREMIUM_TAB)
        )

        # 2️⃣ '내 보험료' 탭 클릭
        try:
            self.wait_for_element(self.PREMIUM_TAB, timeout=5)
            self.click(self.PREMIUM_TAB, "MoveToPremiumTab")
        except Exception as e:
            print(f"[WARN] 탭 텍스트 클릭 실패, 좌표로 시도합니다: {e}")
            self.tap_coordinate(0.75, 0.15, "TapPremiumTabFallback")
            # 좌표 탭 후 타이틀 등장 대기
            WebDriverWait(self.driver, 8).until(
                lambda d: d.find_elements(AppiumBy.XPATH, self.PREMIUM_TITLE)
            )
        
        shot = ss_func("S6_6_DiagnosisPremiumTabEntry") if ss_func else None
        if reporter:
            reporter.step("'내 보험료' 탭 진입", "PASSED", shot)
        
        # 3️⃣ '매월 내는 보험료' 타이틀 노출 확인
        try:
            self.wait_for_element(self.PREMIUM_TITLE, timeout=5)
            print("[OK] '매월 내는 보험료' 타이틀 확인")
            if reporter:
                reporter.step("'매월 내는 보험료' 타이틀 확인", "PASSED")

            # 4️⃣ 실제 보험료 금액 추출 및 확인
            val_el = self.wait_for_element(self.PREMIUM_VALUE, timeout=5)
            amount_text = val_el.text
            print(f"[OK] 보험료 금액 확인됨: {amount_text}")
            
            if reporter:
                shot = ss_func("S6_7_PremiumAmountCheck") if ss_func else None
                reporter.step(f"보험료 금액 확인: {amount_text}", "PASSED", shot)
        except Exception as e:
            print(f"[FAIL] 보험료 정보 미확인: {e}")
            if reporter:
                shot = ss_func("S6_7_FAIL_PremiumCheck") if ss_func else None
                reporter.step("보험료 정보 확인 실패", "FAILED", shot)
            raise e
