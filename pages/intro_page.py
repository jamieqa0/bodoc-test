# -*- coding: utf-8 -*-
"""IntroPage — 앱 최초 실행 시 노출되는 권한 요청 팝업 Page Object.

각 메서드는 팝업이 감지되면 클릭 전에 스크린샷을 촬영하고 True를 반환한다.
팝업이 없으면 예외 없이 False를 반환하며 흐름을 유지한다.

재사용 구조:
  - 개별 메서드(process_initial_rights 등): 단독 호출 또는 커스텀 순서 제어에 사용
  - handle_all_initial_permissions(scenario_tag): 각 시나리오 공통 진입점
    - S2(초기 권한 팝업 처리 시나리오), S3(카카오 로그인 시나리오) 등에서 재사용

스크린샷 파일명 규칙:
  {scenario_tag}_{단계번호}_{권한종류}  예: S2_1_AccessRights, S2_2_PhonePermission
  타임스탬프는 ss() 함수가 자동으로 추가한다.
"""
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class IntroPage(BasePage):

    # ── 앱 내 안내 화면 ──────────────────────────────────────────────
    RIGHTS_SCREEN_TITLE = "//*[contains(@text,'접근권한 안내')]"  # 화면 타이틀 감지용
    RIGHTS_NEXT         = "//*[@text='다음']"   # 접근 권한 안내 화면의 '다음' 버튼
    NOTIF_CONFIRM       = "//*[@text='확인']"   # 알림 안내 팝업의 '확인' 버튼

    # ── Android 시스템 권한 다이얼로그 ───────────────────────────────
    ALLOW_BUTTON = "//*[@text='허용']"

    # ════════════════════════════════════════════════════════════════
    # Internal helper — 공통 스크린샷 + 클릭 로직
    # ════════════════════════════════════════════════════════════════

    def _try_click(self, xpath, label, timeout=5, ss_name=None):
        """요소가 있으면 스크린샷 촬영 후 클릭하고 True, 미노출이면 False를 반환.

        팝업이 노출된 상태를 기록하기 위해 클릭 전에 스크린샷을 촬영한다.
        WebDriverWait 기반으로만 동작하며 sleep을 사용하지 않는다.

        Args:
            xpath:   요소 XPath
            label:   로그 출력용 레이블
            timeout: 최대 대기 시간(초). 기본 5초.
            ss_name: 스크린샷 파일명 접두사. None이면 촬영하지 않는다.
        """
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((AppiumBy.XPATH, xpath))
            )
            # 팝업이 화면에 노출된 상태에서 스크린샷 촬영 (클릭 전)
            if ss_name and self.ss:
                try:
                    self.ss(ss_name)
                except Exception as e:
                    print(f"[SS-ERR] {ss_name} 스크린샷 저장 실패: {e}")
            el.click()
            print(f"[OK] {label}")
            return True
        except Exception:
            print(f"[INFO] {label}: 미노출, 건너뜀")
            return False

    # ════════════════════════════════════════════════════════════════
    # 개별 권한 처리 메서드 — 각 시나리오에서 독립적으로 재사용 가능
    # ════════════════════════════════════════════════════════════════

    def process_initial_rights(self, timeout=5, ss_name=None):
        """접근 권한 안내 화면 처리 — '다음' 버튼 클릭.

        버튼이 화면 아래에 있을 경우를 위해 스크롤 후 재시도한다.
        """
        if self._try_click(
            self.RIGHTS_NEXT, "접근 권한 안내 '다음' 클릭",
            timeout=timeout, ss_name=ss_name,
        ):
            return True
        # 스크롤 후 재시도 (버튼이 fold 아래에 있을 수 있음)
        try:
            self.scroll_down()
            return self._try_click(
                self.RIGHTS_NEXT, "접근 권한 안내 '다음' 클릭 (스크롤 후)",
                timeout=2, ss_name=ss_name,
            )
        except Exception:
            return False

    def allow_phone_permission(self, timeout=5, ss_name=None):
        """전화 권한 시스템 다이얼로그 — '허용' 클릭."""
        return self._try_click(
            self.ALLOW_BUTTON, "전화 권한 '허용' 클릭",
            timeout=timeout, ss_name=ss_name,
        )

    def confirm_notification_guide(self, timeout=5, ss_name=None):
        """앱 내 알림 안내 팝업 — '확인' 클릭."""
        return self._try_click(
            self.NOTIF_CONFIRM, "알림 안내 '확인' 클릭",
            timeout=timeout, ss_name=ss_name,
        )

    def allow_notification_permission(self, timeout=5, ss_name=None):
        """알림 권한 시스템 다이얼로그 — '허용' 클릭."""
        return self._try_click(
            self.ALLOW_BUTTON, "알림 권한 '허용' 클릭",
            timeout=timeout, ss_name=ss_name,
        )

    # ════════════════════════════════════════════════════════════════
    # 통합 처리 메서드 — 각 시나리오 공통 진입점
    # ════════════════════════════════════════════════════════════════

    def handle_all_initial_permissions(self, timeout=5, scenario_tag="S2"):
        """초기 권한 팝업 시퀀스 전체를 순서대로 처리한다.

        각 단계에서 팝업이 감지되면 클릭 전에 스크린샷을 자동으로 촬영한다.
        팝업이 없으면 조용히 건너뛰며 실패로 처리하지 않는다.

        처리 순서 및 자동 스크린샷 파일명:
          1. 접근 권한 안내 화면 → '다음'        → {scenario_tag}_1_AccessRights
          2. 전화 권한 시스템 다이얼로그 → '허용'  → {scenario_tag}_2_PhonePermission
          3. 앱 내 알림 안내 팝업 → '확인'        → {scenario_tag}_3_NotifGuide
          4. 알림 권한 시스템 다이얼로그 → '허용'  → {scenario_tag}_4_NotifPermission

        Args:
            timeout:      각 팝업을 찾을 최대 대기 시간(초). 기본 5초.
            scenario_tag: 스크린샷 파일명 접두사. 예: "S2", "S3"

        Returns:
            dict: 각 단계별 처리 여부.
                  {'rights': bool, 'phone': bool, 'notif_guide': bool, 'notif': bool}
        """
        results = {
            'rights': self.process_initial_rights(
                timeout=timeout,
                ss_name=f"{scenario_tag}_1_AccessRights",
            ),
            'phone': self.allow_phone_permission(
                timeout=timeout,
                ss_name=f"{scenario_tag}_2_PhonePermission",
            ),
            'notif_guide': self.confirm_notification_guide(
                timeout=timeout,
                ss_name=f"{scenario_tag}_3_NotifGuide",
            ),
            'notif': self.allow_notification_permission(
                timeout=timeout,
                ss_name=f"{scenario_tag}_4_NotifPermission",
            ),
        }
        handled = [k for k, v in results.items() if v]
        if handled:
            print(f"[OK] 권한 팝업 처리 완료: {handled}")
        else:
            print("[INFO] 권한 팝업 미노출 — 이미 허용됐거나 최초 실행이 아님")
        return results
