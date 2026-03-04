# Bodoc QA 자동화 — PRD (Product Requirements Document)

> 작성일: 2026-03-04
> 대상 앱: Bodoc(보닥) Android 앱
> 프로젝트 유형: 모바일 QA 테스트 자동화

---

## 1. 목적 (Purpose)

Bodoc 앱의 주요 사용자 시나리오를 자동으로 검증하여 릴리스 품질을 보장하고, 수동 QA 비용을 줄인다.
테스트 실행은 브라우저 기반 대시보드로 누구나 쉽게 수행할 수 있어야 한다.

---

## 2. 사용자 (Stakeholders)

| 역할 | 설명 |
|------|------|
| QA 담당자 | 시나리오 실행, 결과 리포트 확인 |
| 개발자 | 코드 변경 후 회귀 테스트 실행 |
| PM | 대시보드에서 테스트 현황 모니터링 |

---

## 3. 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Python 3.12+ |
| 테스트 프레임워크 | Pytest |
| 모바일 자동화 | Appium + UiAutomator2 |
| 대시보드 | Vanilla Python HTTP Server (포트 8888) |
| 디바이스 연결 | ADB (실기기 전용, 에뮬레이터 미지원) |

---

## 4. 현재 테스트 시나리오 (v현재)

| # | 함수명 | 설명 | 마커 |
|---|--------|------|------|
| 1 | `test_scenario_1_app_launch` | 스플래시 화면 + 앱백신 토스트 동시 감지 | `@observe_launch` |
| 2 | `test_scenario_2_initial_permissions` | 초기 권한 팝업 처리 | `@reset_permissions` |
| 3 | `test_scenario_3_kakao_login` | 카카오 OAuth 로그인 전체 플로우 | - |
| 4 | `test_scenario_4_home_tab` | 홈 탭 상단·하단 요소 확인 | - |
| 5 | `test_scenario_5_home_tab_scroll` | 홈 탭 스크롤 단계별 검증 | - |
| 6 | `test_scenario_6_diagnosis_tab` | 진단 탭 + 내 보험료 탭 금액 확인 | - |
| 7 | `test_scenario_7_product_tab` | 상품 추천 탭 요소 확인 | - |
| 8 | `test_scenario_8_health_tab` | 건강 기록 탭 요소 확인 | - |
| 9 | `test_scenario_9_reward_tab` | 보상 탭 요소 확인 | - |
| 10 | `test_scenario_10_menu_validation` | 전체 메뉴 5개 섹션 확인 | - |
| 11 | `test_scenario_11_mydata` | 마이데이터 연동 플로우 (불안정) | - |

---

## 5. 아키텍처

```
tests/
  test_bodoc_flow.py      # 시나리오 진입점
  conftest.py             # driver / ss / reporter 픽스처

pages/
  base_page.py            # 공통 동작 (Wait, Click, Scroll, Tap)
  login_page.py           # 카카오 OAuth 로그인
  home_page.py            # 홈 탭
  diagnosis_page.py       # 진단 탭
  product_page.py         # 상품 탭
  health_page.py          # 건강 탭
  reward_page.py          # 보상 탭
  menu_page.py            # 전체 메뉴
  splash_page.py          # 스플래시 + 앱백신
  intro_page.py           # 초기 권한 팝업
  mydata_flow.py          # 마이데이터 연동

server.py                 # 대시보드 HTTP 서버 (포트 8888)
utils/config.py           # .env 기반 설정 (gitignore)
outputs/                  # 스크린샷 + JSON 결과 (gitignore)
```

### 주요 설계 원칙

- **Page Object Model**: 모든 로케이터는 `pages/`에만 위치. 테스트에 XPath 직접 노출 금지.
- **명시적 대기**: `time.sleep()` 사용 금지. `WebDriverWait` 또는 `wait_for_element()` 사용.
- **탭 전환 대기**: 탭 클릭 후 `[@selected='true']` 속성 확인으로 실제 활성화 여부 검증.
- **실패 처리**: `AssertionError` → `scenario_context`가 캐치 → `pytest.fail()` + 스크린샷 저장.
- **카카오 로그인**: Chrome Custom Tab 방식 (WebView 아님). `driver.contexts` 호출 금지.

---

## 6. 핵심 제약사항

- 실기기 전용 (ADB 연결 필요, CI/CD 없음)
- Windows 환경 기준 (ADB 경로 탐색이 Windows 전용)
- 카카오 로그인은 앱이 미로그인 상태일 때만 동작
- `test_scenario_11_mydata`는 현재 불안정 — UI 안정화 후 활성화

---

## 7. 로드맵 (향후 개선 과제)

### 단기 (즉시 가능)

- [ ] **멀티 디바이스 지원**: `.env`에 기기 목록 설정, 병렬 실행
- [ ] **CI 연동**: GitHub Actions에서 에뮬레이터 기반 스모크 테스트 자동 실행
- [ ] **시나리오 11 안정화**: 마이데이터 연동 플로우 UI 요소 확정 후 활성화
- [ ] **로케이터 외재화**: XPath를 YAML/JSON으로 분리하여 UI 변경 대응 용이하게

### 중기

- [ ] **iOS 지원**: XCUITest 드라이버 추가, 플랫폼 분기 처리
- [ ] **리포트 고도화**: Allure 리포트 연동 (단계별 스크린샷 + 타임라인)
- [ ] **성능 측정**: 탭 전환 응답 시간, 화면 로드 시간 측정 및 임계값 알림

### 장기

- [ ] **Visual Regression**: 화면 캡처 비교로 UI 변경 자동 감지
- [ ] **AI 기반 로케이터**: 요소 텍스트/좌표 변경 시 자동 재탐색

---

## 8. 대시보드 API 목록

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 대시보드 HTML |
| GET | `/api/appium/start` | Appium 서브프로세스 시작 |
| GET | `/api/appium/stop` | Appium 서브프로세스 중지 |
| GET | `/api/appium/status` | Appium 실행 상태 + 버전 |
| GET | `/api/device/status` | ADB 기기 목록 |
| GET | `/api/run?s=all\|1,2,3` | 시나리오 실행 |
| GET | `/api/stop` | 실행 중 테스트 중단 |
| GET | `/api/test/status` | 현재 실행 상태 |
| GET | `/api/logs?offset=0` | 로그 스트리밍 |
| GET | `/api/results` | 저장된 결과 조회 |
| GET | `/api/test/definition` | 시나리오 목록 (AST 추출) |

---

## 9. 환경 설정 체크리스트

```
[ ] .env 파일 생성 (.env.example 참고)
[ ] DEVICE_NAME = adb devices 시리얼
[ ] CHROMEDRIVER_DIR = platform-tools 경로
[ ] appium 서버 실행 (npm install -g appium)
[ ] appium driver install uiautomator2
[ ] pip install Appium-Python-Client pytest python-dotenv
[ ] 실기기 ADB 연결 및 개발자 옵션 활성화
```
