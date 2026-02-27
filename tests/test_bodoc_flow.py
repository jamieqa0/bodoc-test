# -*- coding: utf-8 -*-
import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import scenario_context
from pages.intro_page import IntroPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.diagnosis_page import DiagnosisPage


# ══════════════════════════════════════════════════════════════════
# 시나리오 1 : 앱 런치
# ══════════════════════════════════════════════════════════════════
def test_scenario_1_app_launch(driver, ss, reporter):
    """앱이 정상적으로 실행되고 초기 화면이 나타나는지 확인"""
    with scenario_context(reporter, "시나리오1_앱_런치", ss, "S1"):
        time.sleep(1)

        shot = ss("S1_Entry_LaunchScreen")
        reporter.step("앱 실행 및 초기화면 진입", "PASSED", shot)

        found = any(
            _try_find(driver, xpath)
            for xpath in [
                "//*[contains(@text,'카카오')]",
                "//*[@text='홈']",
                "//*[contains(@text,'보닥')]",
                "//*[contains(@text,'보험')]",
            ]
        )

        if found:
            reporter.step("앱 화면 요소 확인", "PASSED")
        else:
            reporter.step("앱 화면 요소 확인", "FAILED")
            raise AssertionError("앱 초기 화면 요소를 찾을 수 없습니다.")

        print("[완료] 시나리오 1 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 2 : 카카오 로그인
# ══════════════════════════════════════════════════════════════════
def test_scenario_2_kakao_login(driver, ss, reporter):
    """카카오 계정으로 로그인 완료까지 확인 (이미 로그인된 경우 자동 스킵)"""
    with scenario_context(reporter, "시나리오2_카카오_로그인", ss, "S2"):
        intro = IntroPage(driver, ss)
        login = LoginPage(driver, ss)

        shot = ss("S2_Entry_InitialScreen")
        reporter.step("앱 초기화면 진입", "PASSED", shot)

        # 이미 홈 화면(로그인됨)이면 스킵
        if _try_find(driver, "//*[@text='홈']"):
            shot = ss("S2_Already_Logged_In")
            reporter.step("이미 로그인 상태 — 스킵", "PASSED", shot)
            reporter.end_scenario("PASSED")
            print("[완료] 시나리오 2 — 이미 로그인됨")
            return

        # 초기 권한 화면 처리 (없어도 무시)
        intro.process_initial_rights()
        intro.allow_phone_permission()
        intro.confirm_notification_guide()
        intro.allow_notification_permission()

        # 로그인 화면 확인
        if not _try_find(driver, "//*[@text='카카오로 시작하기']"):
            shot = ss("S2_FAIL_LoginScreen_Not_Found")
            reporter.step("로그인 화면 확인", "FAILED", shot)
            raise AssertionError("카카오 로그인 버튼을 찾을 수 없습니다.")

        shot = ss("S2_Entry_LoginScreen")
        reporter.step("로그인 화면 진입 확인", "PASSED", shot)

        login.start_kakao_login()
        time.sleep(2)
        shot = ss("S2_Switch_KakaoWebView")
        reporter.step("카카오 로그인 버튼 클릭 → 웹뷰 전환", "PASSED", shot)

        login.click_kakao_continue()
        time.sleep(2)
        shot = ss("S2_Switch_After_Continue")
        reporter.step("카카오 계속하기 클릭", "PASSED", shot)

        login.select_first_kakao_account()
        time.sleep(3)
        shot = ss("S2_Switch_After_Account_Select")
        reporter.step("카카오 계정 선택", "PASSED", shot)

        # #8: 15회 루프 → WebDriverWait
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='홈']"))
            )
            shot = ss("S2_Switch_HomeTab_Reached")
            reporter.step("로그인 완료 → 홈 화면 전환 확인", "PASSED", shot)
        except Exception:
            shot = ss("S2_FAIL_HomeTab_Not_Reached")
            reporter.step("로그인 완료 → 홈 화면 전환 확인", "FAILED", shot)
            raise AssertionError("로그인 후 홈 화면으로 이동하지 않았습니다.")

        print("[완료] 시나리오 2 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 3 : 홈 탭 요소 확인 + 하단까지 스크롤
# ══════════════════════════════════════════════════════════════════
def test_scenario_3_home_tab(driver, ss, reporter):
    """홈 탭 주요 요소 확인"""
    with scenario_context(reporter, "시나리오3_홈탭_검증", ss, "S3"):
        home = HomePage(driver, ss)

        home.go_home()
        time.sleep(1)
        shot = ss("S3_Entry_HomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        home.verify_home_elements(ss, reporter)
        home.scroll_to_bottom(ss, reporter)

        print("[완료] 시나리오 3 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 4 : 진단 탭 요소 확인 + 하단까지 스크롤
# ══════════════════════════════════════════════════════════════════
def test_scenario_4_diagnosis_tab(driver, ss, reporter):
    """진단 탭 주요 요소 확인"""
    with scenario_context(reporter, "시나리오4_진단탭_검증", ss, "S4"):
        diagnosis = DiagnosisPage(driver, ss)

        shot = ss("S4_HomeTab_Status_Before_Switch")
        reporter.step("홈 탭 상태 (전환 전)", "PASSED", shot)

        diagnosis.go_diagnosis(ss, reporter)
        diagnosis.verify_diagnosis_elements(ss, reporter)
        diagnosis.scroll_to_bottom(ss, reporter)
        
        # 신규 추가: 내 보험료 탭 확인
        diagnosis.verify_insurance_premium(ss, reporter)

        print("[완료] 시나리오 4 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 5 : 상품 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_5_product_tab(driver, ss, reporter):
    """상품 탭 주요 요소 확인"""
    from pages.product_page import ProductPage
    with scenario_context(reporter, "시나리오5_상품탭_검증", ss, "S5"):
        product = ProductPage(driver, ss)
        product.go_product(ss, reporter)
        product.verify_elements(ss, reporter)
        print("[완료] 시나리오 5 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 6 : 건강 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_6_health_tab(driver, ss, reporter):
    """건강 탭 주요 요소 확인"""
    from pages.health_page import HealthPage
    with scenario_context(reporter, "시나리오6_건강탭_검증", ss, "S6"):
        health = HealthPage(driver, ss)
        health.go_health(ss, reporter)
        health.verify_elements(ss, reporter)
        print("[완료] 시나리오 6 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 7 : 보상 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_7_reward_tab(driver, ss, reporter):
    """보상 탭 주요 요소 확인"""
    from pages.reward_page import RewardPage
    with scenario_context(reporter, "시나리오7_보상탭_검증", ss, "S7"):
        reward = RewardPage(driver, ss)
        reward.go_reward(ss, reporter)
        reward.verify_elements(ss, reporter)
        print("[완료] 시나리오 7 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 10 : 홈 탭에서 마이데이터 연동
# ══════════════════════════════════════════════════════════════════
@pytest.mark.skip(reason="시나리오10 작업 중 — 일시 비활성화")
def test_scenario_10_mydata(driver, ss, reporter):
    """홈 탭 → 내 보험 추가하기 → 40개 연결 → 네이버 인증 → 약관 → 진단받기 → 채팅 종료"""
    with scenario_context(reporter, "시나리오10_마이데이터_연동", ss, "S10"):
        from pages.mydata_flow import MydataFlow

        home = HomePage(driver, ss)
        ins = MydataFlow(driver, ss)

        # 이전 세션 웹뷰 등 초기화
        try:
            driver.switch_to.context('NATIVE_APP')
        except Exception:
            pass
        for _ in range(4):
            if _try_find(driver, "//*[@text='홈']"):
                break
            driver.press_keycode(4)
            time.sleep(0.7)

        home.go_home()
        time.sleep(1)
        shot = ss("S10_Entry_HomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        home.click_add_insurance()
        shot = ss("S10_Entry_Insurance_Connect")
        reporter.step("내 보험 추가하기 클릭 → 보험 연결 화면 진입", "PASSED", shot)

        ins.click_connect_40()
        shot = ss("S10_After_Connect40_Click")
        reporter.step("40개 연결하기 클릭", "PASSED", shot)

        ins.select_naver_cert()
        shot = ss("S10_Entry_Naver_Auth")
        reporter.step("네이버 인증서 선택", "PASSED", shot)

        ins.agree_and_continue()
        shot = ss("S10_After_Agree_Click")
        reporter.step("동의하고 계속하기", "PASSED", shot)

        ins.wait_for_connection()
        shot = ss("S10_DataConnect_Complete")
        reporter.step("마이데이터 연결 대기 완료", "PASSED", shot)

        ins.click_final_confirms()
        shot = ss("S10_Result_Confirm_Complete")
        reporter.step("결과 확인 클릭 완료", "PASSED", shot)

        ins.dismiss_extra_agreements()
        shot = ss("S10_Extra_Agree_Complete")
        reporter.step("추가 약관 동의 처리 완료", "PASSED", shot)

        ins.get_insurance_diagnosis()
        shot = ss("S10_Entry_Diagnosis_Result")
        reporter.step("보험 진단받기 클릭 → 진단 화면 진입", "PASSED", shot)

        ins.close_chat()
        shot = ss("S10_Chat_Closed")
        reporter.step("전문가 채팅 종료", "PASSED", shot)

        print("[완료] 시나리오 10 성공")


# ── 헬퍼 ─────────────────────────────────────────────────────────
def _try_find(driver, xpath):
    """요소 존재 여부를 bool로 반환. 예외는 무시."""
    try:
        driver.find_element(AppiumBy.XPATH, xpath)
        return True
    except Exception:
        return False
