# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy


class HomePage(BasePage):
    HOME_TAB             = "//*[@text='홈']"
    ADD_INSURANCE_BUTTON = "//*[contains(@text, '내 보험 추가하기') or contains(@text, '내 보험 추가')]"
    AI_CONSULTING        = "//*[contains(@text,'AI 고민상담소')]"
    HEALTH_INFO_BTN      = "//*[contains(@text,'건강정보 확인하기')]"

    def go_home(self):
        self.wait_for_home()
        try:
            self.click(self.HOME_TAB, "HomeTab_Move")
        except Exception:
            pass  # 이미 홈이면 무시

    def verify_home_elements(self, ss_func=None, reporter=None):
        # 1. 상단에서 바로 보이는 요소들 (영문ID, 한글명, XPath, 스크롤필요여부)
        checks = [
            ("Home_Tab_Nav",        "홈 탭 네비게이션", "//*[@text='홈']",                              False),
            ("Insurance_Diagnosis", "보험 종합진단",    "//*[contains(@text,'보험 종합진단')]",          False),
            ("Monthly_Premium",     "매월 내는 보험료", "//*[contains(@text,'매월 내는 보험료')]",        False),
        ]
        for eng_id, kor_name, xpath, needs_scroll in checks:
            if needs_scroll:
                self.scroll_to_text(kor_name)
            self.wait_for_element(xpath, timeout=5)
            shot = ss_func(f"S3_Elem_{eng_id}") if ss_func else None
            if reporter:
                reporter.step(f"요소 확인: {kor_name}", "PASSED", shot)
            print(f"[OK] 요소 확인: {kor_name}")

        # 2. 하단 요소 — 스크롤하며 확인
        bottom_checks = [
            ("Hidden_Insurance_Money", "숨은 보험금",   "//*[contains(@text,'숨은 보험금')]"),
            ("Consult_Adjuster",       "손해사정사",     "//*[contains(@text,'손해사정사')]"),
            ("Add_Insurance_Btn",      "내 보험 추가",   "//*[contains(@text,'내 보험 추가') or contains(@text,'보험 추가')]"),
        ]
        for eng_id, kor_name, xpath in bottom_checks:
            self.scroll_until_visible(xpath, max_scrolls=8, check_timeout=1)
            shot = ss_func(f"S3_Elem_Bottom_{eng_id}") if ss_func else None
            if reporter:
                reporter.step(f"하단 요소 확인: {kor_name}", "PASSED", shot)
            print(f"[OK] 하단 요소 확인: {kor_name}")

    def verify_home_scroll_steps(self, ss_func, reporter):
        """시나리오 3-1: 홈탭 주요 요소를 순서대로 스크롤하며 확인.
        각 단계 실패 시 예외를 발생시켜 scenario_context 가 처리하도록 함."""
        # 이전 시나리오로 인해 화면이 하단에 있을 수 있으므로 상단으로 복귀
        self.scroll_up(times=5)

        # (영문ID, 한글명, XPath, 스크롤필요여부)
        # 매월 내는 보험료는 상단 노출 요소 — 스크롤 불필요
        # UiScrollable(scroll_to_text)은 이 기기에서 스와이프당 수십 초 소요 → 사용 안 함
        # scroll_until_visible: scroll_down(1) + XPath 체크 반복 방식으로 대체
        steps = [
            ("Insurance_Diagnosis", "내 보험 종합진단",  "//*[contains(@text,'보험 종합진단')]",    False),
            ("Monthly_Premium",     "매월 내는 보험료",  "//*[contains(@text,'매월 내는 보험료')]",  False),
            ("AI_Consulting",       "AI 고민상담소",     self.AI_CONSULTING,                        True),
            ("Hidden_Insurance",    "숨은 보험금",       "//*[contains(@text,'숨은 보험금')]",       True),
            ("Health_Info",         "건강정보 확인하기", self.HEALTH_INFO_BTN,                      True),
        ]
        for eng_id, kor_name, xpath, do_scroll in steps:
            if do_scroll:
                self.scroll_until_visible(xpath, max_scrolls=10, check_timeout=1)
            else:
                self.wait_for_element(xpath, timeout=5)
            shot = ss_func(f"S3_1_{eng_id}")
            reporter.step(f"요소 확인: {kor_name}", "PASSED", shot)
            print(f"[OK] 요소 확인: {kor_name}")

    def click_add_insurance(self):
        print("> 홈 화면 하단 '내 보험 추가하기' 영역 찾는 중...")
        self.driver.execute_script('mobile: unlock')
        self.scroll_to_text("내 보험 추가")
        self.click(self.ADD_INSURANCE_BUTTON, "S5_AddInsurance_Click")
