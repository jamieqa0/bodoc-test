# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class ProductPage(BasePage):
    PRODUCT_TAB = "//*[@text='상품']"

    def go_product(self, ss_func=None, reporter=None):
        self.click(self.PRODUCT_TAB, "Move_To_Product_Tab")
        time.sleep(1)
        if ss_func:
            shot = ss_func("ProductTab_Entry")
            if reporter:
                reporter.step("상품 탭 진입", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        checks = [
            ("Product_Popular", "상품/랭킹", "//*[contains(@text,'상품') or contains(@text,'인기') or contains(@text,'랭킹')]"),
            ("Product_Recommend", "보험/추천", "//*[contains(@text,'보험') or contains(@text,'추천') or contains(@text,'맞춤')]"),
        ]
        for eng_id, kor_name, xpath in checks:
            if reporter:
                reporter.step(f"요소 대기: {kor_name}")
            self.wait_for_element(xpath, timeout=10)
            print(f"[OK] 요소 확인: {kor_name}")
            if reporter:
                reporter.step(f"요소 확인 완료: {kor_name}", "PASSED")
                if ss_func:
                    shot = ss_func(f"S5_Elem_{eng_id}")
                    reporter.step(f"스크린샷: {kor_name}", "PASSED", shot)
