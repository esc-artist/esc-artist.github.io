---
title: "Stats"
summary: "private training stats"
robotsNoIndex: true
---

<div class="stats-wrap">
<div class="stat-hero">
  <div class="lvl-block">
    <svg class="lvl-hex" viewBox="0 0 128 128" width="120" height="120">
  <defs>
    <clipPath id="hexclip"><polygon points="109.726,37.6 109.726,90.4 64,116.8 18.2739,90.4 18.2739,37.6 64,11.2"/></clipPath>
    <filter id="hexglow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <polygon points="115.962,34 115.962,94 64,124 12.0385,94 12.0385,34 64,4" fill="#050805" stroke="#1d3a24" stroke-width="2"/>
  <g clip-path="url(#hexclip)">
    <rect class="hexfill" x="4.0" y="107.54500000000002" width="120.0" height="3.2550000000000003"
          fill="#33ff66" opacity="0.5525"/>
  </g>
  <polygon points="115.962,34 115.962,94 64,124 12.0385,94 12.0385,34 64,4" fill="none" stroke="#33ff66" stroke-width="2"
           opacity="0.775" filter="url(#hexglow)"/>
  <text x="64.0" y="72.0" text-anchor="middle" fill="#33ff66" font-size="26"
        font-family="ui-monospace,monospace" font-weight="bold" filter="url(#hexglow)">4</text>
</svg>
    <div class="lvl-name">Lv 4 — Restless</div>
    <div class="rank-line">Rank: OSCP → CPTS</div>
  </div>
  <div style="flex:1;min-width:220px">
    <div class="pts-big"><svg viewBox="0 0 20 20" width="26" height="26" class="pts-mark">
  <rect x="4" y="4" width="12" height="12" transform="rotate(45 10 10)"
        fill="none" stroke="#33ff66" stroke-width="2"/></svg><span data-count="151.7">0</span></div>
    <div class="pts-break">from hours: 121.7<br>from blocks: 0.0<br>6h bonuses: 30.0<br>perfect days: 0.0<br>streaks: 0.0</div>
    <div class="pbar"><i data-w="4"></i></div>
    <div class="pts-break">48 points to Lv 5</div>
  </div>
</div>

<div class="tv-card">
  <div class="tv-head">TV Budget — today</div>
  <div class="tv-big">12 min</div>
  <div class="tv-sub">1.6 points yesterday × 7.5 min</div>
  <a href="#" id="tv-open" class="tv-btn" style="display:none">Open TV Control</a><span id="tv-unset"><button class="tv-btn" id="tv-set">Set Pi URL</button></span>
</div>
<script>
(function(){
  var KEY='pi_budget_url';
  var open=document.getElementById('tv-open'), unset=document.getElementById('tv-unset'),
      set=document.getElementById('tv-set');
  function render(){
    var u=localStorage.getItem(KEY);
    if(u){ open.href=u; open.style.display=''; unset.style.display='none'; }
    else { open.style.display='none'; unset.style.display=''; }
  }
  set.onclick=function(){
    var u=prompt('Pi TV app URL (e.g. http://100.x.y.z:5000):', localStorage.getItem(KEY)||'');
    if(u===null) return;
    u=u.trim();
    if(u) localStorage.setItem(KEY,u); else localStorage.removeItem(KEY);
    render();
  };
  render();
})();
</script>

<h3>Rank Path</h3>
<div class="rank-path"><div class="rank-cell" title="OSCP">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="#33ff66" fill-opacity="0.16" stroke="#33ff66" stroke-width="2.5" filter="url(#hexglow)"/>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="#33ff66" opacity="0.92" filter="url(#hexglow)"><path d="M47 12 C34 7, 20 7, 5 12 L5 13.5 C20 9, 34 9, 47 13.5 Z"/><path d="M47 15 C34 11, 22 13, 9 19 L9 20.5 C22 15, 34 13, 47 16.5 Z"/><path d="M47 18 C36 16, 26 20, 15 26 L15 27.5 C26 22, 36 18, 47 19.5 Z"/><path d="M47 11 L56 4 L52 13 Z"/><path d="M37 59 C33 51, 29 45, 33 37 C37 29, 45 29, 48 21 L52 12 L58 16 L52 23 C48 31, 41 33, 39 41 C37 49, 39 56, 37 59 Z"/><path d="M48 11 L61 16 L49 21 L46 16 Z"/></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="1">OSCP</text>
  </svg></div><div class="rank-cell" title="CPTS">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="none" stroke="#33ff66" stroke-width="2.5" stroke-dasharray="7,4" opacity="0.9" filter="url(#hexglow)"><animate attributeName="stroke-dashoffset" from="0" to="22" dur="1.6s" repeatCount="indefinite"/></polygon>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="none" stroke="#33ff66" stroke-width="2.5" opacity="0.95" filter="url(#hexglow)"><g transform="rotate(45 32 32)"><rect x="29" y="6" width="6" height="34" rx="2"/><rect x="20" y="38" width="24" height="5" rx="2"/><rect x="29" y="45" width="6" height="12" rx="3"/></g><g transform="rotate(-45 32 32)"><rect x="29" y="6" width="6" height="34" rx="2"/><rect x="20" y="38" width="24" height="5" rx="2"/><rect x="29" y="45" width="6" height="12" rx="3"/></g></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="0.95">CPTS</text>
  </svg></div><div class="rank-cell" title="CAPE">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"/>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"><rect x="12" y="14" width="18" height="16" rx="1"/><rect x="34" y="14" width="18" height="16" rx="1"/><rect x="12" y="34" width="18" height="16" rx="1"/><rect x="34" y="34" width="18" height="16" rx="1"/></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="0.4">CAPE</text>
  </svg></div><div class="rank-cell" title="OSEP">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"/>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"><path d="M8 26 C8 22 12 20 16 20 L48 20 C52 20 56 22 56 26 L56 34 C56 38 52 40 48 40 L16 40 C12 40 8 38 8 34 Z"/><ellipse cx="22" cy="30" rx="6" ry="4" fill="#050805"/><ellipse cx="42" cy="30" rx="6" ry="4" fill="#050805"/></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="0.4">OSEP</text>
  </svg></div><div class="rank-cell" title="OSWE">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"/>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"><ellipse cx="32" cy="36" rx="10" ry="12"/><circle cx="32" cy="22" r="6"/><path d="M24 28 L12 18 L8 24 M24 34 L10 30 L8 38 M24 42 L10 46 L12 54 M26 48 L18 58 M40 28 L52 18 L56 24 M40 34 L54 30 L56 38 M40 42 L54 46 L52 54 M38 48 L46 58" fill="none" stroke-width="3" stroke-linecap="round"/></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="0.4">OSWE</text>
  </svg></div><div class="rank-cell" title="OSED">
  <svg viewBox="0 0 92 114" width="84" height="106">
    <polygon points="82.3731,25 82.3731,67 46,88 9.62693,67 9.62693,25 46,4" fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"/>
    <g transform="translate(22.0 22.0) scale(0.75)"><g fill="none" stroke="#33ff66" stroke-width="2" opacity="0.3"><g transform="rotate(45 32 38)"><rect x="10" y="35" width="44" height="7" rx="3.5"/><circle cx="12" cy="38" r="5"/><circle cx="52" cy="38" r="5"/></g><g transform="rotate(-45 32 38)"><rect x="10" y="35" width="44" height="7" rx="3.5"/><circle cx="12" cy="38" r="5"/><circle cx="52" cy="38" r="5"/></g><circle cx="32" cy="26" r="13"/><rect x="24" y="32" width="16" height="10" rx="3"/><circle cx="27" cy="25" r="4" fill="#050805"/><circle cx="37" cy="25" r="4" fill="#050805"/></g></g>
    <text x="46.0" y="104.0" text-anchor="middle" fill="#33ff66"
          font-size="11" font-family="ui-monospace,monospace" opacity="0.4">OSED</text>
  </svg></div></div>

<div class="stat-cards"><div class="stat-card"><div class="v">121.7</div><div class="k">total hours</div></div><div class="stat-card"><div class="v">10</div><div class="k">6h+ days</div></div><div class="stat-card"><div class="v">0%</div><div class="k">blocks hit</div></div><div class="stat-card"><div class="v">0</div><div class="k">6h streak</div></div><div class="stat-card"><div class="v">2</div><div class="k">longest 6h streak</div></div></div>

<h3>Heatmap</h3>
<div class="heat-readout" id="heatread">hover or tap a day</div><svg viewBox="0 0 224 98" class="heatmap" id="heatmap"><rect x="0" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="0" data-date="2026-06-15" data-hours="0.0"/><rect x="0" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="1" data-date="2026-06-16" data-hours="0.0"/><rect x="0" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="2" data-date="2026-06-17" data-hours="0.0"/><rect x="0" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="3" data-date="2026-06-18" data-hours="0.0"/><rect x="0" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="4" data-date="2026-06-19" data-hours="0.0"/><rect x="0" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="5" data-date="2026-06-20" data-hours="0.0"/><rect x="0" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="0" data-d="6" data-date="2026-06-21" data-hours="0.0"/><rect x="14" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="0" data-date="2026-06-22" data-hours="0.0"/><rect x="14" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="1" data-date="2026-06-23" data-hours="0.0"/><rect x="14" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="2" data-date="2026-06-24" data-hours="0.0"/><rect x="14" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="3" data-date="2026-06-25" data-hours="0.0"/><rect x="14" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="4" data-date="2026-06-26" data-hours="0.0"/><rect x="14" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="5" data-date="2026-06-27" data-hours="0.0"/><rect x="14" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="1" data-d="6" data-date="2026-06-28" data-hours="0.0"/><rect x="28" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="0" data-date="2026-06-29" data-hours="0.0"/><rect x="28" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="1" data-date="2026-06-30" data-hours="0.0"/><rect x="28" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="2" data-date="2026-07-01" data-hours="0.0"/><rect x="28" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="3" data-date="2026-07-02" data-hours="0.0"/><rect x="28" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="4" data-date="2026-07-03" data-hours="0.0"/><rect x="28" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="5" data-date="2026-07-04" data-hours="0.0"/><rect x="28" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="2" data-d="6" data-date="2026-07-05" data-hours="0.0"/><rect x="42" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="0" data-date="2026-07-06" data-hours="0.0"/><rect x="42" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="1" data-date="2026-07-07" data-hours="0.0"/><rect x="42" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="2" data-date="2026-07-08" data-hours="0.0"/><rect x="42" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="3" data-date="2026-07-09" data-hours="0.0"/><rect x="42" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="4" data-date="2026-07-10" data-hours="0.0"/><rect x="42" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="5" data-date="2026-07-11" data-hours="0.0"/><rect x="42" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="3" data-d="6" data-date="2026-07-12" data-hours="0.0"/><rect x="56" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="0" data-date="2026-07-13" data-hours="0.0"/><rect x="56" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="1" data-date="2026-07-14" data-hours="0.0"/><rect x="56" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="2" data-date="2026-07-15" data-hours="0.0"/><rect x="56" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="3" data-date="2026-07-16" data-hours="0.0"/><rect x="56" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="4" data-date="2026-07-17" data-hours="0.0"/><rect x="56" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="5" data-date="2026-07-18" data-hours="0.0"/><rect x="56" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="4" data-d="6" data-date="2026-07-19" data-hours="0.0"/><rect x="70" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="0" data-date="2026-07-20" data-hours="0.0"/><rect x="70" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="1" data-date="2026-07-21" data-hours="0.0"/><rect x="70" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="2" data-date="2026-07-22" data-hours="0.0"/><rect x="70" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="3" data-date="2026-07-23" data-hours="0.0"/><rect x="70" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="4" data-date="2026-07-24" data-hours="0.0"/><rect x="70" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="5" data-date="2026-07-25" data-hours="0.0"/><rect x="70" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="5" data-d="6" data-date="2026-07-26" data-hours="0.0"/><rect x="84" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="0" data-date="2026-07-27" data-hours="0.0"/><rect x="84" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="1" data-date="2026-07-28" data-hours="0.0"/><rect x="84" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="2" data-date="2026-07-29" data-hours="0.0"/><rect x="84" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="3" data-date="2026-07-30" data-hours="0.0"/><rect x="84" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="4" data-date="2026-07-31" data-hours="0.0"/><rect x="84" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="5" data-date="2026-08-01" data-hours="0.0"/><rect x="84" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="6" data-d="6" data-date="2026-08-02" data-hours="0.0"/><rect x="98" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="0" data-date="2026-08-03" data-hours="0.0"/><rect x="98" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="1" data-date="2026-08-04" data-hours="0.0"/><rect x="98" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="2" data-date="2026-08-05" data-hours="0.0"/><rect x="98" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="3" data-date="2026-08-06" data-hours="0.0"/><rect x="98" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="4" data-date="2026-08-07" data-hours="0.0"/><rect x="98" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="5" data-date="2026-08-08" data-hours="0.0"/><rect x="98" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="7" data-d="6" data-date="2026-08-09" data-hours="0.0"/><rect x="112" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="0" data-date="2026-08-10" data-hours="0.0"/><rect x="112" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="1" data-date="2026-08-11" data-hours="0.0"/><rect x="112" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="2" data-date="2026-08-12" data-hours="0.0"/><rect x="112" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="3" data-date="2026-08-13" data-hours="0.0"/><rect x="112" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="4" data-date="2026-08-14" data-hours="0.0"/><rect x="112" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="5" data-date="2026-08-15" data-hours="0.0"/><rect x="112" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="8" data-d="6" data-date="2026-08-16" data-hours="0.0"/><rect x="126" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="0" data-date="2026-08-17" data-hours="0.0"/><rect x="126" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="1" data-date="2026-08-18" data-hours="0.0"/><rect x="126" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="2" data-date="2026-08-19" data-hours="0.0"/><rect x="126" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="3" data-date="2026-08-20" data-hours="0.0"/><rect x="126" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="4" data-date="2026-08-21" data-hours="0.0"/><rect x="126" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="5" data-date="2026-08-22" data-hours="0.0"/><rect x="126" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="9" data-d="6" data-date="2026-08-23" data-hours="0.0"/><rect x="140" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="0" data-date="2026-08-24" data-hours="0.0"/><rect x="140" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="1" data-date="2026-08-25" data-hours="0.0"/><rect x="140" y="28" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="2" data-date="2026-08-26" data-hours="0.0"/><rect x="140" y="42" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="3" data-date="2026-08-27" data-hours="0.0"/><rect x="140" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="4" data-date="2026-08-28" data-hours="0.0"/><rect x="140" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="5" data-date="2026-08-29" data-hours="0.0"/><rect x="140" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="10" data-d="6" data-date="2026-08-30" data-hours="0.0"/><rect x="154" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="11" data-d="0" data-date="2026-08-31" data-hours="0.0"/><rect x="154" y="14" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="11" data-d="1" data-date="2026-09-01" data-hours="0.0"/><rect x="154" y="28" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="11" data-d="2" data-date="2026-09-02" data-hours="0.9"/><rect x="154" y="42" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="11" data-d="3" data-date="2026-09-03" data-hours="7.9"/><rect x="154" y="56" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="11" data-d="4" data-date="2026-09-04" data-hours="7.2"/><rect x="154" y="70" width="11" height="11" rx="2" fill="#1f7a33" class="hcell" data-w="11" data-d="5" data-date="2026-09-05" data-hours="3.1"/><rect x="154" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="11" data-d="6" data-date="2026-09-06" data-hours="0.0"/><rect x="168" y="0" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="12" data-d="0" data-date="2026-09-07" data-hours="1.9"/><rect x="168" y="14" width="11" height="11" rx="2" fill="#2fbf4f" class="hcell" data-w="12" data-d="1" data-date="2026-09-08" data-hours="4.3"/><rect x="168" y="28" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="12" data-d="2" data-date="2026-09-09" data-hours="8.1"/><rect x="168" y="42" width="11" height="11" rx="2" fill="#2fbf4f" class="hcell" data-w="12" data-d="3" data-date="2026-09-10" data-hours="5.3"/><rect x="168" y="56" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="12" data-d="4" data-date="2026-09-11" data-hours="8.8"/><rect x="168" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="12" data-d="5" data-date="2026-09-12" data-hours="0.0"/><rect x="168" y="84" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="12" data-d="6" data-date="2026-09-13" data-hours="0.0"/><rect x="182" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="13" data-d="0" data-date="2026-09-14" data-hours="0.0"/><rect x="182" y="14" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="13" data-d="1" data-date="2026-09-15" data-hours="10.9"/><rect x="182" y="28" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="13" data-d="2" data-date="2026-09-16" data-hours="1.6"/><rect x="182" y="42" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="13" data-d="3" data-date="2026-09-17" data-hours="6.9"/><rect x="182" y="56" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="13" data-d="4" data-date="2026-09-18" data-hours="8.3"/><rect x="182" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="13" data-d="5" data-date="2026-09-19" data-hours="0.0"/><rect x="182" y="84" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="13" data-d="6" data-date="2026-09-20" data-hours="1.3"/><rect x="196" y="0" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="14" data-d="0" data-date="2026-09-21" data-hours="0.0"/><rect x="196" y="14" width="11" height="11" rx="2" fill="#1f7a33" class="hcell" data-w="14" data-d="1" data-date="2026-09-22" data-hours="3.7"/><rect x="196" y="28" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="14" data-d="2" data-date="2026-09-23" data-hours="11.9"/><rect x="196" y="42" width="11" height="11" rx="2" fill="#1f7a33" class="hcell" data-w="14" data-d="3" data-date="2026-09-24" data-hours="3.8"/><rect x="196" y="56" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="14" data-d="4" data-date="2026-09-25" data-hours="0.7"/><rect x="196" y="70" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="14" data-d="5" data-date="2026-09-26" data-hours="0.0"/><rect x="196" y="84" width="11" height="11" rx="2" fill="#2fbf4f" class="hcell" data-w="14" data-d="6" data-date="2026-09-27" data-hours="4.2"/><rect x="210" y="0" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="15" data-d="0" data-date="2026-09-28" data-hours="7.0"/><rect x="210" y="14" width="11" height="11" rx="2" fill="#33ff66" class="hcell" data-w="15" data-d="1" data-date="2026-09-29" data-hours="9.9"/><rect x="210" y="28" width="11" height="11" rx="2" fill="#1f7a33" class="hcell" data-w="15" data-d="2" data-date="2026-09-30" data-hours="2.1"/><rect x="210" y="42" width="11" height="11" rx="2" fill="#14401f" class="hcell" data-w="15" data-d="3" data-date="2026-10-01" data-hours="1.6"/><rect x="210" y="56" width="11" height="11" rx="2" fill="#0d140e" class="hcell" data-w="15" data-d="4" data-date="2026-10-02" data-hours="0.0"/></svg>

<h3>Badges</h3>
<div class="badge-grid"><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M22 12 L50 32 L22 52 Z"/></g></svg><div class="n">First Stream</div><div class="d">First tracked study stream</div><div class=d>2026-09-02</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M32 6 C32 6 14 30 14 42 a18 18 0 0 0 36 0 C50 30 32 6 32 6 Z"/></g></svg><div class="n">First Blood</div><div class="d">First 6-hour day</div><div class=d>2026-09-03</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M12 34 L26 48 L52 18" fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></svg><div class="n">First Block</div><div class="d">First schedule block hit</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M32 6 L37 27 L58 32 L37 37 L32 58 L27 37 L6 32 L27 27 Z"/></g></svg><div class="n">Warming Up</div><div class="d">10 total hours</div><div class=d>2026-09-04</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M32 6 L37 27 L58 32 L37 37 L32 58 L27 37 L6 32 L27 27 Z"/></g></svg><div class="n">Committed</div><div class="d">25 total hours</div><div class=d>2026-09-08</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/></g></svg><div class="n">Half Century</div><div class="d">50 total hours</div><div class=d>2026-09-15</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/></g></svg><div class="n">Centurion</div><div class="d">100 total hours</div><div class=d>2026-09-27</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/></g></svg><div class="n">Centurion II</div><div class="d">250 total hours</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/></g></svg><div class="n">Centurion III</div><div class="d">500 total hours</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/></g></svg><div class="n">Centurion IV</div><div class="d">1000 total hours</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M36 4 L14 36 L28 36 L26 60 L50 26 L36 26 Z"/></g></svg><div class="n">Overtime</div><div class="d">8+ hours in a day</div><div class=d>2026-09-09</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M16 6 L16 58 M16 10 L50 10 L43 20 L50 30 L16 30 Z"/></g></svg><div class="n">Marathon</div><div class="d">10+ hours in a day</div><div class=d>2026-09-15</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M10 44 L14 22 L24 34 L32 16 L40 34 L50 22 L54 44 Z M10 48 L54 48 L54 52 L10 52 Z"/></g></svg><div class="n">Ultra</div><div class="d">12+ hours in a day</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/></g></svg><div class="n">Grinder</div><div class="d">5 six-hour days</div><div class=d>2026-09-15</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/></g></svg><div class="n">Grinder II</div><div class="d">10 six-hour days</div><div class=d>2026-09-29</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/></g></svg><div class="n">Grinder III</div><div class="d">25 six-hour days</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/></g></svg><div class="n">Grinder IV</div><div class="d">50 six-hour days</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 8 L39 25 L57 25 L42 36 L47 54 L32 43 L17 54 L22 36 L7 25 L25 25 Z"/></g></svg><div class="n">Hat Trick</div><div class="d">3 straight 6-hour days</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/></g></svg><div class="n">Week Clear</div><div class="d">7 straight 6-hour days</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><rect x="12" y="14" width="40" height="38" rx="3" fill="none" stroke-width="5"/><path d="M12 24 L52 24" stroke-width="5"/><path d="M22 8 L22 18 M42 8 L42 18" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Week Straight</div><div class="d">7 days straight studying</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><rect x="12" y="14" width="40" height="38" rx="3" fill="none" stroke-width="5"/><path d="M12 24 L52 24" stroke-width="5"/><path d="M22 8 L22 18 M42 8 L42 18" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Fortnight</div><div class="d">14 days straight studying</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><rect x="12" y="14" width="40" height="38" rx="3" fill="none" stroke-width="5"/><path d="M12 24 L52 24" stroke-width="5"/><path d="M22 8 L22 18 M42 8 L42 18" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Month Straight</div><div class="d">30 days straight studying</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 8 L39 25 L57 25 L42 36 L47 54 L32 43 L17 54 L22 36 L7 25 L25 25 Z"/></g></svg><div class="n">Perfect Day</div><div class="d">Every block hit</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 8 L39 25 L57 25 L42 36 L47 54 L32 43 L17 54 L22 36 L7 25 L25 25 Z"/></g></svg><div class="n">Perfectionist</div><div class="d">5 perfect days</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M10 44 L14 22 L24 34 L32 16 L40 34 L50 22 L54 44 Z M10 48 L54 48 L54 52 L10 52 Z"/></g></svg><div class="n">Perfect Week</div><div class="d">Every block hit, 7 days straight</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="32" r="20" fill="none" stroke-width="5"/><circle cx="32" cy="32" r="11" fill="none" stroke-width="4"/><circle cx="32" cy="32" r="4"/></g></svg><div class="n">Sharpshooter</div><div class="d">10 blocks hit</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="32" r="20" fill="none" stroke-width="5"/><circle cx="32" cy="32" r="11" fill="none" stroke-width="4"/><circle cx="32" cy="32" r="4"/></g></svg><div class="n">Sharpshooter II</div><div class="d">25 blocks hit</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><circle cx="32" cy="32" r="20" fill="none" stroke-width="5"/><circle cx="32" cy="32" r="11" fill="none" stroke-width="4"/><circle cx="32" cy="32" r="4"/></g></svg><div class="n">Sharpshooter III</div><div class="d">50 blocks hit</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M42 36 A20 20 0 1 1 28 8 A16 16 0 1 0 42 36 Z"/></g></svg><div class="n">Night Owl</div><div class="d">Stream started between midnight and 5 AM</div><div class=d>2026-10-01</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M14 44 a18 18 0 0 1 36 0 Z"/><path d="M32 6 L32 14 M12 18 L18 24 M52 18 L46 24 M6 44 L58 44" stroke-width="4" stroke-linecap="round"/></g></svg><div class="n">Early Bird</div><div class="d">Stream started between 5 and 7 AM</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M10 44 a22 22 0 0 1 44 0 Z"/><path d="M32 44 L48 26" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Halfway There</div><div class="d">50% of current exam's estimated hours</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M10 44 a22 22 0 0 1 44 0 Z"/><path d="M32 44 L48 26" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Three-Quarter</div><div class="d">75% of current exam's estimated hours</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M10 44 a22 22 0 0 1 44 0 Z"/><path d="M32 44 L48 26" stroke-width="5" stroke-linecap="round"/></g></svg><div class="n">Exam Ready</div><div class="d">100% of current exam's estimated hours</div></div><div class="badge-cell"><svg viewBox="0 0 64 64" width="64" height="64" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#33ff66" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="#33ff66" stroke="#33ff66"><path d="M52 32 a20 20 0 1 1 -6 -14" fill="none" stroke-width="6"/><path d="M46 6 L48 20 L34 16 Z"/></g></svg><div class="n">Comeback</div><div class="d">6-hour day right after a zero day</div><div class=d>2026-09-15</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M32 8 L39 25 L57 25 L42 36 L47 54 L32 43 L17 54 L22 36 L7 25 L25 25 Z"/></g></svg><div class="n">Weekend Warrior</div><div class="d">Studied Saturday and Sunday</div></div><div class="badge-cell locked"><svg viewBox="0 0 64 64" width="64" height="64" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="#1d3a24" stroke-width="2"/>
  <g fill="#0d140e" stroke="#1d3a24"><path d="M12 34 L26 48 L52 18" fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></g></svg><div class="n">No Zero Week</div><div class="d">7 days straight, none zero</div></div></div>

<div class="rewards">
<h3>Rewards — locked</h3>
<p>Points are being banked. The store opens when the hardware exists —
a dispenser, a filter, whatever the privilege mechanism ends up being.
Exchange rates get set then; the ledger is already honest.</p>
</div>

<p style="opacity:.5;font-size:.85em"><a href="/stats-rules/">How points, levels, and ranks work</a></p>
</div>

<style>
.stats-wrap{max-width:860px;margin:0 auto}
.stat-hero{display:flex;gap:2rem;align-items:center;flex-wrap:wrap;
  background:#050805;border:1px solid #1d3a24;border-radius:12px;padding:1.5rem 2rem;margin:1.5rem 0;
  box-shadow:0 0 30px rgba(51,255,102,.07)}
.lvl-block{text-align:center}
.lvl-name{color:#33ff66;font-family:ui-monospace,Menlo,monospace;font-size:1.1rem;margin-top:.4rem}
.rank-line{color:#8aa392;font-size:.85rem;letter-spacing:.15em;text-transform:uppercase}
.pts-big{font-size:2.6rem;color:#33ff66;font-family:ui-monospace,Menlo,monospace;
  text-shadow:0 0 14px rgba(51,255,102,.4);display:flex;align-items:center;gap:.5rem}
.pts-break{font-size:.85rem;color:#8aa392;margin-top:.4rem;line-height:1.7}
.pbar{height:10px;background:#0d140e;border:1px solid #1d3a24;border-radius:6px;overflow:hidden;margin-top:.6rem}
.pbar>i{display:block;height:100%;width:0;background:linear-gradient(90deg,#1f7a33,#33ff66);
  box-shadow:0 0 12px rgba(51,255,102,.6);transition:width 1.4s cubic-bezier(.2,.8,.2,1)}
.stat-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:.8rem;margin:1.5rem 0}
.stat-card{background:#050805;border:1px solid #1d3a24;border-radius:10px;padding:.9rem 1rem;text-align:center}
.stat-card .v{font-size:1.5rem;color:#33ff66;font-family:ui-monospace,monospace}
.stat-card .k{font-size:.75rem;color:#8aa392;letter-spacing:.08em;text-transform:uppercase;margin-top:.2rem}
.heatmap{width:100%;height:auto;margin:1rem 0}
.hcell{transform-box:fill-box;transform-origin:center;transition:transform .18s ease;cursor:pointer}
.heat-readout{font-family:ui-monospace,Menlo,monospace;color:#33ff66;font-size:.9rem;
  min-height:1.4em;margin-bottom:.2rem;text-shadow:0 0 8px rgba(51,255,102,.35)}
.badge-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:1rem;margin:1.5rem 0}
.badge-cell{text-align:center;opacity:0;animation:fadeup .5s ease forwards}
.badge-cell .n{font-size:.8rem;color:#33ff66;margin-top:.3rem}
.badge-cell .d{font-size:.7rem;color:#8aa392}
.badge-cell.locked .n{color:#4a5a4e}
.badge.locked{opacity:.55}
.badge.earned{animation:badglow 2.6s ease-in-out infinite}
@keyframes badglow{0%,100%{filter:drop-shadow(0 0 3px rgba(51,255,102,.5))}
  50%{filter:drop-shadow(0 0 10px rgba(51,255,102,.9))}}
@keyframes fadeup{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.hexfill{transition:height 1.4s cubic-bezier(.2,.8,.2,1), y 1.4s cubic-bezier(.2,.8,.2,1)}
.rewards{background:#050805;border:1px dashed #1d3a24;border-radius:10px;padding:1.2rem 1.5rem;
  color:#8aa392;margin:1.5rem 0}
.rewards h3{color:#4a5a4e;letter-spacing:.15em;font-size:.85rem;text-transform:uppercase}
.rank-path{display:flex;gap:.4rem;flex-wrap:wrap;justify-content:center;margin:1rem 0 1.5rem}
.rank-cell{text-align:center}
.rank-cell.next svg{animation:rankpulse 2.2s ease-in-out infinite}
@keyframes rankpulse{0%,100%{filter:drop-shadow(0 0 2px rgba(51,255,102,.4))}
  50%{filter:drop-shadow(0 0 9px rgba(51,255,102,.85))}}
.tv-card{background:#050805;border:1px solid #1d3a24;border-radius:12px;padding:1.2rem 1.5rem;
  margin:1.5rem 0;text-align:center;box-shadow:0 0 30px rgba(51,255,102,.07)}
.tv-head{color:#8aa392;font-size:.8rem;letter-spacing:.15em;text-transform:uppercase}
.tv-big{font-size:2.2rem;color:#33ff66;font-family:ui-monospace,Menlo,monospace;
  text-shadow:0 0 14px rgba(51,255,102,.4);margin:.3rem 0}
.tv-sub{font-size:.8rem;color:#8aa392;margin-bottom:.8rem}
.tv-btn{display:inline-block;padding:.5rem 1.2rem;border:1px solid #33ff66;border-radius:8px;
  color:#33ff66;text-decoration:none;font-family:ui-monospace,monospace;font-size:.9rem;
  transition:all .2s}
.tv-btn:hover{background:rgba(51,255,102,.12);box-shadow:0 0 12px rgba(51,255,102,.4)}
.tv-btn.disabled{opacity:.4;cursor:not-allowed;border-color:#4a5a4e;color:#4a5a4e}
</style>
<script>
document.querySelectorAll('.pbar>i').forEach(el=>{
  requestAnimationFrame(()=>{el.style.width=el.dataset.w+'%'});
});
document.querySelectorAll('[data-count]').forEach(el=>{
  const target=parseFloat(el.dataset.count), t0=performance.now(), dur=1400;
  const step=t=>{
    const p=Math.min(1,(t-t0)/dur), e=1-Math.pow(1-p,3);
    el.textContent=(target*e).toFixed(target<10?1:0);
    if(p<1)requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
});
document.querySelectorAll('.badge-cell').forEach((el,i)=>{
  el.style.animationDelay=(i*0.06)+'s';
});
// heatmap ripple + click readout
(function(){
  const hm=document.getElementById('heatmap'), read=document.getElementById('heatread');
  if(!hm||!read)return;
  const cells=[...hm.querySelectorAll('.hcell')];
  const byPos={};
  cells.forEach(c=>{byPos[c.dataset.w+','+c.dataset.d]=c;});
  function ripple(w,d){
    const W=+w,D=+d;
    cells.forEach(c=>{
      const dx=Math.abs(+c.dataset.w-W), dy=Math.abs(+c.dataset.d-D);
      const dist=Math.max(dx,dy);
      c.style.transform=dist===0?'scale(1.6)':dist===1?'scale(1.15)':dist===2?'scale(1.05)':'';
    });
  }
  function clear(){cells.forEach(c=>{c.style.transform='';});}
  function label(c){read.textContent=c.dataset.date+': '+c.dataset.hours+'h';}
  cells.forEach(c=>{
    c.addEventListener('mouseenter',()=>{ripple(c.dataset.w,c.dataset.d);label(c);});
    c.addEventListener('click',()=>{ripple(c.dataset.w,c.dataset.d);label(c);});
  });
  hm.addEventListener('mouseleave',()=>{clear();read.textContent='hover or tap a day';});
})();
</script>
