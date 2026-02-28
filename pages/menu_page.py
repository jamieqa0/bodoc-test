# -*- coding: utf-8 -*-
from pages.base_page import BasePage


class MenuPage(BasePage):
    MENU_BUTTON = "(//*[@text='메뉴' or @content-desc='메뉴'])[1]"

    # (스크린샷 ID, 표시 이름, 스크롤 검색어, XPath 검증식, 추가 스크롤 횟수)
    SECTION_CHECKS = [
        (
            "Insurance",
            "보험",
            "보험",
            "//*[@text='보험' or @content-desc='보험']",
            0,
        ),
        (
            "Claim",
            "보상/청구",
            "보상",
            "//*[contains(@text,'보상') and contains(@text,'청구') "
            "or contains(@content-desc,'보상') and contains(@content-desc,'청구') "
            "or @text='보상/청구' or @content-desc='보상/청구']",
            0,
        ),
        (
            "Life",
            "생활/건강",
            "생활",
            "//*[contains(@text,'생활') and contains(@text,'건강') "
            "or contains(@content-desc,'생활') and contains(@content-desc,'건강') "
            "or @text='생활/건강' or @content-desc='생활/건강']",
            0,
        ),
        (
            "Info",
            "정보",
            "정보",
            "//*[@text='정보' or @content-desc='정보']",
            3,  # 하단에 위치하므로 scroll_to_text 전 추가 스크롤
        ),
        (
            "CustomerService",
            "고객서비스",
            "고객서비스",
            "//*[contains(@text,'고객서비스') or contains(@content-desc,'고객서비스')]",
            0,
        ),
    ]

    def open(self):
        """전체 메뉴 열기"""
        self.wait_for_home()
        self.click(self.MENU_BUTTON, "전체메뉴_열기")

    def verify_elements(self, ss_func=None, reporter=None):
        """전체 메뉴 스크롤 후 5개 섹션 타이틀 노출 확인"""
        for eng_id, kor_name, scroll_keyword, xpath, extra_scrolls in self.SECTION_CHECKS:
            if reporter:
                reporter.step(f"섹션 탐색 중: {kor_name}")

            # 항목에 따라 추가 스크롤 먼저 수행
            if extra_scrolls:
                self.scroll_down(extra_scrolls)

            # 해당 텍스트가 보일 때까지 스크롤
            self.scroll_to_text(scroll_keyword)

            try:
                self.wait_for_element(xpath, timeout=7)
                if reporter:
                    reporter.step(f"섹션 타이틀 노출 확인: {kor_name}", "PASSED")
                if ss_func:
                    shot = ss_func(f"S8_Section_{eng_id}")
                    if reporter:
                        reporter.step(f"스크린샷: {kor_name}", "PASSED", shot)
            except Exception:
                shot = ss_func(f"S8_FAIL_Section_{eng_id}") if ss_func else None
                if reporter:
                    reporter.step(f"섹션 타이틀 미발견: {kor_name}", "FAILED", shot)
                raise AssertionError(
                    f"섹션 타이틀을 찾을 수 없습니다: '{kor_name}'"
                )
