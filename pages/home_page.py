# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy


class HomePage(BasePage):
    HOME_TAB             = "//*[@text='홈']"
    ADD_INSURANCE_BUTTON = "//*[contains(@text, '내 보험 추가하기') or contains(@text, '내 보험 추가')]"

    def go_home(self):
        self.wait_for_home()
        try:
            self.click(self.HOME_TAB, "HomeTab_Move")
        except Exception:
            pass  # 이미 홈이면 무시

    def verify_home_elements(self, ss_func=None, reporter=None):
        # 1. 상단에서 바로 보이는 요소들 (영문ID, 한글명, XPath, 스크롤필요여부)
        checks = [
            ("Home_Tab_Nav", "홈 탭 네비게이션", "//*[@text='홈']", False),
            ("Insurance_Diagnosis", "보험 종합진단", "//*[contains(@text,'보험 종합진단')]", False),
            ("Monthly_Premium", "매월 내는 보험료", "//*[contains(@text,'매월 내는 보험료')]", False),
        ]
        
        for eng_id, kor_name, xpath, needs_scroll in checks:
            try:
                if needs_scroll:
                    self.scroll_to_text(kor_name)

                self.wait_for_element(xpath, timeout=3)
                print(f"[OK] 요소 확인: {kor_name}")
                if reporter:
                    shot = ss_func(f"S3_Elem_{eng_id}") if ss_func else None
                    reporter.step(f"요소 확인: {kor_name}", "PASSED", shot)
            except Exception:
                print(f"[WARN] 요소 미확인: {kor_name}")
                if reporter:
                    shot = ss_func(f"S3_FAIL_{eng_id}") if ss_func else None
                    reporter.step(f"요소 확인: {kor_name}", "FAILED", shot)

        # 2. 하단에 위치하거나 보험 리스트 너머에 있는 요소들 (스크롤하며 확인)
        # max_swipes=5: 요소가 없을 때 최대 ~10초 이내로 포기 (기본 30회 → 150초+ 방지)
        bottom_checks = [
            ("Hidden_Insurance_Money", "숨은 보험금", "//*[contains(@text,'숨은 보험금')]"),
            ("Consult_Adjuster", "손해사정사", "//*[contains(@text,'손해사정사')]"),
            ("Add_Insurance_Btn", "내 보험 추가", "//*[contains(@text,'내 보험 추가') or contains(@text,'보험 추가')]"),
        ]

        for eng_id, kor_name, xpath in bottom_checks:
            try:
                self.scroll_to_text(kor_name, max_swipes=5)
                self.wait_for_element(xpath, timeout=2)
                print(f"[OK] 하단 요소 확인: {kor_name}")
                if reporter:
                    shot = ss_func(f"S3_Elem_Bottom_{eng_id}") if ss_func else None
                    reporter.step(f"하단 요소 확인: {kor_name}", "PASSED", shot)
            except Exception:
                print(f"[WARN] 하단 요소 미확인: {kor_name}")
                if reporter:
                    shot = ss_func(f"S3_FAIL_Bottom_{eng_id}") if ss_func else None
                    reporter.step(f"하단 요소 확인: {kor_name}", "FAILED", shot)

    def scroll_to_bottom(self, ss_func=None, reporter=None):
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S3_Scroll_Home_Mid")
            if reporter:
                reporter.step("홈 스크롤 (중간)", "PASSED", shot)
        self.scroll_down(2)
        if ss_func:
            shot = ss_func("S3_Scroll_Home_Bottom")
            if reporter:
                reporter.step("홈 스크롤 (하단)", "PASSED", shot)

    def click_add_insurance(self):
        print("> 홈 화면 하단 '내 보험 추가하기' 영역 찾는 중...")
        self.driver.execute_script('mobile: unlock')
        self.scroll_to_text("내 보험 추가")
        self.click(self.ADD_INSURANCE_BUTTON, "S5_AddInsurance_Click")
