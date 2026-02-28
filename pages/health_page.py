# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException
import time

class HealthPage(BasePage):
    HEALTH_TAB   = "//*[@text='건강']"
    # 콘텐츠 영역에 '건강' 텍스트가 중복 존재할 수 있으므로 [last()]로 탭바 아이콘 선택
    HEALTH_ICON  = "(//*[@text='건강' or @content-desc='건강'])[last()]"
    TARGET_TEXT  = "건강 기록"
    TARGET_XPATH = "//*[contains(@text,'건강 기록')]"

    def go_health(self, ss_func=None, reporter=None):
        self.wait_for_home()
        self.click(self.HEALTH_ICON, "Move_To_Health_Tab")
        time.sleep(1.5)
        if ss_func:
            shot = ss_func("HealthTab_Entry")
            if reporter:
                reporter.step("건강 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        """건강 탭 주요 요소를 순차적으로 확인"""
        # 1️⃣ 화면을 스크롤하며 대상 요소 탐색
        if reporter:
            reporter.step(f"화면 스크롤하며 대상 탐색: {self.TARGET_TEXT}")
        self.scroll_to_text(self.TARGET_TEXT)

        # 2️⃣ "건강 기록" 타이틀 노출 확인
        try:
            self.wait_for_element(self.TARGET_XPATH, timeout=7)
            shot = ss_func("S6_2_Elem_Health_Record") if ss_func else None
            if reporter:
                reporter.step(f"'{self.TARGET_TEXT}' 노출 확인", "PASSED", shot)
            print(f"[OK] 타이틀 확인: {self.TARGET_TEXT}")

        except TimeoutException:
            shot = ss_func("S6_2_FAIL_Health_Record") if ss_func else None
            if reporter:
                reporter.step(f"'{self.TARGET_TEXT}' 노출 확인 실패", "FAILED", shot)
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{self.TARGET_TEXT}'")

