#!/usr/bin/env python3
"""Private gamified stats page (/stats/) for esc-artist.github.io.

Unlisted: not in nav, noindex. A quiet footer link on /study/ points here.

Economy (points):
  +1 per streamed hour (fractional)
  +3 per 6h+ day
  +2 per day while on a 3+ day run of 6h days

Levels: 1 level = 20 points (configurable per ranks.json), 14 level names.
16.67 TV minutes per point. One cash-in per day, no rollover.
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
CONFIG = f"{HOME}/static/data/ranks.json"
OUT_JSON = f"{HOME}/static/data/stats.json"
OUT_PAGE = f"{HOME}/content/stats.md"
OUT_RULES = f"{HOME}/content/stats-rules.md"


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def daily_hours(videos, start_date=None):
    """{date_iso: hours} from the video store, optionally filtered to start_date."""
    out = {}
    for v in videos.values():
        d = v.get("date")
        s = v.get("secs", 0) or 0
        if not d:
            continue
        if start_date and d < start_date:
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


def points_by_day(hours_by_day):
    """{date_iso: points} with per-day attribution for the Pi budget app."""
    in_streak = streak_days(hours_by_day)
    out = {}
    for d, h in hours_by_day.items():
        p = h  # 1 per hour
        if h >= 6 - 1e-9:
            p += 3
        if d in in_streak:
            p += 2
        out[d] = round(p, 2)
    return out


def compute_points(hours_by_day):
    """Return (total, breakdown dict)."""
    b = {"from hours": 0.0, "6h bonuses": 0, "streaks": 0}
    b["from hours"] = sum(hours_by_day.values())
    six_days = [d for d, h in hours_by_day.items() if h >= 6 - 1e-9]
    b["6h bonuses"] = 3 * len(six_days)
    b["streaks"] = 2 * len(streak_days(hours_by_day))
    total = b["from hours"] + b["6h bonuses"] + b["streaks"]
    return total, b


def longest_run(dates, min_hours):
    """Longest run of consecutive dates with hours >= min_hours. Returns (length, end_date)."""
    best, run, prev = 0, 0, None
    best_end = None
    for d in sorted(dates):
        di = date.fromisoformat(d)
        if dates[d] >= min_hours - 1e-9 and (prev is None or di == prev + timedelta(days=1)):
            run += 1
        elif dates[d] >= min_hours - 1e-9:
            run = 1
        else:
            run = 0
        if run > best:
            best, best_end = run, d
        prev = di
    return best, best_end


def first_reach(dates, key, threshold):
    """First date where cumulative key() reaches threshold."""
    cum = 0.0
    for d in sorted(dates):
        cum += key(d)
        if cum >= threshold - 1e-9:
            return d
    return None


def compute_badges(hours_by_day, cfg=None):
    """Return {badge_id: date_earned_iso_or_None}."""
    earned = {}
    days = sorted(hours_by_day)

    # firsts
    earned["first_stream"] = days[0] if days else None
    earned["first_blood"] = next((d for d in days if hours_by_day[d] >= 6 - 1e-9), None)

    # total-hour milestones
    for bid in ("hours_10", "hours_25", "hours_50", "centurion_100",
                "centurion_250", "centurion_500", "centurion_1000"):
        th = next(b["threshold"] for b in cfg["badges"] if b["id"] == bid)
        earned[bid] = first_reach(hours_by_day, lambda d: hours_by_day[d], th)

    # single-day feats
    for bid, h in (("overtime", 8), ("marathon", 10), ("ultra", 12)):
        earned[bid] = next((d for d in days if hours_by_day[d] >= h - 1e-9), None)

    # six-hour day counts
    for bid in ("grinder_5", "grinder_10", "grinder_25", "grinder_50"):
        th = next(b["threshold"] for b in cfg["badges"] if b["id"] == bid)
        earned[bid] = first_reach(
            hours_by_day, lambda d: 1 if hours_by_day[d] >= 6 - 1e-9 else 0, th)

    # streaks
    six_best, _ = longest_run(hours_by_day, 6)
    any_best, _ = longest_run(hours_by_day, 1e-9)
    # first date each streak length was achieved
    def streak_first(min_hours, need):
        run, prev = 0, None
        for d in days:
            di = date.fromisoformat(d)
            if hours_by_day[d] >= min_hours - 1e-9 and (prev is None or di == prev + timedelta(days=1)):
                run += 1
            elif hours_by_day[d] >= min_hours - 1e-9:
                run = 1
            else:
                run = 0
            if run >= need:
                return d
            prev = di
        return None
    earned["hat_trick"] = streak_first(6, 3)
    earned["week_clear"] = streak_first(6, 7)
    earned["streak_7"] = streak_first(1e-9, 7)
    earned["streak_14"] = streak_first(1e-9, 14)
    earned["streak_30"] = streak_first(1e-9, 30)

    # exam progress
    span = next(sp for sp in cfg["rank_spans"] if sp["from"] == cfg["current_rank"])
    for bid, frac in (("halfway", 0.5), ("three_quarter", 0.75), ("exam_ready", 1.0)):
        earned[bid] = first_reach(hours_by_day, lambda d: hours_by_day[d],
                                  span["exam_hours_est"] * frac)

    # comeback: 6h+ day right after a zero day
    cb = None
    for i, d in enumerate(days):
        if hours_by_day[d] >= 6 - 1e-9 and i > 0:
            prev = date.fromisoformat(d) - timedelta(days=1)
            if hours_by_day.get(prev.isoformat(), 0) < 1e-9:
                cb = d
                break
    earned["comeback"] = cb

    # weekend warrior: Sat and Sun both studied
    ww = None
    for d in days:
        di = date.fromisoformat(d)
        if di.weekday() == 5 and hours_by_day[d] > 1e-9:
            sun = (di + timedelta(days=1)).isoformat()
            if hours_by_day.get(sun, 0) > 1e-9:
                ww = d
                break
    earned["weekend_warrior"] = ww

    # no zero week: 7 consecutive days all >0
    nzw = None
    for d in days:
        di = date.fromisoformat(d)
        if all(hours_by_day.get((di + timedelta(days=k)).isoformat(), 0) > 1e-9 for k in range(7)):
            nzw = d
            break
    earned["no_zero_week"] = nzw

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
    "hex": '<path d="M32 6 L54 19 L54 45 L32 58 L10 45 L10 19 Z"/>',
    "play": '<path d="M22 12 L50 32 L22 52 Z"/>',
    "check": '<path d="M12 34 L26 48 L52 18" fill="none" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>',
    "spark": '<path d="M32 6 L37 27 L58 32 L37 37 L32 58 L27 37 L6 32 L27 27 Z"/>',
    "flag": '<path d="M16 6 L16 58 M16 10 L50 10 L43 20 L50 30 L16 30 Z"/>',
    "target": '<circle cx="32" cy="32" r="20" fill="none" stroke-width="5"/><circle cx="32" cy="32" r="11" fill="none" stroke-width="4"/><circle cx="32" cy="32" r="4"/>',
    "calendar": '<rect x="12" y="14" width="40" height="38" rx="3" fill="none" stroke-width="5"/><path d="M12 24 L52 24" stroke-width="5"/><path d="M22 8 L22 18 M42 8 L42 18" stroke-width="5" stroke-linecap="round"/>',
}

# Rank icons for the cert-path hexagons (viewBox 0 0 64 64), mirroring the calf tattoo
RANK_ICONS = {
    # dragon (OSCP): Kali-style serpentine — flowing S-curve body, trailing whiskers
    "OSCP": ('<path d="M47 12 C34 7, 20 7, 5 12 L5 13.5 C20 9, 34 9, 47 13.5 Z"/>'
             '<path d="M47 15 C34 11, 22 13, 9 19 L9 20.5 C22 15, 34 13, 47 16.5 Z"/>'
             '<path d="M47 18 C36 16, 26 20, 15 26 L15 27.5 C26 22, 36 18, 47 19.5 Z"/>'
             '<path d="M47 11 L56 4 L52 13 Z"/>'
             '<path d="M37 59 C33 51, 29 45, 33 37 C37 29, 45 29, 48 21'
             ' L52 12 L58 16 L52 23 C48 31, 41 33, 39 41 C37 49, 39 56, 37 59 Z"/>'
             '<path d="M48 11 L61 16 L49 21 L46 16 Z"/>'),
    # crossed swords (CPTS)
    "CPTS": ('<g transform="rotate(45 32 32)"><rect x="29" y="6" width="6" height="34" rx="2"/>'
             '<rect x="20" y="38" width="24" height="5" rx="2"/>'
             '<rect x="29" y="45" width="6" height="12" rx="3"/></g>'
             '<g transform="rotate(-45 32 32)"><rect x="29" y="6" width="6" height="34" rx="2"/>'
             '<rect x="20" y="38" width="24" height="5" rx="2"/>'
             '<rect x="29" y="45" width="6" height="12" rx="3"/></g>'),
    # windows logo (CAPE): four panes
    "CAPE": ('<rect x="12" y="14" width="18" height="16" rx="1"/>'
             '<rect x="34" y="14" width="18" height="16" rx="1"/>'
             '<rect x="12" y="34" width="18" height="16" rx="1"/>'
             '<rect x="34" y="34" width="18" height="16" rx="1"/>'),
    # mask (OSEP): domino mask with eye cutouts
    "OSEP": ('<path d="M8 26 C8 22 12 20 16 20 L48 20 C52 20 56 22 56 26 L56 34'
             ' C56 38 52 40 48 40 L16 40 C12 40 8 38 8 34 Z"/>'
             '<ellipse cx="22" cy="30" rx="6" ry="4" fill="' + BG + '"/>'
             '<ellipse cx="42" cy="30" rx="6" ry="4" fill="' + BG + '"/>'),
    # spider (OSWE)
    "OSWE": ('<ellipse cx="32" cy="36" rx="10" ry="12"/>'
             '<circle cx="32" cy="22" r="6"/>'
             '<path d="M24 28 L12 18 L8 24 M24 34 L10 30 L8 38 M24 42 L10 46 L12 54'
             ' M26 48 L18 58 M40 28 L52 18 L56 24 M40 34 L54 30 L56 38'
             ' M40 42 L54 46 L52 54 M38 48 L46 58"'
             ' fill="none" stroke-width="3" stroke-linecap="round"/>'),
    # skull and crossbones (OSED)
    "OSED": ('<g transform="rotate(45 32 38)">'
             '<rect x="10" y="35" width="44" height="7" rx="3.5"/>'
             '<circle cx="12" cy="38" r="5"/><circle cx="52" cy="38" r="5"/></g>'
             '<g transform="rotate(-45 32 38)">'
             '<rect x="10" y="35" width="44" height="7" rx="3.5"/>'
             '<circle cx="12" cy="38" r="5"/><circle cx="52" cy="38" r="5"/></g>'
             '<circle cx="32" cy="26" r="13"/>'
             '<rect x="24" y="32" width="16" height="10" rx="3"/>'
             '<circle cx="27" cy="25" r="4" fill="' + BG + '"/>'
             '<circle cx="37" cy="25" r="4" fill="' + BG + '"/>'),
}


def rank_hex(rank, earned, is_next, size=84):
    """Cert-path hexagon with the rank's icon."""
    r = size / 2
    cx = cy = r + 4
    icon = RANK_ICONS.get(rank, "")
    if earned:
        style = f'fill="{GREEN}" opacity="0.92" filter="url(#hexglow)"'
        poly = (f'<polygon points="{hex_points(cx, cy, r)}" fill="{GREEN}" fill-opacity="0.16"'
                f' stroke="{GREEN}" stroke-width="2.5" filter="url(#hexglow)"/>')
        lbl_op = "1"
    elif is_next:
        style = f'fill="none" stroke="{GREEN}" stroke-width="2.5" opacity="0.95" filter="url(#hexglow)"'
        poly = (f'<polygon points="{hex_points(cx, cy, r)}" fill="none"'
                f' stroke="{GREEN}" stroke-width="2.5" stroke-dasharray="7,4" opacity="0.9"'
                f' filter="url(#hexglow)"><animate attributeName="stroke-dashoffset"'
                f' from="0" to="22" dur="1.6s" repeatCount="indefinite"/></polygon>')
        lbl_op = "0.95"
    else:
        style = f'fill="none" stroke="{GREEN}" stroke-width="2" opacity="0.3"'
        poly = (f'<polygon points="{hex_points(cx, cy, r)}" fill="none"'
                f' stroke="{GREEN}" stroke-width="2" opacity="0.3"/>')
        lbl_op = "0.4"
    return f"""<div class="rank-cell" title="{rank}">
  <svg viewBox="0 0 {size+8} {size+30}" width="{size}" height="{size+22}">
    {poly}
    <g transform="translate({cx-24} {cy-24}) scale(0.75)"><g {style}>{icon}</g></g>
    <text x="{cx}" y="{cy + r + 16}" text-anchor="middle" fill="{GREEN}"
          font-size="11" font-family="ui-monospace,monospace" opacity="{lbl_op}">{rank}</text>
  </svg></div>"""


def badge_svg(icon, earned, size=64):
    path = BADGE_PATHS.get(icon, BADGE_PATHS["star"])
    if earned:
        return f"""<svg viewBox="0 0 64 64" width="{size}" height="{size}" class="badge earned">
  <circle cx="32" cy="32" r="29" fill="none" stroke="{GREEN}" stroke-width="2" filter="url(#hexglow)"/>
  <g fill="{GREEN}" stroke="{GREEN}">{path}</g></svg>"""
    return f"""<svg viewBox="0 0 64 64" width="{size}" height="{size}" class="badge locked">
  <circle cx="32" cy="32" r="29" fill="none" stroke="{DIM}" stroke-width="2"/>
  <g fill="#0d140e" stroke="{DIM}">{path}</g></svg>"""


def points_mark(size=18):
    return f"""<svg viewBox="0 0 20 20" width="{size}" height="{size}" class="pts-mark">
  <rect x="4" y="4" width="12" height="12" transform="rotate(45 10 10)"
        fill="none" stroke="{GREEN}" stroke-width="2"/></svg>"""


def heatmap_svg(hours_by_day, weeks=16):
    """GitHub-style heatmap, most recent `weeks` weeks. Interactive: hover ripples, click shows date."""
    today = date.today()
    # start on the Monday `weeks` weeks ago
    start = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
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
                f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{c}"'
                f' class="hcell" data-w="{w}" data-d="{d}"'
                f' data-date="{day.isoformat()}" data-hours="{h:.1f}"/>')
    W, H = weeks * 14, 7 * 14
    return (f'<div class="heat-readout" id="heatread">hover or tap a day</div>'
            f'<svg viewBox="0 0 {W} {H}" class="heatmap" id="heatmap">{"".join(cells)}</svg>')


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
    for h in cfg.get("rank_history", []):
        # Veteran badges reuse the rank's own icon inside the circular badge frame
        vic = RANK_ICONS.get(h["rank"], BADGE_PATHS["hex"])
        bid = f'vet_{h["rank"]}'
        BADGE_PATHS[bid] = vic
        badges.append(
            f'<div class="badge-cell">'
            f'{badge_svg(bid, h.get("date", ""))}'
            f'<div class="n">{h["rank"]} Veteran</div>'
            f'<div class="d">Reached Lv {h["peak_level"]} — {h["peak_name"]}</div>'
            f'{"<div class=d>" + h["date"] + "</div>" if h.get("date") else ""}</div>')
    # TV budget card (Pi-hole contingency)
    # Pi URL lives in browser localStorage, never in the repo.
    tvb = data.get("tv_budget", {})
    tv_h = tvb.get("minutes", 0) // 60
    tv_m = tvb.get("minutes", 0) % 60
    tv_time = f"{tv_h}h {tv_m}m" if tv_h else f"{tv_m} min"
    tv_btn = ('<a href="#" id="tv-open" class="tv-btn" style="display:none">Open TV Control</a>'
              '<span id="tv-unset"><button class="tv-btn" id="tv-set">Set Pi URL</button></span>')
    tv_card = f"""<div class="tv-card">
  <div class="tv-head">TV Budget — today</div>
  <div class="tv-big">{tv_time}</div>
  <div class="tv-sub">{tvb.get("yesterday_points", 0):.1f} points yesterday × {cfg.get("minutes_per_point", 7.5)} min</div>
  {tv_btn}
</div>
<script>
(function(){{
  var KEY='pi_budget_url';
  var open=document.getElementById('tv-open'), unset=document.getElementById('tv-unset'),
      set=document.getElementById('tv-set');
  function render(){{
    var u=localStorage.getItem(KEY);
    if(u){{ open.href=u; open.style.display=''; unset.style.display='none'; }}
    else {{ open.style.display='none'; unset.style.display=''; }}
  }}
  set.onclick=function(){{
    var u=prompt('Pi TV app URL (e.g. http://100.x.y.z:5000):', localStorage.getItem(KEY)||'');
    if(u===null) return;
    u=u.trim();
    if(u) localStorage.setItem(KEY,u); else localStorage.removeItem(KEY);
    render();
  }};
  render();
}})();
</script>"""
    cards = [
        (f'{data["total_hours"]:.1f}', "total hours"),
        (str(data["six_days"]), "6h+ days"),
        (str(data["cur_streak"]), "6h streak"),
        (str(data["longest_streak"]), "longest 6h streak"),
    ]
    cards_html = "".join(
        f'<div class="stat-card"><div class="v">{v}</div><div class="k">{k}</div></div>'
        for v, k in cards)
    # rank path: ordered hexagons mirroring the calf tattoo
    ordered = []
    for sp in cfg["rank_spans"]:
        if sp["from"] not in ordered:
            ordered.append(sp["from"])
        if sp["to"] not in ordered:
            ordered.append(sp["to"])
    earned_ranks = {cfg["current_rank"]} | {h["rank"] for h in cfg.get("rank_history", [])}
    rank_cells = "".join(
        rank_hex(r, r in earned_ranks, r == span["to"]) for r in ordered)
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

{tv_card}

<h3>Rank Path</h3>
<div class="rank-path">{rank_cells}</div>

<div class="stat-cards">{cards_html}</div>

<h3>Heatmap</h3>
{heatmap_svg(data["hours_by_day"])}

<h3>Badges</h3>
<div class="badge-grid">{"".join(badges)}</div>

<div class="rewards">
<h3>Screen time</h3>
<p>Points buy entertainment. Every point earned today becomes {cfg.get("minutes_per_point", 7.5)} minutes of
unblocked screen time tomorrow — Instagram, TikTok, Netflix, Hulu, HBO Max,
Apple TV+, Reddit, all of it. They're blocked by default; the only way through
is spending yesterday's points.</p>
<p>To spend: open TV Control above, enter the Pi-hole password, tap Start.
Blocking drops for exactly your earned minutes, then comes back on its own.</p>
</div>

<p style="opacity:.5;font-size:.85em"><a href="/stats-rules/">How points, levels, and ranks work</a></p>
</div>

<style>{CSS}</style>
<script>{JS}</script>
"""


def build_rules_page(cfg):
    ppl = cfg["points_per_level"]
    names = ", ".join(f"{i+1}. {n}" for i, n in enumerate(cfg["level_names"]))
    spans = "\n".join(
        f"| {sp['from']} → {sp['to']} | ~{sp['exam_hours_est']}h | {sp['levels']} |"
        for sp in cfg["rank_spans"])
    badges = "\n".join(
        f"| {b['name']} | {b['desc']} |" for b in cfg["badges"])
    start = cfg.get("start_date", "2026-08-30")
    mpp = cfg.get("minutes_per_point", 7.5)
    return f"""---
title: "Stats Rules"
summary: "how points, levels, and ranks work"
robotsNoIndex: true
---

The rulebook for the [stats](/stats/) page. Everything is computed from public data — stream durations — starting {start}.

## Points

| Action | Points |
|---|---|
| 1 hour studied (streamed) | 1 |
| 6+ hour day | +3 |
| Each day of a 3+ day run of 6h days | +2 |

Points never expire and are never taken away. Each point also buys {mpp} minutes of
unblocked screen time, usable the day after it's earned — see Screen time below.

## Levels

1 level = {ppl} points. Thresholds are absolute: level 5 always means 250 points of work, no matter the rank.

{names}

## Ranks

Ranks are earned only by passing certifications — never by points. The current rank is set by hand when an exam is passed.

| Span | Est. hours | Levels |
|---|---|---|
{spans}

When a rank is earned, the level resets to 1 in the new rank. The peak level from the old rank is kept as a Veteran badge — retired, not lost.

## Badges

| Badge | How |
|---|---|
{badges}

## Screen time

Points are spent on entertainment. Each point buys {mpp} minutes of unblocked
screen time, usable the day after it's earned — yesterday's points are today's
budget. One session per day; unused minutes don't roll over.

Blocked by default, at the DNS level: a Pi-hole on the home network sinkholes
Instagram, TikTok, Netflix, Hulu, HBO Max, Apple TV+, and Reddit (domains,
subdomains, and CDN hosts). YouTube is deliberately excluded — it's a study tool.

To spend the budget: open the TV control page (linked from the TV Budget card on
/stats/ — the URL is stored in your browser, never in the repo), enter the
Pi-hole admin password, and tap Start. Blocking lifts for exactly the earned
minutes, then Pi-hole's built-in timer re-enables it automatically. If anything
crashes, it fails closed — blocking stays on.
"""


def main():
    cfg = load_json(CONFIG, None)
    if not cfg:
        print("no config", file=sys.stderr)
        sys.exit(1)
    videos = load_json(VIDEOS, {})

    hours_by_day = daily_hours(videos, cfg.get("start_date"))
    total_points, breakdown = compute_points(hours_by_day)
    cur_streak, longest_streak = streaks(hours_by_day)
    badges = compute_badges(hours_by_day, cfg=cfg)

    span = next(sp for sp in cfg["rank_spans"] if sp["from"] == cfg["current_rank"])
    span_points = total_points - cfg.get("rank_start_points", 0)
    ppl = cfg["points_per_level"]
    level_n = min(int(span_points // ppl) + 1, span["levels"])
    level_name = cfg["level_names"][level_n - 1]
    progress = (span_points % ppl) / ppl if level_n < span["levels"] else 1.0

    six_days = sum(1 for h in hours_by_day.values() if h >= 6 - 1e-9)

    # TV budget: yesterday's points × minutes_per_point
    pbd = points_by_day(hours_by_day)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    yday_points = pbd.get(yesterday, 0)
    tv_budget_min = round(yday_points * cfg.get("minutes_per_point", 7.5))

    data = {
        "points": round(total_points, 1),
        "breakdown": {k: round(v, 1) for k, v in breakdown.items()},
        "level": {"n": level_n, "name": level_name, "progress": round(progress, 3),
                  "to_next": ppl - (span_points % ppl) if level_n < span["levels"] else 0},
        "span": span,
        "badges": badges,
        "total_hours": round(sum(hours_by_day.values()), 1),
        "six_days": six_days,
        "cur_streak": cur_streak,
        "longest_streak": longest_streak,
        "hours_by_day": {d: round(h, 2) for d, h in hours_by_day.items()},
        "points_by_day": pbd,
        "tv_budget": {"yesterday_points": yday_points, "minutes": tv_budget_min,
                      "date": yesterday},
    }
    with open(OUT_JSON, "w") as f:
        json.dump(data, f, indent=1)
    with open(OUT_PAGE, "w") as f:
        f.write(build_page(data, cfg))
    with open(OUT_RULES, "w") as f:
        f.write(build_rules_page(cfg))
    print(f"level {level_n} ({level_name}), {total_points:.1f} points, "
          f"{len([b for b in badges.values() if b])}/{len(badges)} badges")


if __name__ == "__main__":
    main()
