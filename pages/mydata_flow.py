# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.appiumby import AppiumBy


class MydataFlow(BasePage):
    # ── 액션 버튼 로케이터 ──────────────────────────────────────────
    CONNECT_40_BUTTON     = "//*[contains(@text,'연결하기')]"
    NAVER_CERT_BUTTON     = "//*[contains(@text,'네이버')]"
    AGREE_CONTINUE_BUTTON = "//*[contains(@text,'동의하고 계속하기')]"
    CONFIRM_BUTTON        = "//*[@text='확인' or @text='완료']"
    GET_DIAGNOSIS_BUTTON  = "//*[contains(@text,'진단받기')]"
    CHAT_X_BUTTON         = (
        "//*[contains(@content-desc,'닫기') or contains(@content-desc,'X')"
        " or @text='X']"
    )

    # ── 단계 완료 확인용 로케이터 ──────────────────────────────────
    # 인증서/약관 화면 도착 여부
    NAVER_SCREEN_XPATH = "//*[contains(@text,'인증') or contains(@text,'네이버')]"
    AGREE_SCREEN_XPATH = "//*[contains(@text,'동의') or contains(@text,'약관')]"
    # 연결 완료/결과 화면
    DONE_SCREEN_XPATH  = (
        "//*[contains(@text,'완료') or contains(@text,'연결되었')"
        " or contains(@text,'진단받기') or @text='확인' or @text='완료']"
    )
    # 진단 화면 진입 확인
    DIAGNOSIS_SCREEN_XPATH = (
        "//*[contains(@text,'진단') or contains(@text,'보험료') or @text='홈']"
    )

    def click_connect_40(self):
        """보험사 연결 화면에서 '연결하기' 클릭 후 인증 화면 대기"""
        print("> 보험사 연결 화면 하단으로 스크롤 중...")
        self.scroll_to_text("연결하기")
        self.click(self.CONNECT_40_BUTTON, "S10_Connect40_Click")
        # 네이버 인증서 또는 약관 화면 등장 대기
        WebDriverWait(self.driver, 10).until(
            lambda d: (
                d.find_elements(AppiumBy.XPATH, self.NAVER_SCREEN_XPATH)
                or d.find_elements(AppiumBy.XPATH, self.AGREE_SCREEN_XPATH)
            )
        )

    def select_naver_cert(self):
        """네이버 인증서 선택 후 약관 화면 대기"""
        self.click(self.NAVER_CERT_BUTTON, "S10_NaverCert_Select")
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_elements(AppiumBy.XPATH, self.AGREE_SCREEN_XPATH)
        )

    def agree_and_continue(self):
        """약관 동의 화면 스크롤 후 '동의하고 계속하기' 클릭"""
        print("> 약관 동의 화면 스크롤 하단 이동...")
        self.scroll_down()
        self.click(self.AGREE_CONTINUE_BUTTON, "S10_Agree_Continue")

    def wait_for_connection(self, timeout=90):
        """마이데이터 데이터 수집 완료 대기 (최대 90초, sleep 없이 폴링)"""
        print(f"> 마이데이터 데이터 수집 대기 중 (최대 {timeout}초)...")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.find_elements(AppiumBy.XPATH, self.DONE_SCREEN_XPATH)
            )
            print("[OK] 마이데이터 연결 완료 화면 확인")
        except Exception:
            print("[WARN] 연결 완료 화면을 확인하지 못했습니다. 계속 진행합니다.")

    def click_final_confirms(self):
        """결과 화면의 확인/완료 버튼을 최대 3회 처리"""
        for i in range(3):
            try:
                self.wait_for_element(self.CONFIRM_BUTTON, timeout=5)
                self.click(self.CONFIRM_BUTTON, f"S10_Result_Confirm_{i + 1}")
            except Exception:
                print(f"[INFO] 확인 버튼 {i + 1}회 처리 후 더 없음")
                break

    def dismiss_extra_agreements(self, max_attempts=5):
        """결과 확인 후 남아있는 추가 약관 동의 화면을 모두 처리"""
        print("> 추가 약관 동의 화면 처리 중...")
        for i in range(max_attempts):
            try:
                self.wait_for_element(self.AGREE_CONTINUE_BUTTON, timeout=3)
                print(f"  [추가동의 {i + 1}] '동의하고 계속하기' 발견 → 클릭")
                self.scroll_down()
                self.click(self.AGREE_CONTINUE_BUTTON, f"S10_ExtraAgree_{i + 1}")
                # 약관 버튼이 사라지거나 완료 화면이 나올 때까지 대기
                WebDriverWait(self.driver, 8).until(
                    lambda d: (
                        not d.find_elements(AppiumBy.XPATH, self.AGREE_CONTINUE_BUTTON)
                        or d.find_elements(AppiumBy.XPATH, self.DONE_SCREEN_XPATH)
                    )
                )
            except Exception:
                print(f"  [추가동의] 더 이상 동의 화면 없음 (총 {i}회 처리 완료)")
                break

    def get_insurance_diagnosis(self):
        """'진단받기' 버튼 탐색 후 클릭, 진단 화면 진입 대기"""
        print("> '진단받기' 버튼 찾는 중 (스크롤 후 클릭)...")
        self.scroll_to_text("진단받기")
        self.click(self.GET_DIAGNOSIS_BUTTON, "S10_GetDiagnosis_Click")
        WebDriverWait(self.driver, 15).until(
            lambda d: d.find_elements(AppiumBy.XPATH, self.DIAGNOSIS_SCREEN_XPATH)
        )

    def close_chat(self):
        """전문가 채팅 X 버튼 클릭 (실패 시 좌표 폴백)"""
        print("> 전문가 채팅 종료 시도 (X 버튼)...")
        try:
            self.click(self.CHAT_X_BUTTON, "S10_ChatClose_Click")
        except Exception:
            print("[WARN] 채팅 X 버튼 클릭 실패. 좌표 클릭 시도...")
            self.tap_coordinate(0.92, 0.05, "S10_ChatClose_Tap")
