# 📱 Bodoc 앱 자동화 테스트 프로젝트

이 프로젝트는 **Bodoc(보닥)** 안드로이드 앱의 주요 사용자 시나리오(권한 설정, 로그인, 마이데이터 연동)를 자동으로 검증하기 위한 QA 자동화 시스템입니다.

---

## ✨ 주요 기능
- **자동화 시나리오**: 초기 진입, 권한 수락, 카카오 로그인, 마이데이터 연결 및 설문조사 플로우 자동 실행
- **QA 대시보드 (New)**: `server.py`를 통해 웹 브라우저에서 실시간 로그 확인 및 테스트 제어 가능
- **화면 캡처**: 테스트 단계별 스크린샷 자동 저장으로 오류 분석 용이
- **비율 기반 클릭**: 다양한 해상도의 기기에 대응하는 좌표 클릭 알고리즘 적용

---

## 📂 프로젝트 구조 (POM 패턴)

효율적인 유지보수를 위해 **Page Object Model (POM)** 패턴을 따릅니다.

```text
bodoc-test/
├── server.py            # 📊 QA 대시보드 서버 (웹 인터페이스)
├── pages/               # [Page Objects] 화면별 요소 및 동작 정의
│   ├── base_page.py     # 공통 동작 (Wait, Click, Scroll, Tap)
│   ├── login_page.py    # 로그인 및 웹뷰 처리
│   └── ...              # 기타 화면 정의
├── tests/               # [Test Scenarios] 실제 테스트 시나리오
│   └── test_bodoc_flow.py # 통합 테스트 실행 파일
├── utils/               # [Utilities] 설정 및 상수 관리
├── outputs/             # [Outputs] 결과물 (스크린샷, 리포트)
└── .env                 # 기기 및 경로 설정 환경 변수
```

---

## 🛠️ 기술 스택
- **Language**: Python 3.12+
- **Framework**: Pytest
- **Automation**: Appium (UiAutomator2)
- **Dashboard**: HTTP Server (Vanilla Python)

---

## 🚀 빠른 시작 (Setup & Run)

### 1. 사전 준비
- **Appium 서버**: `npm install -g appium`
- **Python 패키지**: `pip install Appium-Python-Client pytest python-dotenv`
- **ADB 연결**: 안드로이드 기기 또는 에뮬레이터가 PC에 연결되어 있어야 합니다.

### 2. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 본인의 기기 환경에 맞게 수정합니다.
```bash
DEVICE_NAME=R3CR10E2AFZ  # adb devices 명령어로 확인
CHROMEDRIVER_DIR=C:\path\to\chromedriver
```

### 3. 실행 방법 (대시보드 사용 권장)
가장 쉬운 실행 방법은 대시보드 서버를 이용하는 것입니다.

1.  **Appium 실행**: 터미널에서 `appium` 입력
2.  **서버 실행**: `python server.py`
3.  **접속**: 브라우저에서 `http://localhost:8888` 열기
4.  **테스트**: 웹 화면에서 [Run Test] 버튼을 눌러 시나리오 시작

---

## 💡 유지보수 가이드

### UI 변경 대응
앱의 UI가 변경되어 버튼을 찾지 못할 경우, `tests/` 코드를 직접 수정하지 않고 `pages/` 폴더 내의 해당 화면 파일에서 **XPath** 또는 **좌표 비율** 상수만 업데이트하면 됩니다.

### 문제 해결
- **기기 인식 불가**: `adb devices` 명령어로 연결 상태를 확인하세요.
- **포트 충돌**: 8888번 포트가 사용 중이면 `server.py`의 `PORT` 상수를 변경하세요.
- **로그 확인**: `outputs/screenshots` 폴더에서 실패 시점의 화면을 확인할 수 있습니다.

