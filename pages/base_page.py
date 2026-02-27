# -*- coding: utf-8 -*-
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# #3: 테스트 프레임워크(pytest)에 의존하지 않는 커스텀 예외
class ElementInteractionError(Exception):
    """요소를 찾거나 클릭하는 데 실패했을 때 발생."""


class BasePage:
    def __init__(self, driver, screenshot_func=None):
        self.driver = driver
        self.ss = screenshot_func

    def wait_for_home(self, timeout=15):
        """하단 탭바(홈)가 나타날 때까지 대기 — 단독 실행 시 앱 재시작 후 로그인 완료 보장"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_elements(AppiumBy.XPATH, "//*[@text='홈' or @content-desc='홈']")
            )
        except Exception:
            raise AssertionError("홈 화면 진입 실패 — 로그인 상태 또는 앱 초기화를 확인하세요.")

    def wait_for_element(self, xpath, timeout=5):
        """요소를 찾을 때까지 대기"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((AppiumBy.XPATH, xpath))
        )

    def click(self, xpath, step_name="Click"):
        """요소 클릭. StaleElement 발생 시 1회 재시도."""
        last_exc = None
        for attempt in range(2):
            try:
                element = self.wait_for_element(xpath, timeout=5)
                element.click()
                print(f"[OK] 클릭 성공: {step_name}")
                time.sleep(0.2)
                if self.ss:
                    self.ss(step_name.replace(" ", "_"))
                return
            except Exception as e:
                last_exc = e
                if attempt == 0 and "stale" in str(e).lower():
                    print(f"[WARN] '{step_name}' StaleElement — 0.5초 후 재시도...")
                    time.sleep(0.5)
                else:
                    break

        # 실패 시 디버그 정보 출력
        print(f"[DEBUG] '{step_name}' 클릭 실패. 현재 화면 주요 요소 (상위 15개):")
        for el in self.driver.find_elements(
            AppiumBy.XPATH, "//*[@text!='' or @content-desc!='']"
        )[:15]:
            try:
                txt = el.text or el.get_attribute("content-desc")
                if txt:
                    print(f"[DEBUG]   - {txt}")
            except Exception:
                pass

        if self.ss:
            self.ss(f"FAIL_{step_name.replace(' ', '_')}")

        # #3: pytest.fail() 대신 커스텀 예외 → 상위(scenario_context)에서 처리
        raise ElementInteractionError(f"클릭 실패: {step_name} — {last_exc}")

    def scroll_down(self, times=1):
        """화면 아래로 스크롤 (기본 1회)"""
        size = self.driver.get_window_size()
        w, h = size['width'], size['height']

        for _ in range(times):
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(w * 0.5, h * 0.8)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(w * 0.5, h * 0.2)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            time.sleep(0.5)

        print(f"[OK] 아래로 스크롤 {times}회 완료")

    def scroll_up(self, times=1):
        """화면 위로 스크롤 (기본 1회)"""
        size = self.driver.get_window_size()
        w, h = size['width'], size['height']

        for _ in range(times):
            actions = ActionChains(self.driver)
            actions.w3c_actions.pointer_action.move_to_location(w * 0.5, h * 0.2)
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.move_to_location(w * 0.5, h * 0.8)
            actions.w3c_actions.pointer_action.pointer_up()
            actions.perform()
            time.sleep(0.5)

        print(f"[OK] 위로 스크롤 {times}회 완료")

    def scroll_to_text(self, text):
        """텍스트가 보일 때까지 스크롤 (Android UiScrollable 사용)"""
        print(f"> '{text}' 요소를 찾는 중 (스크롤)...")
        try:
            self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                f'new UiScrollable(new UiSelector().scrollable(true).instance(0))'
                f'.scrollIntoView(new UiSelector().textContains("{text}").instance(0))'
            )
            time.sleep(0.5)
            print(f"[OK] '{text}' 발견!")
        except Exception as e:
            print(f"[WARN] '{text}' 스크롤 찾기 실패: {e}")
            self.scroll_down(2)

    def tap_coordinate(self, x_ratio, y_ratio, step_name="Tap"):
        """비율 기반 좌표 클릭"""
        size = self.driver.get_window_size()
        tap_x = int(size['width'] * x_ratio)
        tap_y = int(size['height'] * y_ratio)

        print(f"[INFO] 좌표 클릭: {step_name} (X={tap_x}, Y={tap_y})")
        actions = ActionChains(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(tap_x, tap_y)
        actions.w3c_actions.pointer_action.click()
        actions.perform()

        time.sleep(1)
        if self.ss:
            self.ss(step_name.replace(" ", "_"))
