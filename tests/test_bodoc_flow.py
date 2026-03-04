# -*- coding: utf-8 -*-
import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from conftest import scenario_context, _element_exists, _INITIAL_SCREEN_XPATH
from pages.splash_page import SplashPage
from pages.intro_page import IntroPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.diagnosis_page import DiagnosisPage
from pages.menu_page import MenuPage


# ══════════════════════════════════════════════════════════════════
# 시나리오 1 : 앱 런치 — 스플래시 화면 + 앱백신 토스트 검증
# ══════════════════════════════════════════════════════════════════
@pytest.mark.observe_launch
def test_scenario_1_app_launch(driver, ss, reporter):
    """앱 런치 시퀀스 검증.

    app_reset이 앱을 재실행한 직후 즉시 실행된다 (초기 화면 대기 없음).
    스플래시 화면과 앱백신 토스트가 거의 동시에 나타나므로
    단일 폴링 루프에서 두 조건을 함께 추적한다.
    두 조건이 모두 만족될 때만 성공으로 처리한다:
      1) 스플래시 화면이 표시됨
      2) "TouchEn mVaccine이 구동중입니다." 토스트가 노출됨
    """
    with scenario_context(reporter, "시나리오1_앱_런치", ss, "S1"):
        splash = SplashPage(driver, ss)

        # 1️⃣ + 2️⃣ 스플래시 화면 & 앱백신 토스트 동시 감지 ────────
        splash_ok, toast_ok = splash.verify_launch_sequence(timeout=10)

        if not splash_ok:
            shot = ss("S1_FAIL_SplashNotVisible")
            reporter.step(
                f"스플래시 화면 미노출 (현재 Activity: {driver.current_activity})",
                "FAILED", shot,
            )
            raise AssertionError(
                "스플래시 화면이 앱 실행 후 10초 내에 표시되지 않았습니다.\n"
                f"현재 Activity: {driver.current_activity}\n"
                "조치: SplashPage.SPLASH_LOGO 또는 SPLASH_ACTIVITY_KEYWORD를 "
                "실기기 값으로 수정하세요."
            )

        if not toast_ok:
            shot = ss("S1_FAIL_AppVaccineToastNotVisible")
            reporter.step(
                f"앱백신 토스트 미노출 (기대: '{SplashPage.APPVACCINE_TOAST_TEXT}')",
                "FAILED", shot,
            )
            raise AssertionError(
                f"앱백신 토스트 '{SplashPage.APPVACCINE_TOAST_TEXT}'가 "
                "10초 내에 감지되지 않았습니다.\n"
                "조치: SplashPage.APPVACCINE_TOAST 의 XPath를 확인하세요."
            )

        shot = ss("S1_1_SplashAndToastDetected")
        reporter.step("스플래시 화면 노출 확인", "PASSED", shot)
        reporter.step(
            f"앱백신 토스트 노출 확인 — '{SplashPage.APPVACCINE_TOAST_TEXT}'",
            "PASSED", shot,
        )

        # 3️⃣ 초기 화면 진입 확인 (로그인 화면, 홈 화면, 또는 접근권한 안내 화면) ──
        try:
            WebDriverWait(driver, 15).until(
                lambda d: _element_exists(d, _INITIAL_SCREEN_XPATH)
            )
        except Exception:
            shot = ss("S1_3_FAIL_InitialScreenTimeout")
            reporter.step("초기 화면 진입 타임아웃", "FAILED", shot)
            raise AssertionError(
                "앱백신 처리 후 초기 화면(로그인/홈/접근권한 안내)이 15초 내에 나타나지 않았습니다."
            )

        shot = ss("S1_3_InitialScreenReached")
        if _element_exists(driver, "//*[@text='홈']"):
            reporter.step("초기 화면 진입 확인 — 홈 화면 (로그인 상태)", "PASSED", shot)
        elif _element_exists(driver, "//*[contains(@text,'접근권한 안내')]"):
            reporter.step("초기 화면 진입 확인 — 스마트폰 앱 접근권한 안내 화면 (최초 실행)", "PASSED", shot)
        else:
            reporter.step("초기 화면 진입 확인 — 로그인 화면 (미로그인 상태)", "PASSED", shot)

        print("[완료] 시나리오 1 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 2 : 초기 권한 팝업 처리
# ══════════════════════════════════════════════════════════════════
@pytest.mark.reset_permissions
def test_scenario_2_initial_permissions(driver, ss, reporter):
    """초기 권한 팝업 처리 검증.

    앱 최초 실행 시 노출되는 권한 요청 팝업 시퀀스를 처리하고,
    이후 정상 화면(로그인 또는 홈)이 표시됨을 확인한다.

    성공 조건:
      - 권한 팝업이 노출된 경우: 팝업 감지 시 스크린샷 촬영 후 처리, 초기 화면 진입 확인
      - 권한 팝업이 없는 경우: 로그만 남기고 PASSED 처리 (실패하지 않음)

    ※ noReset=True 환경에서는 대부분 팝업이 나타나지 않으므로 PASSED가 정상.
       Android 13+ POST_NOTIFICATIONS 다이얼로그는 어느 시점에든 나타날 수 있다.
    """
    with scenario_context(reporter, "시나리오2_초기_권한_팝업_처리", ss, "S2"):
        intro = IntroPage(driver, ss)

        # 1️⃣ 초기 권한 팝업 시퀀스 처리
        # 팝업이 감지되면 클릭 전 자동으로 스크린샷 촬영 (scenario_tag="S2")
        # 스크린샷: S2_1_AccessRights, S2_2_PhonePermission, S2_3_NotifGuide, S2_4_NotifPermission
        results = intro.handle_all_initial_permissions(timeout=5, scenario_tag="S2")
        handled = [k for k, v in results.items() if v]

        shot = ss("S2_1_AfterPermissionHandling")
        if handled:
            reporter.step(
                f"권한 팝업 처리 완료 — {len(handled)}개 처리됨: {', '.join(handled)}",
                "PASSED", shot,
            )
        else:
            reporter.step(
                "권한 팝업 미노출 — 이미 허용됐거나 최초 실행이 아님 (정상)",
                "PASSED", shot,
            )

        # 2️⃣ 권한 처리 후 초기 화면 진입 확인 (로그인 또는 홈)
        try:
            WebDriverWait(driver, 10).until(
                lambda d: _element_exists(d, _INITIAL_SCREEN_XPATH)
            )
        except Exception:
            shot = ss("S2_FAIL_ScreenLost")
            reporter.step("권한 처리 후 초기 화면 이탈 또는 타임아웃", "FAILED", shot)
            raise AssertionError(
                "권한 팝업 처리 후 초기 화면(로그인/홈)이 10초 내에 표시되지 않았습니다."
            )

        shot = ss("S2_2_InitialScreenOK")
        if _element_exists(driver, "//*[@text='홈']"):
            reporter.step("초기 화면 정상 진입 — 홈 화면 (로그인 상태)", "PASSED", shot)
        elif _element_exists(driver, "//*[contains(@text,'접근권한 안내')]"):
            reporter.step("초기 화면 정상 진입 — 스마트폰 앱 접근권한 안내 화면 (최초 실행)", "PASSED", shot)
        else:
            reporter.step("초기 화면 정상 진입 — 로그인 화면 (미로그인 상태)", "PASSED", shot)

        print("[완료] 시나리오 2 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 3 : 카카오 로그인
# ══════════════════════════════════════════════════════════════════
def test_scenario_3_kakao_login(driver, ss, reporter):
    """카카오 계정 로그인 플로우 전체 검증.

    성공 조건:
      카카오 계정 선택 완료 후 홈 화면('홈' 탭)이 노출되면 성공.
      탭바 전체 검증은 시나리오 4~5(홈 탭 검증)에서 수행한다.

    ※ 앱이 이미 로그인된 상태라면 로그인 화면이 표시되지 않아 실패합니다.
       이 경우 대시보드 UI의 Skip 버튼으로 이 시나리오를 건너뛰세요.
    """
    with scenario_context(reporter, "시나리오3_카카오_로그인", ss, "S3"):
        intro = IntroPage(driver, ss)
        login = LoginPage(driver, ss)

        # 1️⃣ 초기 권한 팝업 처리 (노출되지 않으면 무시)
        results = intro.handle_all_initial_permissions(timeout=5, scenario_tag="S3")
        handled = [k for k, v in results.items() if v]
        shot = ss("S3_1_PermissionsHandled")
        reporter.step(
            f"초기 권한 팝업 처리 완료 ({len(handled)}개)" if handled
            else "권한 팝업 미노출 (무시)",
            "PASSED", shot,
        )

        # 2️⃣ 로그인 화면 진입 확인
        login.ensure_login_screen()
        shot = ss("S3_2_LoginScreenVisible")
        reporter.step("로그인 화면 진입 확인 ('카카오로 시작하기' 버튼 노출)", "PASSED", shot)

        # 3️⃣ '카카오로 시작하기' 버튼 클릭
        login.start_kakao_login()
        shot = ss("S3_3_KakaoButtonClicked")
        reporter.step("'카카오로 시작하기' 버튼 클릭", "PASSED", shot)

        # 4️⃣ 카카오 OAuth 페이지 로드 확인 (NATIVE 컨텍스트, WebView 전환 없음)
        login.wait_for_kakao_oauth_ui()
        shot = ss("S3_4_KakaoOAuthPageLoaded")
        reporter.step("카카오 OAuth 페이지 로드 확인", "PASSED", shot)

        # 5️⃣ '계속하기' 클릭
        login.click_kakao_continue()
        shot = ss("S3_5_KakaoContinueClicked")
        reporter.step("'계속하기' 클릭", "PASSED", shot)

        # 6️⃣ 첫 번째 카카오 계정 선택
        login.select_first_kakao_account()
        shot = ss("S3_6_KakaoAccountSelected")
        reporter.step("카카오 계정 선택 완료", "PASSED", shot)

        # 7️⃣ 홈 화면 진입 확인 — '홈' 탭 노출만 확인 (간소화)
        try:
            WebDriverWait(driver, 20).until(
                lambda d: _element_exists(d, "//*[@text='홈']")
            )
        except Exception:
            shot = ss("S3_7_FAIL_HomeNotReached")
            reporter.step("로그인 후 홈 화면 미진입", "FAILED", shot)
            raise AssertionError(
                "카카오 로그인 후 20초 내에 홈 화면으로 이동하지 않았습니다."
            )

        shot = ss("S3_7_HomeScreenReached")
        reporter.step("홈 화면 진입 확인 — '홈' 탭 노출", "PASSED", shot)

        print("[완료] 시나리오 3 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 4 : 홈 탭 주요 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_4_home_tab(driver, ss, reporter):
    """홈 탭 상단·하단 요소 확인.

    홈 탭 진입 → 홈 탭 네비게이션·보험 종합진단·매월 내는 보험료 확인
    → 스크롤 후 숨은 보험금·손해사정사·내 보험 추가 확인
    """
    with scenario_context(reporter, "시나리오4_홈탭_검증", ss, "S4"):
        home = HomePage(driver, ss)

        home.go_home()
        shot = ss("S4_1_EntryHomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        home.verify_home_elements(ss, reporter)

        print("[완료] 시나리오 4 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 5 : 홈 탭 스크롤 단계별 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_5_home_tab_scroll(driver, ss, reporter):
    """홈 탭 주요 요소 순차 스크롤 확인.

    내 보험 종합진단 → 매월 내는 보험료 → AI 고민상담소 → 숨은 보험금 → 건강정보 확인하기
    """
    with scenario_context(reporter, "시나리오5_홈탭_스크롤_검증", ss, "S5"):
        home = HomePage(driver, ss)

        home.go_home()
        shot = ss("S5_1_EntryHomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        home.verify_home_scroll_steps(ss, reporter)

        print("[완료] 시나리오 5 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 6 : 진단 탭 요소 확인
# ══════════════════════════════════════════════════════════════════
def test_scenario_6_diagnosis_tab(driver, ss, reporter):
    """진단 탭 진입 및 내 보험료 탭 금액 확인.

    진단 탭 진입 → 진단 탭 네비게이션·보험 진단 텍스트 확인 → 하단 스크롤
    → 내 전보험료 탭 클릭 → 매월 내는 보험료 타이틀·금액 노출 확인
    """
    with scenario_context(reporter, "시나리오6_진단탭_검증", ss, "S6"):
        diagnosis = DiagnosisPage(driver, ss)

        diagnosis.go_diagnosis(ss, reporter)
        diagnosis.verify_diagnosis_elements(ss, reporter)
        diagnosis.scroll_to_bottom(ss, reporter)
        diagnosis.verify_insurance_premium(ss, reporter)

        print("[완료] 시나리오 6 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 7 : 상품 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_7_product_tab(driver, ss, reporter):
    """상품 탭 요소 확인.

    상품 탭 진입 → 스크롤 탐색 → '보닥 회원만을 위한 추천 상품' 타이틀 노출 확인
    """
    from pages.product_page import ProductPage
    with scenario_context(reporter, "시나리오7_상품탭_검증", ss, "S7"):
        product = ProductPage(driver, ss)

        product.go_product(ss, reporter)
        product.verify_elements(ss, reporter)

        print("[완료] 시나리오 7 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 8 : 건강 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_8_health_tab(driver, ss, reporter):
    """건강 탭 요소 확인.

    건강 탭 진입 → 스크롤 탐색 → '건강 기록' 타이틀 노출 확인
    """
    from pages.health_page import HealthPage
    with scenario_context(reporter, "시나리오8_건강탭_검증", ss, "S8"):
        health = HealthPage(driver, ss)

        health.go_health(ss, reporter)
        health.verify_elements(ss, reporter)

        print("[완료] 시나리오 8 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 9 : 보상 탭 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_9_reward_tab(driver, ss, reporter):
    """보상 탭 요소 확인.

    보상 탭 진입 → 스크롤 탐색 → 유형별 보상 사례·자주 묻는 보상 질문 중 하나 이상 노출 확인
    """
    from pages.reward_page import RewardPage
    with scenario_context(reporter, "시나리오9_보상탭_검증", ss, "S9"):
        reward = RewardPage(driver, ss)

        reward.go_reward(ss, reporter)
        reward.verify_elements(ss, reporter)

        print("[완료] 시나리오 9 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 10 : 전체 메뉴 진입 검증
# ══════════════════════════════════════════════════════════════════
def test_scenario_10_menu_validation(driver, ss, reporter):
    """전체 메뉴 진입 요소 확인.

    전체 메뉴 열기 → 보험 → 보상/청구 → 생활/건강 → 정보 → 고객서비스 섹션 확인
    """
    with scenario_context(reporter, "시나리오10_메뉴_검증", ss, "S10"):
        menu = MenuPage(driver, ss)

        menu.open()
        shot = ss("S10_1_MenuOpened")
        reporter.step("전체 메뉴 열기 완료", "PASSED", shot)

        menu.verify_elements(ss, reporter)

        # 홈으로 복귀
        driver.back()
        WebDriverWait(driver, 10).until(
            lambda d: _element_exists(d, "//*[@text='홈']")
        )
        print("[완료] 시나리오 10 성공")


# ══════════════════════════════════════════════════════════════════
# 시나리오 11 : 홈 탭에서 마이데이터 연동
# @pytest.mark.skip(reason="미구현 — UI 안정화 후 활성화 예정")
# ══════════════════════════════════════════════════════════════════
def test_scenario_11_mydata(driver, ss, reporter):
    """홈 탭에서 마이데이터 연동.

    홈 탭 → 내 보험 추가하기 → 40개 연결 → 네이버 인증 → 약관 → 진단받기 → 채팅 종료
    """
    with scenario_context(reporter, "시나리오11_마이데이터_연동", ss, "S11"):
        from pages.mydata_flow import MydataFlow

        home = HomePage(driver, ss)
        ins = MydataFlow(driver, ss)

        # 1️⃣ 홈 탭 진입
        home.go_home()
        shot = ss("S11_1_EntryHomeTab")
        reporter.step("홈 탭 진입", "PASSED", shot)

        # 2️⃣ '내 보험 추가하기' 클릭 및 연결 화면 진입
        home.click_add_insurance()
        shot = ss("S11_2_EntryInsuranceConnect")
        reporter.step("내 보험 추가하기 클릭 → 보험 연결 화면 진입", "PASSED", shot)

        # 3️⃣ '40개 연결하기' 클릭
        ins.click_connect_40()
        shot = ss("S11_3_AfterConnect40Click")
        reporter.step("40개 연결하기 클릭", "PASSED", shot)

        # 4️⃣ 네이버 인증서 선택
        ins.select_naver_cert()
        shot = ss("S11_4_EntryNaverAuth")
        reporter.step("네이버 인증서 선택", "PASSED", shot)

        # 5️⃣ 동의하고 계속하기 클릭
        ins.agree_and_continue()
        shot = ss("S11_5_AfterAgreeClick")
        reporter.step("동의하고 계속하기", "PASSED", shot)

        # 6️⃣ 마이데이터 연결 대기
        ins.wait_for_connection()
        shot = ss("S11_6_DataConnectComplete")
        reporter.step("마이데이터 연결 대기 완료", "PASSED", shot)

        # 7️⃣ 결과 확인 화면에서 확인 처리
        ins.click_final_confirms()
        shot = ss("S11_7_ResultConfirmComplete")
        reporter.step("결과 확인 클릭 완료", "PASSED", shot)

        # 8️⃣ 추가 약관 동의 처리
        ins.dismiss_extra_agreements()
        shot = ss("S11_8_ExtraAgreeComplete")
        reporter.step("추가 약관 동의 처리 완료", "PASSED", shot)

        # 9️⃣ 보험 진단받기
        ins.get_insurance_diagnosis()
        shot = ss("S11_9_EntryDiagnosisResult")
        reporter.step("보험 진단받기 클릭 → 진단 화면 진입", "PASSED", shot)

        # 🔟 채팅 종료
        ins.close_chat()
        shot = ss("S11_10_ChatClosed")
        reporter.step("전문가 채팅 종료", "PASSED", shot)

        print("[완료] 시나리오 11 성공")
