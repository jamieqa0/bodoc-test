# -*- coding: utf-8 -*-
import atexit
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.config import APPIUM_SERVER_URL, CAPABILITIES, SCREENSHOT_DIR, RESULTS_DIR, REPORT_DIR
from utils.reporter import TestReporter


# ── #9: run_id → 모듈 전역 대신 session 픽스처로 관리 ─────────
@pytest.fixture(scope="session")
def run_id():
    return datetime.now().strftime('%Y%m%d_%H%M%S')


# ── 드라이버 ─────────────────────────────────────────────────
@pytest.fixture(scope="session")
def driver_setup(reporter):
    print("\n[INFO] Appium 드라이버 초기화 시작...")
    options = UiAutomator2Options().load_capabilities(CAPABILITIES)
    options.set_capability('appium:uiautomator2ServerInstallTimeout', 60000)
    try:
        driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
        driver.implicitly_wait(5)
        driver.execute_script('mobile: unlock')
        try:
            driver.terminate_app(CAPABILITIES['appPackage'])
            print("[INFO] 앱 종료 완료 (이전 상태 초기화)")
            time.sleep(2)
        except Exception:
            pass
        driver.activate_app(CAPABILITIES['appPackage'])
        # #8: time.sleep(5) → 앱이 포그라운드에 올 때까지 명시적 대기
        WebDriverWait(driver, 15).until(
            lambda d: d.current_package == CAPABILITIES['appPackage']
        )
        print("[OK] 앱 연결 성공!")
        try:
            info = driver.execute_script('mobile: deviceInfo')
            model = info.get('model', '') if isinstance(info, dict) else ''
            android_ver = info.get('platformVersion', '') if isinstance(info, dict) else ''
            if not (model or android_ver):
                caps = driver.capabilities
                model = caps.get('deviceModel', '')
                android_ver = caps.get('platformVersion', '')
            reporter.set_device(model, android_ver)
            print(f"[INFO] 기기 정보: {model} | Android {android_ver}")
        except Exception:
            pass
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


# ── 스크린샷 ─────────────────────────────────────────────────
@pytest.fixture
def ss(driver_setup, run_id):
    """스크린샷을 outputs/screenshots/{run_id}/ 에 저장.
    reporter에 전달할 '{run_id}/{filename}' 형태의 상대 경로를 반환."""
    run_dir = os.path.join(SCREENSHOT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    def take(name):
        # MMDD-HHmm 형식 (예: 0226-1647)
        timestamp = datetime.now().strftime('%m%d-%H%M')
        # name: S1_Launch -> 0226-1647_S1_Launch.png
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


# ── #1: 리포터 — Ctrl+C 등 강제 종료 시에도 save() 보장 ───────
@pytest.fixture(scope="session")
def reporter(run_id):
    r = TestReporter(RESULTS_DIR, REPORT_DIR, SCREENSHOT_DIR, run_id=run_id)
    _saved = [False]

    def _save_once():
        if not _saved[0]:
            _saved[0] = True
            r.save()

    atexit.register(_save_once)   # 프로세스 종료 시 반드시 저장
    yield r
    _save_once()                  # 정상 종료 시 즉시 저장


# ── #2: 시나리오 컨텍스트 매니저 ─────────────────────────────
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
        # 오류 메시지를 자르지 않고 전체 전달하되, step 이름은 첫 줄만 표시
        full_err = str(e)
        short_err = full_err.split('\n')[0][:100] + ('...' if len(full_err.split('\n')[0]) > 100 else '')
        reporter.step(f"오류: {short_err}", "FAILED", shot)
        reporter.end_scenario("FAILED", error=full_err)
        pytest.fail(full_err)


# ── 각 테스트 전/후 처리 ──────────────────────────────────────
@pytest.fixture(autouse=True)
def ensure_awake(request, driver_setup, run_id):
    """각 테스트 시작 전 화면 깨우기 + 종료 시 자동 스크린샷"""
    driver_setup.execute_script('mobile: unlock')
    driver_setup.activate_app(CAPABILITIES['appPackage'])
    # #8: time.sleep(2) → 명시적 대기
    WebDriverWait(driver_setup, 10).until(
        lambda d: d.current_package == CAPABILITIES['appPackage']
    )

    yield

    try:
        label = (request.node.name
                 .upper()
                 .replace("TEST_SCENARIO_", "S")
                 .replace("_", "-"))[:15]
        # MMDD-HHmm 형식
        timestamp = datetime.now().strftime('%m%d-%H%M')
        # 0226-1647_S1_FINAL.png 형식
        filename = f"{timestamp}_{label}_FINAL.png"
        run_dir = os.path.join(SCREENSHOT_DIR, run_id)
        os.makedirs(run_dir, exist_ok=True)
        driver_setup.save_screenshot(os.path.join(run_dir, filename))
        print(f"[SS-종료] {filename}")
    except Exception as e:
        print(f"[SS-ERR] 종료 스크린샷 실패: {e}")
