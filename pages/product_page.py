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
        TARGET_TEXT = "보닥 회원만을 위한 추천 상품"
        TARGET_XPATH = "//*[contains(@text,'보닥 회원만을 위한 추천 상품')]"

        if reporter:
            reporter.step(f"'{TARGET_TEXT}' 탐색 중")

        # 타이틀이 보일 때까지 스크롤
        self.scroll_to_text("보닥 회원만을 위한 추천 상품")

        try:
            self.wait_for_element(TARGET_XPATH, timeout=7)
            print(f"[OK] 타이틀 확인: {TARGET_TEXT}")
            if reporter:
                reporter.step(f"'{TARGET_TEXT}' 노출 확인", "PASSED")
            if ss_func:
                shot = ss_func("S5_Elem_Recommend_Title")
                if reporter:
                    reporter.step(f"{TARGET_TEXT} 스크린샷", "PASSED", shot)
        except Exception:
            if ss_func:
                ss_func("S5_FAIL_Recommend_Title")
            raise AssertionError(f"타이틀을 찾을 수 없습니다: '{TARGET_TEXT}'")
