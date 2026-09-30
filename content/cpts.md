---
title: "CPTS Countdown"
date: 2026-09-30
draft: false
---

<div class="countdown-wrap">
<div class="cd-target">December 6, 2026 &mdash; exam day.</div>
<div class="countdown-digits">
<div class="cd-cell"><div class="cd-num" id="cd-d">&ndash;&ndash;</div><div class="cd-label">days</div></div>
<div class="cd-sep">:</div>
<div class="cd-cell"><div class="cd-num" id="cd-h">&ndash;&ndash;</div><div class="cd-label">hours</div></div>
<div class="cd-sep">:</div>
<div class="cd-cell"><div class="cd-num" id="cd-m">&ndash;&ndash;</div><div class="cd-label">minutes</div></div>
<div class="cd-sep">:</div>
<div class="cd-cell"><div class="cd-num" id="cd-s">&ndash;&ndash;</div><div class="cd-label">seconds</div></div>
</div>
<div class="cd-note" id="cd-note">The date does not move.</div>
</div>

<div class="cd-about">
<div class="cd-about-title">&gt; what is CPTS_</div>
<p><strong>CPTS</strong> — Certified Penetration Testing Specialist — is Hack&nbsp;The&nbsp;Box's hands-on penetration testing certification. The exam is a <strong>10-day (240-hour)</strong> practical: a black-box simulated corporate network of roughly eight Linux and Windows machines, heavy on Active Directory. Fourteen flags are hidden in the environment; you need <strong>twelve</strong> to pass, plus a <strong>professional-grade penetration test report</strong> — the report is where plenty of candidates fail. The exam only unlocks after completing HTB Academy's 28-module Penetration Tester path.</p>
<p>That's the thing ticking down above.</p>
</div>

## Date history

Every change to this date is published here. There is nowhere to hide a moved deadline.

<div id="cd-history" class="cd-history"></div>

<script>
(function () {
  var FALLBACK_TARGET = "2026-12-06T00:00:00";
  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function renderHistory(items) {
    var el = document.getElementById("cd-history");
    el.innerHTML = items.map(function (h) {
      return '<div class="cd-hist-row"><span class="cd-hist-date">' + h.date +
        '</span><span class="cd-hist-event">' + h.event + "</span></div>";
    }).join("");
  }
  function start(targetStr, history) {
    var target = new Date(targetStr);
    renderHistory(history || []);
    function tick() {
      var ms = target - new Date();
      if (ms <= 0) {
        document.getElementById("cd-d").textContent = "00";
        document.getElementById("cd-h").textContent = "00";
        document.getElementById("cd-m").textContent = "00";
        document.getElementById("cd-s").textContent = "00";
        document.getElementById("cd-note").textContent = "Time's up. Go take the exam.";
        return;
      }
      var s = Math.floor(ms / 1000);
      document.getElementById("cd-d").textContent = Math.floor(s / 86400);
      document.getElementById("cd-h").textContent = pad(Math.floor(s / 3600) % 24);
      document.getElementById("cd-m").textContent = pad(Math.floor(s / 60) % 60);
      document.getElementById("cd-s").textContent = pad(s % 60);
    }
    tick();
    setInterval(tick, 1000);
  }
  fetch("/data/cpts-target.json")
    .then(function (r) { return r.json(); })
    .then(function (d) { start(d.target || FALLBACK_TARGET, d.history); })
    .catch(function () { start(FALLBACK_TARGET, [{date: "2026-09-30", event: "Target set: December 6, 2026 — exam start. The date does not move."}]); });
})();
</script>
