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
            self.click(self.HOME_TAB, "HomeTabMove")
        except Exception:
            pass  # 이미 홈이면 무시

    def verify_home_elements(self, ss_func=None, reporter=None):
        """홈 탭 주요 요소를 순차적으로 확인 (시나리오 4)

        실제 화면 기준 상단 → 하단 순서:
          내 보험 종합진단 → 매월 내는 보험료 → 숨은 보험금 → 내 보험 추가하기
        """

        # 1️⃣ 홈 탭 네비게이션 확인 (상단 노출)
        self.wait_for_element(self.HOME_TAB, timeout=5)
        shot = ss_func("S4_2_HomeTabNav") if ss_func else None
        if reporter:
            reporter.step("홈 탭 네비게이션 노출 확인", "PASSED", shot)
        print("[OK] 홈 탭 네비게이션 확인")

        # 2️⃣ 내 보험 종합진단 확인 (상단 노출)
        self.wait_for_element("//*[contains(@text,'보험 종합진단')]", timeout=5)
        shot = ss_func("S4_3_HomeInsuranceDiagnosis") if ss_func else None
        if reporter:
            reporter.step("내 보험 종합진단 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 종합진단 확인")

        # 3️⃣ 매월 내는 보험료 확인 (상단 노출, 스크롤 불필요)
        self.wait_for_element("//*[contains(@text,'매월 내는 보험료')]", timeout=5)
        shot = ss_func("S4_4_HomeMonthlyPremium") if ss_func else None
        if reporter:
            reporter.step("매월 내는 보험료 노출 확인", "PASSED", shot)
        print("[OK] 매월 내는 보험료 확인")

        # 4️⃣ 숨은 보험금 확인 (스크롤 필요)
        self.scroll_until_visible("//*[contains(@text,'숨은 보험금')]", max_scrolls=8, check_timeout=1)
        shot = ss_func("S4_5_HomeHiddenInsurance") if ss_func else None
        if reporter:
            reporter.step("숨은 보험금 노출 확인", "PASSED", shot)
        print("[OK] 숨은 보험금 확인")

        # 5️⃣ 내 보험 추가하기 확인 (하단, 스크롤 필요)
        self.scroll_until_visible(self.ADD_INSURANCE_BUTTON, max_scrolls=10, check_timeout=1)
        shot = ss_func("S4_6_HomeAddInsuranceBtn") if ss_func else None
        if reporter:
            reporter.step("내 보험 추가하기 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 추가하기 확인")

    def verify_home_scroll_steps(self, ss_func, reporter):
        """홈 화면을 단계별로 스크롤하며 실제 화면 순서대로 요소 확인 (시나리오 5)

        실제 화면 기준 상단 → 하단 순서:
          내 보험 종합진단 → 매월 내는 보험료 → 숨은 보험금
          → 이런 상황일 때/손해사정사에게 → AI 고민상담소 → 건강정보 확인하기
        """

        # 0️⃣ 홈 상단으로 이동
        self.scroll_up(times=5)

        # 2️⃣ 홈탭 진입 확인 (scroll_up 후 탑 재확인; S5_1은 테스트에서 이미 촬영)
        self.wait_for_element(self.HOME_TAB, timeout=5)
        shot = ss_func("S5_2_HomeEntry")
        reporter.step("홈탭 진입 확인", "PASSED", shot)
        print("[OK] 홈탭 진입 확인")

        # 3️⃣ 내 보험 종합진단
        self.wait_for_element("//*[contains(@text,'보험 종합진단')]", timeout=5)
        shot = ss_func("S5_3_HomeInsuranceDiagnosis")
        reporter.step("내 보험 종합진단 노출 확인", "PASSED", shot)
        print("[OK] 내 보험 종합진단 확인")
        self.scroll_down(1)

        # 4️⃣ 매월 내는 보험료
        self.wait_for_element("//*[contains(@text,'매월 내는 보험료')]", timeout=5)
        shot = ss_func("S5_4_HomeMonthlyPremium")
        reporter.step("매월 내는 보험료 노출 확인", "PASSED", shot)
        print("[OK] 매월 내는 보험료 확인")
        self.scroll_down(1)

        # 5️⃣ 숨은 보험금 (실제 화면에서 매월 내는 보험료 다음에 등장)
        self.scroll_until_visible("//*[contains(@text,'숨은 보험금')]", max_scrolls=5, check_timeout=1)
        shot = ss_func("S5_5_HomeHiddenInsurance")
        reporter.step("숨은 보험금 노출 확인", "PASSED", shot)
        print("[OK] 숨은 보험금 확인")
        self.scroll_down(1)

        # 6️⃣ 이런 상황일 때 OR 손해사정사에게 (숨은 보험금 바로 아래)
        target_xpath = (
            "//*[contains(@text,'이런 상황일 때') or "
            "contains(@text,'손해사정사에게')]"
        )
        self.scroll_until_visible(target_xpath, max_scrolls=5, check_timeout=1)
        shot = ss_func("S5_6_HomeAdjuster")
        reporter.step("'이런 상황일 때' 또는 '손해사정사에게' 노출 확인", "PASSED", shot)
        print("[OK] 상황 안내 영역 확인")

        # 7️⃣ AI 고민상담소 (이런 상황일 때 아래에 위치)
        self.scroll_until_visible(self.AI_CONSULTING, max_scrolls=8, check_timeout=1)
        shot = ss_func("S5_7_HomeAIConsulting")
        reporter.step("AI 고민상담소 노출 확인", "PASSED", shot)
        print("[OK] AI 고민상담소 확인")

        # 🔽 가장 아래로 이동
        self.scroll_to_bottom()

        # 8️⃣ 건강정보 확인하기 (최하단)
        self.scroll_until_visible(self.HEALTH_INFO_BTN, max_scrolls=5, check_timeout=1)
        shot = ss_func("S5_8_HomeHealthInfo")
        reporter.step("건강정보 확인하기 노출 확인", "PASSED", shot)
        print("[OK] 건강정보 확인하기 확인")

    def click_add_insurance(self):
        print("> 홈 화면 하단 '내 보험 추가하기' 영역 찾는 중...")
        self.driver.execute_script('mobile: unlock')
        self.scroll_to_text("내 보험 추가")
        self.click(self.ADD_INSURANCE_BUTTON, "S5_Home_AddInsurance_Click")
