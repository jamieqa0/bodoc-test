# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class ProductPage(BasePage):
    PRODUCT_TAB = "//*[@text='상품']"

    def go_product(self, ss_func=None, reporter=None):
        self.wait_for_home()
        self.click(self.PRODUCT_TAB, "Move_To_Product_Tab")
        time.sleep(1)
        if ss_func:
            shot = ss_func("ProductTab_Entry")
            if reporter:
                reporter.step("상품 탭 진입", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        """상품 탭 주요 요소를 순차적으로 확인"""
        TARGET_TEXT = "보닥 회원만을 위한 추천 상품"
        TARGET_XPATH = "//*[contains(@text,'보닥 회원만을 위한 추천 상품')]"

        # 1️⃣ 화면을 스크롤하며 대상 요소 탐색
        if reporter:
            reporter.step(f"화면 스크롤하며 대상 탐색: {TARGET_TEXT}")
        self.scroll_to_text(TARGET_TEXT)

        # 2️⃣ "보닥 회원만을 위한 추천 상품" 타이틀 노출 확인
        try:
            self.wait_for_element(TARGET_XPATH, timeout=7)
            shot = ss_func("S5_2_Elem_Recommend_Title") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 타이틀 노출 확인", "PASSED", shot)
            print(f"[OK] 타이틀 확인: {TARGET_TEXT}")
                
        except Exception:
            shot = ss_func("S5_2_FAIL_Recommend_Title") if ss_func else None
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 타이틀 노출 확인 실패", "FAILED", shot)
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{TARGET_TEXT}'")
