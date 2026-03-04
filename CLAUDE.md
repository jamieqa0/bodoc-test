# CLAUDE.md

이 파일은 Claude Code(claude.ai/code)가 이 저장소의 코드를 작업할 때 참고하는 안내 문서입니다.

---

## 프로젝트 개요

**Bodoc QA 자동화**는 Bodoc 보험 앱을 위한 Android 모바일 테스트 자동화 프로젝트입니다. 다음 요소로 구성됩니다:
- **Pytest + Appium** 테스트 시나리오 (Page Object Model)
- **Python HTTP 대시보드** (`server.py`) — 브라우저에서 테스트를 실행하고 결과를 확인
- **HTML 리포트 생성** — 스크린샷과 단계별 로그 포함

프로젝트는 ADB를 통해 실제 Android 기기를 대상으로 합니다. 테스트는 로컬에서 실행되며 CI/CD 파이프라인은 없습니다.

---

## 설정 및 구성

### 환경 변수

`.env.example`을 `.env`로 복사(gitignore됨)하고 기기별 값을 입력하세요:

```env
APPIUM_SERVER_URL=http://localhost:4723
DEVICE_NAME=<your_adb_device_serial>
CHROMEDRIVER_DIR=<path_to_platform-tools>
```

`utils/config.py`는 실행 시 `.env`에서 자동 생성되며 gitignore됩니다. 두 파일 모두 직접 수정하거나 커밋하지 마세요.

### 설치

```bash
pip install Appium-Python-Client pytest python-dotenv
npm install -g appium
appium driver install uiautomator2
```

---

## 테스트 실행

### 대시보드를 통한 실행 (권장)

```bash
# 터미널 1
appium

# 터미널 2
python server.py
# 브라우저: http://localhost:8888
```

### pytest 직접 실행

```bash
# 전체 시나리오
pytest tests/test_bodoc_flow.py -v

# 단일 시나리오 (부분 매칭 방지를 위해 전체 함수명 사용)
pytest tests/test_bodoc_flow.py::test_scenario_1_app_launch

# 키워드로 여러 시나리오 선택 (-k "scenario_1"은 scenario_10, scenario_11도 매칭되므로 주의)
pytest tests/test_bodoc_flow.py -k "test_scenario_4_home_tab or test_scenario_5_home_tab_scroll"
```

---

## 테스트 시나리오 (현재)

| # | 테스트 함수 | 설명 |
|---|------------|------|
| 1 | `test_scenario_1_app_launch` | 스플래시 화면 + 앱백신 토스트 동시 감지 (`@observe_launch`) |
| 2 | `test_scenario_2_initial_permissions` | 초기 권한 팝업 처리 (`@reset_permissions`) |
| 3 | `test_scenario_3_kakao_login` | Chrome Custom Tab을 통한 카카오 OAuth 로그인 (NATIVE 컨텍스트 전용) |
| 4 | `test_scenario_4_home_tab` | 홈 탭 요소 검증 |
| 5 | `test_scenario_5_home_tab_scroll` | 홈 탭 스크롤 단계별 검증 |
| 6 | `test_scenario_6_diagnosis_tab` | 진단 탭 + 보험료 탭 |
| 7 | `test_scenario_7_product_tab` | 상품 추천 탭 |
| 8 | `test_scenario_8_health_tab` | 건강 기록 탭 |
| 9 | `test_scenario_9_reward_tab` | 리워드/보상 탭 |
| 10 | `test_scenario_10_menu_validation` | 전체 메뉴 섹션 (5개 카테고리) |
| 11 | `test_scenario_11_mydata` | 마이데이터 연동 플로우 (불안정할 수 있음) |

시나리오 ID는 `server.py:_extract_scenarios()`의 AST 파싱을 통해 테스트 파일에서 동적으로 추출됩니다. 정적 `TEST_DEFINITIONS` 딕셔너리는 없으며, 새 테스트 함수가 자동으로 인식됩니다.

---

## 아키텍처 및 주요 패턴

### Page Object Model (POM)

모든 UI 인터랙션은 `pages/`에 위치합니다. 테스트는 페이지 메서드만 호출하며, 로케이터는 테스트 파일에 등장하지 않습니다.

- 모든 페이지 클래스는 `BasePage` (`pages/base_page.py`)를 상속
- `BasePage` 제공 메서드: `wait_for_element()`, `click()`(stale-element 재시도), `scroll_down()`, `scroll_up()`, `scroll_to_text()`, `tap_coordinate()`, `wait_for_home()`, `dismiss_any_permission_popup()`
- 페이지 클래스는 `(driver, ss)`로 인스턴스화 — driver와 스크린샷 함수 모두 전달
- `splash_page.py`는 스플래시 + 앱백신 토스트 동시 감지 처리 (구 문서에는 없지만 `pages/`에 존재)

### 픽스처 플로우 (`tests/conftest.py`)

```
run_id (세션 범위 타임스탬프)
  └── reporter (세션 범위 TestReporter + atexit 저장)
        └── driver_setup (세션 범위 Appium 드라이버 초기화/정리)
              ├── ss (함수 범위 스크린샷 헬퍼 → outputs/screenshots/{run_id}/)
              ├── inject_device_info (세션 autouse — 기기 모델/OS를 reporter에 전달)
              └── app_reset (함수 autouse — 모든 테스트 전후 실행)
```

**`app_reset`** (autouse)은 모든 테스트 전에 실행:
1. WebView에 있으면 `NATIVE_APP` 컨텍스트로 복귀
2. `terminate_app`으로 앱 완전 종료
3. `@pytest.mark.reset_permissions` 마커 시: `adb shell pm clear <pkg>`로 앱 데이터 초기화
4. 화면 잠금 해제 (`mobile: unlock` + `adb shell wm dismiss-keyguard`)
5. `activate_app`으로 앱 재실행
6. 초기 화면 대기 (`_INITIAL_SCREEN_XPATH`) — `@pytest.mark.observe_launch` 시 생략

각 테스트 후 `app_reset`이 최종 스크린샷을 자동으로 캡처합니다.

### `scenario_context` 사용법

모든 테스트는 본문을 다음으로 감쌉니다:

```python
with scenario_context(reporter, "시나리오N_설명", ss, "SN"):
    ...
```

시그니처: `scenario_context(reporter, name, ss, fail_prefix)`.
예외 발생 시: `{fail_prefix}_FAIL` 이름으로 스크린샷 저장, FAILED 처리 후 `pytest.fail()` 호출.

### Pytest 마커

| 마커 | 효과 |
|------|------|
| `@pytest.mark.observe_launch` | `app_reset`의 초기 화면 대기 생략; 테스트가 직접 실행 시퀀스를 관찰 |
| `@pytest.mark.reset_permissions` | 실행 전 `adb shell pm clear`로 권한 팝업 재노출 강제 |

### 카카오 OAuth — NATIVE 컨텍스트 전용

카카오 SDK 2.x 이상은 WebView가 아닌 **Chrome Custom Tab**을 사용합니다. 로그인 플로우에서 `driver.contexts`를 호출하지 마세요 — Chromedriver 세션 오류가 발생합니다. `LoginPage`는 텍스트 기반 XPath 셀렉터를 사용하여 `NATIVE_APP` UiAutomator2 컨텍스트 내에서만 카카오 OAuth 화면과 인터랙션합니다. 텍스트 요소를 찾지 못하면 좌표 폴백을 사용합니다.

### 로케이터 전략 (우선순위)

1. **XPath 텍스트/content-desc** — `LOCATOR = "//*[@text='...']"` (클래스 상수는 `UPPER_SNAKE_CASE`)
2. **UiAutomator 스크롤** — 화면 밖 요소용
3. **`tap_coordinate(x_ratio, y_ratio)`** — 화면 크기 무관 비율 기반 탭
4. **`[last()]` XPath 조건** — 중복 텍스트가 있을 때 탭 바 아이콘 지정

### 스크린샷 명명 규칙

```
outputs/screenshots/{run_id}/{MMDD-HHMM}_{ScenarioTag}_{StepName}.png
```

예: `0226-1647_S3_Kakao_OAuth_Page_Loaded.png`

### 로그 접두어

| 접두어 | 의미 |
|--------|------|
| `[OK]` | 단계 통과 |
| `[WARN]` | 치명적이지 않은 문제 |
| `[FAIL]` | 단계 또는 시나리오 실패 |
| `[INFO]` | 일반 정보 |
| `[DEBUG]` | 상세 진단 |

---

## HTTP API (`server.py` — 포트 8888)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 대시보드 HTML |
| `GET` | `/api/appium/start` | Appium 서브프로세스 시작 |
| `GET` | `/api/appium/stop` | Appium 서브프로세스 중지 |
| `GET` | `/api/appium/status` | Appium 실행 상태 + 버전 |
| `GET` | `/api/device/status` | ADB 기기 목록 (모델 및 Android 버전 포함) |
| `GET` | `/api/env` | Python/pytest 환경 정보 |
| `GET` | `/api/run?s=all\|1,2,3` | 선택한 시나리오 테스트 실행 |
| `GET` | `/api/stop` | 실행 중인 테스트 프로세스 중단 |
| `GET` | `/api/test/status` | 현재 실행 상태 + 진행 인덱스 |
| `GET` | `/api/logs?offset=0` | 오프셋 페이지네이션으로 로그 스트리밍 |
| `GET` | `/api/logs/clear` | 로그 버퍼 초기화 |
| `GET` | `/api/results` | 저장된 JSON 결과 조회 |
| `GET` | `/api/results/delete?date=YYYY-MM-DD` | 해당 날짜 이전 결과 파일 삭제 |
| `GET` | `/api/test/definition` | 시나리오 목록 (테스트 파일에서 AST 추출) |
| `GET` | `/screenshots/{run_id}/{file}` | PNG 스크린샷 제공 |

모든 응답은 JSON 형식입니다. CORS가 활성화되어 있습니다 (`Access-Control-Allow-Origin: *`).

---

## 코딩 컨벤션

- **Python 스타일**: PEP 8; 메서드와 변수는 `snake_case`
- **로케이터 상수**: 각 페이지 클래스의 `UPPER_SNAKE_CASE` 클래스 속성
- **페이지 클래스에 테스트 로직 금지** — 페이지 클래스는 액션과 요소 대기만 노출
- **테스트 파일에 로케이터 금지** — 모든 셀렉터는 `pages/`에 위치
- **오류 처리**: 요소/단계 실패 시 `AssertionError` 발생; `scenario_context`가 이를 잡아 `pytest.fail()` 호출
- **설정**: 기기명, 앱 패키지, URL 하드코딩 금지 — `.env` / `utils/config.py` 사용
- **대기**: `WebDriverWait` / `wait_for_element()` 사용, `time.sleep()` 사용 금지

---

## 새 테스트 또는 페이지 추가

### 새 페이지 클래스

1. `pages/my_feature_page.py` 생성 후 `BasePage` 상속
2. 로케이터 상수를 클래스 속성으로 정의 (`UPPER_SNAKE_CASE`)
3. `self.wait_for_element()`, `self.click()` 등을 사용해 액션 메서드 구현
4. 테스트 함수에서 `MyPage(driver, ss)`로 인스턴스화

### 새 테스트 시나리오

1. `tests/test_bodoc_flow.py`에 `test_scenario_N_name(driver, ss, reporter)` 추가
2. 본문을 `with scenario_context(reporter, "시나리오N_설명", ss, "SN"):` 으로 감싸기
3. 대시보드가 AST 파싱을 통해 새 시나리오를 자동으로 인식 — 별도 등록 불필요

---

## 주의 사항

- 카카오 로그인 플로우에서 `driver.contexts` 호출 금지 — Chrome Custom Tab이 Chromedriver 세션 오류를 유발
- 한 자리 N에 대해 pytest에서 `-k scenario_N` 사용 금지 (예: `-k scenario_1`은 scenario_10, scenario_11도 매칭됨); 전체 함수명 사용
- `outputs/`, `.env`, `utils/config.py` 커밋 금지
- `utils/config.py` 직접 수정 금지 — `.env`에서 재생성됨

---

## 알려진 한계

- `server.py`의 ADB 경로 탐색은 Windows 전용 (하드코딩된 Windows 경로); Linux/Mac 사용자는 `adb`가 `PATH`에 등록되어 있어야 함
- 삼성 기기는 잠금 화면 해제를 위해 `mobile: unlock` 외에 `adb shell wm dismiss-keyguard` 추가 필요
- `splash_page.py`의 로케이터 (`SPLASH_LOGO`, `SPLASH_ACTIVITY_KEYWORD`)와 `login_page.py`의 로케이터 (`KAKAO_OAUTH_READY` 등)는 각 물리적 기기에 맞게 조정 필요
- `test_scenario_11_mydata`는 구현되었으나 UI 안정화 전까지 불안정할 수 있음
- CI/CD 없음 — 모든 테스트는 연결된 Android 기기를 통해 수동 실행
