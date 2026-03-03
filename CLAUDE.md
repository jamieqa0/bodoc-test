# CLAUDE.md — Bodoc QA Automation Project

This file provides context for AI assistants working in this repository.

---

## Project Overview

**Bodoc QA Automation** is an Android mobile test automation project for the Bodoc insurance app. It combines:
- **Pytest + Appium** test scenarios (Page Object Model)
- **Python HTTP dashboard** (`server.py`) for triggering tests and viewing results from a browser
- **HTML report generation** with screenshots and step-level logs

The project targets real Android devices via ADB. Tests run locally; there is no CI/CD pipeline.

---

## Repository Structure

```
bodoc-test/
├── server.py                # QA Dashboard HTTP server (main entry point, port 8888)
├── .env.example             # Environment variable template
├── README.md                # Project docs (Korean)
│
├── pages/                   # Page Object Model (POM) classes
│   ├── base_page.py         # BasePage: shared helpers (wait, click, scroll, swipe)
│   ├── intro_page.py        # Initial permissions / intro screen
│   ├── login_page.py        # Kakao login + webview context switching
│   ├── home_page.py         # Home tab elements & navigation
│   ├── diagnosis_page.py    # Diagnosis tab & insurance premium tab
│   ├── product_page.py      # Product recommendations tab
│   ├── health_page.py       # Health records tab
│   ├── reward_page.py       # Reward/compensation tab
│   ├── menu_page.py         # Full menu navigation
│   ├── mydata_flow.py       # MyData connection flow (complex multi-step)
│   ├── consult_page.py      # Consultation features
│   └── notification_page.py # Notification handling
│
├── tests/
│   ├── conftest.py          # Pytest fixtures: driver, reporter, screenshot, scenario_context
│   └── test_bodoc_flow.py   # 8 active test scenarios + 1 skipped
│
└── utils/
    ├── reporter.py          # TestReporter class + embedded HTML dashboard template
    └── config.py            # Runtime config (gitignored; generated from .env)
```

**Generated at runtime** (gitignored):
```
outputs/
├── screenshots/{run_id}/    # PNG files per test run
├── results/result_*.json    # JSON test results (timestamped)
└── reports/report.html      # Combined HTML report
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12+ |
| Test Framework | Pytest |
| Mobile Automation | Appium (UiAutomator2 driver) |
| WebView Handling | Selenium WebDriver |
| Dashboard Server | Python `http.server.ThreadingHTTPServer` |
| Dashboard Frontend | Vanilla JS + HTML5 + CSS3 (embedded in `reporter.py`) |
| Config | `python-dotenv` (.env) |
| Device Communication | ADB (Android Debug Bridge) |

---

## Setup & Configuration

### Environment Variables

Copy `.env.example` to `.env` (gitignored) and fill in device-specific values:

```env
APPIUM_SERVER_URL=http://localhost:4723
DEVICE_NAME=<your_adb_device_serial>
CHROMEDRIVER_DIR=<path_to_platform-tools>
```

`utils/config.py` is generated from `.env` at runtime and is also gitignored. Do not commit either file.

### Installation

```bash
pip install Appium-Python-Client pytest python-dotenv
npm install -g appium
appium driver install uiautomator2
```

### ADB Path Discovery (Windows-specific)

`server.py` searches for `adb.exe` in multiple locations:
- `%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe`
- `%USERPROFILE%\scoop\apps\adb\current\adb.exe`
- `C:\platform-tools\adb.exe`

---

## Running Tests

### Via Dashboard (recommended)

```bash
# Terminal 1
appium

# Terminal 2
python server.py

# Browser
open http://localhost:8888
```

The dashboard lets you start/stop Appium, check device status, select scenarios, and view live logs + results.

### Via pytest directly

```bash
# All scenarios
pytest tests/test_bodoc_flow.py -v

# Single scenario
pytest tests/test_bodoc_flow.py::test_scenario_1_app_launch

# Multiple scenarios by keyword
pytest tests/test_bodoc_flow.py -k "scenario_2 or scenario_3"
```

---

## Test Scenarios

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_scenario_1_app_launch` | App launch & initial screen |
| 2 | `test_scenario_2_kakao_login` | Kakao login via webview |
| 3 | `test_scenario_3_home_tab` | Home tab element verification |
| 4 | `test_scenario_4_diagnosis_tab` | Diagnosis tab + Premium tab |
| 5 | `test_scenario_5_product_tab` | Product recommendations |
| 6 | `test_scenario_6_health_tab` | Health records |
| 7 | `test_scenario_7_reward_tab` | Reward/compensation info |
| 8 | `test_scenario_8_menu_validation` | Full menu sections (5 items) |
| — | `test_scenario_10_mydata` | MyData connection *(skipped — under development)* |

---

## Architecture & Key Patterns

### Page Object Model (POM)

All UI interaction lives in `pages/`. Tests only call page methods; locators never appear in test files.

- Page classes inherit `BasePage` (`pages/base_page.py`)
- `BasePage` provides: `wait_for_element()`, `click()` (with stale-element retry), `scroll_down()`, `scroll_up()`, `scroll_to_text()`, `tap_coordinate()`, `wait_for_home()`

### Fixture Flow in `conftest.py`

```
run_id (session-scoped timestamp)
  └── driver_setup (session-scoped Appium driver init/cleanup)
        ├── ss (function-scoped screenshot helper)
        ├── reporter (session-scoped TestReporter + atexit save)
        └── ensure_awake (autouse — pre/post test device setup)
```

`scenario_context(reporter, scenario_name)` is a context manager used in every test to:
1. Call `reporter.start_scenario()`
2. Catch exceptions → capture screenshot → mark FAILED → call `pytest.fail()`
3. Call `reporter.end_scenario()` on success

### Locator Strategy (priority order)

1. **XPath text/content-desc** — `LOCATOR = "//*[@text='...']"` (UPPER_SNAKE_CASE constants on page classes)
2. **UiAutomator scroll** — for off-screen elements
3. **Ratio-based coordinates** — `tap_coordinate(x_ratio, y_ratio)` for screen-size-agnostic taps
4. **`[last()]` XPath predicate** — to target tab bar icons when duplicate text exists

### Webview Context Switching

`LoginPage` switches between `NATIVE_APP` and `WEBVIEW_*` Appium contexts for the Kakao OAuth flow.

### Screenshot Naming

```
outputs/screenshots/{run_id}/{MMDD-HHMM}_{ScenarioTag}_{StepName}.png
```

Example: `0226-1647_S1_Launch_AppName.png`

### Log Prefixes

| Prefix | Meaning |
|--------|---------|
| `[OK]` | Step passed |
| `[WARN]` | Non-fatal issue |
| `[FAIL]` | Step or scenario failed |
| `[INFO]` | General information |
| `[DEBUG]` | Verbose diagnostic |

---

## HTTP API (server.py — port 8888)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Dashboard HTML (embeds latest JSON results) |
| `GET` | `/api/appium/start` | Start Appium subprocess |
| `GET` | `/api/appium/stop` | Stop Appium subprocess |
| `GET` | `/api/appium/status` | Appium running state + version |
| `GET` | `/api/device/status` | ADB device list with model & Android version |
| `GET` | `/api/env` | Python/pytest environment info |
| `GET` | `/api/run?s=all\|1,2,3` | Trigger test run for selected scenarios |
| `GET` | `/api/stop` | Abort running test process |
| `GET` | `/api/test/status` | Current execution state |
| `GET` | `/api/logs?offset=0` | Stream logs with offset pagination |
| `GET` | `/api/logs/clear` | Clear log buffer |
| `GET` | `/api/results` | Retrieve saved JSON results |
| `GET` | `/api/test/definition` | Test scenario metadata |
| `GET` | `/screenshots/{run_id}/{file}` | Serve PNG screenshot |

All responses are JSON. CORS headers are enabled (`Access-Control-Allow-Origin: *`).

---

## Coding Conventions

- **Python style**: PEP 8; `snake_case` for methods and variables
- **Locator constants**: `UPPER_SNAKE_CASE` class attributes on each page class
- **No test logic in page classes** — page classes only expose actions and element waits
- **No locators in test files** — all selectors belong in `pages/`
- **Error handling**: Raise `ElementInteractionError` (custom) for element-level failures; let `scenario_context` handle scenario-level failures
- **Output directories**: Always write to `outputs/` subdirectories; never commit generated output files
- **Config**: Never hardcode device names, app packages, or URLs — use `.env` / `utils/config.py`

---

## Adding New Tests or Pages

### New Page Class

1. Create `pages/my_feature_page.py` inheriting `BasePage`
2. Define locator constants as class attributes (`UPPER_SNAKE_CASE`)
3. Implement action methods using `self.wait_for_element()`, `self.click()`, etc.
4. Import and instantiate in `conftest.py` or directly in the test

### New Test Scenario

1. Add a test function `test_scenario_N_name(driver_setup, ss, reporter)` in `tests/test_bodoc_flow.py`
2. Wrap body in `with scenario_context(reporter, "Scenario N - Description"):`
3. Register the scenario in the `TEST_DEFINITIONS` dict in `server.py` so the dashboard shows it

---

## What to Avoid

- Do not modify `utils/config.py` directly — it is regenerated from `.env`
- Do not commit `outputs/`, `.env`, or `utils/config.py`
- Do not add hardcoded device serials, app packages, or credentials to any tracked file
- Do not use `time.sleep()` for waiting — use `WebDriverWait` / `wait_for_element()` instead
- Do not bypass the POM — add new locators and actions to the appropriate page class

---

## Known Limitations

- Windows-only ADB path discovery logic in `server.py` (paths are Windows-style); Linux/Mac users must set `CHROMEDRIVER_DIR` or ensure `adb` is on `PATH`
- `test_scenario_10_mydata` is skipped pending UI stabilization
- No CI/CD — all tests are run manually against a connected Android device
