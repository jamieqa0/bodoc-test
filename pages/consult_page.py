# -*- coding: utf-8 -*-
from pages.base_page import BasePage


class ConsultPage(BasePage):
    # 상단 상담 버튼
    CONSULT_BUTTON         = "//*[@content-desc='상담'] | //*[@text='상담']"
    # 빠른상담 플로팅 버튼
    FLOATING_CONSULT_BUTTON = "//*[contains(@text,'빠른상담')] | //*[contains(@content-desc,'빠른상담')]"

    def open_from_top(self):
        """상단 바 상담 버튼으로 진입"""
        self.click(self.CONSULT_BUTTON, "Top_Consult_Open")

    def open_from_floating(self):
        """빠른상담 플로팅 버튼으로 진입"""
        self.click(self.FLOATING_CONSULT_BUTTON, "Floating_QuickConsult_Open")

    def verify_elements(self, ss_func=None, reporter=None):
        # (영문ID, 한글명, XPath)
        checks = [
            ("Consult_Entry", "상담 화면 진입", "//*[contains(@text,'상담')]"),
        ]
        for eng_id, kor_name, xpath in checks:
            try:
                self.wait_for_element(xpath, timeout=5)
                if reporter:
                    reporter.step(f"요소 확인: {kor_name}", "PASSED")
                    if ss_func:
                        shot = ss_func(f"Consult_Elem_{eng_id}")
                        reporter.step(f"스크린샷: {kor_name}", "PASSED", shot)
            except Exception:
                if reporter:
                    reporter.step(f"요소 확인: {kor_name}", "FAILED")
