# -*- coding: utf-8 -*-
from pages.base_page import BasePage


class NotificationPage(BasePage):
    NOTIFICATION_BUTTON = "//*[@content-desc='알림'] | //*[@text='알림']"
    NOTIFICATION_LIST   = "//*[contains(@resource-id, 'notification')]"

    def open(self):
        self.click(self.NOTIFICATION_BUTTON, "알림_열기")

    def verify_elements(self, ss_func=None, reporter=None):
        checks = [
            ("알림 화면 진입", self.NOTIFICATION_LIST),
        ]
        for name, xpath in checks:
            try:
                self.wait_for_element(xpath, timeout=5)
                if reporter:
                    reporter.step(f"요소 확인: {name}", "PASSED")
                    if ss_func:
                        shot = ss_func(f"알림_요소_{name[:15]}")
                        reporter.step(f"요소 스크린샷: {name}", "PASSED", shot)
            except Exception:
                if reporter:
                    shot = ss_func(f"알림_FAIL_{name[:15]}") if ss_func else None
                    reporter.step(f"요소 확인: {name}", "FAILED", shot)
