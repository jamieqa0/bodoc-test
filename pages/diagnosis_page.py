# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time


class DiagnosisPage(BasePage):
    DIAGNOSIS_TAB = "//*[@text='진단']"

    def go_diagnosis(self, ss_func=None, reporter=None):
        self.wait_for_home()
        self.click(self.DIAGNOSIS_TAB, "DiagnosisTab_Move")
        time.sleep(1)
        if ss_func:
            shot = ss_func("DiagnosisTab_Entry")
            if reporter:
                reporter.step("진단탭 진입", "PASSED", shot)

    def verify_diagnosis_elements(self, ss_func=None, reporter=None):
        # (영문ID, 한글명, XPath)
        checks = [
            ("Diagnosis_Tab_Nav",   "진단 탭 네비게이션",    "//*[@text='진단']"),
            ("Diagnosis_Text_Check","보험 진단 관련 텍스트", "//*[contains(@text,'진단') or contains(@text,'보험료') or contains(@text,'분석')]"),
        ]
        for eng_id, kor_name, xpath in checks:
            self.wait_for_element(xpath, timeout=5)
            shot = ss_func(f"S4_Elem_{eng_id}") if ss_func else None
            if reporter:
                reporter.step(f"요소 확인: {kor_name}", "PASSED", shot)
            print(f"[OK] 요소 확인: {kor_name}")

    def scroll_to_bottom(self, ss_func=None, reporter=None):
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S4_Scroll_Diagnosis_Mid")
            if reporter:
                reporter.step("진단 스크롤 (중간)", "PASSED", shot)
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S4_Scroll_Diagnosis_Bottom")
            if reporter:
                reporter.step("진단 스크롤 (하단)", "PASSED", shot)

    def verify_insurance_premium(self, ss_func=None, reporter=None):
        """'내 보험료' 탭으로 이동하여 보험료 금액이 표시되는지 확인"""
        print("> '내 보험료' 탭 찾는 중 (상단)...")
        
        # 하단까지 내려갔으므로 다시 위로 충분히 스크롤 (탭은 보통 상단에 위치)
        self.scroll_up(5)
        time.sleep(1)
        
        # 탭 이동 (XPath 유연화: 공백 유무 대응)
        PREMIUM_TAB = "//*[contains(@text,'내 보험료') or contains(@text,'내보험료')]"
        
        try:
            self.click(PREMIUM_TAB, "Move_To_Premium_Tab")
        except Exception as e:
            # 텍스트로 못 찾을 경우, 좌표 기반 클릭으로 최후의 시도 (상단 탭 영역)
            print(f"[WARN] 탭 텍스트 클릭 실패, 좌표로 시도합니다: {e}")
            self.tap_coordinate(0.5, 0.15, "Tap_Premium_Tab_Fallback")
            time.sleep(1.5)
        
        if ss_func:
            shot = ss_func("S4_Premium_Tab_Entry")
            if reporter:
                reporter.step("'내 보험료' 탭 진입", "PASSED", shot)
        
        # '매월 내는 보험료' 텍스트 및 금액 확인
        PREMIUM_TITLE = "//*[contains(@text,'매월 내는 보험료')]"
        PREMIUM_VALUE = "//*[contains(@text,'원') and string-length(@text) > 2]"
        
        try:
            self.wait_for_element(PREMIUM_TITLE, timeout=5)
            print("[OK] '매월 내는 보험료' 타이틀 확인")
            if reporter:
                reporter.step("'매월 내는 보험료' 타이틀 확인", "PASSED")
            
            val_el = self.wait_for_element(PREMIUM_VALUE, timeout=5)
            amount_text = val_el.text
            print(f"[OK] 보험료 금액 확인됨: {amount_text}")
            
            if reporter:
                reporter.step(f"보험료 금액 확인: {amount_text}", "PASSED")
                if ss_func:
                    shot = ss_func("S4_Premium_Amount_Check")
                    reporter.step("보험료 금액 스크린샷", "PASSED", shot)
        except Exception as e:
            print(f"[FAIL] 보험료 정보 미확인: {e}")
            if reporter:
                shot = ss_func("S4_FAIL_Premium_Check") if ss_func else None
                reporter.step("보험료 정보 확인 실패", "FAILED", shot)
            raise e
