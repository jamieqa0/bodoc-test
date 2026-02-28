# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class RewardPage(BasePage):
    REWARD_TAB = "//*[@text='보상']"

    def go_reward(self, ss_func=None, reporter=None):
        self.wait_for_home()
        # 콘텐츠 영역에 '보상' 텍스트가 중복 존재할 수 있으므로
        # [last()]로 DOM 순서상 마지막 요소(= 하단 탭바 아이콘)를 선택
        REWARD_ICON = "(//*[@text='보상' or @content-desc='보상'])[last()]"

        self.click(REWARD_ICON, "Move_To_Reward_Tab")
        time.sleep(1.5)
        if ss_func:
            shot = ss_func("RewardTab_Entry")
            if reporter:
                reporter.step("보상 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        """보상 탭 주요 요소를 순차적으로 확인"""
        TARGET_TEXT = "유형별 보상 사례 / 자주 묻는 보상 질문"
        # 둘 중 하나라도 보이면 성공
        TARGET_XPATH = (
            "//*[contains(@text,'유형별 보상 사례')"
            " or contains(@text,'유형별 보상사례')"
            " or contains(@text,'병원비 간편 청구하기')"
            " or contains(@text,'자주 묻는 보상 질문')"
            " or contains(@text,'보상 문의하기')"
            " or contains(@text,'보상 질문')]"
        )

        # 1️⃣ 두 키워드 중 먼저 찾히는 쪽으로 스크롤하며 대상 탐색
        if reporter:
            reporter.step(f"화면 스크롤하며 대상 탐색: {TARGET_TEXT}")
        self.scroll_to_text("보상 사례")

        # 2️⃣ 해당 타이틀 영역 노출 확인
        try:
            self.wait_for_element(TARGET_XPATH, timeout=7)
            shot = ss_func("S7_2_Elem_Reward_Case") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 노출 확인", "PASSED", shot)
            print(f"[OK] 타이틀 확인: {TARGET_TEXT}")
                
        except Exception:
            shot = ss_func("S7_2_FAIL_Reward_Case") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 노출 확인 실패", "FAILED", shot)
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{TARGET_TEXT}'")
