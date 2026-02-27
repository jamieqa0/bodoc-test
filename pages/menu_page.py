# -*- coding: utf-8 -*-
from pages.base_page import BasePage


class MenuPage(BasePage):
    MENU_BUTTON = "//*[@content-desc='메뉴'] | //*[@content-desc='더보기'] | //*[@text='메뉴']"

    def open(self):
        """햄버거 메뉴 열기"""
        self.click(self.MENU_BUTTON, "햄버거메뉴_열기")

    def verify_elements(self, ss_func=None, reporter=None):
        checks = [
            ("메뉴 화면 진입", "//*[contains(@text,'설정') or contains(@text,'마이페이지') or contains(@text,'메뉴')]"),
        ]
        for name, xpath in checks:
            try:
                self.wait_for_element(xpath, timeout=5)
                if reporter:
                    reporter.step(f"요소 확인: {name}", "PASSED")
                    if ss_func:
                        shot = ss_func(f"메뉴_요소_{name[:15]}")
                        reporter.step(f"요소 스크린샷: {name}", "PASSED", shot)
            except Exception:
                if reporter:
                    reporter.step(f"요소 확인: {name}", "FAILED")
