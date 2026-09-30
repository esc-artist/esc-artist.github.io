#!/usr/bin/env python3
"""Build the Study Log page from @constantinestudies stream durations.

Usage: studylog.py /tmp/streams.txt
Reads lines: "YYYYMMDD <seconds> <id> <title>", keeps the last 14 days,
writes content/study.md with inline SVG charts (hours only, no money).
"""
import sys, json, re
from datetime import date, timedelta
from collections import defaultdict

SRC = sys.argv[1]
TODAY = date(2026, 9, 30)
START = TODAY - timedelta(days=20)  # 21 days inclusive

per_day = defaultdict(float)
n_videos = 0
date_re = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})\s*$')
for line in open(SRC):
    parts = line.strip().split(None, 3)
    if len(parts) < 3:
        continue
    dur = parts[1]
    title = parts[3] if len(parts) > 3 else ""
    # attribute by the date in the stream title (his study-day convention);
    # upload_date is UTC and shifts late-night EDT streams a day forward
    m = date_re.search(title)
    if not m:
        continue
    try:
        d = date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        secs = float(dur)
    except (ValueError, IndexError):
        continue
    if secs <= 0 or not (START <= d <= TODAY):
        continue
    per_day[d.isoformat()] += secs / 3600.0
    n_videos += 1

days = [START + timedelta(days=i) for i in range(21)]
hours = [round(per_day.get(d.isoformat(), 0.0), 2) for d in days]

total = round(sum(hours), 1)
nonzero = [h for h in hours if h > 0]
avg = round(total / 21, 1)
best = max(hours) if hours else 0
best_day = days[hours.index(best)].strftime("%a %-m/%-d") if hours else "-"
streak = 0
for h in reversed(hours):
    if h > 0:
        streak += 1
    elif streak > 0:
        break

# weekly buckets (Sun-Sat)
weeks = defaultdict(float)
for d, h in zip(days, hours):
    sun = d - timedelta(days=(d.weekday() + 1) % 7)
    weeks[sun.isoformat()] += h
week_list = sorted(weeks.items())

def svg_bars(labels, values, title, w=680, h=220, color="#33ff66"):
    pad_l, pad_r, pad_t, pad_b = 44, 12, 26, 30
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    vmax = max(values) if values and max(values) > 0 else 1
    # round max up to a nice number
    import math
    vmax = math.ceil(vmax)
    bw = iw / len(values)
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">']
    parts.append(f'<style>text{{fill:#8a9a8f;font-family:monospace}}</style>')
    parts.append(f'<text x="{pad_l}" y="16" font-size="13" fill="#c9f5d6">{title}</text>')
    # gridlines at 0, half, max
    for gv in (0, vmax / 2, vmax):
        y = pad_t + ih - (gv / vmax) * ih
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" stroke="#1d3a24" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-6}" y="{y+4:.1f}" font-size="10" text-anchor="end">{gv:g}h</text>')
    for i, (lab, v) in enumerate(zip(labels, values)):
        bh = (v / vmax) * ih
        x = pad_l + i * bw + bw * 0.18
        bw2 = bw * 0.64
        y = pad_t + ih - bh
        fill = color if v > 0 else "#16241a"
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw2:.1f}" height="{max(bh,2):.1f}" rx="3" fill="{fill}" opacity="0.92"><title>{lab}: {v:.1f}h</title></rect>')
        if len(values) <= 16 or i % 2 == 0:
            parts.append(f'<text x="{x+bw2/2:.1f}" y="{h-10}" font-size="10" text-anchor="middle">{lab}</text>')
        if v > 0 and len(values) <= 16:
            parts.append(f'<text x="{x+bw2/2:.1f}" y="{y-5:.1f}" font-size="10" text-anchor="middle" fill="#c9f5d6">{v:.1f}</text>')
    parts.append('</svg>')
    return "\n".join(parts)

day_labels = [d.strftime("%-m/%-d") for d in days]
week_labels = [date.fromisoformat(s).strftime("%-m/%-d") for s, _ in week_list]
week_vals = [round(v, 1) for _, v in week_list]

daily_svg = svg_bars(day_labels, hours, "Hours per day — last 3 weeks")
weekly_svg = svg_bars(week_labels, week_vals, "Hours per week", color="#2f9e4f")

def fmt(h):
    return f"{int(h)}h{int(round((h-int(h))*60)):02d}m"

md = f"""---
title: "Study Log"
date: 2026-09-30
draft: false
---

Public study hours, for accountability. Totals come from the durations of my public study streams — hours only, no money involved.

<div class="stat-row">
<div class="stat"><span class="stat-num">{total:.1f}h</span><span class="stat-label">last 3 weeks</span></div>
<div class="stat"><span class="stat-num">{avg:.1f}h</span><span class="stat-label">avg / day</span></div>
<div class="stat"><span class="stat-num">{best:.1f}h</span><span class="stat-label">best day ({best_day})</span></div>
<div class="stat"><span class="stat-num">{streak}</span><span class="stat-label">day streak</span></div>
</div>

{daily_svg}

{weekly_svg}

Sessions are screen-recorded study streams on [YouTube @constantinestudies](https://www.youtube.com/@constantinestudies) — boring to watch, useful to log. Hours are summed from public stream durations by upload date.
"""
open("/home/hatch/workspace/esc-artist-blog/content/study.md", "w").write(md)

summary = {
    "window": [START.isoformat(), TODAY.isoformat()],
    "videos": n_videos,
    "total_hours": total,
    "per_day": {d.isoformat(): h for d, h in zip(days, hours)},
}
open("/home/hatch/workspace/esc-artist-blog/scripts/study_data.json", "w").write(json.dumps(summary, indent=1))
print(f"videos={n_videos} total={total}h avg={avg}h best={best}h({best_day}) streak={streak}d")
print("per-day:", " ".join(f"{d.strftime('%-m/%-d')}={h:.1f}h" for d, h in zip(days, hours)))
