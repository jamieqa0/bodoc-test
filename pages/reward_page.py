# -*- coding: utf-8 -*-
from pages.base_page import BasePage
import time

class RewardPage(BasePage):
    REWARD_TAB = "//*[@text='보상']"

    def go_reward(self, ss_func=None, reporter=None):
        REWARD_ICON = "//*[@text='보상' and (contains(@resource-id, 'tab') or contains(@resource-id, 'bottom'))]"
        if not _try_find(self.driver, REWARD_ICON):
            REWARD_ICON = "//*[@text='보상']"

        self.click(REWARD_ICON, "Move_To_Reward_Tab")
        time.sleep(1.5)
        if ss_func:
            shot = ss_func("RewardTab_Entry")
            if reporter:
                reporter.step("보상 탭 진입 확인", "PASSED", shot)

    def verify_elements(self, ss_func=None, reporter=None):
        checks = [
            ("Reward_Claim", "보험금 청구", "//*[contains(@text,'청구') or contains(@text,'접수') or contains(@text,'받기')]"),
            ("Reward_Guide", "가이드/서류", "//*[contains(@text,'가이드') or contains(@text,'방법') or contains(@text,'서류')]"),
        ]
        for eng_id, kor_name, xpath in checks:
            if reporter:
                reporter.step(f"요소 대기: {kor_name}")
            self.wait_for_element(xpath, timeout=10)
            print(f"[OK] 요소 확인: {kor_name}")
            if reporter:
                reporter.step(f"요소 확인 완료: {kor_name}", "PASSED")
                if ss_func:
                    shot = ss_func(f"S7_Elem_{eng_id}")
                    reporter.step(f"스크린샷: {kor_name}", "PASSED", shot)

def _try_find(driver, xpath):
    from appium.webdriver.common.appiumby import AppiumBy
    try:
        driver.find_element(AppiumBy.XPATH, xpath)
        return True
    except:
        return False
