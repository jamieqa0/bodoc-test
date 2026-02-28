from pages.base_page import BasePage

class IntroPage(BasePage):
    # Locators
    NEXT_BUTTON = "//*[@text='다음']"
    ALLOW_BUTTON = "//*[@text='허용']"
    CONFIRM_BUTTON = "//*[@text='확인']"

    def process_initial_rights(self):
        """초기 접근 권한 안내 처리 (있을 경우에만)"""
        try:
            self.scroll_down()
            self.click(self.NEXT_BUTTON, "Scenario1_01_Rights_Next_Click")
        except Exception:
            print("[INFO] 초기 접근 권한 안내 화면이 없어 다음으로 진행합니다.")

    def allow_phone_permission(self):
        try:
            self.click(self.ALLOW_BUTTON, "Scenario1_02_Permission_Phone_Allow")
        except Exception:
            print("[INFO] '전화' 권한 허용 버튼이 없어 다음으로 진행합니다.")

    def confirm_notification_guide(self):
        try:
            self.click(self.CONFIRM_BUTTON, "Scenario1_03_NotificationGuide_Confirm")
        except Exception:
            print("[INFO] 앱 알림 안내 확인 버튼이 없어 다음으로 진행합니다.")

    def allow_notification_permission(self):
        try:
            self.click(self.ALLOW_BUTTON, "Scenario1_04_Permission_Notification_Allow")
        except Exception:
            print("[INFO] '알림' 권한 허용 버튼이 없어 다음으로 진행합니다.")
