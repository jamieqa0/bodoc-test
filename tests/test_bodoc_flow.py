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
from pages.menu_page import MenuPage


# ══════════════════════════════════════════════════════════════════
# 시나리오 1 : 앱 런치
# ══════════════════════════════════════════════════════════════════
def test_scenario_1_app_launch(driver, ss, reporter):
    """앱 실행 및 화면 진입:
    앱 실행 → 초기화면 진입 → 로그인 화면 또는 홈 화면 중 하나 확인"""
    with scenario_context(reporter, "시나리오1_앱_런치", ss, "S1"):
        # 1️⃣ 앱 초기 로드 대기 — 로그인 버튼 또는 홈 탭 중 하나가 나타날 때까지
        try:
            WebDriverWait(driver, 15).until(
                lambda d: (
                    _try_find(d, "//*[@text='카카오로 시작하기']")
                    or _try_find(d, "//*[@text='홈']")
                )
            )
        except Exception:
            shot = ss("S1_FAIL_App_Not_Loaded")
            reporter.step("앱 초기 화면 로드 실패", "FAILED", shot)
            raise AssertionError("15초 내에 앱 초기 화면이 표시되지 않았습니다.")

        shot = ss("S1_2_Entry_LaunchScreen")
        reporter.step("앱 실행 및 초기화면 진입", "PASSED", shot)

        # 2️⃣ 화면 상태 판별 및 검증
        if _try_find(driver, "//*[@text='홈']"):
            reporter.step("홈 화면 진입 확인 (로그인 상태)", "PASSED", shot)
        elif _try_find(driver, "//*[@text='카카오로 시작하기']"):
            reporter.step("로그인 화면 진입 확인 (미로그인 상태)", "PASSED", shot)
        else:
            reporter.step("앱 화면 요소 노출 확인", "FAILED", shot)
            raise AssertionError("앱 초기 화면 요소를 찾을 수 없습니다.")

        print("[완료] 시나리오 1 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 2 : 카카오 로그인
# ══════════════════════════════════════════════════════════════════
def test_scenario_2_kakao_login(driver, ss, reporter):
    """카카오 계정 로그인 (로그인된 경우 스킵):
    화면 진입 → 로그인 여부 확인 → 권한 허용 처리 → 카카오로 시작하기 클릭
    → 웹뷰 전환 → 계속하기 클릭 → 카카오 계정 선택 → 홈 화면 진입 확인"""
    with scenario_context(reporter, "시나리오2_카카오_로그인", ss, "S2"):
        intro = IntroPage(driver, ss)
        login = LoginPage(driver, ss)

        # 1️⃣ 앱 초기화면 진입
        shot = ss("S2_1_Entry_InitialScreen")
        reporter.step("앱 초기화면 진입", "PASSED", shot)

        # 2️⃣ 이미 로그인 상태인지 확인 (홈 화면 노출 여부)
        if _try_find(driver, "//*[@text='홈']"):
            shot = ss("S2_2_Already_Logged_In")
            reporter.step("이미 로그인 상태 확인 (스킵)", "PASSED", shot)
            reporter.end_scenario("PASSED")
            print("[완료] 시나리오 2 — 이미 로그인됨")
            return

        # 3️⃣ 초기 권한 화면 처리 (없어도 무시)
        # (별도의 step 기록보다는 동작 수행 중심)
        intro.process_initial_rights()
        intro.allow_phone_permission()
        intro.confirm_notification_guide()
        intro.allow_notification_permission()

        # 4️⃣ 로그인 화면 확인 ('카카오로 시작하기' 버튼)
        if not _try_find(driver, "//*[@text='카카오로 시작하기']"):
            shot = ss("S2_4_FAIL_LoginScreen_Not_Found")
            reporter.step("로그인 화면 (카카오 버튼) 확인", "FAILED", shot)
            raise AssertionError("카카오 로그인 버튼을 찾을 수 없습니다.")

        shot = ss("S2_4_Entry_LoginScreen")
        reporter.step("로그인 화면 진입 확인", "PASSED", shot)

        # 5️⃣ 카카오 로그인 시작 및 웹뷰 전환 확인
        login.start_kakao_login()
        try:
            WebDriverWait(driver, 10).until(
                lambda d: any('WEBVIEW' in c for c in d.contexts)
            )
            shot = ss("S2_5_Switch_KakaoWebView")
            reporter.step("카카오 로그인 버튼 클릭 및 웹뷰 전환 확인", "PASSED", shot)
        except Exception:
            shot = ss("S2_5_FAIL_KakaoWebView")
            reporter.step("웹뷰 전환 실패", "FAILED", shot)
            raise AssertionError("카카오 로그인 후 웹뷰로 전환되지 않았습니다.")

        # 6️⃣ 카카오 계속하기 클릭
        login.click_kakao_continue()
        shot = ss("S2_6_Switch_After_Continue")
        reporter.step("카카오 '계속하기' 클릭", "PASSED", shot)

        # 7️⃣ 카카오 계정 선택
        login.select_first_kakao_account()
        shot = ss("S2_7_Switch_After_Account_Select")
        reporter.step("카카오 계정 선택 완료", "PASSED", shot)

        # 8️⃣ 로그인 완료 후 홈 화면 전환 대기 및 확인
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//*[@text='홈']"))
            )
            shot = ss("S2_8_Switch_HomeTab_Reached")
            reporter.step("로그인 완료 및 홈 화면 전환 확인", "PASSED", shot)
        except Exception:
            shot = ss("S2_8_FAIL_HomeTab_Not_Reached")
            reporter.step("로그인 완료 및 홈 화면 전환 확인", "FAILED", shot)
            raise AssertionError("로그인 후 홈 화면으로 이동하지 않았습니다.")

        print("[완료] 시나리오 2 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 3 : 홈 탭 주요 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_3_home_tab(driver, ss, reporter):
    """홈 탭 상단·하단 요소 확인:
    홈 탭 진입 → 홈 탭 네비게이션·보험 종합진단·매월 내는 보험료 확인
    → 스크롤 후 숨은 보험금·손해사정사·내 보험 추가 확인"""
    with scenario_context(reporter, "시나리오3_홈탭_검증", ss, "S3"):
        home = HomePage(driver, ss)

        # 1️⃣ 홈 탭 진입 (go_home 내부에서 wait_for_home으로 대기)
        home.go_home()
        shot = ss("S3_1_Entry_HomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        # 2️⃣ 홈 탭 요소 (상단/하단) 스크롤하며 확인 (verify_home_elements 내부에 step 구현됨)
        home.verify_home_elements(ss, reporter)

        print("[완료] 시나리오 3 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 3-1 : 홈 탭 스크롤 단계별 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_3_1_home_tab_scroll(driver, ss, reporter):
    """홈 탭 주요 요소 순차 스크롤 확인:
    내 보험 종합진단 → 매월 내는 보험료 → AI 고민상담소 → 숨은 보험금 → 건강정보 확인하기"""
    with scenario_context(reporter, "시나리오3-1_홈탭_스크롤_검증", ss, "S3_1"):
        home = HomePage(driver, ss)

        # 1️⃣ 홈 탭 진입 (go_home 내부에서 wait_for_home으로 대기)
        home.go_home()
        shot = ss("S3-1_1_Entry_HomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        # 2️⃣ 홈 탭 요소 스크롤하며 단계별 확인 (verify_home_scroll_steps 내부에 step 구현됨)
        home.verify_home_scroll_steps(ss, reporter)

        print("[완료] 시나리오 3-1 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 4 : 진단 탭 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_4_diagnosis_tab(driver, ss, reporter):
    """진단 탭 진입 및 내 보험료 탭 금액 확인:
    진단 탭 진입 → 진단 탭 네비게이션·보험 진단 텍스트 확인 → 하단 스크롤
    → 내 전보험료 탭 클릭 → 매월 내는 보험료 타이틀·금액 노출 확인"""
    with scenario_context(reporter, "시나리오4_진단탭_검증", ss, "S4"):
        diagnosis = DiagnosisPage(driver, ss)

        # 1️⃣ 홈 탭 상태 확인 (전환 전) — 홈 화면이 준비된 것을 확인
        WebDriverWait(driver, 10).until(
            lambda d: _try_find(d, "//*[@text='홈']")
        )
        shot = ss("S4_1_HomeTab_Status_Before_Switch")
        reporter.step("홈 탭 상태 (전환 전)", "PASSED", shot)

        # 2️⃣ 진단 탭으로 이동 및 상단 요소 노출 확인
        diagnosis.go_diagnosis(ss, reporter)
        diagnosis.verify_diagnosis_elements(ss, reporter)

        # 3️⃣ 화면 하단으로 스크롤 이동
        diagnosis.scroll_to_bottom(ss, reporter)
        
        # 4️⃣ 탭 이동 후 내 보험료 확인
        diagnosis.verify_insurance_premium(ss, reporter)

        print("[완료] 시나리오 4 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 5 : 상품 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_5_product_tab(driver, ss, reporter):
    """상품 탭 요소 확인:
    상품 탭 진입 → 스크롤 탐색 → '보닥 회원만을 위한 추천 상품' 타이틀 노출 확인"""
    from pages.product_page import ProductPage
    with scenario_context(reporter, "시나리오5_상품탭_검증", ss, "S5"):
        product = ProductPage(driver, ss)

        # 1️⃣ 상품 탭 진입
        product.go_product(ss, reporter)

        # 2️⃣ 화면 스크롤 후 대상 타이틀 확인
        product.verify_elements(ss, reporter)
        print("[완료] 시나리오 5 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 6 : 건강 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_6_health_tab(driver, ss, reporter):
    """건강 탭 요소 확인:
    건강 탭 진입 → 스크롤 탐색 → '건강 기록' 타이틀 노출 확인"""
    from pages.health_page import HealthPage
    with scenario_context(reporter, "시나리오6_건강탭_검증", ss, "S6"):
        health = HealthPage(driver, ss)

        # 1️⃣ 건강 탭 진입
        health.go_health(ss, reporter)

        # 2️⃣ 화면 스크롤 후 건강 기록 확인
        health.verify_elements(ss, reporter)
        print("[완료] 시나리오 6 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 7 : 보상 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_7_reward_tab(driver, ss, reporter):
    """보상 탭 요소 확인:
    보상 탭 진입 → 스크롤 탐색 → 유형별 보상 사례·자주 묻는 보상 질문 중 하나 이상 노출 확인"""
    from pages.reward_page import RewardPage
    with scenario_context(reporter, "시나리오7_보상탭_검증", ss, "S7"):
        reward = RewardPage(driver, ss)

        # 1️⃣ 보상 탭 진입
        reward.go_reward(ss, reporter)

        # 2️⃣ 화면 스크롤 후 보상 관련 타이틀 영역 확인
        reward.verify_elements(ss, reporter)
        print("[완료] 시나리오 7 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 8 : 전체 메뉴 진입 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_8_menu_validation(driver, ss, reporter):
    """전체 메뉴 진입 확인:
    전체 메뉴 열기 → 보험 → 보상/청구 → 생활/건강 → 정보 → 고객서비스 섹션 확인"""
    with scenario_context(reporter, "시나리오8_메뉴_검증", ss, "S8"):
        menu = MenuPage(driver, ss)
        
        # 1️⃣ 우측 하단의 전체 메뉴 열기
        menu.open()
        shot = ss("S8_1_Menu_Opened")
        reporter.step("전체 메뉴 열기 완료", "PASSED", shot)
        
        # 2️⃣ 주요 메뉴 섹션 노출 확인 (실패 시 예외 발생)
        menu.verify_elements(ss, reporter)
        
        # 3️⃣ 확인 완료 후 홈으로 복귀 (다음 테스트를 위해)
        driver.back()
        WebDriverWait(driver, 10).until(
            lambda d: _try_find(d, "//*[@text='홈']")
        )
        print("[완료] 시나리오 8 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 10 : 홈 탭에서 마이데이터 연동
# ══════════════════════════════════════════════════════════════════
@pytest.mark.skip(reason="시나리오10 작업 중 — 일시 비활성화")
def test_scenario_10_mydata(driver, ss, reporter):
    """홈 탭 → 내 보험 추가하기:
    홈 탭 → 내 보험 추가하기 → 40개 연결 → 네이버 인증 → 약관 → 진단받기 → 채팅 종료"""
    with scenario_context(reporter, "시나리오10_마이데이터_연동", ss, "S10"):
        from pages.mydata_flow import MydataFlow

        home = HomePage(driver, ss)
        ins = MydataFlow(driver, ss)

        # 1️⃣ 이전 세션 웹뷰 등 초기화 및 홈 탭 복귀 처리
        try:
            driver.switch_to.context('NATIVE_APP')
        except Exception:
            pass
        for _ in range(4):
            if _try_find(driver, "//*[@text='홈']"):
                break
            driver.press_keycode(4)
            time.sleep(0.7)

        # 2️⃣ 홈 탭 진입
        home.go_home()
        time.sleep(1)
        shot = ss("S10_2_Entry_HomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        # 3️⃣ '내 보험 추가하기' 클릭 및 연결 화면 진입
        home.click_add_insurance()
        shot = ss("S10_3_Entry_Insurance_Connect")
        reporter.step("내 보험 추가하기 클릭 → 보험 연결 화면 진입", "PASSED", shot)

        # 4️⃣ '40개 연결하기' 클릭
        ins.click_connect_40()
        shot = ss("S10_4_After_Connect40_Click")
        reporter.step("40개 연결하기 클릭", "PASSED", shot)

        # 5️⃣ 네이버 인증서 선택
        ins.select_naver_cert()
        shot = ss("S10_5_Entry_Naver_Auth")
        reporter.step("네이버 인증서 선택", "PASSED", shot)

        # 6️⃣ 동의하고 계속하기 클릭
        ins.agree_and_continue()
        shot = ss("S10_6_After_Agree_Click")
        reporter.step("동의하고 계속하기", "PASSED", shot)

        # 7️⃣ 마이데이터 연결 대기
        ins.wait_for_connection()
        shot = ss("S10_7_DataConnect_Complete")
        reporter.step("마이데이터 연결 대기 완료", "PASSED", shot)

        # 8️⃣ 결과 확인 화면에서 예/확인 처리
        ins.click_final_confirms()
        shot = ss("S10_8_Result_Confirm_Complete")
        reporter.step("결과 확인 클릭 완료", "PASSED", shot)

        # 9️⃣ 추가 약관 동의 안내 처리
        ins.dismiss_extra_agreements()
        shot = ss("S10_9_Extra_Agree_Complete")
        reporter.step("추가 약관 동의 처리 완료", "PASSED", shot)

        ins.get_insurance_diagnosis()
        shot = ss("S10_10_Entry_Diagnosis_Result")
        reporter.step("보험 진단받기 클릭 → 진단 화면 진입", "PASSED", shot)

        ins.close_chat()
        shot = ss("S10_11_Chat_Closed")
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
