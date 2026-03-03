# -*- coding: utf-8 -*-
# ── pytest 마커 등록 ─────────────────────────────────────────────
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "observe_launch: 앱 런치 시퀀스(스플래시 + 토스트)를 직접 관찰하는 테스트. "
        "app_reset이 초기 화면 대기를 생략하고 즉시 제어권을 넘긴다."
    )


import atexit
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.config import APPIUM_SERVER_URL, CAPABILITIES, SCREENSHOT_DIR, RESULTS_DIR, REPORT_DIR
from utils.reporter import TestReporter


# ── 공통 상수 ─────────────────────────────────────────────────────
# 앱 초기화 성공 여부를 판단하는 화면
#   - 로그인 화면 : '카카오로 시작하기'
#   - 홈 화면     : '홈'
#   - 접근권한 안내 화면 : '스마트폰 앱 접근권한 안내' (최초 실행 시 노출)
_INITIAL_SCREEN_XPATH = (
    "//*[@text='카카오로 시작하기']"
    " | //*[@text='홈']"
    " | //*[contains(@text,'접근권한 안내')]"
)


# ── 공통 헬퍼 ─────────────────────────────────────────────────────
def _element_exists(driver, xpath):
    """XPath 요소의 존재 여부를 bool로 반환. 예외는 무시."""
    try:
        driver.find_element(AppiumBy.XPATH, xpath)
        return True
    except Exception:
        return False


def _unlock_screen(driver):
    """화면 깨우기 + 삼성 Bouncer 잠금화면 해제.

    mobile: unlock 만으로는 삼성 커스텀 잠금화면이 해제되지 않는 경우가 있으므로
    adb shell wm dismiss-keyguard 를 추가로 호출한다.
    """
    driver.execute_script('mobile: unlock')
    adb_dir = CAPABILITIES.get('appium:chromedriverExecutableDir', '')
    adb_candidate = os.path.join(adb_dir, 'adb.exe') if adb_dir else ''
    adb = adb_candidate if os.path.exists(adb_candidate) else (shutil.which('adb') or 'adb')
    device = CAPABILITIES.get('deviceName', '')
    try:
        subprocess.run(
            [adb, '-s', device, 'shell', 'wm', 'dismiss-keyguard'],
            capture_output=True, timeout=5
        )
    except Exception:
        pass


# ── run_id ───────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def run_id():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


# ── 드라이버 (세션당 1회) ─────────────────────────────────────────
@pytest.fixture(scope="session")
def driver_setup(reporter):
    """Appium 드라이버 세션을 생성하고 세션 종료 시 정리한다.

    앱 실행·초기화는 각 테스트 전에 실행되는 app_reset 픽스처가 담당한다.
    이 픽스처는 드라이버 연결만 책임진다.
    """
    print("\n[INFO] Appium 드라이버 초기화 시작...")
    options = UiAutomator2Options().load_capabilities(CAPABILITIES)
    options.set_capability('appium:uiautomator2ServerInstallTimeout', 60000)
    try:
        driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
        driver.implicitly_wait(5)
        print("[OK] 드라이버 연결 성공!")
        yield driver
    except Exception as e:
        print(f"[ERROR] 드라이버 초기화 실패: {e}")
        reporter.start_scenario("드라이버 초기화 실패")
        reporter.step(f"Appium/디바이스 연결 오류: {str(e)}", "FAILED")
        reporter.end_scenario("FAILED", error=e)
        raise
    finally:
        if 'driver' in locals() and driver:
            print("\n[INFO] 드라이버 종료...")
            driver.quit()


@pytest.fixture
def driver(driver_setup):
    return driver_setup


# ── 스크린샷 ─────────────────────────────────────────────────────
@pytest.fixture
def ss(driver_setup, run_id):
    """스크린샷을 outputs/screenshots/{run_id}/ 에 저장.
    reporter에 전달할 '{run_id}/{filename}' 형태의 상대 경로를 반환."""
    run_dir = os.path.join(SCREENSHOT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    def take(name):
        timestamp = datetime.now().strftime('%m%d-%H%M')
        filename = f"{timestamp}_{name}.png"
        path = os.path.join(run_dir, filename)
        try:
            driver_setup.save_screenshot(path)
            print(f"[SS] {filename}")
        except Exception as e:
            print(f"[SS-ERR] {e}")
            return None
        return f"{run_id}/{filename}"

    return take


# ── 리포터 ───────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def reporter(run_id):
    r = TestReporter(RESULTS_DIR, REPORT_DIR, SCREENSHOT_DIR, run_id=run_id)
    _saved = [False]

    def _save_once():
        if not _saved[0]:
            _saved[0] = True
            r.save()

    atexit.register(_save_once)
    yield r
    _save_once()


# ── 디바이스 정보 리포터에 주입 (세션당 1회) ──────────────────────
@pytest.fixture(scope="session", autouse=True)
def inject_device_info(driver_setup, reporter):
    caps = driver_setup.capabilities
    udid = (caps.get('udid') or caps.get('deviceUDID')
            or CAPABILITIES.get('deviceName', ''))
    version = caps.get('platformVersion', '')
    model = caps.get('deviceModel', '')
    try:
        adb = shutil.which('adb') or 'adb'
        model = subprocess.check_output(
            [adb, '-s', udid, 'shell', 'getprop', 'ro.product.model'],
            encoding='utf-8', errors='replace', timeout=5
        ).strip()
    except Exception:
        pass
    print(f"[INFO] 실행 디바이스: {model} / Android {version} / {udid}")
    reporter.set_device(model=model, android=version)


# ══════════════════════════════════════════════════════════════════
# 시나리오 0 : 공통 앱 초기화 (각 테스트 전 자동 실행)
# ══════════════════════════════════════════════════════════════════
@pytest.fixture(autouse=True)
def app_reset(request, driver_setup, run_id):
    """시나리오 0 — 각 테스트 전 앱을 완전히 초기화한다.

    실행 순서:
      1. WebView 잔여 컨텍스트 → NATIVE_APP 복귀
      2. 앱 완전 종료 (terminate_app)
      3. 화면 깨우기 (unlock + dismiss-keyguard)
      4. 앱 재실행 (activate_app)
      5. 초기 화면 노출 대기 (로그인 화면 또는 홈 화면)

    모든 테스트는 이 픽스처 덕분에 앱의 초기 상태에서 독립적으로 시작된다.
    """
    pkg = CAPABILITIES['appPackage']
    test_name = request.node.name
    print(f"\n[시나리오 0] 앱 초기화 시작 → {test_name}")

    # 1. WebView 잔여 컨텍스트 정리
    try:
        ctx = driver_setup.current_context or ''
        if 'WEBVIEW' in ctx:
            driver_setup.switch_to.context('NATIVE_APP')
            print("[시나리오 0] WebView 컨텍스트 → NATIVE_APP 복귀")
    except Exception:
        pass

    # 2. 앱 완전 종료
    try:
        driver_setup.terminate_app(pkg)
        print("[시나리오 0] 앱 종료 완료")
    except Exception:
        pass

    # 3. 화면 깨우기
    _unlock_screen(driver_setup)

    # 4. 앱 재실행
    driver_setup.activate_app(pkg)
    print("[시나리오 0] 앱 재실행 완료")

    # 5. 초기 화면 노출 대기 (로그인 또는 홈)
    # observe_launch 마커가 있으면 대기 생략 —
    # 해당 테스트가 직접 런치 시퀀스(스플래시·토스트)를 관찰한 뒤 초기 화면을 확인한다.
    if request.node.get_closest_marker('observe_launch'):
        print(f"[시나리오 0] 앱 재실행 완료 → {test_name} 런치 시퀀스 직접 관찰 시작")
    else:
        WebDriverWait(driver_setup, 15).until(
            lambda d: _element_exists(d, _INITIAL_SCREEN_XPATH)
        )
        print(f"[시나리오 0] 초기화 완료 → {test_name} 시작")

    yield

    # ── 테스트 종료 후: 최종 스크린샷 저장 ───────────────────────
    try:
        label = (test_name
                 .upper()
                 .replace("TEST_SCENARIO_", "S")
                 .replace("_", "-"))[:15]
        timestamp = datetime.now().strftime('%m%d-%H%M')
        filename = f"{timestamp}_{label}_FINAL.png"
        run_dir = os.path.join(SCREENSHOT_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)
        driver_setup.save_screenshot(os.path.join(run_dir, filename))
        print(f"[SS-종료] {filename}")
    except Exception as e:
        print(f"[SS-ERR] 종료 스크린샷 실패: {e}")


# ── 시나리오 컨텍스트 매니저 ──────────────────────────────────────
@contextmanager
def scenario_context(reporter, name, ss, fail_prefix):
    """시나리오의 공통 에러 처리·리포팅을 담당한다.

    - 정상 종료 → PASSED
    - 예외 발생 → 스크린샷 촬영 후 FAILED, pytest.fail() 호출
    - 시나리오 내부에서 reporter.end_scenario()를 먼저 호출해도 안전 (no-op 처리됨)
    """
    reporter.start_scenario(name)
    try:
        yield
        reporter.end_scenario("PASSED")
    except Exception as e:
        shot = ss(f"{fail_prefix}_FAIL")
        full_err = str(e)
        short_err = full_err.split('\n')[0][:100] + ('...' if len(full_err.split('\n')[0]) > 100 else '')
        reporter.step(f"오류: {short_err}", "FAILED", shot)
        reporter.end_scenario("FAILED", error=full_err)
        pytest.fail(full_err)
