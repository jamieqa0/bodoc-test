# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════
# 보닥 앱 자동화 테스트 — 시나리오 목록
# ──────────────────────────────────────────────────────────────────
# S1  앱 런치            앱 실행 후 초기화면 핵심 요소 존재 확인
# S2  카카오 로그인       카카오 계정 로그인 → 홈 화면 진입 확인
# S3  홈 탭             종합진단·보험료·숨은보험금·내보험추가 노출 확인
# S4  진단 탭           진단 탭 진입 → 내 보험료 금액 노출 확인
# S5  상품 탭           상품 탭 스크롤 → 추천 상품 섹션 타이틀 노출 확인
# S6  건강 탭           건강 탭 스크롤 → 건강 기록 섹션 타이틀 노출 확인
# S7  보상 탭           보상 탭 스크롤 → 보상 사례 섹션 타이틀 노출 확인
# S8  전체 메뉴         전체 메뉴 진입 → 5개 섹션 타이틀 순서대로 노출 확인
# S9  (미사용)
# S10 마이데이터 연동    내 보험 추가 → 40개 연결 → 진단 수행 (현재 SKIP)
# ══════════════════════════════════════════════════════════════════
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
from pages.menu_page import MenuPage


# ══════════════════════════════════════════════════════════════════
# 시나리오 1 : 앱 런치
# ══════════════════════════════════════════════════════════════════
def test_scenario_1_app_launch_initial_screen(driver, ss, reporter):
    """
    앱 런치
    [목적] 앱이 정상적으로 실행되고 초기화면 핵심 요소가 존재하는지 확인
    [재현] 앱 실행 → 1초 대기 → 화면 요소 존재 여부 체크
    [성공] 카카오·홈·보닥·보험 중 하나 이상 노출
    """
    with scenario_context(reporter, "S1 앱 런치", ss, "S1"):
        time.sleep(1)

        shot = ss("S1_Entry_LaunchScreen")
        reporter.step("앱 실행 후 초기화면 진입", "PASSED", shot)

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
            reporter.step("초기화면 핵심 요소 확인", "PASSED")
        else:
            reporter.step("초기화면 요소 미발견", "FAILED")
            raise AssertionError("앱 초기 화면 요소를 찾을 수 없습니다.")

        print("[완료] 시나리오 1 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 2 : 카카오 로그인
# ══════════════════════════════════════════════════════════════════
def test_scenario_2_kakao_login_home_entry(driver, ss, reporter):
    """
    카카오 로그인
    [목적] 카카오 계정으로 로그인 후 홈 화면까지 정상 진입하는지 확인
    [재현] 이미 로그인 상태이면 스킵 → 권한 처리 → 카카오로 시작하기 클릭
           → 계속하기 → 계정 선택 → 홈 탭 진입 대기
    [성공] 로그인 완료 후 홈 탭(하단 탭바)이 15초 이내 노출
    """
    with scenario_context(reporter, "S2 카카오 로그인", ss, "S2"):
        intro = IntroPage(driver, ss)
        login = LoginPage(driver, ss)

        shot = ss("S2_Entry_InitialScreen")
        reporter.step("앱 초기화면 진입 확인", "PASSED", shot)

        # 이미 홈 화면(로그인됨)이면 스킵
        if _try_find(driver, "//*[@text='홈']"):
            shot = ss("S2_Already_Logged_In")
            reporter.step("이미 로그인 상태 — 로그인 단계 스킵", "PASSED", shot)
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
            reporter.step("카카오 로그인 화면 미진입", "FAILED", shot)
            raise AssertionError("카카오 로그인 버튼을 찾을 수 없습니다.")

        shot = ss("S2_Entry_LoginScreen")
        reporter.step("로그인 화면 진입 확인", "PASSED", shot)

        login.start_kakao_login()
        time.sleep(2)
        shot = ss("S2_Switch_KakaoWebView")
        reporter.step("카카오 웹뷰 전환", "PASSED", shot)

        login.click_kakao_continue()
        time.sleep(2)
        shot = ss("S2_Switch_After_Continue")
        reporter.step("카카오 '계속하기' 클릭", "PASSED", shot)

        login.select_first_kakao_account()
        time.sleep(3)
        shot = ss("S2_Switch_After_Account_Select")
        reporter.step("첫 번째 카카오 계정 선택", "PASSED", shot)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='홈']"))
            )
            shot = ss("S2_Switch_HomeTab_Reached")
            reporter.step("홈 화면 진입 확인", "PASSED", shot)
        except Exception:
            shot = ss("S2_FAIL_HomeTab_Not_Reached")
            reporter.step("홈 화면 전환 실패", "FAILED", shot)
            raise AssertionError("로그인 후 홈 화면으로 이동하지 않았습니다.")

        print("[완료] 시나리오 2 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 3 : 홈 탭 요소 확인 + 하단까지 스크롤
# ══════════════════════════════════════════════════════════════════
def test_scenario_3_home_key_elements_visible(driver, ss, reporter):
    """
    홈 탭 검증
    [목적] 홈 탭의 주요 콘텐츠(보험 종합진단·보험료·숨은보험금 등)가 정상 노출되는지 확인
    [재현] 홈 탭 진입 → 상단 요소 확인 → 하단까지 스크롤하며 추가 요소 확인
    [성공] 보험 종합진단·매월 내는 보험료·숨은 보험금·내 보험 추가 노출
    """
    with scenario_context(reporter, "S3 홈 탭 검증", ss, "S3"):
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
def test_scenario_4_diagnosis_insurance_premium_visible(driver, ss, reporter):
    """
    진단 탭 검증
    [목적] 진단 탭 진입 후 '내 보험료' 탭에서 월 보험료 금액이 정상 노출되는지 확인
    [재현] 진단 탭 클릭 → 진단 요소 확인 → 하단 스크롤 → 내 보험료 탭 클릭
           → 매월 내는 보험료 타이틀 및 금액 노출 확인
    [성공] '매월 내는 보험료' 타이틀과 금액(원) 텍스트 노출
    """
    with scenario_context(reporter, "S4 진단 탭 검증", ss, "S4"):
        diagnosis = DiagnosisPage(driver, ss)

        shot = ss("S4_HomeTab_Status_Before_Switch")
        reporter.step("전환 전 화면 상태 기록", "PASSED", shot)

        diagnosis.go_diagnosis(ss, reporter)
        diagnosis.verify_diagnosis_elements(ss, reporter)
        diagnosis.scroll_to_bottom(ss, reporter)

        # 내 보험료 탭 확인
        diagnosis.verify_insurance_premium(ss, reporter)

        print("[완료] 시나리오 4 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 5 : 상품 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_5_product_recommend_section_visible(driver, ss, reporter):
    """
    상품 탭 검증
    [목적] 상품 탭 스크롤 시 '보닥 회원만을 위한 추천 상품' 섹션이 노출되는지 확인
    [재현] 상품 탭 클릭 → 아래로 스크롤 → 추천 상품 타이틀 노출 확인
    [성공] '보닥 회원만을 위한 추천 상품' 타이틀 텍스트 노출
    """
    from pages.product_page import ProductPage
    with scenario_context(reporter, "S5 상품 탭 검증", ss, "S5"):
        product = ProductPage(driver, ss)
        product.go_product(ss, reporter)
        product.verify_elements(ss, reporter)
        print("[완료] 시나리오 5 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 6 : 건강 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_6_health_record_section_visible(driver, ss, reporter):
    """
    건강 탭 검증
    [목적] 건강 탭 스크롤 시 '건강 기록' 섹션이 정상 노출되는지 확인
    [재현] 건강 탭 클릭 → 아래로 스크롤 → 건강 기록 타이틀 노출 확인
    [성공] '건강 기록' 타이틀 텍스트 노출
    """
    from pages.health_page import HealthPage
    with scenario_context(reporter, "S6 건강 탭 검증", ss, "S6"):
        health = HealthPage(driver, ss)
        health.go_health(ss, reporter)
        health.verify_elements(ss, reporter)
        print("[완료] 시나리오 6 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 7 : 보상 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_7_reward_case_section_visible(driver, ss, reporter):
    """
    보상 탭 검증
    [목적] 보상 탭 스크롤 시 보상 사례 또는 보상 질문 섹션이 노출되는지 확인
    [재현] 보상 탭 클릭 → 아래로 스크롤 → 보상 사례/질문 타이틀 노출 확인
    [성공] '유형별 보상 사례' 또는 '자주 묻는 보상 질문' 중 하나 이상 노출
    """
    from pages.reward_page import RewardPage
    with scenario_context(reporter, "S7 보상 탭 검증", ss, "S7"):
        reward = RewardPage(driver, ss)
        reward.go_reward(ss, reporter)
        reward.verify_elements(ss, reporter)
        print("[완료] 시나리오 7 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 8 : 전체 메뉴 진입 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_8_fullmenu_sections_visible(driver, ss, reporter):
    """
    전체 메뉴 검증
    [목적] 전체 메뉴에서 스크롤 시 5개 섹션 타이틀이 순서대로 모두 노출되는지 확인
    [재현] 메뉴 버튼 클릭 → 순서대로 스크롤하며 섹션 확인
           (보험 → 보상/청구 → 생활/건강 → 정보 → 고객서비스)
    [성공] 5개 섹션 타이틀 전부 노출 (하나라도 미노출 시 즉시 실패)
    """
    with scenario_context(reporter, "S8 전체 메뉴 검증", ss, "S8"):
        menu = MenuPage(driver, ss)

        menu.open()
        shot = ss("S8_Menu_Opened")
        reporter.step("전체 메뉴 진입", "PASSED", shot)

        menu.verify_elements(ss, reporter)

        # 홈으로 복귀 (다음 테스트를 위해)
        driver.back()
        time.sleep(1)
        print("[완료] 시나리오 8 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 10 : 홈 탭에서 마이데이터 연동
# ══════════════════════════════════════════════════════════════════
@pytest.mark.skip(reason="외부 인증(네이버) 의존 — 전용 테스트 환경 구성 후 활성화 예정")
def test_scenario_10_mydata_insurance_connect_flow(driver, ss, reporter):
    """
    마이데이터 연동
    [목적] 마이데이터 연동을 통해 40개 보험사 연결 후 보험 진단까지 수행되는지 확인
    [재현] 홈 → 내 보험 추가하기 → 40개 연결 → 네이버 인증 → 약관 동의
           → 연결 완료 대기 → 결과 확인 → 보험 진단받기 → 채팅 종료
    [성공] 채팅 종료까지 전 단계 오류 없이 완료
    [비고] 네이버 인증서 등 외부 서비스 의존 — 현재 SKIP 처리
    """
    with scenario_context(reporter, "S10 마이데이터 연동", ss, "S10"):
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
        reporter.step("'내 보험 추가하기' 클릭 → 보험 연결 화면 진입", "PASSED", shot)

        ins.click_connect_40()
        shot = ss("S10_After_Connect40_Click")
        reporter.step("'40개 연결하기' 클릭", "PASSED", shot)

        ins.select_naver_cert()
        shot = ss("S10_Entry_Naver_Auth")
        reporter.step("네이버 인증서 선택", "PASSED", shot)

        ins.agree_and_continue()
        shot = ss("S10_After_Agree_Click")
        reporter.step("'동의하고 계속하기' 클릭", "PASSED", shot)

        ins.wait_for_connection()
        shot = ss("S10_DataConnect_Complete")
        reporter.step("마이데이터 연결 완료 대기", "PASSED", shot)

        ins.click_final_confirms()
        shot = ss("S10_Result_Confirm_Complete")
        reporter.step("연결 결과 확인 클릭", "PASSED", shot)

        ins.dismiss_extra_agreements()
        shot = ss("S10_Extra_Agree_Complete")
        reporter.step("추가 약관 동의 처리", "PASSED", shot)

        ins.get_insurance_diagnosis()
        shot = ss("S10_Entry_Diagnosis_Result")
        reporter.step("'보험 진단받기' 클릭 → 진단 화면 진입", "PASSED", shot)

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
