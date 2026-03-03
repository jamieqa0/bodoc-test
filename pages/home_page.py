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
        """홈 탭 주요 요소를 순차적으로 확인"""

        # 1️⃣ 홈 탭 네비게이션 확인 (상단 노출)
        self.wait_for_element(self.HOME_TAB, timeout=5)
        shot = ss_func("S3_2_Home_Tab_Nav") if ss_func else None
        if reporter:
            reporter.step("홈 탭 네비게이션 노출 확인", "PASSED", shot)
        print("[OK] 홈 탭 네비게이션 확인")

        # 2️⃣ 보험 종합진단 확인 (상단 노출)
        self.wait_for_element("//*[contains(@text,'보험 종합진단')]", timeout=5)
        shot = ss_func("S3_3_Home_Insurance_Diagnosis") if ss_func else None
        if reporter:
            reporter.step("보험 종합진단 노출 확인", "PASSED", shot)
        print("[OK] 보험 종합진단 확인")

        # 3️⃣ 매월 내는 보험료 확인 (상단 노출)
        self.wait_for_element("//*[contains(@text,'매월 내는 보험료')]", timeout=5)
        shot = ss_func("S3_4_Home_Monthly_Premium") if ss_func else None
        if reporter:
            reporter.step("매월 내는 보험료 노출 확인", "PASSED", shot)
        print("[OK] 매월 내는 보험료 확인")

        # 4️⃣ 숨은 보험금 확인 (스크롤 필요)
        self.scroll_until_visible("//*[contains(@text,'숨은 보험금')]", max_scrolls=8, check_timeout=1)
        shot = ss_func("S3_5_Home_Hidden_Insurance") if ss_func else None
        if reporter:
            reporter.step("숨은 보험금 노출 확인", "PASSED", shot)
        print("[OK] 숨은 보험금 확인")

        # 5️⃣ 내 보험 추가 확인 (스크롤 필요)
        self.scroll_until_visible("//*[contains(@text,'내 보험 추가') or contains(@text,'보험 추가')]", max_scrolls=8, check_timeout=1)
        shot = ss_func("S3_6_Home_Add_Insurance_Btn") if ss_func else None
        if reporter:
            reporter.step("내 보험 추가 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 추가 확인")

    def verify_home_scroll_steps(self, ss_func, reporter):
        """홈 화면을 단계별로 한 블록씩 스크롤하며 요소 확인"""

        # 0️⃣ 홈 상단으로 이동
        self.scroll_up(times=5)

        # 1️⃣ 홈탭 진입 확인
        self.wait_for_element(self.HOME_TAB, timeout=5)
        shot = ss_func("S3-1_2_Home_Entry")
        reporter.step("홈탭 진입 확인", "PASSED", shot)
        print("[OK] 홈탭 진입 확인")

        # 2️⃣ 내 보험 종합진단
        self.wait_for_element("//*[contains(@text,'보험 종합진단')]", timeout=5)
        shot = ss_func("S3-1_3_Home_Insurance_Diagnosis")
        reporter.step("내 보험 종합진단 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 종합진단 확인")
        self.scroll_down(1)

        # 3️⃣ 매월 내는 보험료
        self.wait_for_element("//*[contains(@text,'매월 내는 보험료')]", timeout=5)
        shot = ss_func("S3-1_4_Home_Monthly_Premium")
        reporter.step("매월 내는 보험료 노출 확인", "PASSED", shot)
        print("[OK] 매월 내는 보험료 확인")
        self.scroll_down(1)

        # 4️⃣ AI 고민상담소
        self.scroll_until_visible(self.AI_CONSULTING, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3-1_5_Home_AI_Consulting")
        reporter.step("AI 고민상담소 노출 확인", "PASSED", shot)
        print("[OK] AI 고민상담소 확인")
        self.scroll_down(1)

        # 5️⃣ 숨은 보험금
        self.scroll_until_visible("//*[contains(@text,'숨은 보험금')]", max_scrolls=5, check_timeout=1)
        shot = ss_func("S3-1_6_Home_Hidden_Insurance")
        reporter.step("숨은 보험금 노출 확인", "PASSED", shot)
        print("[OK] 숨은 보험금 확인")
        self.scroll_down(1)

        # 6️⃣ 이런 상황일 때 OR 손해사정사에게
        target_xpath = (
            "//*[contains(@text,'이런 상황일 때') or "
            "contains(@text,'손해사정사에게')]"
        )
        self.scroll_until_visible(target_xpath, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3-1_7_Home_Adjuster")
        reporter.step("'이런 상황일 때' 또는 '손해사정사에게' 노출 확인", "PASSED", shot)
        print("[OK] 상황 안내 영역 확인")

        # 🔽 가장 아래로 이동
        self.scroll_to_bottom()

        # 7️⃣ 건강정보 확인하기
        self.scroll_until_visible(self.HEALTH_INFO_BTN, max_scrolls=5, check_timeout=1)
        shot = ss_func("S3-1_8_Home_Health_Info")
        reporter.step("건강정보 확인하기 노출 확인", "PASSED", shot)
        print("[OK] 건강정보 확인하기 확인")

    def click_add_insurance(self):
        print("> 홈 화면 하단 '내 보험 추가하기' 영역 찾는 중...")
        self.driver.execute_script('mobile: unlock')
        self.scroll_to_text("내 보험 추가")
        self.click(self.ADD_INSURANCE_BUTTON, "S5_Home_AddInsurance_Click")
