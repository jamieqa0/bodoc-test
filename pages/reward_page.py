# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.appiumby import AppiumBy

class RewardPage(BasePage):
    REWARD_TAB   = "//*[@text='보상']"
    # 콘텐츠 영역에 '보상' 텍스트가 중복 존재할 수 있으므로 [last()]로 탭바 아이콘 선택
    REWARD_ICON  = "(//*[@text='보상' or @content-desc='보상'])[last()]"
    TARGET_TEXT  = "유형별 보상 사례 / 자주 묻는 보상 질문"
    TARGET_XPATH = (
        "//*[contains(@text,'유형별 보상 사례')"
        " or contains(@text,'유형별 보상사례')"
        " or contains(@text,'병원비 간편 청구하기')"
        " or contains(@text,'자주 묻는 보상 질문')"
        " or contains(@text,'보상 문의하기')"
        " or contains(@text,'보상 질문')]"
    )

    def go_reward(self, ss_func=None, reporter=None):
        self.wait_for_home()
        self.click(self.REWARD_ICON, "Move_To_Reward_Tab")
        # 탭 전환 후 보상 탭 콘텐츠가 로드될 때까지 대기
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_elements(AppiumBy.XPATH, self.REWARD_TAB)
        )
        if ss_func:
            shot = ss_func("RewardTab_Entry")
            if reporter:
                reporter.step("보상 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        """보상 탭 주요 요소를 순차적으로 확인"""
        # 1️⃣ 스크롤하며 대상 탐색
        if reporter:
            reporter.step(f"화면 스크롤하며 대상 탐색: {self.TARGET_TEXT}", "INFO")
        self.scroll_to_text("보상 사례")

        # 2️⃣ 해당 타이틀 영역 노출 확인
        try:
            self.wait_for_element(self.TARGET_XPATH, timeout=7)
            shot = ss_func("S7_2_Elem_Reward_Case") if ss_func else None
            if reporter:
                reporter.step(f"'{self.TARGET_TEXT}' 노출 확인", "PASSED", shot)
            print(f"[OK] 타이틀 확인: {self.TARGET_TEXT}")

        except TimeoutException:
            shot = ss_func("S7_2_FAIL_Reward_Case") if ss_func else None
            if reporter:
                reporter.step(f"'{self.TARGET_TEXT}' 노출 확인 실패", "FAILED", shot)
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{self.TARGET_TEXT}'")
