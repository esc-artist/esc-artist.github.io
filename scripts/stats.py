#!/usr/bin/env python3
"""Private gamified stats page (/stats/) for esc-artist.github.io.

Unlisted: not in nav, noindex. A quiet footer link on /study/ points here.

Economy (points):
  +1 per streamed hour (fractional)
  +2 per schedule block hit
  +3 per 6h+ day
  +5 per fully adhered day (all blocks hit)
  +2 per day while on a 3+ day run of 6h days

Levels: 1 level = 50 points (configurable), named per ranks.json.
Ranks are cert-based and updated manually (current_rank in ranks.json).

Usage:
    python3 scripts/stats.py --build
"""

import json
import os
import sys
from datetime import date, timedelta

HOME = "/home/hatch/workspace/esc-artist-blog"
VIDEOS = f"{HOME}/scripts/study_videos.json"
SCHED_LOG = f"{HOME}/static/data/schedules/_log.json"
CONFIG = f"{HOME}/static/data/ranks.json"
OUT_JSON = f"{HOME}/static/data/stats.json"
OUT_PAGE = f"{HOME}/content/stats.md"


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def daily_hours(videos):
    """{date_iso: hours} from the video store."""
    out = {}
    for v in videos.values():
        d = v.get("date")
        s = v.get("secs", 0) or 0
        if not d:
            continue
        out[d] = out.get(d, 0) + s / 3600.0
    return out


def streaks(hours_by_day):
    """Return (current_streak, longest_streak) of consecutive 6h+ days.

    Current streak counts back from today; a streak ending yesterday still
    counts as current (today may not be over).
    """
    days = sorted(hours_by_day)
    if not days:
        return 0, 0
    good = {d for d in days if hours_by_day[d] >= 6 - 1e-9}

    longest = 0
    run = 0
    prev = None
    for d in days:
        di = date.fromisoformat(d)
        if d in good and (prev is None or di == prev + timedelta(days=1)):
            run += 1
        elif d in good:
            run = 1
        else:
            run = 0
        longest = max(longest, run)
        prev = di

    # current: walk back from today
    today = date.today()
    cur = 0
    d = today
    # allow today to be incomplete: start from yesterday if today isn't 6h yet
    if hours_by_day.get(d.isoformat(), 0) < 6 - 1e-9:
        d -= timedelta(days=1)
    while hours_by_day.get(d.isoformat(), 0) >= 6 - 1e-9:
        cur += 1
        d -= timedelta(days=1)
    return cur, longest


def streak_days(hours_by_day, min_len=3):
    """Set of dates belonging to a 6h+ streak of at least min_len days."""
    days = sorted(hours_by_day)
    good = [d for d in days if hours_by_day[d] >= 6 - 1e-9]
    out = set()
    run = []
    prev = None
    for d in good:
        di = date.fromisoformat(d)
        if prev is not None and di == prev + timedelta(days=1):
            run.append(d)
        else:
            if len(run) >= min_len:
                out.update(run)
            run = [d]
        prev = di
    if len(run) >= min_len:
        out.update(run)
    return out


def compute_points(hours_by_day, sched_log):
    """Return (total, breakdown dict)."""
    b = {"from hours": 0.0, "from blocks": 0, "6h bonuses": 0, "perfect days": 0, "streaks": 0}
    b["from hours"] = sum(hours_by_day.values())
    for d in sched_log:
        if not isinstance(d, dict):
            continue
        hits = sum(1 for r in d.get("block_results", []) if r.get("hit"))
        b["from blocks"] += 2 * hits
        if d.get("verdict") == "adhered":
            b["perfect days"] += 5
    six_days = [d for d, h in hours_by_day.items() if h >= 6 - 1e-9]
    b["6h bonuses"] = 3 * len(six_days)
    b["streaks"] = 2 * len(streak_days(hours_by_day))
    total = b["from hours"] + b["from blocks"] + b["6h bonuses"] + b["perfect days"] + b["streaks"]
    return total, b


def compute_badges(hours_by_day, sched_log, cfg):
    """Return {badge_id: date_earned_iso_or_None}."""
    earned = {}
    days = sorted(hours_by_day)

    def first(cond):
        for d in days:
            if cond(d):
                return d
        return None

    earned["first_blood"] = first(lambda d: hours_by_day[d] >= 6 - 1e-9)
    earned["marathon"] = first(lambda d: hours_by_day[d] >= 10 - 1e-9)
    # comeback: 6h+ day right after a zero day
    cb = None
    for i, d in enumerate(days):
        if hours_by_day[d] >= 6 - 1e-9 and i > 0:
            prev = date.fromisoformat(d) - timedelta(days=1)
            if hours_by_day.get(prev.isoformat(), 0) < 1e-9:
                cb = d
                break
    earned["comeback"] = cb
    # week_clear: 7 straight 6h days
    wc = None
    good = {d for d in days if hours_by_day[d] >= 6 - 1e-9}
    for d in days:
        di = date.fromisoformat(d)
        if all((di + timedelta(days=k)).isoformat() in good for k in range(7)):
            wc = d
            break
    earned["week_clear"] = wc
    # centurions
    total_h = sum(hours_by_day.values())
    for bid in ("centurion_100", "centurion_250", "centurion_500", "centurion_1000"):
        th = next(b["threshold"] for b in cfg["badges"] if b["id"] == bid)
        earned[bid] = None
        cum = 0.0
        for d in days:
            cum += hours_by_day[d]
            if cum >= th - 1e-9:
                earned[bid] = d
                break
    # schedule-based
    log_by_date = {d["date"]: d for d in sched_log if isinstance(d, dict)}
    earned["perfect_day"] = None
    for d in sorted(log_by_date):
        if log_by_date[d].get("verdict") == "adhered":
            earned["perfect_day"] = d
            break
    earned["perfect_week"] = None
    for d in sorted(log_by_date):
        di = date.fromisoformat(d)
        if all(log_by_date.get((di + timedelta(days=k)).isoformat(), {}).get("verdict") == "adhered"
               for k in range(7)):
            earned["perfect_week"] = d
            break
    # stream-time badges from judged-day streams
    earned["night_owl"] = earned["early_bird"] = None
    for d in sorted(log_by_date):
        for s in log_by_date[d].get("streams", []):
            st = s.get("start", "")
            # format "10-01 3:40 AM"
            try:
                hm, ap = st.split()[1], st.split()[2]
                h = int(hm.split(":")[0]) % 12 + (12 if ap == "PM" else 0)
            except (IndexError, ValueError):
                continue
            if 0 <= h < 5 and earned["night_owl"] is None:
                earned["night_owl"] = d
            if 5 <= h < 7 and earned["early_bird"] is None:
                earned["early_bird"] = d
    # halfway: 50% of current exam's estimate
    span = next(sp for sp in cfg["rank_spans"] if sp["from"] == cfg["current_rank"])
    earned["halfway"] = None
    cum = 0.0
    for d in days:
        cum += hours_by_day[d]
        if cum >= span["exam_hours_est"] / 2 - 1e-9:
            earned["halfway"] = d
            break
    return earned


# ---------------------------------------------------------------- SVG ---

GREEN = "#33ff66"
DIM = "#1d3a24"
BG = "#050805"


def hex_points(cx, cy, r):
    import math
    pts = []
    for i in range(6):
        a = math.pi / 3 * i - math.pi / 6  # flat-top
        pts.append("%g,%g" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    return " ".join(pts)


def level_hexagon(level, max_level, progress, size=120):
    """Hexagon emblem: fill rises with progress to next level, glow by level."""
    r = size / 2
    cx = cy = r + 4
    # fill height proportional to progress within current level
    inner_h = (r * 1.55) * progress
    glow = 0.25 + 0.75 * (level / max(max_level, 1))
    return f"""<svg class="lvl-hex" viewBox="0 0 {size+8} {size+8}" width="{size}" height="{size}">
  <defs>
    <clipPath id="hexclip"><polygon points="{hex_points(cx, cy, r*0.88)}"/></clipPath>
    <filter id="hexglow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <polygon points="{hex_points(cx, cy, r)}" fill="{BG}" stroke="{DIM}" stroke-width="2"/>
  <g clip-path="url(#hexclip)">
    <rect class="hexfill" x="{cx-r}" y="{cy + r*0.78 - inner_h}" width="{2*r}" height="{inner_h}"
          fill="{GREEN}" opacity="{0.25 + 0.55*glow}"/>
  </g>
  <polygon points="{hex_points(cx, cy, r)}" fill="none" stroke="{GREEN}" stroke-width="2"
           opacity="{0.5 + 0.5*glow}" filter="url(#hexglow)"/>
  <text x="{cx}" y="{cy+8}" text-anchor="middle" fill="{GREEN}" font-size="26"
        font-family="ui-monospace,monospace" font-weight="bold" filter="url(#hexglow)">{level}</text>
</svg>"""


BADGE_PATHS = {
    "droplet": '<path d="M32 6 C32 6 14 30 14 42 a18 18 0 0 0 36 0 C50 30 32 6 32 6 Z"/>',
    "star": '<path d="M32 8 L39 25 L57 25 L42 36 L47 54 L32 43 L17 54 L22 36 L7 25 L25 25 Z"/>',
    "crown": '<path d="M10 44 L14 22 L24 34 L32 16 L40 34 L50 22 L54 44 Z M10 48 L54 48 L54 52 L10 52 Z"/>',
    "flame": '<path d="M32 4 C28 18 16 24 16 40 a16 16 0 0 0 32 0 C48 30 40 26 38 18 C34 22 32 14 32 4 Z"/>',
    "medal": '<circle cx="32" cy="26" r="14"/><path d="M24 38 L18 58 L32 50 L46 58 L40 38 Z"/>',
    "moon": '<path d="M42 36 A20 20 0 1 1 28 8 A16 16 0 1 0 42 36 Z"/>',
    "sunrise": '<path d="M14 44 a18 18 0 0 1 36 0 Z"/><path d="M32 6 L32 14 M12 18 L18 24 M52 18 L46 24 M6 44 L58 44" stroke-width="4" stroke-linecap="round"/>',
    "bolt": '<path d="M36 4 L14 36 L28 36 L26 60 L50 26 L36 26 Z"/>',
    "rebirth": '<path d="M52 32 a20 20 0 1 1 -6 -14" fill="none" stroke-width="6"/><path d="M46 6 L48 20 L34 16 Z"/>',
    "gauge": '<path d="M10 44 a22 22 0 0 1 44 0 Z"/><path d="M32 44 L48 26" stroke-width="5" stroke-linecap="round"/>',
}


def badge_svg(icon, earned, size=64):
    path = BADGE_PATHS.get(icon, BADGE_PATHS["star"])
    if earned:
        return f"""<svg viewBox="0 0 64 64" width="{size}" height="{size}" class="badge earned">
  <g fill="{GREEN}" stroke="{GREEN}" filter="url(#hexglow)">{path}</g></svg>"""
    return f"""<svg viewBox="0 0 64 64" width="{size}" height="{size}" class="badge locked">
  <g fill="#0d140e" stroke="{DIM}">{path}</g></svg>"""


def points_mark(size=18):
    return f"""<svg viewBox="0 0 20 20" width="{size}" height="{size}" class="pts-mark">
  <rect x="4" y="4" width="12" height="12" transform="rotate(45 10 10)"
        fill="none" stroke="{GREEN}" stroke-width="2"/></svg>"""


def heatmap_svg(hours_by_day, weeks=16):
    """GitHub-style heatmap, most recent `weeks` weeks."""
    today = date.today()
    # start on the Monday `weeks` weeks ago
    start = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
    max_h = max(hours_by_day.values(), default=0)
    cells = []
    for w in range(weeks):
        for d in range(7):
            day = start + timedelta(days=7 * w + d)
            if day > today:
                continue
            h = hours_by_day.get(day.isoformat(), 0)
            if h <= 0:
                c = "#0d140e"
            elif h < 2:
                c = "#14401f"
            elif h < 4:
                c = "#1f7a33"
            elif h < 6:
                c = "#2fbf4f"
            else:
                c = "#33ff66"
            x, y = w * 14, d * 14
            cells.append(
                f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{c}">'
                f'<title>{day.isoformat()}: {h:.1f}h</title></rect>')
    W, H = weeks * 14, 7 * 14
    return f'<svg viewBox="0 0 {W} {H}" class="heatmap">{"".join(cells)}</svg>'


# ---------------------------------------------------------------- page ---

CSS = """
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
"""

JS = """
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
"""


def build_page(data, cfg):
    lvl = data["level"]
    span = data["span"]
    badges = []
    for i, b in enumerate(cfg["badges"]):
        earned = data["badges"].get(b["id"])
        badges.append(
            f'<div class="badge-cell{" locked" if not earned else ""}">'
            f'{badge_svg(b["icon"], earned)}'
            f'<div class="n">{b["name"]}</div>'
            f'<div class="d">{b["desc"]}</div>'
            f'{"<div class=d>" + earned + "</div>" if earned else ""}</div>')
    cards = [
        (f'{data["total_hours"]:.1f}', "total hours"),
        (str(data["six_days"]), "6h+ days"),
        (f'{data["adherence"]:.0f}%', "blocks hit"),
        (str(data["cur_streak"]), "day streak"),
        (str(data["longest_streak"]), "longest streak"),
    ]
    cards_html = "".join(
        f'<div class="stat-card"><div class="v">{v}</div><div class="k">{k}</div></div>'
        for v, k in cards)
    return f"""---
title: "Stats"
summary: "private training stats"
robotsNoIndex: true
---

<div class="stats-wrap">
<div class="stat-hero">
  <div class="lvl-block">
    {level_hexagon(lvl["n"], span["levels"], lvl["progress"])}
    <div class="lvl-name">Lv {lvl["n"]} — {lvl["name"]}</div>
    <div class="rank-line">Rank: {cfg["current_rank"]} → {span["to"]}</div>
  </div>
  <div style="flex:1;min-width:220px">
    <div class="pts-big">{points_mark(26)}<span data-count="{data["points"]:.1f}">0</span></div>
    <div class="pts-break">{"<br>".join(
        f"{k}: {v:.1f}" for k, v in data["breakdown"].items())}</div>
    <div class="pbar"><i data-w="{lvl["progress"]*100:.0f}"></i></div>
    <div class="pts-break">{lvl["to_next"]:.0f} points to Lv {lvl["n"]+1}</div>
  </div>
</div>

<div class="stat-cards">{cards_html}</div>

<h3>Heatmap</h3>
{heatmap_svg(data["hours_by_day"])}

<h3>Badges</h3>
<div class="badge-grid">{"".join(badges)}</div>

<div class="rewards">
<h3>Rewards — locked</h3>
<p>Points are being banked. The store opens when the hardware exists —
a dispenser, a filter, whatever the privilege mechanism ends up being.
Exchange rates get set then; the ledger is already honest.</p>
</div>
</div>

<style>{CSS}</style>
<script>{JS}</script>
"""


def main():
    cfg = load_json(CONFIG, None)
    if not cfg:
        print("no config", file=sys.stderr)
        sys.exit(1)
    videos = load_json(VIDEOS, {})
    sched_log = load_json(SCHED_LOG, [])

    hours_by_day = daily_hours(videos)
    total_points, breakdown = compute_points(hours_by_day, sched_log)
    cur_streak, longest_streak = streaks(hours_by_day)
    badges = compute_badges(hours_by_day, sched_log, cfg)

    span = next(sp for sp in cfg["rank_spans"] if sp["from"] == cfg["current_rank"])
    span_points = total_points - cfg.get("rank_start_points", 0)
    ppl = cfg["points_per_level"]
    level_n = min(int(span_points // ppl) + 1, span["levels"])
    level_name = cfg["level_names"][level_n - 1]
    progress = (span_points % ppl) / ppl if level_n < span["levels"] else 1.0

    total_blocks = sum(len(d.get("block_results", [])) for d in sched_log if isinstance(d, dict))
    hits = sum(1 for d in sched_log if isinstance(d, dict)
               for r in d.get("block_results", []) if r.get("hit"))
    adherence = 100 * hits / total_blocks if total_blocks else 0
    six_days = sum(1 for h in hours_by_day.values() if h >= 6 - 1e-9)

    data = {
        "points": round(total_points, 1),
        "breakdown": {k: round(v, 1) for k, v in breakdown.items()},
        "level": {"n": level_n, "name": level_name, "progress": round(progress, 3),
                  "to_next": ppl - (span_points % ppl) if level_n < span["levels"] else 0},
        "span": span,
        "badges": badges,
        "total_hours": round(sum(hours_by_day.values()), 1),
        "six_days": six_days,
        "adherence": round(adherence, 1),
        "cur_streak": cur_streak,
        "longest_streak": longest_streak,
        "hours_by_day": {d: round(h, 2) for d, h in hours_by_day.items()},
    }
    with open(OUT_JSON, "w") as f:
        json.dump(data, f, indent=1)
    with open(OUT_PAGE, "w") as f:
        f.write(build_page(data, cfg))
    print(f"level {level_n} ({level_name}), {total_points:.1f} points, "
          f"{len([b for b in badges.values() if b])}/{len(badges)} badges")


if __name__ == "__main__":
    main()
