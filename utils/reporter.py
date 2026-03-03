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
  .execution-split { display: flex; gap: 0; height: calc(100vh - 120px); overflow: hidden; }
  .split-left { flex: none; width: 50%; min-width: 180px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
  .split-right { flex: 1; min-width: 180px; display: flex; flex-direction: column; gap: 15px; overflow: hidden; }
  .split-divider { width: 14px; flex-shrink: 0; cursor: col-resize; display: flex; align-items: center; justify-content: center; }
  .split-divider::after { content: ''; display: block; width: 3px; height: 48px; background: #d1d5db; border-radius: 3px; transition: background 0.15s, height 0.15s; }
  .split-divider:hover::after { background: var(--brand); height: 64px; }
  .split-divider.dragging::after { background: var(--brand); height: 80px; }

  .s-card { background: #fff; border: 1.2px solid var(--border); border-left-width: 4px; border-radius: 10px; margin-bottom: 8px; overflow: hidden; transition: background 0.25s, border-color 0.25s, box-shadow 0.25s; }
  .s-card.sc-idle    { border-left-color: #d1d5db; }
  .s-card.sc-running { border-left-color: #3b82f6; background: #f0f7ff; animation: card-glow 2s ease-in-out infinite; }
  .s-card.sc-passed  { border-left-color: var(--success); background: #f0fdf4; }
  .s-card.sc-failed  { border-left-color: var(--danger);  background: #fff5f5; }
  .s-card.sc-skipped { border-left-color: var(--warning); background: #fffbeb; }
  .s-card.sc-done    { border-left-color: #9ca3af; background: #f9fafb; }
  @keyframes card-glow {
    0%, 100% { box-shadow: 0 0 0 2px rgba(59,130,246,0.12); }
    50%       { box-shadow: 0 0 0 6px rgba(59,130,246,0.30); }
  }
  .s-header { padding: 12px 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; gap: 8px; }
  .s-info { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
  .s-num { font-size: 10px; color: var(--brand); font-weight: 800; flex-shrink: 0; }
  .s-name { font-size: 13px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .s-meta { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
  .s-body { display: none; padding: 15px 16px; border-top: 1px solid #f8f9fc; background: #fafafa; }
  .s-card.open .s-body { display: block; }
  .s-code { background: #1e2130; color: #fff; padding: 10px; border-radius: 6px; font-size: 10.5px; overflow-x: auto; margin-top: 10px; border: 1px solid #333; }
  .s-badge { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px; white-space: nowrap; }
  .s-badge.sc-idle    { background: #f3f4f6; color: #9ca3af; }
  .s-badge.sc-running { background: #dbeafe; color: #1d4ed8; }
  .s-badge.sc-passed  { background: #dcfce7; color: #15803d; }
  .s-badge.sc-failed  { background: #fee2e2; color: #b91c1c; }
  .s-badge.sc-skipped { background: #fef9c3; color: #a16207; }
  .s-badge.sc-done    { background: #f3f4f6; color: #6b7280; }
  .s-elapsed { font-size: 11px; color: #9ca3af; font-family: 'Consolas', monospace; min-width: 56px; text-align: right; }
  .s-elapsed.live { color: #3b82f6; font-weight: 700; }
  .s-card.sc-user-skip { opacity: 0.45; }
  .s-card.sc-user-skip .s-name { text-decoration: line-through; color: #9ca3af; }
  .skip-btn { font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 10px; cursor: pointer; border: 1.5px solid #d1d5db; background: #f9fafb; color: #9ca3af; white-space: nowrap; }
  .skip-btn.skipped { background: #fef9c3; color: #a16207; border-color: #fcd34d; }

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
  
  .dot { width: 10px; height: 10px; border-radius: 50%; background: #ccc; display: inline-block; flex-shrink: 0; }
  .dot.on  { background: var(--success); box-shadow: 0 0 6px rgba(46,204,113,0.5); }
  .dot.off { background: var(--danger);  box-shadow: 0 0 6px rgba(255,71,87,0.3); }

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
          <div class="split-left" id="split-left">
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
          <div class="split-divider" id="split-divider" title="드래그하여 패널 크기 조절"></div>
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
          <div class="card">
            <b class="card-title">🗑️ 이전 결과 삭제</b>
            <div style="margin-top:10px;">
              <label style="font-size:11px; color:#888; display:block; margin-bottom:6px;">기준 날짜 이전(포함) 결과를 삭제합니다</label>
              <input type="date" id="delete-date-input"
                style="width:100%; box-sizing:border-box; padding:6px 8px; border:1px solid var(--border); border-radius:6px; background:#fff; color:var(--text-main); font-size:13px; color-scheme:light;" />
              <button class="btn btn-ghost" style="width:100%; margin-top:8px; color:#e57373;"
                onclick="deleteResultsByDate()">삭제</button>
              <div id="delete-result-msg" style="font-size:11px; margin-top:6px; min-height:16px;"></div>
            </div>
          </div>
        </div>
        <div class="card" style="height:350px; display:flex; flex-direction:column;">
          <div class="card-header"><b class="card-title">📋 시스템 통합 로그</b><button class="btn btn-ghost" style="padding:4px 10px; font-size:11px;" onclick="clearLogs('log-panel-set')">비우기</button></div>
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
let _scenarioList = [];  // 정렬된 시나리오 ID 배열
let _cardStatus   = {};  // { id: 'idle'|'running'|'passed'|'failed'|'skipped'|'done' }
let _cardStart    = {};  // { id: ms } 실행 시작 시각
let _prevRunning  = false;
let _prevIdx      = 0;
const SC_LABEL = { idle:'Idle', running:'Running', passed:'Passed', failed:'Failed', skipped:'Skipped', done:'Done' };
const SC_ICON  = { idle:'○', running:'▶', passed:'✓', failed:'✗', skipped:'—', done:'●' };
let _skipSet = new Set(JSON.parse(localStorage.getItem('bodoc_skip') || '[]'));

function esc(str) { return str ? str.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") : ""; }

async function api(path, timeout=5000) {
    const ctrl = new AbortController();
    const tid  = setTimeout(() => ctrl.abort(), timeout);
    try {
        const r = await fetch(API + path + (path.includes('?') ? '&' : '?') + 't=' + Date.now(), { signal: ctrl.signal });
        clearTimeout(tid);
        return r.ok ? await r.json() : null;
    } catch(e) { clearTimeout(tid); return null; }
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
    if (_results.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="5" style="text-align:center; color:#aaa; padding:20px 0; font-size:13px;">실행 이력이 없습니다</td>`;
        tbody.appendChild(tr);
    } else {
        _results.slice(0, 5).forEach(r => {
            const tr = document.createElement('tr');
            const ok = r.summary.failed === 0;
            tr.innerHTML = `<td>${r.date} ${r.time}</td><td style="font-family:monospace; font-size:11px; color:#666;">${r.run_id}</td><td><span class="badge ${ok?'badge-success':'badge-danger'}">${ok?'PASS':'FAIL'}</span></td><td>${r.summary.passed} / ${r.summary.failed}</td><td><button class="run-mini-btn" onclick="switchTab('res'); setTimeout(()=>showReportByID('${r.run_id}'), 100)">상세</button></td>`;
            tbody.appendChild(tr);
        });
    }
}

async function updateStatus() {
    const [s, d, t] = await Promise.all([
        api('/api/appium/status'),
        api('/api/device/status'),
        api('/api/test/status'),
    ]);

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
                prog = `시나리오 실행 중 (${Math.min(cur + 1, t.total_count)}/${t.total_count})`;
            }
            badge.innerHTML = `<span class="badge" style="background:var(--warning); color:#fff; padding:6px 12px; font-size:12px; border-radius:20px; animation: pulse 2s infinite;">⏳ ${prog}</span>`;
        } else {
            badge.innerHTML = '<span class="badge" style="background:#e2e8f0; color:#64748b; padding:6px 12px; font-size:12px; border-radius:20px;">💤 대기 중</span>';
        }
    }
    
    // ── 실행 시작/종료 전환 감지 ──────────────────────────────
    if(!_prevRunning && _isRunning) {
        // 새 실행 시작 → 전체 카드 초기화
        _cardStart = {};
        _prevIdx   = 0;
        _scenarioList.forEach(id => setCardStatus(id, 'idle'));
    }
    if(_prevRunning && !_isRunning) {
        // 실행 완료 → 결과 동기화
        syncResultsToCards();
    }
    _prevRunning = _isRunning;

    // ── 실행 중 카드 상태 업데이트 ────────────────────────────
    if(_isRunning && t) {
        const idx = t.current_idx || 0;
        if(_runningID === 'all') {
            // 이전 폴링 이후 완료된 카드 처리 (log파싱 미처리분 보완)
            for(let i = _prevIdx; i < idx && i < _scenarioList.length; i++) {
                const id = _scenarioList[i];
                if(_cardStatus[id] === 'running') setCardStatus(id, 'done');
            }
            // 현재 실행 중인 카드 강조
            if(idx < _scenarioList.length) {
                const runId = _scenarioList[idx];
                if(!['passed','failed','skipped'].includes(_cardStatus[runId])) {
                    if(!_cardStart[runId]) _cardStart[runId] = Date.now();
                    if(_cardStatus[runId] !== 'running') setCardStatus(runId, 'running');
                    const el = document.querySelector(`.s-card[data-id="${runId}"]`);
                    if(el) el.scrollIntoView({behavior:'smooth', block:'nearest'});
                }
            }
        } else {
            // 단일 시나리오 실행
            const runId = String(_runningID);
            if(!['passed','failed','skipped'].includes(_cardStatus[runId])) {
                if(!_cardStart[runId]) _cardStart[runId] = Date.now();
                if(_cardStatus[runId] !== 'running') setCardStatus(runId, 'running');
            }
        }
        _prevIdx = idx;
    }

    // ── Run 버튼 상태 일괄 갱신 ───────────────────────────────
    document.querySelectorAll('.s-card').forEach(card => {
        const btn = card.querySelector('.run-mini-btn');
        if(!btn) return;
        const id = card.getAttribute('data-id');
        if(_cardStatus[id] === 'running') {
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div>';
            btn.classList.add('running');
        } else {
            btn.disabled = _isRunning || _skipSet.has(id);
            btn.innerHTML = 'Run';
            btn.classList.remove('running');
        }
    });

    const dashSys = document.getElementById('dash-sys-status');
    if(dashSys) {
        if(!s && !d && !t) {
            dashSys.innerHTML = '<span style="color:var(--danger)">⚠️ 서버에 응답 없음 (타임아웃) — Appium 및 서버 상태를 확인하세요.</span>';
        } else {
            dashSys.innerHTML = `Appium 서버: <b style="color:${s&&s.running?'var(--success)':'var(--danger)'}">${s&&s.running?'작동 중':'중지됨'}</b><br>연결 기기: <b>${d?d.count:'0'}</b>대<br>테스트 상태: ${_isRunning?'<b style="color:var(--warning)">진행 중...</b>':'<b style="color:#888">대기</b>'}`;
        }
    }
}

async function renderScenarioGrid() {
    const d = await api('/api/test/definition');
    const list = document.getElementById('scenario-list');
    if(!d || !d.scenarios || !list) return;
    function _scKey(id) { const p=String(id).split('_').map(Number); return (p[0]||0)+(p[1]||0)/100; }
    const sorted = d.scenarios.slice().sort((a,b) => _scKey(a.id) - _scKey(b.id));
    _scenarioList = sorted.map(s => String(s.id));
    const prevStatus = {..._cardStatus};
    list.innerHTML = '';
    sorted.forEach(s => {
        const id = String(s.id);
        const st = prevStatus[id] || 'idle';
        if(!prevStatus[id]) _cardStatus[id] = 'idle';
        const card = document.createElement('div');
        const skipped = _skipSet.has(id);
        card.className = 's-card sc-' + st + (skipped ? ' sc-user-skip' : '');
        card.setAttribute('data-id', id);
        const name = s.description ? s.description.split('\n')[0] : s.name;
        card.innerHTML = `
            <div class="s-header">
                <div class="s-info"><span class="s-num">S${esc(id)}</span> <span class="s-name">${esc(name)}</span></div>
                <div class="s-meta">
                    <span class="s-elapsed${st==='running'?' live':''}" data-elapsed></span>
                    <button class="skip-btn${skipped?' skipped':''}" data-skip-btn title="${skipped?'Click to include in run':'Click to skip'}">⏭ ${skipped?'Skipped':'Skip'}</button>
                    <button class="run-mini-btn"${skipped?' disabled':''}>Run</button>
                    <span class="s-badge sc-${st}" data-badge>${SC_ICON[st]||'○'} ${SC_LABEL[st]||'Idle'}</span>
                </div>
            </div>
            <div class="s-body">
                <div style="font-size:12px; color:#555; line-height:1.6; white-space:pre-wrap;">${esc(s.description || '상세 설명 없음')}</div>
                ${s.code ? `<div class="s-code"><pre>${esc(s.code)}</pre></div>` : ''}
            </div>
        `;
        card.querySelector('.s-header').onclick = (e) => { if(e.target.tagName !== 'BUTTON') card.classList.toggle('open'); };
        card.querySelector('[data-skip-btn]').onclick = (e) => { e.stopPropagation(); toggleSkip(id); };
        card.querySelector('.run-mini-btn').onclick = (e) => { e.stopPropagation(); runTests(s.name); };
        list.appendChild(card);
    });
    updateStatus();
}

async function runTests(id) {
    if(_isRunning) return;
    let runId = id;
    if(id === 'all' && _skipSet.size > 0) {
        const active = _scenarioList.filter(s => !_skipSet.has(s));
        if(active.length === 0) { alert('실행할 시나리오가 없습니다. 스킵 설정을 확인하세요.'); return; }
        runId = active.join(',');
    }
    await api('/api/run?s=' + runId);
    _isRunning = true; _runningID = runId;
    document.getElementById('badge-area').innerHTML = '<span style="color:var(--warning); font-weight:700; font-size:12px;">⏳ 대기 중...</span>';
}

async function stopTests() { if(confirm("현재 진행 중인 테스트를 강제 종료하시겠습니까?")) await api('/api/stop'); }

async function loadResults() {
    let data = await api('/api/results');
    // API 호출 실패 시 (정적 HTML로 직접 열었을 경우 등) 내장된 데이터 사용
    if(!data) {
        try {
            const raw = document.getElementById('reports-data').textContent;
            if(raw && raw.trim().startsWith('[')) {
                data = JSON.parse(raw);
            }
        } catch(e) {}
    }
    
    if(data) _results = data;
    const list = document.getElementById('run-list');
    if(!list) return;
    list.innerHTML = '';
    
    const filtered = _results.filter(r => {
        if(_filter === 'pass') return r.summary.failed === 0;
        if(_filter === 'fail') return r.summary.failed > 0;
        return true;
    });

    if (filtered.length === 0) {
        const msg = document.createElement('div');
        const isFiltered = _filter !== 'all';
        msg.style.cssText = 'text-align:center; padding:40px 16px; color:#aaa; font-size:13px; line-height:1.8;';
        msg.textContent = isFiltered
            ? `'${_filter === 'pass' ? '성공' : '실패'}' 결과가 없습니다`
            : '실행 이력이 없습니다';
        list.appendChild(msg);
    } else {
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
}

function showReportByID(id) {
    const r = _results.find(x => x.run_id === id);
    if(r) showReport(r, document.querySelector(`.res-item[data-runid="${id}"]`));
}

function fmtDuration(secs) {
    if (!secs) return '-';
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = Math.floor(secs % 60);
    return [h, m, s].map(v => String(v).padStart(2, '0')).join(':');
}

function showReport(r, el) {
    document.querySelectorAll('.res-item').forEach(i=>i.classList.remove('active'));
    if(el) el.classList.add('active');
    
    const det = document.getElementById('rpt-detail');
    const cards = (r.scenarios || []).map(s => {
        const duration = s.duration ? `(${fmtDuration(s.duration)})` : "";
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
            <div style="font-size:11px; color:#888; margin-top:5px;">실행 ID: ${r.run_id} | 일시: ${r.date} ${r.time} ${r.duration ? ` | 총 소요시간: ${fmtDuration(r.duration)}` : ''}</div>
        ${(r.device && (r.device.model || r.device.android)) ? `<div style="font-size:11px; color:#888; margin-top:3px;">연결 기기: ${r.device.model || '-'} | Android ${r.device.android || '-'}</div>` : ''}
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px;">
                <div style="display:flex; gap:15px;">
                    <span style="font-size:13px">전체 시나리오: <b>${r.summary.total}</b></span>
                    <span style="font-size:13px; color:var(--success)">성공: <b>${r.summary.passed}</b></span>
                    <span style="font-size:13px; color:var(--danger)">실패: <b>${r.summary.failed}</b></span>
                </div>
                <button class="btn btn-ghost" style="padding:4px 12px; font-size:12px;" onclick="toggleAllScCards(this)">▼ 전체 접기</button>
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
            if(autoScroll) requestAnimationFrame(() => p.scrollTo({ top: p.scrollHeight, behavior: 'instant' }));
        });
        // ── 시나리오 결과 실시간 파싱 ─────────────────────────
        // 형식: [INFO] ...::test_scenario_N_name PASSED / [ERROR] ...FAILED / [DEBUG] ...SKIPPED
        d.logs.forEach(l => {
            const m = l.match(/test_scenario_(\d+(?:_\d+)?)[_a-z]* (PASSED|FAILED|SKIPPED)/);
            if(!m) return;
            const id = m[1];
            const raw = m[2];
            const st = raw === 'PASSED' ? 'passed' : raw === 'SKIPPED' ? 'skipped' : 'failed';
            if(_cardStatus[id] !== st) {
                _cardStatus[id] = st;
                setCardStatus(id, st);
                // 완료된 카드에 실행 시간 기록
                if(_cardStart[id]) {
                    const secs = (Date.now() - _cardStart[id]) / 1000;
                    const card = document.querySelector(`.s-card[data-id="${id}"]`);
                    if(card) {
                        const el = card.querySelector('[data-elapsed]');
                        if(el) { el.textContent = fmtDuration(secs); el.className = 's-elapsed'; }
                    }
                }
            }
        });
        logOffset = d.total;
    }
}
function clearLogs(id) { document.getElementById(id).innerHTML = ''; }
function openImg(src) { event.stopPropagation(); const lb=document.getElementById('lb'); document.getElementById('lb-img').src=src; lb.classList.add('on'); }
async function startAppium() { await api('/api/appium/start'); }
async function stopAppium() { await api('/api/appium/stop'); }

// ── 시나리오 카드 상태 적용 ────────────────────────────────────
function setCardStatus(id, status) {
    _cardStatus[id] = status;
    const card = document.querySelector(`.s-card[data-id="${id}"]`);
    if(!card) return;
    const states = ['sc-idle','sc-running','sc-passed','sc-failed','sc-skipped','sc-done'];
    card.classList.remove(...states);
    card.classList.add('sc-' + status);
    const badge = card.querySelector('[data-badge]');
    if(badge) {
        badge.className = 's-badge sc-' + status;
        badge.textContent = (SC_ICON[status]||'○') + ' ' + (SC_LABEL[status]||status);
    }
    const el = card.querySelector('[data-elapsed]');
    if(el && status === 'running') el.className = 's-elapsed live';
    else if(el && status !== 'running') el.classList.remove('live');
}

// ── 실행 완료 후 결과 API로 카드 상태 동기화 ──────────────────
async function syncResultsToCards() {
    const data = await api('/api/results');
    if(!data || !data.length) return;
    const latest = data[0];
    if(!latest || !latest.scenarios) return;
    latest.scenarios.forEach(s => {
        // 시나리오 이름에서 번호 추출: "시나리오1_..." 또는 "Scenario 1" 패턴
        const m = (s.name || '').match(/(?:시나리오|scenario|s)\s*(\d+(?:[_-]\d+)?)/i);
        if(!m) return;
        const id = m[1].replace('-', '_');
        const st = s.status === 'PASSED' ? 'passed' : s.status === 'SKIPPED' ? 'skipped' : 'failed';
        if(_cardStatus[id] !== st) setCardStatus(id, st);
        // 결과 파일의 duration으로 경과 시간 갱신
        if(s.duration) {
            const card = document.querySelector(`.s-card[data-id="${id}"]`);
            if(card) {
                const el = card.querySelector('[data-elapsed]');
                if(el) { el.textContent = fmtDuration(s.duration); el.className = 's-elapsed'; }
            }
        }
    });
}

// ── 실행 중인 카드 경과 시간 갱신 (매 초) ─────────────────────
function tickElapsed() {
    const now = Date.now();
    document.querySelectorAll('.s-card').forEach(card => {
        const id = card.getAttribute('data-id');
        if(_cardStatus[id] !== 'running' || !_cardStart[id]) return;
        const el = card.querySelector('[data-elapsed]');
        if(el) { el.textContent = fmtDuration((now - _cardStart[id]) / 1000); el.className = 's-elapsed live'; }
    });
}

// ── 시나리오 스킵 토글 ────────────────────────────────────────
function toggleSkip(id) {
    if(_skipSet.has(id)) _skipSet.delete(id);
    else _skipSet.add(id);
    localStorage.setItem('bodoc_skip', JSON.stringify([..._skipSet]));
    applySkipUI(id);
}

function applySkipUI(id) {
    const card = document.querySelector(`.s-card[data-id="${id}"]`);
    if(!card) return;
    const skipped = _skipSet.has(id);
    card.classList.toggle('sc-user-skip', skipped);
    const skipBtn = card.querySelector('[data-skip-btn]');
    if(skipBtn) {
        skipBtn.textContent = skipped ? '⏭ Skipped' : '⏭ Skip';
        skipBtn.classList.toggle('skipped', skipped);
        skipBtn.title = skipped ? 'Click to include in run' : 'Click to skip';
    }
    const runBtn = card.querySelector('.run-mini-btn');
    if(runBtn) runBtn.disabled = skipped || _isRunning;
}

// ── 이전 결과 삭제 ────────────────────────────────────────────
function initDeleteDate() {
    const el = document.getElementById('delete-date-input');
    if (!el) return;
    const d = new Date();
    d.setDate(d.getDate() - 1);
    el.value = d.toISOString().slice(0, 10);
}

async function deleteResultsByDate() {
    const dateEl = document.getElementById('delete-date-input');
    const msgEl  = document.getElementById('delete-result-msg');
    const date   = dateEl ? dateEl.value : '';
    if (!date) { if (msgEl) { msgEl.style.color = 'var(--danger)'; msgEl.textContent = '날짜를 선택하세요.'; } return; }
    if (!confirm(`${date} 이전(포함) 결과를 모두 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.`)) return;
    if (msgEl) { msgEl.style.color = '#888'; msgEl.textContent = '삭제 중...'; }
    const r = await api(`/api/results/delete?date=${date}`, 10000);
    if (r && r.ok) {
        if (msgEl) { msgEl.style.color = 'var(--success)'; msgEl.textContent = `${r.count}개 삭제 완료`; }
        refreshDashboard();
    } else {
        if (msgEl) { msgEl.style.color = 'var(--danger)'; msgEl.textContent = `오류: ${r ? r.error : '요청 실패'}`; }
    }
}

// ── 패널 드래그 리사이즈 ──────────────────────────────────────
function initSplitResize() {
    const divider  = document.getElementById('split-divider');
    const left     = document.getElementById('split-left');
    const container = divider && divider.parentElement;
    if (!divider || !left || !container) return;

    const STORAGE_KEY = 'bodoc_split_w';
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) left.style.width = saved + 'px';

    let dragging = false, startX = 0, startW = 0;

    divider.addEventListener('mousedown', e => {
        dragging = true;
        startX = e.clientX;
        startW = left.getBoundingClientRect().width;
        divider.classList.add('dragging');
        document.body.style.cssText += 'cursor:col-resize;user-select:none;';
        e.preventDefault();
    });
    document.addEventListener('mousemove', e => {
        if (!dragging) return;
        const total = container.getBoundingClientRect().width - 14;
        const newW  = Math.max(180, Math.min(total - 180, startW + e.clientX - startX));
        left.style.width = newW + 'px';
    });
    document.addEventListener('mouseup', () => {
        if (!dragging) return;
        dragging = false;
        divider.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        localStorage.setItem(STORAGE_KEY, Math.round(left.getBoundingClientRect().width));
    });
}

function toggleAllScCards(btn) {
    const cards = document.querySelectorAll('#rpt-detail .sc-card');
    const hasOpen = [...cards].some(c => !c.classList.contains('closed'));
    cards.forEach(c => c.classList.toggle('closed', hasOpen));
    btn.textContent = hasOpen ? '▶ 전체 펼치기' : '▼ 전체 접기';
}

function init() {
    // 개별 API 호출은 독립적으로 실행 — 어느 하나가 느려도 UI 전체를 블로킹하지 않음
    api('/api/env').then(env => {
        if(env) document.getElementById('env-info').innerHTML = `Python: ${env.python}<br>Pytest: ${env.pytest}<br>Ver: 1.3.3 Analysis`;
    });
    initSplitResize();
    initDeleteDate();
    updateStatus();
    refreshDashboard();
    setInterval(pollLogs, 1000);
    setInterval(updateStatus, 3000);
    setInterval(tickElapsed, 1000);
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
            "device": {"model": "", "android": ""},
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
            "error": None,
            "step_count": 0  # 이 시나리오의 전체 스텝 수
        }

    def step(self, name, status="PASSED", screenshot=None):
        if self._current is None: return
        self._current["step_count"] += 1
        step_number = self._current["step_count"]
        # 결과 JSON의 steps에 "1️⃣ 스텝 이름" 형태로 저장
        numbered_name = f"{step_number}️⃣ {name}"
        self._current["steps"].append({"name": numbered_name, "status": status, "screenshot": screenshot})

    def end_scenario(self, status, error=None):
        if self._current is None: return
        self._current["status"] = status
        self._current["end"] = datetime.now().strftime('%H:%M:%S')
        self._current["duration"] = round(time.time() - self._current.get("start_ts", time.time()), 1)
        if error:
            self._current["error"] = str(error)[:3000]
        
        self.data["scenarios"].append(self._current)
        self.data["summary"]["total"] += 1
        if status == "PASSED": self.data["summary"]["passed"] += 1
        else: self.data["summary"]["failed"] += 1
        self._current = None

    def set_device(self, model, android):
        self.data["device"] = {"model": model, "android": android}

    def save(self):
        self.data["duration"] = round(time.time() - self._start, 1)
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
