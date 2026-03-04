# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Bodoc QA Automation** is an Android mobile test automation project for the Bodoc insurance app. It combines:
- **Pytest + Appium** test scenarios (Page Object Model)
- **Python HTTP dashboard** (`server.py`) for triggering tests and viewing results from a browser
- **HTML report generation** with screenshots and step-level logs

The project targets real Android devices via ADB. Tests run locally; there is no CI/CD pipeline.

---

## Setup & Configuration

### Environment Variables

Copy `.env.example` to `.env` (gitignored) and fill in device-specific values:

```env
APPIUM_SERVER_URL=http://localhost:4723
DEVICE_NAME=<your_adb_device_serial>
CHROMEDRIVER_DIR=<path_to_platform-tools>
```

`utils/config.py` is generated from `.env` at runtime and is also gitignored. Do not modify or commit either file.

### Installation

```bash
pip install Appium-Python-Client pytest python-dotenv
npm install -g appium
appium driver install uiautomator2
```

---

## Running Tests

### Via Dashboard (recommended)

```bash
# Terminal 1
appium

# Terminal 2
python server.py
# Browser: http://localhost:8888
```

### Via pytest directly

```bash
# All scenarios
pytest tests/test_bodoc_flow.py -v

# Single scenario (use full function name to avoid partial match)
pytest tests/test_bodoc_flow.py::test_scenario_1_app_launch

# Multiple scenarios by keyword (use full names: -k "scenario_1" matches scenario_10, scenario_11 too)
pytest tests/test_bodoc_flow.py -k "test_scenario_4_home_tab or test_scenario_5_home_tab_scroll"
```

---

## Test Scenarios (current)

| # | Test Function | Description |
|---|--------------|-------------|
| 1 | `test_scenario_1_app_launch` | Splash screen + appvaccine toast simultaneous detection (`@observe_launch`) |
| 2 | `test_scenario_2_initial_permissions` | Initial permission popup handling (`@reset_permissions`) |
| 3 | `test_scenario_3_kakao_login` | Kakao OAuth login via Chrome Custom Tab (NATIVE context only) |
| 4 | `test_scenario_4_home_tab` | Home tab element verification |
| 5 | `test_scenario_5_home_tab_scroll` | Home tab scroll step-by-step verification |
| 6 | `test_scenario_6_diagnosis_tab` | Diagnosis tab + insurance premium tab |
| 7 | `test_scenario_7_product_tab` | Product recommendations tab |
| 8 | `test_scenario_8_health_tab` | Health records tab |
| 9 | `test_scenario_9_reward_tab` | Reward/compensation tab |
| 10 | `test_scenario_10_menu_validation` | Full menu sections (5 categories) |
| 11 | `test_scenario_11_mydata` | MyData connection flow (may be unstable) |

Scenario IDs are dynamically extracted from the test file via AST parsing in `server.py:_extract_scenarios()` — there is no static `TEST_DEFINITIONS` dict. New test functions are picked up automatically.

---

## Architecture & Key Patterns

### Page Object Model (POM)

All UI interaction lives in `pages/`. Tests only call page methods; locators never appear in test files.

- All page classes inherit `BasePage` (`pages/base_page.py`)
- `BasePage` provides: `wait_for_element()`, `click()` (stale-element retry), `scroll_down()`, `scroll_up()`, `scroll_to_text()`, `tap_coordinate()`, `wait_for_home()`, `dismiss_any_permission_popup()`
- Page classes are instantiated with `(driver, ss)` — both driver and the screenshot function are passed
- `splash_page.py` handles simultaneous splash + appvaccine toast detection (not listed in older docs but present in `pages/`)

### Fixture Flow (`tests/conftest.py`)

```
run_id (session-scoped timestamp)
  └── reporter (session-scoped TestReporter + atexit save)
        └── driver_setup (session-scoped Appium driver init/cleanup)
              ├── ss (function-scoped screenshot helper → outputs/screenshots/{run_id}/)
              ├── inject_device_info (session autouse — pushes device model/OS to reporter)
              └── app_reset (function autouse — runs before/after every test)
```

**`app_reset`** (autouse) runs before every test:
1. Return to `NATIVE_APP` context if in a WebView
2. `terminate_app` to fully kill the app
3. If `@pytest.mark.reset_permissions`: run `adb shell pm clear <pkg>` to reset app data
4. Unlock screen (`mobile: unlock` + `adb shell wm dismiss-keyguard`)
5. `activate_app` to relaunch
6. Wait for initial screen (`_INITIAL_SCREEN_XPATH`) — skipped if `@pytest.mark.observe_launch`

After each test, `app_reset` captures a final screenshot automatically.

### `scenario_context` Usage

Every test wraps its body in:

```python
with scenario_context(reporter, "시나리오N_설명", ss, "SN"):
    ...
```

Signature: `scenario_context(reporter, name, ss, fail_prefix)`.
On exception: takes a screenshot named `{fail_prefix}_FAIL`, marks FAILED, calls `pytest.fail()`.

### Pytest Markers

| Marker | Effect |
|--------|--------|
| `@pytest.mark.observe_launch` | Skips initial screen wait in `app_reset`; test observes the launch sequence directly |
| `@pytest.mark.reset_permissions` | Runs `adb shell pm clear` before launch to force permission popups to reappear |

### Kakao OAuth — NATIVE Context Only

Kakao SDK 2.x+ uses **Chrome Custom Tab**, not a WebView. Never call `driver.contexts` for the login flow — it triggers a Chromedriver session error. `LoginPage` interacts with the Kakao OAuth screen entirely in the `NATIVE_APP` UiAutomator2 context using text-based XPath selectors. Coordinate fallbacks are used when text elements aren't found.

### Locator Strategy (priority order)

1. **XPath text/content-desc** — `LOCATOR = "//*[@text='...']"` (`UPPER_SNAKE_CASE` class constants)
2. **UiAutomator scroll** — for off-screen elements
3. **`tap_coordinate(x_ratio, y_ratio)`** — screen-size-agnostic ratio-based taps
4. **`[last()]` XPath predicate** — targets tab bar icons when duplicate text exists

### Screenshot Naming

```
outputs/screenshots/{run_id}/{MMDD-HHMM}_{ScenarioTag}_{StepName}.png
```

Example: `0226-1647_S3_Kakao_OAuth_Page_Loaded.png`

### Log Prefixes

| Prefix | Meaning |
|--------|---------|
| `[OK]` | Step passed |
| `[WARN]` | Non-fatal issue |
| `[FAIL]` | Step or scenario failed |
| `[INFO]` | General information |
| `[DEBUG]` | Verbose diagnostic |

---

## HTTP API (`server.py` — port 8888)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Dashboard HTML |
| `GET` | `/api/appium/start` | Start Appium subprocess |
| `GET` | `/api/appium/stop` | Stop Appium subprocess |
| `GET` | `/api/appium/status` | Appium running state + version |
| `GET` | `/api/device/status` | ADB device list with model & Android version |
| `GET` | `/api/env` | Python/pytest environment info |
| `GET` | `/api/run?s=all\|1,2,3` | Trigger test run for selected scenarios |
| `GET` | `/api/stop` | Abort running test process |
| `GET` | `/api/test/status` | Current execution state + progress index |
| `GET` | `/api/logs?offset=0` | Stream logs with offset pagination |
| `GET` | `/api/logs/clear` | Clear log buffer |
| `GET` | `/api/results` | Retrieve saved JSON results |
| `GET` | `/api/results/delete?date=YYYY-MM-DD` | Delete result files on or before date |
| `GET` | `/api/test/definition` | Scenario list (AST-extracted from test file) |
| `GET` | `/screenshots/{run_id}/{file}` | Serve PNG screenshot |

All responses are JSON. CORS is enabled (`Access-Control-Allow-Origin: *`).

---

## Coding Conventions

- **Python style**: PEP 8; `snake_case` for methods and variables
- **Locator constants**: `UPPER_SNAKE_CASE` class attributes on each page class
- **No test logic in page classes** — page classes only expose actions and element waits
- **No locators in test files** — all selectors belong in `pages/`
- **Error handling**: Raise `AssertionError` for element/step failures; `scenario_context` catches and calls `pytest.fail()`
- **Config**: Never hardcode device names, app packages, or URLs — use `.env` / `utils/config.py`
- **Waiting**: Use `WebDriverWait` / `wait_for_element()`, never `time.sleep()`

---

## Adding New Tests or Pages

### New Page Class

1. Create `pages/my_feature_page.py` inheriting `BasePage`
2. Define locator constants as class attributes (`UPPER_SNAKE_CASE`)
3. Implement action methods using `self.wait_for_element()`, `self.click()`, etc.
4. Instantiate with `MyPage(driver, ss)` in the test function

### New Test Scenario

1. Add `test_scenario_N_name(driver, ss, reporter)` to `tests/test_bodoc_flow.py`
2. Wrap body in `with scenario_context(reporter, "시나리오N_설명", ss, "SN"):`
3. The dashboard picks up the new scenario automatically via AST parsing — no registration needed

---

## What to Avoid

- Do not call `driver.contexts` in the Kakao login flow — Chrome Custom Tab causes a Chromedriver session error
- Do not use `-k scenario_N` in pytest for single-digit N (e.g., `-k scenario_1` also matches scenario_10, scenario_11); use the full function name instead
- Do not commit `outputs/`, `.env`, or `utils/config.py`
- Do not modify `utils/config.py` directly — it is regenerated from `.env`

---

## Known Limitations

- Windows-only ADB path discovery in `server.py` (hardcoded Windows paths); Linux/Mac users must have `adb` on `PATH`
- Samsung devices require `adb shell wm dismiss-keyguard` in addition to `mobile: unlock` for lock screen dismissal
- Locators in `splash_page.py` (`SPLASH_LOGO`, `SPLASH_ACTIVITY_KEYWORD`) and `login_page.py` (`KAKAO_OAUTH_READY`, etc.) may need calibration for each physical device
- `test_scenario_11_mydata` is implemented but may be unstable pending UI stabilization
- No CI/CD — all tests are run manually against a connected Android device
