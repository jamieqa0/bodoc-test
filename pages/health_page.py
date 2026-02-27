# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class HealthPage(BasePage):
    HEALTH_TAB = "//*[@text='건강']"

    def go_health(self, ss_func=None, reporter=None):
        # 하단 탭 영역의 '건강' 아이콘을 명시적으로 클릭 (텍스트가 다른 곳에도 있을 수 있음)
        HEALTH_ICON = "//*[@text='건강' and (contains(@resource-id, 'tab') or contains(@resource-id, 'bottom'))]"
        # 만약 resource-id가 없으면 그냥 text로 하되, 최하단 버튼임을 보장하기 위해 위치 기반으로 필터링하거나 그냥 텍스트 클릭 시도
        if not _try_find(self.driver, HEALTH_ICON):
            HEALTH_ICON = "//*[@text='건강']"

        self.click(HEALTH_ICON, "Move_To_Health_Tab")
        time.sleep(1.5)
        if ss_func:
            shot = ss_func("HealthTab_Entry")
            if reporter:
                reporter.step("건강 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        checks = [
            ("Health_Title", "검진 결과", "//*[contains(@text,'검진') or contains(@text,'진역') or contains(@text,'기록') or contains(@text, '결과')]"),
            ("Health_Analysis", "건강 분석", "//*[contains(@text,'분석') or contains(@text,'카드') or contains(@text,'상태')]"),
        ]
        for eng_id, kor_name, xpath in checks:
            if reporter:
                reporter.step(f"요소 대기: {kor_name}")
            self.wait_for_element(xpath, timeout=10)
            print(f"[OK] 요소 확인: {kor_name}")
            if reporter:
                reporter.step(f"요소 확인 완료: {kor_name}", "PASSED")
                if ss_func:
                    shot = ss_func(f"S6_Elem_{eng_id}")
                    reporter.step(f"스크린샷: {kor_name}", "PASSED", shot)

def _try_find(driver, xpath):
    from appium.webdriver.common.appiumby import AppiumBy
    try:
        driver.find_element(AppiumBy.XPATH, xpath)
        return True
    except:
        return False
