# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime
from pathlib import Path

# ── HTML 템플릿 (V1.3.3: Analysis & Debugging Tools) ──────────────────────────
_HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bodoc QA Dashboard</title>
<style>
  :root {
    --side-bg: #1e2130;
    --side-active: #2a2f45;
    --brand: #7eaaff;
    --bg: #f8f9fc;
    --card-bg: #ffffff;
    --text-main: #333a4d;
    --text-muted: #8a94a8;
    --border: #eef1f6;
    --danger: #ff4757;
    --success: #2ecc71;
    --warning: #f59e0b;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', 'Segoe UI', 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text-main); height: 100vh; display: flex; overflow: hidden; }
  @keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(0.98); }
    100% { opacity: 1; transform: scale(1); }
  }

  /* ── 레이아웃 ── */
  .app-container { display: flex; width: 100%; height: 100%; }
  .sidebar { width: 240px; background: var(--side-bg); color: #fff; display: flex; flex-direction: column; flex-shrink: 0; z-index: 100; box-shadow: 4px 0 10px rgba(0,0,0,0.1); }
  .side-header { padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.05); }
  .brand { font-size: 18px; font-weight: 800; color: var(--brand); letter-spacing: -0.5px; }

  .side-nav { flex: 1; padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; }
  .nav-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px; cursor: pointer; color: #8a94a8; border: none; background: none; width: 100%; text-align: left; transition: 0.2s; font-size: 14px; font-weight: 500; font-family: inherit; }
  .nav-item:hover { background: rgba(255,255,255,0.05); color: #fff; }
  .nav-item.active { background: var(--brand); color: #fff; box-shadow: 0 4px 12px rgba(126, 170, 255, 0.3); }

  .main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
  .page-header { background: #fff; padding: 16px 28px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
  .page-title { font-size: 18px; font-weight: 700; color: #1e2130; }

  .pane-container { flex: 1; overflow-y: auto; padding: 24px 28px; display: flex; flex-direction: column; gap: 20px; }
  .tab-pane { display: none; flex-direction: column; gap: 20px; width: 100%; }
  .tab-pane.active { display: flex; }

  /* 카드 */
  .card { background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); border: 1px solid var(--border); }
  .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
  .card-title { font-size: 14px; font-weight: 700; color: #1e2130; display: flex; align-items: center; gap: 8px; }
  
  /* 대시보드 */
  .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; width: 100%; }
  .stat-card { background: #fff; padding: 20px; border-radius: 12px; border: 1px solid var(--border); text-align: center; }
  .stat-value { font-size: 28px; font-weight: 800; }
  .stat-label { font-size: 11px; color: var(--text-muted); font-weight: 600; margin-top: 4px; text-transform: uppercase; }

  .history-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
  .history-table th { text-align: left; padding: 10px; border-bottom: 2px solid var(--border); color: #888; }
  .history-table td { padding: 12px 10px; border-bottom: 1px solid var(--border); }
  .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; }
  .badge-success { background: #e6fffa; color: #319795; }
  .badge-danger { background: #fff5f5; color: #e53e3e; }

  /* 실행 레이아웃 */
  .execution-split { display: flex; gap: 20px; height: calc(100vh - 120px); overflow: hidden; }
  .split-left { width: 440px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; flex-shrink: 0; }
  .split-right { flex: 1; display: flex; flex-direction: column; gap: 15px; overflow: hidden; }

  .s-card { background: #fff; border: 1.2px solid var(--border); border-radius: 10px; margin-bottom: 8px; overflow: hidden; transition: 0.2s; }
  .s-card.running { border-color: var(--danger); box-shadow: 0 0 0 2px rgba(255, 71, 87, 0.2); }
  .s-header { padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
  .s-info { display: flex; align-items: center; gap: 8px; }
  .s-num { font-size: 10px; color: var(--brand); font-weight: 800; }
  .s-name { font-size: 13px; font-weight: 600; }
  .s-body { display: none; padding: 15px 16px; border-top: 1px solid #f8f9fc; background: #fafafa; }
  .s-card.open .s-body { display: block; }
  .s-code { background: #1e2130; color: #fff; padding: 10px; border-radius: 6px; font-size: 10.5px; overflow-x: auto; margin-top: 10px; border: 1px solid #333; }

  .log-box { background: #1e2130; border-radius: 12px; height: 100%; overflow-y: auto; padding: 16px; font-family: 'Consolas', monospace; font-size: 12px; color: #eee; line-height: 1.5; scroll-behavior: smooth; }
  .log-line { border-bottom: 1px solid rgba(255,255,255,0.03); padding: 2px 0; word-break: break-all; }
  .log-line.ok { color: #4ade80; font-weight: 600; }
  .log-line.err { color: #f87171; font-weight: 600; }
  .log-line.info { color: #fff; }
  .log-line.debug { color: #6b7280; font-size: 11.5px; }

  /* 결과 상 세 */
  .res-layout { display: flex; height: calc(100vh - 120px); gap: 20px; overflow: hidden; }
  .res-sidebar { width: 320px; background: #fff; border-radius: 12px; border: 1px solid var(--border); display: flex; flex-direction: column; overflow: hidden; }
  .res-filter { padding: 12px; border-bottom: 1px solid var(--border); display: flex; gap: 4px; background: #fcfdfe; }
  .filter-btn { flex: 1; border: 1px solid var(--border); background: #fff; padding: 6px; font-size: 11px; border-radius: 4px; cursor: pointer; font-weight: 600; color: #666; }
  .filter-btn.active { background: var(--brand); color: #fff; border-color: var(--brand); }
  
  #run-list { flex: 1; overflow-y: auto; }
  .res-main { flex: 1; background: #fff; border-radius: 12px; border: 1px solid var(--border); padding: 24px; overflow-y: auto; }
  .res-item { padding: 16px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: background 0.2s; position: relative; }
  .res-item:hover { background: #f8f9fc; }
  .res-item.active { background: #f0f4ff; border-left: 4px solid var(--brand); }

  .status-icon { font-weight: 900; font-size: 14px; }
  .status-icon.pass { color: var(--success); }
  .status-icon.fail { color: var(--danger); }

  .report-header { margin-bottom: 24px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
  .err-msg-box { background: #fff5f5; border: 1px solid #feb2b2; color: #c53030; padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 10px; font-family: 'Consolas', monospace; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; }

  .sc-card { border: 1px solid var(--border); border-radius: 8px; margin-bottom: 15px; overflow: hidden; }
  .sc-head { padding: 14px 18px; background: #fcfdfe; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
  .sc-body { padding: 18px; border-top: 1px solid var(--border); }
  .sc-card.closed .sc-body { display: none; }
  
  .step-img { width: 140px; height: 180px; object-fit: cover; border-radius: 6px; margin-top: 10px; cursor: zoom-in; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid var(--border); transition: transform 0.2s; }
  .step-img:hover { transform: scale(1.05); }
  .step-img.fail { border-color: var(--danger); box-shadow: 0 0 10px rgba(255, 71, 87, 0.4); }

  /* 버튼 */
  .btn { border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: 0.2s; position: relative; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(1); }
  .btn-primary { background: var(--brand); color: #fff; }
  .btn-danger { background: #fff; color: var(--danger); border: 1px solid var(--danger); }
  .btn-ghost { background: #f0f2f5; color: #555; }
  .run-mini-btn { padding: 4px 10px; font-size: 10px; font-weight: 700; color: var(--brand); border: 1.5px solid var(--brand); background: #fff; border-radius: 15px; cursor: pointer; }
  .run-mini-btn.running { background: var(--brand); color: #fff; }

  .spinner { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.8s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  #lb { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.9); z-index: 9999; align-items: center; justify-content: center; }
  #lb.on { display: flex; }
  #lb img { max-width: 95%; max-height: 95%; }
  
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
</style>
</head>
<body>

<div id="error-display"></div>

<div class="app-container">
  <aside class="sidebar">
    <div class="side-header"><div class="brand">🧪 BODOC QA</div></div>
    <nav class="side-nav">
      <button class="nav-item active" id="nav-home" onclick="switchTab('home')">🏠 대시보드</button>
      <button class="nav-item" id="nav-run" onclick="switchTab('run')">🚀 테스트 실행</button>
      <button class="nav-item" id="nav-res" onclick="switchTab('res')">📊 테스트 결과</button>
      <button class="nav-item" id="nav-set" onclick="switchTab('set')">⚙️ 설정</button>
    </nav>
  </aside>

  <main class="main-content">
    <header class="page-header">
      <div class="page-title" id="page-title">대시보드</div>
      <div id="badge-area"></div>
    </header>

    <div class="pane-container">
      
      <!-- 1. Dashboard -->
      <div class="tab-pane active" id="pane-home">
        <div class="stat-grid">
           <div class="stat-card"><div class="stat-value" id="dash-total">0</div><div class="stat-label">전체 실행 횟수</div></div>
           <div class="stat-card"><div class="stat-value" id="dash-pass-rate" style="color:var(--success)">0%</div><div class="stat-label">테스트 성공률</div></div>
           <div class="stat-card"><div class="stat-value" id="dash-last-fail">0</div><div class="stat-label">최근 실패 건수</div></div>
           <div class="stat-card"><div class="stat-value" id="dash-scenario-count">0</div><div class="stat-label">등록 시나리오</div></div>
        </div>
        
        <div class="card">
          <div class="card-header"><b class="card-title">📅 최근 실행 이력</b></div>
          <table class="history-table">
            <thead><tr><th>날짜 / 시간</th><th>실행 ID</th><th>결과</th><th>Pass / Fail</th><th>상세</th></tr></thead>
            <tbody id="dash-history-body"></tbody>
          </table>
        </div>

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div class="card"><b class="card-title">🔍 시스템 상태</b><div id="dash-sys-status" style="font-size:13px; margin-top:10px; line-height:1.8;">시스템 상태를 불러오는 중...</div></div>
          <div class="card"><b class="card-title">📖 빠른 도움말</b><div style="font-size:13px; color:#666; margin-top:10px; line-height:1.6;">1. <b>테스트 실행</b> 메뉴에서 실행할 테스트를 선택하세요.<br>2. <b>테스트 결과</b> 메뉴에서 상세 로그와 스크린샷을 확인하세요.<br>3. 실패 시 빨간색 테두리 스크린샷을 클릭하여 확대해 보세요.</div></div>
        </div>
      </div>

      <!-- 2. Test Execution -->
      <div class="tab-pane" id="pane-run">
        <div class="execution-split">
          <div class="split-left">
            <div class="card" style="height:100%; display:flex; flex-direction:column;">
              <div class="card-header">
                <b class="card-title">🧪 테스트 시나리오</b>
                <div style="display:flex; gap:6px;">
                  <button id="btn-run-all" class="btn btn-primary" onclick="runTests('all')">전체 실행</button>
                  <button id="btn-stop-test" class="btn btn-danger" onclick="stopTests()" disabled>중지</button>
                </div>
              </div>
              <div id="scenario-list" style="flex:1; overflow-y:auto;"></div>
            </div>
          </div>
          <div class="split-right">
            <div class="card" style="height:100%; display:flex; flex-direction:column;">
              <div class="card-header">
                <b class="card-title">📋 실시간 실행 로그</b>
                <div style="display:flex; gap:8px; align-items:center;">
                    <label style="font-size:11px; color:#888; display:flex; align-items:center; gap:4px; cursor:pointer;">
                        <input type="checkbox" id="chk-auto-scroll" checked> 자동 스크롤
                    </label>
                    <button class="btn btn-ghost" style="padding:4px 10px; font-size:11px;" onclick="clearLogs('log-panel-run')">비우기</button>
                </div>
              </div>
              <div class="log-box" id="log-panel-run"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. Test Results -->
      <div class="tab-pane" id="pane-res">
        <div class="res-layout">
          <div class="res-sidebar">
            <div class="res-filter">
               <button class="filter-btn active" id="filter-all" onclick="setFilter('all')">전체</button>
               <button class="filter-btn" id="filter-pass" onclick="setFilter('pass')">성공</button>
               <button class="filter-btn" id="filter-fail" onclick="setFilter('fail')">실패</button>
            </div>
            <div id="run-list"></div>
          </div>
          <div class="res-main" id="rpt-detail">
             <div style="text-align:center; margin-top:150px; color:#aaa;">왼쪽 리스트에서 결과 항목을 선택해 주세요.</div>
          </div>
        </div>
      </div>

      <!-- 4. Settings -->
      <div class="tab-pane" id="pane-set">
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:20px;">
          <div class="card">
            <b class="card-title">📡 Appium 서버</b>
            <div style="margin-top:10px; display:flex; gap:8px; align-items:center;">
              <div id="appium-dot" class="dot"></div> <span id="appium-text">상태 확인 중...</span>
            </div>
            <div style="margin-top:10px; display:flex; gap:8px;">
              <button class="btn btn-ghost" style="flex:1" onclick="startAppium()">실행</button>
              <button class="btn btn-ghost" style="flex:1" onclick="stopAppium()">중지</button>
            </div>
          </div>
          <div class="card">
            <div class="card-header" style="margin-bottom:0px;">
              <b class="card-title">📱 안드로이드 디바이스</b>
              <button class="btn btn-ghost" style="padding:4px 10px; font-size:11px;" onclick="updateStatus()">갱신</button>
            </div>
            <div style="margin-top:10px; display:flex; gap:8px; align-items:center;">
              <div id="device-dot" class="dot"></div> <span id="device-text">기기 검색 중...</span>
            </div>
            <div id="device-list" style="font-size:11px; color:#888; margin-top:8px;"></div>
          </div>
          <div class="card"><b class="card-title">⚙️ 실행 환경 정보</b><div id="env-info" style="font-size:11px; line-height:1.6; margin-top:10px;"></div></div>
        </div>
        <div class="card" style="height:350px; display:flex; flex-direction:column;">
          <div class="card-header"><b class="card-title">📋 시스템 통합 로그 (ANSI 정제됨)</b><button class="btn btn-ghost" style="padding:4px 10px; font-size:11px;" onclick="clearLogs('log-panel-set')">비우기</button></div>
          <div class="log-box" id="log-panel-set"></div>
        </div>
      </div>
    </div>
  </main>
</div>

<div id="lb" onclick="this.classList.remove('on')"><img id="lb-img"></div>
<script id="reports-data" type="application/json">__REPORTS_JSON__</script>

<script>
let API = (window.location.protocol === 'file:') ? 'http://localhost:8888' : '';
const labels = { home: '대시보드', run: '테스트 실행', res: '테스트 결과', set: '설정' };
let _results = [];
let _filter = 'all';
let _isRunning = false;
let _runningID = null;

function esc(str) { return str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") : ""; }

async function api(path) {
    try {
        const r = await fetch(API + path + (path.includes('?') ? '&' : '?') + 't=' + Date.now());
        return r.ok ? await r.json() : null;
    } catch(e) { return null; }
}

function setFilter(f) {
    _filter = f;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.toggle('active', b.id === 'filter-' + f));
    loadResults();
}

function switchTab(target) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById('nav-' + target).classList.add('active');
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.getElementById('pane-' + target).classList.add('active');
    document.getElementById('page-title').textContent = labels[target];
    if(target === 'home') refreshDashboard();
    if(target === 'run') renderScenarioGrid();
    if(target === 'res') loadResults();
}

async function refreshDashboard() {
    await loadResults();
    const sc = await api('/api/test/definition');
    document.getElementById('dash-scenario-count').textContent = (sc && sc.scenarios) ? sc.scenarios.length : '0';
    document.getElementById('dash-total').textContent = _results.length;
    let passCount = _results.filter(r => r.summary.failed === 0).length;
    document.getElementById('dash-pass-rate').textContent = _results.length > 0 ? Math.round((passCount/_results.length)*100)+'%' : '0%';
    
    // Fail Card Color Logic
    const failVal = _results.slice(0,5).filter(r => r.summary.failed > 0).length;
    const failEl = document.getElementById('dash-last-fail');
    failEl.textContent = failVal;
    failEl.style.color = failVal > 0 ? 'var(--danger)' : 'var(--success)';

    const tbody = document.getElementById('dash-history-body');
    tbody.innerHTML = '';
    _results.slice(0, 5).forEach(r => {
        const tr = document.createElement('tr');
        const ok = r.summary.failed === 0;
        tr.innerHTML = `<td>${r.date} ${r.time}</td><td style="font-family:monospace; font-size:11px; color:#666;">${r.run_id}</td><td><span class="badge ${ok?'badge-success':'badge-danger'}">${ok?'PASS':'FAIL'}</span></td><td>${r.summary.passed} / ${r.summary.failed}</td><td><button class="run-mini-btn" onclick="switchTab('res'); setTimeout(()=>showReportByID('${r.run_id}'), 100)">상세</button></td>`;
        tbody.appendChild(tr);
    });
}

async function updateStatus() {
    const s = await api('/api/appium/status');
    const d = await api('/api/device/status');
    const t = await api('/api/test/status');

    if(s) {
        const adot = document.getElementById('appium-dot');
        const atxt = document.getElementById('appium-text');
        if(s.running) { adot.className='dot on'; atxt.textContent='온라인 (v'+s.version+')'; }
        else { adot.className='dot off'; atxt.textContent='오프라인'; }
    }

    if(d) {
        const ddot = document.getElementById('device-dot');
        const dtxt = document.getElementById('device-text');
        if(d.count > 0) { ddot.className='dot on'; dtxt.textContent=d.count+'대 연결됨'; document.getElementById('device-list').innerHTML = d.devices.join('<br>'); }
        else { ddot.className='dot off'; dtxt.textContent='연결된 기기 없음'; document.getElementById('device-list').innerHTML = ''; }
    }

    if(t) {
        _isRunning = t.running;
        _runningID = t.current_scenario;
        document.getElementById('btn-stop-test').disabled = !_isRunning;
        document.getElementById('btn-run-all').disabled = _isRunning;

        // 진행 상태 표시 강화
        const badge = document.getElementById('badge-area');
        if(_isRunning) {
            let prog = '진행 중...';
            if(t.total_count > 0) {
                const cur = t.current_idx || 0;
                prog = `시나리오 실행 중 (${cur}/${t.total_count})`;
            }
            badge.innerHTML = `<span class="badge" style="background:var(--warning); color:#fff; padding:6px 12px; font-size:12px; border-radius:20px; animation: pulse 2s infinite;">⏳ ${prog}</span>`;
        } else {
            badge.innerHTML = '<span class="badge" style="background:#e2e8f0; color:#64748b; padding:6px 12px; font-size:12px; border-radius:20px;">💤 대기 중</span>';
        }
    }
    
    if(document.getElementById('pane-run').classList.contains('active')) {
        document.querySelectorAll('.s-card').forEach(card => {
            const id = card.getAttribute('data-id');
            const btn = card.querySelector('.run-mini-btn');
            if(_isRunning && (id === _runningID || _runningID === 'all')) {
                card.classList.add('running'); btn.disabled = true;
                btn.innerHTML = '<div class="spinner"></div> 실행중'; btn.classList.add('running');
            } else {
                card.classList.remove('running'); btn.disabled = _isRunning;
                btn.innerHTML = 'Run'; btn.classList.remove('running');
            }
        });
    }

    const dashSys = document.getElementById('dash-sys-status');
    if(dashSys) dashSys.innerHTML = `Appium 서버: <b style="color:${s&&s.running?'var(--success)':'var(--danger)'}">${s&&s.running?'작동 중':'중지됨'}</b><br>연결 기기: <b>${d?d.count:'0'}</b>대<br>테스트 상태: ${_isRunning?'<b style="color:var(--warning)">진행 중...</b>':'<b style="color:#888">대기</b>'}`;
}

async function renderScenarioGrid() {
    const d = await api('/api/test/definition');
    const list = document.getElementById('scenario-list');
    if(!d || !d.scenarios || !list) return;
    list.innerHTML = '';
    d.scenarios.sort((a,b)=>a.id-b.id).forEach(s => {
        const card = document.createElement('div');
        card.className = 's-card'; card.setAttribute('data-id', s.id);
        const name = s.description ? s.description.split('\n')[0] : s.name;
        card.innerHTML = `
            <div class="s-header">
                <div class="s-info"><span class="s-num">S${s.id}</span> <span class="s-name">${esc(name)}</span></div>
                <button class="run-mini-btn">Run</button>
            </div>
            <div class="s-body">
                <div style="font-size:12px; color:#555; line-height:1.6; white-space:pre-wrap;">${esc(s.description || '상세 설명 없음')}</div>
                ${s.code ? `<div class="s-code"><pre>${esc(s.code)}</pre></div>` : ''}
            </div>
        `;
        card.querySelector('.s-header').onclick = (e) => { if(e.target.tagName !== 'BUTTON') card.classList.toggle('open'); };
        card.querySelector('.run-mini-btn').onclick = (e) => { e.stopPropagation(); runTests(s.id); };
        list.appendChild(card);
    });
    updateStatus();
}

async function runTests(id) {
    if(_isRunning) return;
    await api('/api/run?s=' + id);
    _isRunning = true; _runningID = id;
    document.getElementById('badge-area').innerHTML = '<span style="color:var(--warning); font-weight:700; font-size:12px;">⏳ 대기 중...</span>';
}

async function stopTests() { if(confirm("현재 진행 중인 테스트를 강제 종료하시겠습니까?")) await api('/api/stop'); }

async function loadResults() {
    const data = await api('/api/results');
    if(data) _results = data;
    const list = document.getElementById('run-list');
    if(!list) return;
    list.innerHTML = '';
    
    const filtered = _results.filter(r => {
        if(_filter === 'pass') return r.summary.failed === 0;
        if(_filter === 'fail') return r.summary.failed > 0;
        return true;
    });

    filtered.forEach(r => {
        const div = document.createElement('div');
        div.className = 'res-item';
        div.setAttribute('data-runid', r.run_id);
        const ok = r.summary.failed === 0;
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                   <div style="font-weight:700; font-size:13px;">${r.date} ${r.time}</div>
                   <div style="font-size:11px; color:#999; margin-top:4px;">${r.run_id}</div>
                </div>
                <span class="status-icon ${ok?'pass':'fail'}">${ok?'✓':'✗'}</span>
            </div>
        `;
        div.onclick = () => showReport(r, div);
        list.appendChild(div);
    });
}

function showReportByID(id) {
    const r = _results.find(x => x.run_id === id);
    if(r) showReport(r, document.querySelector(`.res-item[data-runid="${id}"]`));
}

function showReport(r, el) {
    document.querySelectorAll('.res-item').forEach(i=>i.classList.remove('active'));
    if(el) el.classList.add('active');
    
    const det = document.getElementById('rpt-detail');
    const cards = (r.scenarios || []).map(s => {
        const duration = s.duration ? `(${s.duration}s)` : "";
        const steps = (s.steps||[]).map(st => `
            <div style="margin-bottom:12px;">
                <div style="display:flex; gap:8px;">
                    <span class="status-icon ${st.status==='PASSED'?'pass':'fail'}">${st.status==='PASSED'?'✓':'✗'}</span>
                    <div style="flex:1;">
                        <b style="font-size:13px; display:block; margin-bottom:4px;">${esc(st.name)}</b>
                        ${st.screenshot ? `<div style="margin-top:8px;"><img src="../screenshots/${st.screenshot}" class="step-img ${st.status==='FAILED'?'fail':''}" onclick="openImg(this.src)"></div>` : ''}
                        ${st.status === 'FAILED' && s.error ? `<div class="err-msg-box">실패 원인:<br>${esc(s.error)}</div>` : ''}
                    </div>
                </div>
            </div>
        `).join('');
        return `<div class="sc-card">
            <div class="sc-head" onclick="this.parentElement.classList.toggle('closed')">
                <b style="font-size:14px; display:flex; gap:8px; align-items:center;">
                    <span class="status-icon ${s.status==='PASSED'?'pass':'fail'}">${s.status==='PASSED'?'✓':'✗'}</span> ${esc(s.name)} ${duration}
                </b>
                <small style="color:#aaa">${s.start}</small>
            </div>
            <div class="sc-body">${steps}</div>
        </div>`;
    }).join('');

    det.innerHTML = `
        <div class="report-header">
            <h2 style="font-size:20px;">실행 리포트 (Execution Report)</h2>
            <div style="font-size:11px; color:#888; margin-top:5px;">실행 ID: ${r.run_id} | 일시: ${r.date} ${r.time} ${r.duration ? ` | 총 소요시간: ${r.duration}초` : ''}</div>
            <div style="display:flex; gap:15px; margin-top:12px;">
                <span style="font-size:13px">전체 시나리오: <b>${r.summary.total}</b></span>
                <span style="font-size:13px; color:var(--success)">성공: <b>${r.summary.passed}</b></span>
                <span style="font-size:13px; color:var(--danger)">실패: <b>${r.summary.failed}</b></span>
            </div>
        </div>
        ${cards || '<p style="color:#aaa">기록된 시나리오가 없습니다.</p>'}
    `;
}

let logOffset = 0;
async function pollLogs() {
    const d = await api('/api/logs?offset=' + logOffset);
    if(d && d.logs && d.logs.length > 0) {
        const autoScroll = document.getElementById('chk-auto-scroll').checked;
        ['log-panel-run', 'log-panel-set'].forEach(id => {
            const p = document.getElementById(id); if(!p) return;
            d.logs.forEach(l => {
                const div = document.createElement('div');
                let cls = 'log-line';
                if(l.includes('[ERROR]') || l.includes('FAILED')) cls += ' err';
                else if(l.includes('[PASSED]') || l.includes('✅')) cls += ' ok';
                else if(l.includes('[INFO]')) cls += ' info';
                else if(l.includes('[DEBUG]')) cls += ' debug';
                
                div.className = cls;
                div.textContent = l; p.appendChild(div);
            });
            if(autoScroll) p.scrollTop = p.scrollHeight;
        });
        logOffset = d.total;
    }
}
function clearLogs(id) { document.getElementById(id).innerHTML = ''; }
function openImg(src) { event.stopPropagation(); const lb=document.getElementById('lb'); document.getElementById('lb-img').src=src; lb.classList.add('on'); }
async function startAppium() { await api('/api/appium/start'); }
async function stopAppium() { await api('/api/appium/stop'); }

async function init() {
    const env = await api('/api/env');
    if(env) document.getElementById('env-info').innerHTML = `Python: ${env.python}<br>Pytest: ${env.pytest}<br>Ver: 1.3.3 Analysis`;
    updateStatus(); await refreshDashboard();
    setInterval(pollLogs, 1000); setInterval(updateStatus, 3000);
}
init();
</script>
</body>
</html>"""


class TestReporter:
    def __init__(self, results_dir, reports_dir, screenshots_dir, run_id=None):
        self.results_dir = results_dir
        self.reports_dir = reports_dir
        self.screenshots_dir = screenshots_dir
        self.run_id = run_id or datetime.now().strftime('%Y%m%d_%H%M%S')
        self._start = time.time()
        self._current = None
        self.data = {
            "run_id": self.run_id,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": datetime.now().strftime('%H:%M:%S'),
            "duration": 0,
            "scenarios": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
        }

    def start_scenario(self, name):
        self._current = {
            "name": name,
            "status": "RUNNING",
            "start": datetime.now().strftime('%H:%M:%S'),
            "start_ts": time.time(),
            "end": None,
            "duration": 0,
            "steps": [],
            "error": None
        }

    def step(self, name, status="PASSED", screenshot=None):
        if self._current is None: return
        self._current["steps"].append({"name": name, "status": status, "screenshot": screenshot})

    def end_scenario(self, status, error=None):
        if self._current is None: return
        self._current["status"] = status
        self._current["end"] = datetime.now().strftime('%H:%M:%S')
        self._current["duration"] = round(time.time() - self._current.get("start_ts", time.time()), 1)
        if error:
            # 에러 메시지가 너무 길면 잘릴 수 있으므로 최대한 보관
            self._current["error"] = str(error)
        
        self.data["scenarios"].append(self._current)
        self.data["summary"]["total"] += 1
        if status == "PASSED": self.data["summary"]["passed"] += 1
        else: self.data["summary"]["failed"] += 1
        self._current = None

    def save(self):
        self.data["duration"] = round(time.time() - self._start, 1)
        if not self.data["scenarios"]: return
        os.makedirs(self.results_dir, exist_ok=True)
        json_path = os.path.join(self.results_dir, f"result_{self.run_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self._generate_html()

    def _generate_html(self):
        os.makedirs(self.reports_dir, exist_ok=True)
        all_results = []
        if os.path.exists(self.results_dir):
            for r in sorted(Path(self.results_dir).glob("result_*.json"), reverse=True):
                try:
                    with open(str(r), encoding="utf-8") as f:
                        all_results.append(json.load(f))
                except: continue
        reports_json = json.dumps(all_results, ensure_ascii=True)
        html = _HTML.replace('__REPORTS_JSON__', reports_json)
        html_path = os.path.join(self.reports_dir, "report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[REPORT] HTML 업데이트 완료: {html_path}")
