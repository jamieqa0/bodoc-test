# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class HealthPage(BasePage):
    HEALTH_TAB = "//*[@text='건강']"

    def go_health(self, ss_func=None, reporter=None):
        self.wait_for_home()
        # 상품 탭 콘텐츠 안에 '건강' 텍스트 요소가 중복 존재할 수 있으므로
        # [last()]로 DOM 순서상 마지막 요소(= 하단 탭바 아이콘)를 명시적으로 선택
        HEALTH_ICON = "(//*[@text='건강' or @content-desc='건강'])[last()]"

        self.click(HEALTH_ICON, "Move_To_Health_Tab")
        time.sleep(1.5)
        if ss_func:
            shot = ss_func("HealthTab_Entry")
            if reporter:
                reporter.step("건강 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        """건강 탭 주요 요소를 순차적으로 확인"""
        TARGET_TEXT = "건강 기록"
        TARGET_XPATH = "//*[contains(@text,'건강 기록')]"

        # 1️⃣ 화면을 스크롤하며 대상 요소 탐색
        if reporter:
            reporter.step(f"화면 스크롤하며 대상 탐색: {TARGET_TEXT}")
        self.scroll_to_text(TARGET_TEXT)

        # 2️⃣ "건강 기록" 타이틀 노출 확인
        try:
            self.wait_for_element(TARGET_XPATH, timeout=7)
            shot = ss_func("S6_2_Elem_Health_Record") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 노출 확인", "PASSED", shot)
            print(f"[OK] 타이틀 확인: {TARGET_TEXT}")
                
        except Exception:
            shot = ss_func("S6_2_FAIL_Health_Record") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 노출 확인 실패", "FAILED", shot)
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{TARGET_TEXT}'")

