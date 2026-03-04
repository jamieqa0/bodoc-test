# Bodoc QA Dashboard — 웹 PRD (Product Requirements Document)

> 작성일: 2026-03-04
> 대상: http://localhost:8888 (server.py 기동 후 접속)
> 버전: V1.3.3

---

## 1. 제품 개요

Bodoc QA 대시보드는 Bodoc Android 앱 자동화 테스트를 **코드 없이 웹 브라우저에서** 실행·모니터링·결과 확인할 수 있는 단일 페이지 관리 UI다.

- **서버**: Vanilla Python `ThreadingHTTPServer` (포트 8888)
- **클라이언트**: 단일 HTML 파일 (SPA, 외부 의존성 없음)
- **통신**: REST API (JSON, CORS 허용)

---

## 2. 레이아웃 구조

```
┌────────────────────────────────────────────────────┐
│  Sidebar (240px)  │  Main Content                  │
│  ─────────────    │  ─────────────                 │
│  🏠 대시보드       │  [Page Header: 제목 + 배지]     │
│  🚀 테스트 실행    │                                 │
│  📊 테스트 결과    │  [Tab Pane: 활성 탭 콘텐츠]     │
│  ⚙️ 설정          │                                 │
└────────────────────────────────────────────────────┘
```

탭 전환 시 URL 변경 없이 SPA 방식으로 콘텐츠 영역만 교체된다.

---

## 3. 탭별 세부 기능

---

### 3-1. 🏠 대시보드 탭

홈 진입 시 가장 먼저 보이는 화면. 전체 현황을 한눈에 파악한다.

#### 3-1-1. 요약 통계 카드 (4개)

| 카드 | 표시 내용 | 데이터 출처 |
|------|----------|------------|
| 전체 실행 횟수 | 저장된 result_*.json 파일 수 | `/api/results` |
| 최근 성공률 | 가장 최근 결과의 PASS/FAIL 비율 | `/api/results` |
| 등록 시나리오 수 | test 파일에서 AST 파싱된 함수 수 | `/api/test/definition` |
| 시스템 상태 요약 | Appium 상태 + 기기 연결 수 + 테스트 상태 | `/api/appium/status`, `/api/device/status` |

#### 3-1-2. 최근 실행 이력 테이블

- 저장된 결과를 역순(최신순)으로 나열
- 컬럼: 날짜/시간 | 실행 ID | PASS/FAIL 배지 | Pass 수 / Fail 수 | 상세 버튼
- 상세 버튼 클릭 → 테스트 결과 탭으로 이동 후 해당 결과 자동 선택
- 이력 없을 경우: "실행 이력이 없습니다" 안내 텍스트 표시

#### 3-1-3. 빠른 도움말 카드

- 3줄 요약: 실행 → 결과 확인 → 스크린샷 확대 방법 안내
- 처음 사용자를 위한 온보딩 가이드

---

### 3-2. 🚀 테스트 실행 탭

테스트 시나리오를 선택·실행하고 실시간 로그를 확인하는 핵심 화면.

#### 3-2-1. 시나리오 카드 그리드

- `GET /api/test/definition` 으로 테스트 파일을 AST 파싱해 시나리오 목록 동적 로드
- 새 테스트 함수 추가 시 별도 등록 없이 자동 반영
- 각 카드에 표시되는 정보:

| 항목 | 설명 |
|------|------|
| 시나리오 번호 | ID (예: 1, 3_1) |
| 시나리오 명 | 함수 docstring 첫 줄 |
| 상태 배지 | PASS / FAIL / RUNNING / 대기 |
| 경과 시간 | 실행 중 매 초 갱신 (완료 후 최종 소요시간 표시) |
| Skip 버튼 | 해당 시나리오를 전체 실행에서 제외 (노란색으로 토글) |
| Run 버튼 | 해당 시나리오만 단독 실행 |

- 카드 상태 색상:
  - PASS → 초록 테두리
  - FAIL → 빨간 테두리
  - RUNNING → 브랜드 컬러 + pulse 애니메이션
  - 대기 → 기본 (회색)

#### 3-2-2. 전체 실행 / 중지 버튼

| 버튼 | 동작 | API |
|------|------|-----|
| 전체 실행 | 스킵되지 않은 모든 시나리오를 순서대로 실행 | `GET /api/run?s=all` |
| 중지 | 실행 중인 pytest 프로세스 강제 종료 (confirm 다이얼로그) | `GET /api/stop` |

- 실행 중 → 전체 실행 버튼 비활성화, 중지 버튼 활성화
- 스킵된 시나리오가 모두인 경우 "실행할 시나리오가 없습니다" alert

#### 3-2-3. 진행률 표시

- 실행 중 상태 배지 영역에: `시나리오 실행 중 (현재/전체)` 표시
- `GET /api/test/status` 폴링으로 `current_idx` / `total_count` 업데이트

#### 3-2-4. 실시간 실행 로그 패널

- `GET /api/logs?offset=N` 폴링 방식 (오프셋 증분으로 새 로그만 추가)
- 로그 태깅:
  - `PASSED` 포함 → `[INFO]` (초록)
  - `FAILED` 포함 → `[ERROR]` (빨간)
  - `SKIPPED` / `collected` → `[DEBUG]` (회색)
- 자동 스크롤 체크박스 (기본 ON): 새 로그 입력 시 하단 유지
- 비우기 버튼: 로그 패널 내용 클리어 (서버 측 로그 버퍼는 유지)

---

### 3-3. 📊 테스트 결과 탭

과거 및 현재 테스트의 상세 결과를 조회하는 화면.

#### 3-3-1. 결과 목록 (좌측 패널)

- 결과 필터 버튼: **전체 / 성공 / 실패**
- 각 항목 표시: 실행 날짜·시간, PASS/FAIL 배지
- 선택 시 우측 상세 패널에 해당 결과 표시

#### 3-3-2. 결과 상세 (우측 패널)

- 패널 크기 드래그로 좌우 분할 조정 가능 (`initSplitResize`)
- 실행 리포트 헤더:
  - 실행 ID (타임스탬프 기반 `run_id`)
  - 실행 일시
  - 총 소요시간 (초 → 분:초 포맷)
  - 연결 기기 모델명 + Android 버전
  - 전체 시나리오 수 / PASS 수 / FAIL 수

- **시나리오 카드 (Accordion)**:
  - 시나리오명 클릭으로 접기/펼치기
  - "전체 접기" 버튼으로 일괄 처리
  - 각 카드 내부:
    - 단계별 스텝 목록 (단계명, PASSED/FAILED 배지)
    - 스텝별 스크린샷 썸네일 (클릭 → 라이트박스 원본 확대)
    - FAILED 스텝은 빨간 테두리로 강조

- 데이터 출처: `outputs/results/result_*.json` 파일 (JSON 포맷)

---

### 3-4. ⚙️ 설정 탭

환경 상태 확인 및 관리 기능.

#### 3-4-1. Appium 서버 제어 카드

| 항목 | 설명 |
|------|------|
| 상태 표시 | 초록 dot(작동 중) / 빨간 dot(중지됨) + 버전 표시 |
| 실행 버튼 | `GET /api/appium/start` → 포트 4723 Appium 서브프로세스 시작 |
| 중지 버튼 | `GET /api/appium/stop` → 프로세스 종료 (외부 실행 시 netstat로 PID 탐색) |
| 중복 실행 방지 | 이미 실행 중이면 "already_running" 응답, 재시작 안 함 |

#### 3-4-2. 기기 연결 상태 카드

| 항목 | 설명 |
|------|------|
| 상태 dot | 초록(1대 이상 연결) / 빨간(없음) |
| 기기 목록 | serial \| 모델명 \| Android 버전 형식 |
| 갱신 버튼 | `GET /api/device/status` 재호출 |
| adb 버전 | adb version 첫 줄 표시 |

#### 3-4-3. 실행 환경 정보 카드

- Python 버전
- pytest 버전

#### 3-4-4. 이전 결과 삭제 카드

- 기준 날짜(YYYY-MM-DD) 입력 → 해당 날짜 이전(포함) `result_*.json` 파일 일괄 삭제
- API: `GET /api/results/delete?date=YYYY-MM-DD`
- 삭제된 파일 목록과 개수 응답

#### 3-4-5. 시스템 통합 로그 패널

- 실행 탭과 동일한 로그 버퍼를 공유 (동일 `_logs` 배열)
- Appium 시작/종료, 테스트 프로세스 메시지 모두 표시
- 비우기 버튼: `GET /api/logs/clear` → 서버 측 로그 버퍼까지 초기화

---

## 4. 공통 UI 동작

### 4-1. 실시간 폴링

- `updateStatus()` 주기적 호출 → Appium 상태, 기기 상태, 테스트 실행 상태 갱신
- `pollLogs()` 주기적 호출 → 오프셋 방식으로 새 로그만 수신
- 기기·Appium 응답 타임아웃 시: "서버에 응답 없음" 경고 메시지 표시

### 4-2. 시나리오 카드 실시간 상태 동기화

1. 실행 시작 → 전체 카드 초기화
2. 로그 스트림 파싱 → `test_scenario_` 패턴 감지 → 해당 카드 RUNNING 상태로 전환
3. 실행 완료 → `/api/results` 재조회 → 카드 PASS/FAIL 동기화
4. 실행 중 매 초 경과 시간 갱신 (`tickElapsed`)

### 4-3. 스크린샷 라이트박스

- 결과 상세 패널의 스크린샷 썸네일 클릭 시 오버레이 확대
- `GET /screenshots/{run_id}/{filename}.png` 로 이미지 서빙
- 클릭으로 닫기

### 4-4. ANSI 로그 정제

- pytest 출력에 포함된 ANSI 이스케이프 코드 자동 제거
- 숫자·콤마만으로 구성된 노이즈 라인 필터링
- 최대 로그 버퍼 크기: 1,000줄 (초과 시 오래된 것부터 제거)

---

## 5. API 명세

| 메서드 | 경로 | 파라미터 | 응답 | 설명 |
|--------|------|----------|------|------|
| GET | `/` | - | HTML | 대시보드 SPA |
| GET | `/api/appium/start` | - | `{status}` | Appium 시작 |
| GET | `/api/appium/stop` | - | `{status}` | Appium 중지 |
| GET | `/api/appium/status` | - | `{running, version}` | Appium 상태 |
| GET | `/api/device/status` | - | `{devices, count, adb_version}` | ADB 기기 목록 |
| GET | `/api/env` | - | `{python, pytest}` | 환경 버전 정보 |
| GET | `/api/run` | `s=all\|1,2,3` | `{status}` | 테스트 실행 |
| GET | `/api/stop` | - | `{status}` | 테스트 강제 종료 |
| GET | `/api/test/status` | - | `{running, current_scenario, total_count, current_idx}` | 실행 진행 상태 |
| GET | `/api/logs` | `offset=N` | `{logs[], total}` | 로그 스트리밍 |
| GET | `/api/logs/clear` | - | `{ok}` | 로그 버퍼 초기화 |
| GET | `/api/results` | - | `[result, ...]` | 저장된 결과 목록 |
| GET | `/api/results/delete` | `date=YYYY-MM-DD` | `{ok, deleted[], count}` | 날짜 기준 결과 삭제 |
| GET | `/api/test/definition` | - | `{scenarios[]}` | 시나리오 목록 (AST) |
| GET | `/screenshots/{run_id}/{file}` | - | PNG | 스크린샷 이미지 |

- 모든 응답: `Content-Type: application/json`, `Cache-Control: no-store`
- CORS: `Access-Control-Allow-Origin: *` (전체 허용)

---

## 6. 로드맵 (향후 개선 과제)

### 단기

- [ ] **WebSocket 실시간 로그**: 폴링 방식 → WebSocket으로 전환해 레이턴시 및 서버 부하 감소
- [ ] **실행 중 진행 바**: 시나리오 단위 진행률 시각화 (현재는 텍스트만)
- [ ] **다크 모드**: 사이드바는 다크, 본문은 라이트 — 전체 다크 모드 옵션 추가
- [ ] **스킵 설정 영속화**: 현재 메모리에만 유지 → `localStorage`에 저장

### 중기

- [ ] **결과 비교**: 두 실행 결과를 나란히 비교하는 diff 뷰
- [ ] **시나리오별 실패율 통계**: 히스토리 기반 시나리오 안정성 차트
- [ ] **슬랙/이메일 알림**: 테스트 완료 시 결과 요약 발송
- [ ] **모바일 반응형**: 태블릿에서도 사용 가능하도록 레이아웃 조정

### 장기

- [ ] **CI 연동 뷰**: GitHub Actions 실행 결과와 대시보드 결과 통합
- [ ] **멀티 기기 동시 실행**: 여러 기기를 병렬로 실행하고 기기별 결과 분리

---

## 7. 알려진 제약사항

| 항목 | 내용 |
|------|------|
| 플랫폼 | Windows 전용 (adb.exe 탐색, appium.cmd 경로) |
| 동시 접속 | ThreadingHTTPServer 사용으로 다중 접속 가능하나 테스트 실행은 단일 프로세스 |
| 인증 | 인증 없음 — 로컬 네트워크 내부 전용 |
| 로그 보관 | 메모리 내 최대 1,000줄, 서버 재시작 시 초기화 |
| 결과 파일 | `outputs/results/` 에 JSON으로 영속 저장 (서버 재시작 후에도 유지) |
| 스킵 설정 | 브라우저 새로고침 시 초기화 (메모리 유지) |
