# -*- coding: utf-8 -*-
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage


class SplashPage(BasePage):
    """앱 초기 런치 시퀀스(스플래시 화면 + 앱백신 토스트)를 검증하는 Page Object.

    ⚠ 스플래시 로케이터 캘리브레이션 방법:
      - SPLASH_ACTIVITY_KEYWORD: adb shell dumpsys activity | grep mResumedActivity
      - SPLASH_LOGO: Appium Inspector 또는 adb shell uiautomator dump
    """

    # ── 스플래시 화면 ──────────────────────────────────────────────
    # Activity 이름 기반 감지 (대소문자 무관 포함 검사)
    SPLASH_ACTIVITY_KEYWORD = 'splash'

    # UI 요소 기반 감지 (폴백) — 실기기 resource-id 확인 후 수정
    SPLASH_LOGO = (
        "//*[contains(@resource-id,'com.mrp.doctor:id/') and ("
        "contains(@resource-id,'splash') or "
        "contains(@resource-id,'logo') or "
        "contains(@resource-id,'img') or "
        "contains(@resource-id,'icon'))]"
        " | //android.widget.ImageView[@package='com.mrp.doctor']"
    )

    # ── 앱백신 토스트 팝업 ──────────────────────────────────────────
    # TouchEn mVaccine 보안 라이브러리 기동 시 표시되는 Android Toast 메시지
    APPVACCINE_TOAST_TEXT = "TouchEn mVaccine이 구동중입니다."
    APPVACCINE_TOAST = (
        f"//android.widget.Toast[contains(@text,'TouchEn mVaccine')]"
    )

    # ── 핵심 검증: 스플래시 + 토스트 동시 감지 ────────────────────

    def verify_launch_sequence(self, timeout: int = 10) -> tuple:
        """스플래시 화면과 앱백신 토스트를 단일 폴링 루프에서 동시에 감지한다.

        두 요소가 거의 동시에 나타나고 토스트는 수 초 내에 사라지므로,
        순차 체크 대신 하나의 루프에서 각각 감지 여부를 누적 추적한다.

        Args:
            timeout: 두 조건 모두 감지될 때까지의 최대 대기 시간(초). 기본 10초.

        Returns:
            (splash_detected: bool, toast_detected: bool) 튜플.
            두 값이 모두 True일 때 완전 성공.
        """
        splash_detected = [False]
        toast_detected  = [False]

        def _poll(d):
            # 스플래시: 한 번 감지되면 이후 체크 생략
            if not splash_detected[0]:
                if (
                    self.SPLASH_ACTIVITY_KEYWORD in (d.current_activity or '').lower()
                    or bool(d.find_elements(AppiumBy.XPATH, self.SPLASH_LOGO))
                ):
                    splash_detected[0] = True
                    print(f"[OK] 스플래시 화면 감지 (activity: {d.current_activity})")

            # 토스트: 한 번 감지되면 이후 체크 생략
            if not toast_detected[0]:
                if bool(d.find_elements(AppiumBy.XPATH, self.APPVACCINE_TOAST)):
                    toast_detected[0] = True
                    print(f"[OK] 앱백신 토스트 감지: '{self.APPVACCINE_TOAST_TEXT}'")

            return splash_detected[0] and toast_detected[0]

        self.driver.implicitly_wait(0)  # 빠른 폴링을 위해 암묵적 대기 해제
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=0.2).until(_poll)
        except Exception:
            # timeout — 부분 감지 결과를 그대로 반환해 호출 측에서 분기 처리
            if not splash_detected[0]:
                print(
                    f"[WARN] 스플래시 화면 미감지 "
                    f"(activity: {self.driver.current_activity}, timeout: {timeout}s)"
                )
            if not toast_detected[0]:
                print(
                    f"[WARN] 앱백신 토스트 미감지 "
                    f"(기대 텍스트: '{self.APPVACCINE_TOAST_TEXT}', timeout: {timeout}s)"
                )
        finally:
            self.driver.implicitly_wait(5)  # 암묵적 대기 복원

        return splash_detected[0], toast_detected[0]
