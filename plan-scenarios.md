# Bodoc QA — 테스트 시나리오 명세서

> 작성일: 2026-03-04
> 테스트 파일: `tests/test_bodoc_flow.py`
> 환경: Android 실기기 + Appium (UiAutomator2)

---

## 공통 사항

### 픽스처 실행 흐름

모든 시나리오는 `app_reset` autouse 픽스처가 사전에 실행된다.

```
app_reset (각 시나리오 실행 전)
  ├── 1. WebView 컨텍스트 → NATIVE_APP 복귀
  ├── 2. terminate_app (앱 완전 종료)
  ├── 3. @reset_permissions 마커 시: adb shell pm clear (앱 데이터 초기화)
  ├── 4. 화면 잠금 해제 (mobile: unlock + adb shell wm dismiss-keyguard)
  ├── 5. activate_app (앱 재실행)
  └── 6. 초기 화면 대기 (_INITIAL_SCREEN_XPATH) — @observe_launch 시 생략
```

### 시나리오 래퍼

모든 시나리오는 `scenario_context`로 감싸져 있다.

```python
with scenario_context(reporter, "시나리오N_설명", ss, "SN"):
    ...
# 예외 발생 시: {SN}_FAIL 스크린샷 저장 → FAILED 처리 → pytest.fail()
```

### 스크린샷 명명 규칙

```
outputs/screenshots/{run_id}/{MMDD-HHMM}_{ScenarioTag}_{StepName}.png
예) 0304-1430_S3_KakaoOAuthPageLoaded.png
```

#### ScenarioTag 규칙

| 시나리오 | ScenarioTag | 담당 파일 |
|---------|------------|---------|
| 1 앱 런치 | `S1` | `test_bodoc_flow.py` |
| 2 초기 권한 | `S2` | `test_bodoc_flow.py`, `intro_page.py` |
| 3 카카오 로그인 | `S3` | `test_bodoc_flow.py`, `login_page.py` |
| 4 홈 탭 | `S4` | `home_page.verify_home_elements` |
| 5 홈 탭 스크롤 | `S5` | `home_page.verify_home_scroll_steps` |
| 6 진단 탭 | `S6` | `diagnosis_page.py` |
| 7 상품 탭 | `S7` | `product_page.py` |
| 8 건강 탭 | `S8` | `health_page.py` |
| 9 보상 탭 | `S9` | `reward_page.py` |
| 10 메뉴 | `S10` | `menu_page.py` |
| 11 마이데이터 | `S11` | `test_bodoc_flow.py` |

#### StepName 규칙

- **형식**: `{단계번호}_{설명}` (예: `S4_2_HomeTabNav`)
- **설명 부분은 CamelCase**: 단어 첫 글자를 대문자로, 내부 언더스코어 금지 (예: `Home_Tab_Nav` ❌ → `HomeTabNav` ✅)
- **단계 번호**: 테스트 파일에서 `ss("S{N}_1_...")` 로 진입 촬영 → 페이지 메서드는 `S{N}_2_`부터 시작
- **실패 스크린샷**: `S{N}_{단계번호}_FAIL_{CamelCase설명}` 또는 `S{N}_FAIL` (시나리오 전체 실패)
- **공유 헬퍼 메서드** (`go_home`, `go_diagnosis` 등) 내부에서 `self.click()`이 자동 촬영하는 `MoveToXxx` 계열은 예외적으로 ScenarioTag 생략 허용

---

## 시나리오 목록

| # | 함수명 | 마커 | 상태 |
|---|--------|------|------|
| 1 | `test_scenario_1_app_launch` | `@observe_launch` | 안정 |
| 2 | `test_scenario_2_initial_permissions` | `@reset_permissions` | 안정 |
| 3 | `test_scenario_3_kakao_login` | - | 안정 |
| 4 | `test_scenario_4_home_tab` | - | 안정 |
| 5 | `test_scenario_5_home_tab_scroll` | - | 안정 |
| 6 | `test_scenario_6_diagnosis_tab` | - | 안정 |
| 7 | `test_scenario_7_product_tab` | - | 안정 |
| 8 | `test_scenario_8_health_tab` | - | 안정 |
| 9 | `test_scenario_9_reward_tab` | - | 안정 |
| 10 | `test_scenario_10_menu_validation` | - | 안정 |
| 11 | `test_scenario_11_mydata` | - | ⚠️ 불안정 |

---

## 시나리오 1 — 앱 런치

**함수**: `test_scenario_1_app_launch`
**마커**: `@pytest.mark.observe_launch`
**목적**: 앱 실행 직후 스플래시 화면과 보안 앱백신 토스트가 정상 노출되는지 검증

> `@observe_launch` 마커로 인해 `app_reset`의 초기 화면 대기 단계를 생략하고,
> 이 시나리오가 직접 앱 시작 시퀀스를 관찰한다.

### 검증 단계

| 단계 | 설명 | 성공 조건 | 타임아웃 | 스크린샷 |
|------|------|----------|----------|----------|
| 1+2 | 스플래시 화면 + 앱백신 토스트 동시 감지 | 두 조건 모두 True | 10초 | `S1_1_SplashAndToastDetected` |
| 3 | 초기 화면 진입 확인 | 로그인/홈/접근권한 안내 화면 중 하나 | 15초 | `S1_3_InitialScreenReached` |

### 스플래시 감지 방법 (동시 폴링, 0.2초 간격)

- **Activity 기반**: `driver.current_activity`에 `'splash'` 포함 여부
- **UI 요소 기반 (폴백)**: `resource-id`에 `splash`, `logo`, `img`, `icon` 포함 ImageView

### 앱백신 토스트 감지

- XPath: `//android.widget.Toast[contains(@text,'TouchEn mVaccine')]`
- 토스트는 수 초 내에 사라지므로 단일 폴링 루프에서 누적 추적

### 초기 화면 분기 판별

```
홈 화면 ('@text=홈' 존재)     → "홈 화면 (로그인 상태)"
접근권한 안내 화면 존재        → "스마트폰 앱 접근권한 안내 (최초 실행)"
그 외                         → "로그인 화면 (미로그인 상태)"
```

### 실패 케이스

| 조건 | 스크린샷 | 에러 메시지 |
|------|----------|------------|
| 스플래시 미감지 | `S1_FAIL_SplashNotVisible` | 현재 Activity 포함, 로케이터 수정 안내 |
| 앱백신 토스트 미감지 | `S1_FAIL_AppVaccineToastNotVisible` | 기대 텍스트 포함, XPath 확인 안내 |
| 초기 화면 타임아웃 | `S1_3_FAIL_InitialScreenTimeout` | 15초 내 화면 미노출 |

---

## 시나리오 2 — 초기 권한 팝업 처리

**함수**: `test_scenario_2_initial_permissions`
**마커**: `@pytest.mark.reset_permissions`
**목적**: 앱 최초 실행 시 노출되는 권한 요청 팝업 시퀀스를 처리하고 초기 화면 진입 확인

> `@reset_permissions` 마커로 인해 실행 전 `adb shell pm clear`로 앱 데이터를 초기화해 권한 팝업을 강제 노출시킨다.

### 처리하는 권한 팝업 시퀀스

| 순서 | 팝업명 | 동작 | 스크린샷 태그 |
|------|--------|------|--------------|
| 1 | 스마트폰 앱 접근권한 안내 | 스크롤 후 '다음' 클릭 | `S2_1_AccessRights` |
| 2 | 전화 권한 허용 | '허용' 클릭 | `S2_2_PhonePermission` |
| 3 | 앱 알림 안내 확인 | '확인' 클릭 | `S2_3_NotifGuide` |
| 4 | 알림 권한 허용 | '허용' 클릭 | `S2_4_NotifPermission` |
| 5 | mop-up (잔여 팝업 처리) | '허용' / '확인' 반복 클릭 (최대 4회) | — |

> 각 팝업은 선택적(optional) — 노출되지 않으면 `except Exception`으로 무시하고 다음 단계 진행

### Android 버전별 팝업 순서 차이

| Android 버전 | 팝업 노출 순서 |
|-------------|--------------|
| Android 15 | 접근권한(다음) → 전화(허용) → 앱 알림 안내(확인) → 알림 시스템(허용) |
| Android 8  | 접근권한(다음) → 전화(허용) → 알림 시스템(허용) → 앱 알림 안내(확인) |

Android 8에서는 3·4번 순서가 반전되므로 고정 4단계만으로는 마지막 '확인' 팝업이 잔류한다.
mop-up 단계(5번)에서 `허용`/`확인` 중 남아있는 것을 추가 처리해 두 버전 모두 대응한다.

### 검증 단계

| 단계 | 설명 | 성공 조건 | 타임아웃 |
|------|------|----------|----------|
| 1 | 권한 팝업 시퀀스 처리 | 처리 건수 포함 PASSED (0건도 정상) | 각 5초 |
| 2 | 처리 후 초기 화면 진입 | 로그인/홈/접근권한 화면 중 하나 | 10초 |

### 주의사항

- `noReset=True` 환경에서는 팝업이 노출되지 않아 0건 처리가 정상
- Android 13+ `POST_NOTIFICATIONS` 다이얼로그는 어느 시점에든 나타날 수 있음 (`dismiss_any_permission_popup`으로 처리)
- Android 버전마다 팝업 노출 순서가 다를 수 있으므로 mop-up 단계가 필수 (`intro_page.py` `handle_all_initial_permissions` 참고)

---

## 시나리오 3 — 카카오 로그인

**함수**: `test_scenario_3_kakao_login`
**목적**: 카카오 계정을 통한 OAuth 로그인 전체 플로우 검증

> **중요**: 앱이 이미 로그인된 상태라면 실패. 대시보드 UI의 Skip 버튼으로 건너뛸 것.

### 카카오 로그인 기술 배경

Kakao SDK 2.x는 WebView가 아닌 **Chrome Custom Tab**을 사용한다.
- `driver.contexts` 호출 → Chromedriver 세션 오류 발생 → **절대 호출 금지**
- 해결: `NATIVE_APP` 컨텍스트(UiAutomator2)만으로 텍스트 기반 XPath 접근

### 검증 단계

| 단계 | 설명 | 담당 메서드 | 스크린샷 |
|------|------|------------|----------|
| 1 | 초기 권한 팝업 처리 (옵션) | `intro.handle_all_initial_permissions()` | `S3_1_PermissionsHandled` |
| 2 | 로그인 화면 진입 확인 | `login.ensure_login_screen()` (15초 대기) | `S3_2_LoginScreenVisible` |
| 3 | '카카오로 시작하기' 버튼 클릭 | `login.start_kakao_login()` | `S3_3_KakaoButtonClicked` |
| 4 | 카카오 OAuth 페이지 로드 확인 | `login.wait_for_kakao_oauth_ui()` (15초) | `S3_4_KakaoOAuthPageLoaded` |
| 5 | '계속하기' 클릭 | `login.click_kakao_continue()` | `S3_5_KakaoContinueClicked` |
| 6 | 첫 번째 카카오 계정 선택 | `login.select_first_kakao_account()` | `S3_6_KakaoAccountSelected` |
| 7 | 홈 화면 진입 확인 | `WebDriverWait` 20초 | `S3_7_HomeScreenReached` |

### 폴백 전략

| 단계 | 1차 시도 | 폴백 |
|------|----------|------|
| '계속하기' 클릭 | XPath 텍스트 기반 | 좌표 `(0.5, 0.66)` |
| 계정 선택 | XPath `@text='@...'` | 좌표 `(0.5, 0.35)` |
| 자동 로그인 완료 감지 | '홈' 탭 존재 확인 | 계정 선택 건너뜀 |

### 로케이터

```python
KAKAO_START_BUTTON        = "//*[@text='카카오로 시작하기']"
KAKAO_OAUTH_READY         = "//*[@text='계속하기'] | //*[@text='카카오계정으로 로그인'] | ..."
KAKAO_CONTINUE_NATIVE     = "//*[@text='계속하기' or @text='Continue' or @text='동의']"
KAKAO_FIRST_ACCOUNT_NATIVE = "(//*[contains(@text,'@') or contains(@resource-id,'account')])[1] | ..."
```

---

## 시나리오 4 — 홈 탭 요소 확인

**함수**: `test_scenario_4_home_tab`
**목적**: 홈 탭 진입 후 주요 UI 요소가 모두 정상 노출되는지 확인

### 실제 화면 구성 (스크린샷 기준)

홈 탭 최상단부터 하단 순서:
1. 내 보험 종합진단 (점수 게이지 + 전문가 의견 듣기 버튼)
2. 매월 내는 보험료
3. 숨은 보험금 (총 금액 + 숨은 보험금 조회하기 버튼)
4. 이런 상황일 때, 보험금 받을 수 있을까요?
5. AI 고민상담소
6. 내 건강검진 분석 결과는? (건강정보 확인하기 버튼)
7. 내 보험 추가하기 (최하단)

### 검증 단계

| 단계 | 검증 요소 | 스크롤 필요 | 스크린샷 |
|------|----------|------------|----------|
| 진입 | 홈 탭 이동 (`wait_for_home` → HOME_TAB 클릭) | - | `S4_1_EntryHomeTab` |
| 1 | 홈 탭 네비게이션 노출 | 불필요 | `S4_2_HomeTabNav` |
| 2 | '보험 종합진단' 텍스트 | 불필요 | `S4_3_HomeInsuranceDiagnosis` |
| 3 | '매월 내는 보험료' 텍스트 | 불필요 | `S4_4_HomeMonthlyPremium` |
| 4 | '숨은 보험금' 텍스트 | 필요 (최대 8회) | `S4_5_HomeHiddenInsurance` |
| 5 | '내 보험 추가하기' 텍스트 | 필요 (최대 10회) | `S4_6_HomeAddInsuranceBtn` |

### 사전 조건

- 앱이 로그인된 상태
- `wait_for_home()` 통과 (홈 탭바 노출 확인, 15초 타임아웃)

---

## 시나리오 5 — 홈 탭 스크롤 단계별 검증

**함수**: `test_scenario_5_home_tab_scroll`
**목적**: 홈 화면을 처음부터 끝까지 순차 스크롤하며 모든 콘텐츠 섹션 노출 확인

### 실제 화면 스크롤 순서 (스크린샷 실측 기준)

```
내 보험 종합진단 → 매월 내는 보험료 → 숨은 보험금
  → 이런 상황일 때/손해사정사에게 → AI 고민상담소 → 건강정보 확인하기
```

> ⚠️ 이전 코드는 AI 고민상담소(4번)를 숨은 보험금(5번)보다 먼저 찾으려 했으나,
> 실제 화면에서는 숨은 보험금이 더 위에 위치한다. 순서 수정 완료.

### 검증 단계 (상단→하단 순서)

| 단계 | 검증 요소 | 동작 | 스크린샷 |
|------|----------|------|----------|
| 0 | 화면 상단 초기화 | `scroll_up(5)` | - |
| **1** | **테스트 진입** | **`ss("S5_1_EntryHomeTab")` — test_bodoc_flow.py에서 촬영** | `S5_1_EntryHomeTab` |
| 2 | 홈탭 상단 재확인 | HOME_TAB 대기 (scroll_up 후) | `S5_2_HomeEntry` |
| 3 | 내 보험 종합진단 | 요소 대기 후 1회 스크롤 다운 | `S5_3_HomeInsuranceDiagnosis` |
| 4 | 매월 내는 보험료 | 요소 대기 후 1회 스크롤 다운 | `S5_4_HomeMonthlyPremium` |
| 5 | 숨은 보험금 | `scroll_until_visible` (최대 5회) | `S5_5_HomeHiddenInsurance` |
| 6 | '이런 상황일 때' 또는 '손해사정사에게' | `scroll_until_visible` (최대 5회) | `S5_6_HomeAdjuster` |
| 7 | AI 고민상담소 | `scroll_until_visible` (최대 8회) | `S5_7_HomeAIConsulting` |
| - | 최하단 도달 | `scroll_to_bottom()` (최대 12회 스와이프) | - |
| 8 | 건강정보 확인하기 | `scroll_until_visible` (최대 5회) | `S5_8_HomeHealthInfo` |

---

## 시나리오 6 — 진단 탭 요소 확인

**함수**: `test_scenario_6_diagnosis_tab`
**목적**: 진단 탭 진입, 콘텐츠 확인, '내 보험료' 서브탭의 보험료 금액 표시 검증

### 검증 단계

| 단계 | 설명 | 담당 메서드 | 스크린샷 |
|------|------|------------|----------|
| 진입 | 진단 탭 클릭 + 탭 활성화 대기 | `go_diagnosis()` | `S6_1_DiagnosisTabEntry` |
| 1 | 진단 탭 네비게이션 노출 | `wait_for_element(DIAGNOSIS_TAB)` | `S6_2_DiagnosisTabNav` |
| 2 | 보험 진단 관련 텍스트 | `"//*[contains(@text,'진단') or ...]"` | `S6_3_DiagnosisTextCheck` |
| 3 | 중간 스크롤 | `scroll_down(2)` × 2회 | `S6_4_ScrollDiagnosisMid`, `S6_5_ScrollDiagnosisBottom` |
| 4 | 상단으로 스크롤 후 '내 보험료' 탭 대기 | `scroll_up(3)` + `WebDriverWait(PREMIUM_TAB)` | - |
| 5 | '내 보험료' 탭 클릭 | `click(PREMIUM_TAB)` (실패 시 좌표 `(0.75, 0.15)` 폴백) | `S6_6_DiagnosisPremiumTabEntry` |
| 6 | '매월 내는 보험료' 타이틀 확인 | `wait_for_element(PREMIUM_TITLE, 5초)` | - |
| 7 | 실제 보험료 금액 추출 | `val_el.text` (`"원"` 포함 요소) | `S6_7_PremiumAmountCheck` |

### 로케이터

```python
DIAGNOSIS_TAB  = "//*[@text='진단']"
PREMIUM_TAB    = "//*[contains(@text,'내 보험료') or contains(@text,'내보험료')]"
PREMIUM_TITLE  = "//*[contains(@text,'매월 내는 보험료')]"
PREMIUM_VALUE  = "//*[contains(@text,'원') and string-length(@text) > 2]"
```

### 탭 전환 대기 방식

```python
# 탭 클릭 후 해당 탭이 선택(활성화)됐을 때만 통과
WebDriverWait(self.driver, 10).until(
    lambda d: d.find_elements(AppiumBy.XPATH, self.DIAGNOSIS_TAB + "[@selected='true']")
)
```

---

## 시나리오 7 — 상품 탭 요소 확인

**함수**: `test_scenario_7_product_tab`
**목적**: 상품 탭 진입 및 추천 상품 타이틀 노출 확인

### 검증 단계

| 단계 | 설명 | 성공 조건 | 스크린샷 |
|------|------|----------|----------|
| 진입 | 상품 탭 클릭 + `[@selected='true']` 대기 | 탭 활성화 | `S7_1_ProductTabEntry` |
| 1 | '보닥 회원만을 위한 추천 상품' 타이틀 탐색 | UiScrollable 스크롤 후 XPath 확인 (7초) | `S7_2_ElemRecommendTitle` |

### 로케이터

```python
PRODUCT_TAB  = "//*[@text='상품']"
TARGET_TEXT  = "보닥 회원만을 위한 추천 상품"
TARGET_XPATH = "//*[contains(@text,'보닥 회원만을 위한 추천 상품')]"
```

---

## 시나리오 8 — 건강 탭 요소 확인

**함수**: `test_scenario_8_health_tab`
**목적**: 건강 탭 진입 및 '건강 기록' 타이틀 노출 확인

### 검증 단계

| 단계 | 설명 | 성공 조건 | 스크린샷 |
|------|------|----------|----------|
| 진입 | 건강 탭 아이콘 클릭 + `[@selected='true']` 대기 | 탭 활성화 | `S8_1_HealthTabEntry` |
| 1 | '건강 기록' 타이틀 탐색 | UiScrollable 스크롤 후 XPath 확인 (7초) | `S8_2_ElemHealthRecord` |

### 로케이터 특이사항

```python
# 콘텐츠 영역에도 '건강' 텍스트가 중복 존재 → [last()]로 탭바 아이콘 선택
HEALTH_ICON = "(//*[@text='건강' or @content-desc='건강'])[last()]"
HEALTH_TAB  = "//*[@text='건강']"
```

---

## 시나리오 9 — 보상 탭 요소 확인

**함수**: `test_scenario_9_reward_tab`
**목적**: 보상 탭 진입 및 보상 관련 타이틀 노출 확인

### 검증 단계

| 단계 | 설명 | 성공 조건 | 스크린샷 |
|------|------|----------|----------|
| 진입 | 보상 탭 아이콘 클릭 + `[@selected='true']` 대기 | 탭 활성화 | `S9_1_RewardTabEntry` |
| 1 | 보상 관련 타이틀 탐색 ('보상 사례' 키워드 스크롤) | 아래 XPath 중 하나 (7초) | `S9_2_ElemRewardCase` |

### 검증 XPath (다중 조건 OR)

```python
"//*[contains(@text,'유형별 보상 사례')
  or contains(@text,'유형별 보상사례')
  or contains(@text,'병원비 간편 청구하기')
  or contains(@text,'자주 묻는 보상 질문')
  or contains(@text,'보상 문의하기')
  or contains(@text,'보상 질문')]"
```

### 로케이터 특이사항

```python
# 콘텐츠 영역에도 '보상' 텍스트 중복 → [last()]로 탭바 아이콘 선택
REWARD_ICON = "(//*[@text='보상' or @content-desc='보상'])[last()]"
```

---

## 시나리오 10 — 전체 메뉴 검증

**함수**: `test_scenario_10_menu_validation`
**목적**: 전체 메뉴 진입 후 5개 섹션 타이틀이 모두 노출되는지 확인

### 검증 단계

| 단계 | 설명 | 스크린샷 |
|------|------|----------|
| 진입 | '메뉴' 버튼 클릭 (`[1]`로 첫 번째 선택) | `S10_1_MenuOpened` |
| 1 | '보험' 섹션 타이틀 확인 | `S10_SectionInsurance` |
| 2 | '보상/청구' 섹션 타이틀 확인 | `S10_SectionClaim` |
| 3 | '생활/건강' 섹션 타이틀 확인 | `S10_SectionLife` |
| 4 | '정보' 섹션 타이틀 확인 (추가 scroll_down 3회) | `S10_SectionInfo` |
| 5 | '고객서비스' 섹션 타이틀 확인 | `S10_SectionCustomerService` |
| 복귀 | `driver.back()` + '홈' 탭 등장 대기 (10초) | - |

### 섹션 탐색 전략

각 섹션마다:
1. (필요 시) 추가 `scroll_down` 수행
2. `scroll_to_text(keyword)` (UiScrollable, 최대 8회)
3. `wait_for_element(xpath, 7초)` 로 타이틀 존재 확인

### '정보' 섹션 주의사항

메뉴 최하단에 위치하므로 `scroll_to_text` 전 `scroll_down(3)` 선행 수행.

---

## 시나리오 11 — 마이데이터 연동 ⚠️

**함수**: `test_scenario_11_mydata`
**상태**: 구현 완료, UI 안정화 전까지 불안정할 수 있음
**목적**: 홈 탭에서 마이데이터 연동 전체 플로우 검증

### 검증 단계

| 단계 | 설명 | 스크린샷 |
|------|------|----------|
| 1 | 홈 탭 진입 | `S11_1_EntryHomeTab` |
| 2 | '내 보험 추가하기' 클릭 → 보험 연결 화면 진입 | `S11_2_EntryInsuranceConnect` |
| 3 | '40개 연결하기' 클릭 | `S11_3_AfterConnect40Click` |
| 4 | 네이버 인증서 선택 | `S11_4_EntryNaverAuth` |
| 5 | '동의하고 계속하기' 클릭 | `S11_5_AfterAgreeClick` |
| 6 | 마이데이터 연결 완료 대기 | `S11_6_DataConnectComplete` |
| 7 | 결과 확인 화면 확인 클릭 | `S11_7_ResultConfirmComplete` |
| 8 | 추가 약관 동의 처리 | `S11_8_ExtraAgreeComplete` |
| 9 | '보험 진단받기' 클릭 → 진단 화면 진입 | `S11_9_EntryDiagnosisResult` |
| 10 | 전문가 채팅 종료 | `S11_10_ChatClosed` |

### 불안정 요인

- 네이버 인증 화면 요소가 OS/앱 버전마다 다를 수 있음
- 마이데이터 연결 소요 시간이 네트워크 상태에 따라 가변적
- 추가 약관 팝업 노출 여부가 계정 상태에 따라 다름

---

## 로케이터 관리 원칙

### 우선순위

1. XPath `@text` / `@content-desc` — 가장 안정적
2. UiScrollable (`ANDROID_UIAUTOMATOR`) — 화면 밖 요소 스크롤 탐색
3. `tap_coordinate(x_ratio, y_ratio)` — XPath 폴백 (해상도 독립적 비율 사용)
4. `[last()]` XPath 조건 — 중복 텍스트 요소 중 탭바 아이콘 특정

### 탭 전환 대기 패턴

```python
# 탭 클릭 후 반드시 @selected='true' 로 활성화 확인
WebDriverWait(driver, 10).until(
    lambda d: d.find_elements(AppiumBy.XPATH, TAB_XPATH + "[@selected='true']")
)
```

### UI 변경 시 수정 위치

| 변경 사항 | 수정 파일 |
|----------|----------|
| 탭 텍스트 변경 | 해당 `pages/*.py` 의 클래스 상수 |
| 스플래시 요소 변경 | `pages/splash_page.py` — `SPLASH_LOGO`, `SPLASH_ACTIVITY_KEYWORD` |
| 카카오 OAuth 요소 변경 | `pages/login_page.py` — `KAKAO_OAUTH_READY` |
| 테스트 단계 추가 | `tests/test_bodoc_flow.py` 또는 해당 `pages/*.py` |

---

## 실패 처리 흐름

```
시나리오 내 AssertionError 발생
  └── scenario_context.__exit__
        ├── ss("{prefix}_FAIL") — 실패 시점 스크린샷 저장
        ├── reporter.step("...", "FAILED") — 결과 JSON에 기록
        └── pytest.fail(str(e)) — pytest 종료 코드 반영
```

---

## 실행 명령어

```bash
# 전체 시나리오
pytest tests/test_bodoc_flow.py -v

# 단일 시나리오 (함수명 전체 지정)
pytest tests/test_bodoc_flow.py::test_scenario_6_diagnosis_tab

# 여러 시나리오 선택 (-k "1"은 10, 11도 매칭되므로 전체명 사용)
pytest tests/test_bodoc_flow.py -k "test_scenario_4_home_tab or test_scenario_5_home_tab_scroll"

# 대시보드에서 실행 (권장)
python server.py → http://localhost:8888 → 테스트 실행 탭
```
