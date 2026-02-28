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
            ("Add_Insurance_Btn",      "내 보험 추가",   "//*[contains(@text,'내 보험 추가') or contains(@text,'보험 추가')]"),
        ]
        for eng_id, kor_name, xpath in bottom_checks:
            self.scroll_until_visible(xpath, max_scrolls=8, check_timeout=1)
            shot = ss_func(f"S3_Elem_Bottom_{eng_id}") if ss_func else None
            if reporter:
                reporter.step(f"하단 요소 확인: {kor_name}", "PASSED", shot)
            print(f"[OK] 하단 요소 확인: {kor_name}")

    def verify_home_scroll_steps(self, ss_func, reporter):
        """홈 화면을 단계별로 한 블록씩 스크롤하며 요소 확인"""

        # 0️⃣ 홈 상단으로 이동
        self.scroll_up(times=5)

        # 1️⃣ 홈탭 진입 확인
        self.wait_for_element(self.HOME_TAB, timeout=5)
        shot = ss_func("S3_1_Home_Entry")
        reporter.step("홈탭 진입 확인", "PASSED", shot)
        print("[OK] 홈탭 진입 확인")

        # 2️⃣ 내 보험 종합진단
        self.wait_for_element("//*[contains(@text,'보험 종합진단')]", timeout=5)
        shot = ss_func("S3_2_Insurance_Diagnosis")
        reporter.step("내 보험 종합진단 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 종합진단 확인")
        self.scroll_down(1)

        # 3️⃣ 매월 내는 보험료
        self.wait_for_element("//*[contains(@text,'매월 내는 보험료')]", timeout=5)
        shot = ss_func("S3_3_Monthly_Premium")
        reporter.step("매월 내는 보험료 노출 확인", "PASSED", shot)
        print("[OK] 매월 내는 보험료 확인")
        self.scroll_down(1)

        # 4️⃣ AI 고민상담소
        self.scroll_until_visible(self.AI_CONSULTING, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3_4_AI_Consulting")
        reporter.step("AI 고민상담소 노출 확인", "PASSED", shot)
        print("[OK] AI 고민상담소 확인")
        self.scroll_down(1)

        # 5️⃣ 숨은 보험금
        self.scroll_until_visible("//*[contains(@text,'숨은 보험금')]", max_scrolls=5, check_timeout=1)
        shot = ss_func("S3_5_Hidden_Insurance")
        reporter.step("숨은 보험금 노출 확인", "PASSED", shot)
        print("[OK] 숨은 보험금 확인")
        self.scroll_down(1)

        # 6️⃣ 이런 상황일 때 OR 손해사정사에게
        target_xpath = (
            "//*[contains(@text,'이런 상황일 때') or "
            "contains(@text,'손해사정사에게')]"
        )
        self.scroll_until_visible(target_xpath, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3_6_Situation_Or_Adjuster")
        reporter.step("'이런 상황일 때' 또는 '손해사정사에게' 노출 확인", "PASSED", shot)
        print("[OK] 상황 안내 영역 확인")

        # 🔽 가장 아래로 이동
        self.scroll_to_bottom()

        # 7️⃣ 건강정보 확인하기
        self.scroll_until_visible(self.HEALTH_INFO_BTN, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3_7_Health_Info")
        reporter.step("건강정보 확인하기 노출 확인", "PASSED", shot)
        print("[OK] 건강정보 확인하기 확인")

    def click_add_insurance(self):
        print("> 홈 화면 하단 '내 보험 추가하기' 영역 찾는 중...")
        self.driver.execute_script('mobile: unlock')
        self.scroll_to_text("내 보험 추가")
        self.click(self.ADD_INSURANCE_BUTTON, "S5_AddInsurance_Click")
