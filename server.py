#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bodoc QA Dashboard Server
실행: python server.py
접속: http://localhost:8888
"""
import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# Windows cp949 터미널에서 유니코드 출력 허용
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from utils.config import REPORT_DIR, RESULTS_DIR, SCREENSHOT_DIR

PORT        = 8888
REPORT_HTML = os.path.join(REPORT_DIR, 'report.html')

# ── 공유 상태 ──────────────────────────────────────
_appium_proc = None
_test_proc   = None
_current_scenario = None
_logs        = []
_lock        = threading.Lock()
_running_idx = 0

# 윈도우 인코딩 감지 (한글 깨짐 방지)
import locale
SYS_ENC = locale.getpreferredencoding()
if SYS_ENC.lower() == 'cp949' or SYS_ENC.lower() == 'ansi_x3.4-1968':
    # 윈도우 한글 환경이면 CP949 우선 사용
    SYS_ENC = 'cp949'
else:
    SYS_ENC = 'utf-8'


def add_log(msg):
    import re
    # 1. 포괄적인 ANSI/ESC 코드 제거 (더 강력한 패턴)
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    msg = ansi_escape.sub('', msg)
    
    # 2. 불필요한 노이즈 로그 필터링 (숫자 나열, 수많은 점 등)
    # 단 단일 숫자만 있거나 숫자+콤마 위주인 라인은 디스크립션 수집 노이즈일 확률이 높음
    if re.match(r'^[0-9,\. ]+$', msg.strip()) and len(msg.strip()) > 1:
        return

    with _lock:
        _logs.append(msg)
        if len(_logs) > 1000:
            _logs.pop(0)
    try:
        print(msg)
    except:
        try: print(msg.encode('utf-8', errors='replace').decode('utf-8'))
        except: pass


# ── adb 경로 탐색 ──────────────────────────────────
def _find_adb():
    import shutil
    # 1. PATH에서 먼저 찾기
    found = shutil.which('adb')
    if found: return found
    
    # 2. 알려진 경로들 및 .env 설정 경로 확인
    path_hints = [
        os.environ.get('ANDROID_HOME', ''), 
        os.environ.get('ANDROID_SDK_ROOT', ''),
        os.environ.get('CHROMEDRIVER_DIR', '') # 사용자가 .env에 지정한 경로 우선 확인
    ]
    for home in path_hints:
        if home:
            p = os.path.join(home, 'adb.exe')
            if os.path.exists(p): return p
            p2 = os.path.join(home, 'platform-tools', 'adb.exe')
            if os.path.exists(p2): return p2
            
    candidates = [
        os.path.expandvars(r'%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe'),
        os.path.expandvars(r'%USERPROFILE%\scoop\apps\adb\current\adb.exe'),
        r'C:\platform-tools\adb.exe',
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return 'adb'


# ── Appium 버전 (실행 중인 서버에서 조회) ────────────
def _get_appium_version():
    try:
        with urllib.request.urlopen('http://localhost:4723/status', timeout=2) as r:
            data = json.loads(r.read())
            return data.get('value', {}).get('build', {}).get('version', '')
    except Exception:
        return ''


# ── Appium 실행 여부 ────────────────────────────────
def _appium_running():
    if _appium_proc is not None and _appium_proc.poll() is None:
        return True
    try:
        with socket.create_connection(('127.0.0.1', 4723), timeout=1):
            return True
    except OSError:
        return False


def _test_running():
    return _test_proc is not None and _test_proc.poll() is None


# ── HTTP 핸들러 ────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # 콘솔 노이즈 억제

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        raw_path = urlparse(self.path).path
        p = unquote(raw_path).rstrip('/') or '/'
        qs = parse_qs(urlparse(self.path).query)
        

        if p == '/':
            self._serve_html()
        elif p.startswith('/screenshots/'):
            # p는 '/screenshots/run_id/file.png' 형태
            # relative_path = 'screenshots/run_id/file.png'
            relative_path = p.lstrip('/')
            full_path = os.path.normpath(os.path.join(ROOT, 'outputs', relative_path))
            self._serve_file(full_path, 'image/png')
        elif p == '/api/appium/start':
            self._appium_start()
        elif p == '/api/appium/stop':
            self._appium_stop()
        elif p == '/api/appium/status':
            running = _appium_running()
            version = _get_appium_version() if running else ''
            self._json({'running': running, 'version': version})
        elif p == '/api/device/status':
            self._device_status()
        elif p == '/api/env':
            self._env_info()
        elif p == '/api/run':
            s = qs.get('s', ['all'])[0]
            # #5: 'all' 또는 쉼표로 구분된 숫자만 허용
            import re
            if s != 'all' and not re.fullmatch(r'[\w,]+', s):
                self._json({'error': 'invalid scenario parameter'}, 400)
            else:
                self._run(s)
        elif p == '/api/stop':
            self._stop_tests()
        elif p == '/api/test/status':
            total_sc_count = 0
            if _current_scenario == 'all':
                sc, _ = _extract_scenarios()
                total_sc_count = len(sc)
            elif _current_scenario:
                total_sc_count = len(_current_scenario.split(','))
            self._json({
                'running': _test_running(), 
                'current_scenario': _current_scenario, 
                'total_count': total_sc_count,
                'current_idx': _running_idx
            })
        elif p == '/api/logs':
            offset = int(qs.get('offset', [0])[0])
            with _lock:
                self._json({'logs': _logs[offset:], 'total': len(_logs)})
        elif p == '/api/logs/clear':
            with _lock:
                _logs.clear()
            self._json({'ok': True})
        elif p == '/api/results':
            self._results()
        elif p == '/api/test/definition':
            self._test_definition()
        else:
            self.send_response(404)
            self.end_headers()

    # ── 유틸 ──────────────────────────────────────
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')


    def _json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=True).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path, mime):
        try:
            data = open(path, 'rb').read()
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def _serve_html(self):
        from utils.reporter import _HTML
        # 동적 리포트 생성 중
        try:
            all_results = []
            if os.path.exists(RESULTS_DIR):
                for p in sorted(Path(RESULTS_DIR).glob("result_*.json"), reverse=True):
                    try:
                        all_results.append(json.loads(p.read_text(encoding='utf-8')))
                    except: continue
            
            reports_json = json.dumps(all_results, ensure_ascii=True) # ensure_ascii=True for safer transport
            html_content = _HTML.replace('__REPORTS_JSON__', reports_json)
            
            if '__REPORTS_JSON__' in html_content:
                print(f"[WARN] Placeholder __REPORTS_JSON__ was NOT replaced in {self.path}")
            
            body = html_content.encode('utf-8')
            # [HTTP] 응답 준비 완료
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            print(f"[ERR] 리포트 생성 실패: {e}")
            msg = f"<h2>Internal Server Error: {e}</h2>".encode()
            self.send_response(500)
            self.end_headers()
            self.wfile.write(msg)

    # ── 디바이스 상태 ──────────────────────────────
    def _device_status(self):
        adb = _find_adb()
        try:
            out = subprocess.check_output(
                [adb, 'devices'], encoding='utf-8', errors='replace', timeout=5
            )
            lines = [l.strip() for l in out.splitlines()
                     if l.strip() and 'List of' not in l]
            devices = []
            for line in lines:
                if '\t' not in line:
                    continue
                serial, state = line.split('\t', 1)
                serial, state = serial.strip(), state.strip()
                if state == 'device':
                    try:
                        model = subprocess.check_output(
                            [adb, '-s', serial, 'shell', 'getprop', 'ro.product.model'],
                            encoding='utf-8', errors='replace', timeout=5
                        ).strip()
                        android = subprocess.check_output(
                            [adb, '-s', serial, 'shell', 'getprop', 'ro.build.version.release'],
                            encoding='utf-8', errors='replace', timeout=5
                        ).strip()
                        devices.append(f'{serial}  |  {model}  |  Android {android}')
                    except Exception:
                        devices.append(serial)
                else:
                    devices.append(f'{serial}  [{state}]')

            # adb 버전
            try:
                adb_ver_out = subprocess.check_output(
                    [adb, 'version'], encoding='utf-8', errors='replace', timeout=5
                )
                adb_ver = adb_ver_out.splitlines()[0] if adb_ver_out else ''
            except Exception:
                adb_ver = ''

            self._json({'devices': devices, 'count': len(devices), 'adb_version': adb_ver})
        except FileNotFoundError:
            self._json({'devices': [], 'count': 0, 'adb_version': '', 'error': 'adb를 찾을 수 없습니다'})
        except Exception as e:
            self._json({'devices': [], 'count': 0, 'adb_version': '', 'error': str(e)})

    # ── 환경 정보 ──────────────────────────────────
    def _env_info(self):
        py_ver = sys.version.split()[0]
        try:
            import pytest
            pytest_ver = pytest.__version__
        except Exception:
            pytest_ver = ''
        self._json({
            'python': py_ver,
            'pytest': pytest_ver,
        })

    # ── Appium ─────────────────────────────────────
    def _appium_start(self):
        global _appium_proc
        is_run = _appium_running()
        if is_run:
            add_log('[APPIUM] 이미 실행 중입니다 (포트 4723 응답함)')
            self._json({'status': 'already_running'})
            return
            
        add_log('[APPIUM] 서버 시작 중...')
        
        # Windows에서 appium.cmd를 더 잘 찾기 위한 로직
        appium_cmd = 'appium'
        appdata = os.environ.get('APPDATA')
        if appdata:
            npm_appium = os.path.join(appdata, 'npm', 'appium.cmd')
            if os.path.exists(npm_appium):
                appium_cmd = npm_appium

        cmd = [appium_cmd, '--log-level', 'warn']
        add_log(f'[APPIUM] 실행 명령: {" ".join(cmd)}')
        
        try:
            _appium_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                encoding='utf-8', errors='replace',  # Node.js는 UTF-8 출력
                shell=True
            )
        except Exception as e:
            add_log(f'[APPIUM] ⚠️ 시작 실패: {e}')
            self._json({'status': 'error', 'msg': str(e)}, 500)
            return

        def _stream():
            for line in _appium_proc.stdout:
                add_log(f'[APPIUM] {line.rstrip()}')
        threading.Thread(target=_stream, daemon=True).start()

        time.sleep(4)
        if _appium_running():
            add_log('[APPIUM] ✅ 시작 완료 (port 4723)')
            self._json({'status': 'started'})
        else:
            # 실패 시 로그 일부 출력 시도
            add_log('[APPIUM] ❌ 시작 실패 (4초 내 응답 없음)')
            self._json({'status': 'failed'}, 500)

    def _appium_stop(self):
        global _appium_proc
        if not _appium_running():
            self._json({'status': 'not_running'})
            return
        # 프로세스 핸들이 있으면 terminate
        if _appium_proc is not None:
            _appium_proc.terminate()
            _appium_proc = None
        else:
            # 외부에서 실행된 경우 포트로 PID 찾아 종료
            try:
                out = subprocess.check_output(
                    ['netstat', '-ano'], encoding='utf-8', errors='replace'
                )
                for line in out.splitlines():
                    if ':4723' in line and 'LISTENING' in line:
                        pid = line.strip().split()[-1]
                        subprocess.run(['taskkill', '/F', '/PID', pid],
                                       capture_output=True)
                        break
            except Exception:
                pass
        add_log('[APPIUM] 서버 종료')
        self._json({'status': 'stopped'})

    # ── 테스트 실행 ────────────────────────────────
    def _run(self, scenarios):
        global _test_proc, _current_scenario, _running_idx
        if _test_running():
            self._json({'status': 'already_running'})
            return
        with _lock:
            _logs.clear()
            _current_scenario = scenarios
            _running_idx = 0

        if scenarios == 'all':
            cmd = [sys.executable, '-m', 'pytest', 'tests/test_bodoc_flow.py', '-v', '--tb=short']
        else:
            kw = ' or '.join(
                s if s.startswith('test_scenario_') else f'test_scenario_{s}'
                for s in scenarios.split(',')
            )
            cmd = [sys.executable, '-m', 'pytest', 'tests/test_bodoc_flow.py', '-v', '--tb=short', '-k', kw]

        add_log(f'[TEST] 실행: {" ".join(cmd)}')
        _test_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding=SYS_ENC, errors='replace',
            cwd=ROOT
        )

        def _stream():
            global _current_scenario, _running_idx
            for line in _test_proc.stdout:
                msg = line.rstrip()
                if not msg: continue
                
                # 시나리오 전환 감지 (진행률 추적용)
                if 'test_scenario_' in msg and '::' in msg:
                    _running_idx += 1

                # 로그 가독성을 위한 태깅
                if '[DEBUG]' in msg: pass # 이미 되어있음
                elif 'PASSED' in msg: msg = f"[INFO] {msg}"
                elif 'FAILED' in msg: msg = f"[ERROR] {msg}"
                elif 'SKIPPED' in msg: msg = f"[DEBUG] {msg}"
                elif 'collected' in msg: msg = f"[DEBUG] {msg}"
                else: msg = f"[INFO] {msg}"
                
                add_log(msg)
            rc = _test_proc.wait()
            _current_scenario = None
            _running_idx = 0
            add_log(f'[TEST] {"✅ 완료" if rc == 0 else f"❌ 실패 (exit {rc})"}')
        threading.Thread(target=_stream, daemon=True).start()
        self._json({'status': 'started'})

    def _stop_tests(self):
        global _test_proc
        if _test_running():
            _test_proc.terminate()
            add_log('[TEST] 강제 종료')
            self._json({'status': 'stopped'})
        else:
            self._json({'status': 'not_running'})

    # ── 결과 데이터 ────────────────────────────────
    def _results(self):
        all_r = []
        if os.path.exists(RESULTS_DIR):
            for p in sorted(Path(RESULTS_DIR).glob("result_*.json"), reverse=True):
                try:
                    all_r.append(json.loads(p.read_text(encoding='utf-8')))
                except: continue
        self._json(all_r)

    def _test_definition(self):
        scenarios, err = _extract_scenarios()
        if err:
            print(f"[ERR] 시나리오 추출 실패: {err}")
            self._json({"scenarios": [], "error": err}, 500 if "없음" not in err else 404)
        else:
            self._json({"scenarios": scenarios})

def _extract_scenarios():
    """테스트 파일에서 시나리오 목록을 추출하는 전역 함수"""
    test_file = os.path.join(ROOT, 'tests', 'test_bodoc_flow.py')
    scenarios = []
    try:
        if not os.path.exists(test_file):
            return [], f"파일 없음: {test_file}"

        import ast
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
        
        lines = content.splitlines()
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_scenario_'):
                try:
                    parts = node.name.split('_')
                    s_id = parts[2] if len(parts) >= 3 else "0"
                    # test_scenario_3_1_... 형태: 세 번째 파트 다음이 숫자면 "3_1" 로 결합
                    if len(parts) >= 4 and parts[3].isdigit():
                        s_id = f"{parts[2]}_{parts[3]}"
                    doc = ast.get_docstring(node) or "설명 없음"
                    func_lines = lines[node.lineno-1 : node.end_lineno]
                    code = "\n".join(func_lines)
                    
                    scenarios.append({
                        "id": s_id,
                        "name": node.name,
                        "description": doc,
                        "code": code
                    })
                except: continue
        return scenarios, None
    except Exception as e:
        return [], str(e)



if __name__ == '__main__':
    print(f'Bodoc QA Dashboard -> http://localhost:{PORT}')
    print('   Ctrl+C to stop')
    try:
        ThreadingHTTPServer(('', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\n서버 종료')
