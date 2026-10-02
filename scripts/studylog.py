#!/usr/bin/env python3
"""Study Log page builder for esc-artist.github.io/study/.

Master store: scripts/study_videos.json  {video_id: {date, secs, title}}
  date = stream-title date (Constantine's study-day convention); falls back
  to release_date (actual broadcast date) when untitled.

  --fetch : pull newest 60 streams via yt-dlp, merge into master store
  --build : aggregate master store -> content/study.md (inline SVG charts)

Hours only. Never mention money anywhere in the output.
"""
import sys, json, re, subprocess
from datetime import date, timedelta
from collections import defaultdict

HOME = "/home/hatch/workspace/esc-artist-blog"
STORE = f"{HOME}/scripts/study_videos.json"
TITLE_RE = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})\s*$')
START = date(2026, 8, 30)


def pick_date(upload_dstr, title):
    m = TITLE_RE.search(title or "")
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
        except ValueError:
            pass
    if upload_dstr and upload_dstr != "NA" and len(upload_dstr) == 8:
        try:
            return date(int(upload_dstr[:4]), int(upload_dstr[4:6]),
                        int(upload_dstr[6:8])).isoformat()
        except ValueError:
            pass
    return None


def load_store():
    try:
        return json.load(open(STORE))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_store(vids):
    json.dump(vids, open(STORE, "w"), indent=1, sort_keys=True)


def merge_tsv(path, vids):
    """Merge a yt-dlp --print '%(release_date)s %(duration)s %(id)s %(title)s' file."""
    added = 0
    for line in open(path):
        parts = line.strip().split(None, 3)
        if len(parts) < 3:
            continue
        udstr, dur, vid = parts[0], parts[1], parts[2]
        title = parts[3] if len(parts) > 3 else ""
        try:
            secs = float(dur)
        except ValueError:
            continue
        if secs <= 0:
            continue
        d = pick_date(udstr, title)
        if not d:
            continue
        if vid not in vids:
            added += 1
        vids[vid] = {"date": d, "secs": secs, "title": title}
    return added


def do_fetch():
    vids = load_store()
    out = subprocess.run(
        ["yt-dlp", "-i", "--playlist-end", "60",
         "--print", "%(release_date)s %(duration)s %(id)s %(title)s",
         "--skip-download",
         "https://www.youtube.com/@constantinestudies/streams"],
        capture_output=True, text=True, timeout=1200)
    added = 0
    for line in out.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 3:
            continue
        udstr, dur, vid = parts[0], parts[1], parts[2]
        title = parts[3] if len(parts) > 3 else ""
        try:
            secs = float(dur)
        except ValueError:
            continue
        if secs <= 0:
            continue
        d = pick_date(udstr, title)
        if not d:
            continue
        if vid not in vids:
            added += 1
        vids[vid] = {"date": d, "secs": secs, "title": title}
    save_store(vids)
    print(f"fetch: {len(vids)} videos in store, {added} new")
    if out.returncode != 0:
        print("yt-dlp stderr tail:", out.stderr[-500:])


def svg_bars(labels, values, title, w=680, h=220, color="#33ff66", target=None):
    import math
    pad_l, pad_r, pad_t, pad_b = 44, 12, 26, 30
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    vmax = math.ceil(max(values)) if values and max(values) > 0 else 1
    if target is not None and target > vmax:
        vmax = math.ceil(target)
    bw = iw / len(values)
    p = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">']
    p.append('<style>text{fill:#8a9a8f;font-family:monospace}</style>')
    p.append(f'<text x="{pad_l}" y="16" font-size="13" fill="#c9f5d6">{title}</text>')
    for gv in (0, vmax / 2, vmax):
        y = pad_t + ih - (gv / vmax) * ih
        p.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" stroke="#1d3a24" stroke-width="1"/>')
        p.append(f'<text x="{pad_l-6}" y="{y+4:.1f}" font-size="10" text-anchor="end">{gv:g}h</text>')
    step = 1 if len(values) <= 16 else 2
    for i, (lab, v) in enumerate(zip(labels, values)):
        bh = (v / vmax) * ih
        x = pad_l + i * bw + bw * 0.18
        bw2 = bw * 0.64
        y = pad_t + ih - bh
        fill = color if v > 0 else "#16241a"
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw2:.1f}" height="{max(bh,2):.1f}" rx="3" fill="{fill}" opacity="0.92"><title>{lab}: {v:.1f}h</title></rect>')
        if i % step == 0:
            p.append(f'<text x="{x+bw2/2:.1f}" y="{h-10}" font-size="10" text-anchor="middle">{lab}</text>')
        if v > 0 and len(values) <= 24:
            p.append(f'<text x="{x+bw2/2:.1f}" y="{y-5:.1f}" font-size="10" text-anchor="middle" fill="#c9f5d6">{v:.1f}</text>')
    if target is not None:
        y = pad_t + ih - (target / vmax) * ih
        p.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" stroke="#e5484d" stroke-width="1.5" stroke-dasharray="6,4"/>')
        p.append(f'<text x="{w-pad_r}" y="{y-6:.1f}" font-size="10" text-anchor="end" fill="#e5484d">{target:g}h target</text>')
    p.append('</svg>')
    return "\n".join(p)


def load_summary():
    """Editorial summary written by Migi from the numbers (strictly public
    data only — never anything from chat). Refreshed by the Sunday job."""
    try:
        with open(f"{HOME}/static/data/study/_summary.md") as f:
            return f.read().strip()
    except OSError:
        return ""


def do_build():
    vids = load_store()
    today = date.today()
    ndays = (today - START).days + 1
    days = [START + timedelta(days=i) for i in range(ndays)]
    per_day = defaultdict(float)
    for v in vids.values():
        try:
            d = date.fromisoformat(v["date"])
        except (ValueError, KeyError):
            continue
        if START <= d <= today:
            per_day[d.isoformat()] += v["secs"] / 3600.0
    hours = [round(per_day.get(d.isoformat(), 0.0), 2) for d in days]

    total = round(sum(hours), 1)
    avg = round(total / ndays, 1)
    best = max(hours)
    best_day = days[hours.index(best)].strftime("%a %-m/%-d")
    streak = 0
    for h in reversed(hours):
        if h > 0:
            streak += 1
        elif streak > 0:
            break

    # daily chart: cap at last 45 days so bars stay readable
    ddays, dhours = days, hours
    dtitle = "Hours per day — since Aug 30"
    if len(days) > 45:
        ddays, dhours = days[-45:], hours[-45:]
        dtitle = "Hours per day — last 45 days"
    day_labels = [d.strftime("%-m/%-d") for d in ddays]
    daily_svg = svg_bars(day_labels, dhours, dtitle, target=6)

    weeks = defaultdict(float)
    for d, h in zip(days, hours):
        sun = d - timedelta(days=(d.weekday() + 1) % 7)
        weeks[sun.isoformat()] += h
    week_list = sorted(weeks.items())
    week_labels = [date.fromisoformat(s).strftime("%-m/%-d") for s, _ in week_list]
    weekly_svg = svg_bars(week_labels, [round(v, 1) for _, v in week_list],
                           "Hours per week (42h = 6h/day)", color="#2f9e4f",
                           target=42)

    hit6 = sum(1 for h in hours if h >= 6 - 1e-9)

    md = f"""---
title: "Study Log"
date: {today.isoformat()}
draft: false
---

{load_summary()}

Public study hours, for accountability. Totals come from the durations of my public study streams.

<div class="stat-row">
<div class="stat"><span class="stat-num">{total:.1f}h</span><span class="stat-label">since Aug 30</span></div>
<div class="stat"><span class="stat-num">{avg:.1f}h</span><span class="stat-label">avg / day (target 6h)</span></div>
<div class="stat"><span class="stat-num">{best:.1f}h</span><span class="stat-label">best day ({best_day})</span></div>
<div class="stat"><span class="stat-num">{streak}</span><span class="stat-label">day streak</span></div>
<div class="stat"><span class="stat-num">{hit6}/{ndays}</span><span class="stat-label">days ≥ 6h</span></div>
</div>

{daily_svg}

{weekly_svg}

Sessions are screen-recorded study streams on [YouTube @constantinestudies](https://www.youtube.com/@constantinestudies) — boring to watch, useful to log. Hours are summed from public stream durations.

Whether I studied *when I said I would* is tracked separately on the [Schedule](/schedule/) page.

<span style="opacity:.35;font-size:.8em">[stats](/stats/)</span>
"""
    open(f"{HOME}/content/study.md", "w").write(md)
    print(f"build: {len(vids)} videos, {ndays} days, total={total}h avg={avg}h best={best}h({best_day}) streak={streak}d")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        do_fetch()
    if "--build" in sys.argv:
        do_build()
    if len(sys.argv) == 1:
        print("usage: studylog.py [--fetch] [--build]")
