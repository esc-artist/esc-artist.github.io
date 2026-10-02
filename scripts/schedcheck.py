#!/usr/bin/env python3
"""Daily study-schedule adherence check.

Compares the morning-filed plan (static/data/schedules/YYYY-MM-DD.json)
against the day's public study streams (start times via yt-dlp), using a
10-minute grace window, and regenerates the public schedule page.

Tamper model (mirrors the CPTS countdown guard): the morning snapshot is
canonical and stores the full plan content. Any post-filing change
(modified or deleted plan) is logged in a public changelog, the original
is restored, and the day is judged against the original schedule.
Plans are timestamped by their git commit; a plan committed after its
first block started is `late_plan` (unverifiable).
Plans must total at least 6 hours (`short_plan` otherwise); days with
fewer than 6 streamed hours are marked regardless of timing.
Blocks past midnight count toward the plan date.

Usage:
    python3 scripts/schedcheck.py --check [YYYY-MM-DD]   # default: today ET
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN_DIR = os.path.join(REPO, "static", "data", "schedules")
LOG_PATH = os.path.join(PLAN_DIR, "_log.json")
CHANGELOG_PATH = os.path.join(PLAN_DIR, "_changelog.json")
STATE_PATH = os.path.expanduser("~/workspace/sched-guard/hidden_files/state.json")
PAGE_PATH = os.path.join(REPO, "content", "schedule.md")
GRACE = timedelta(minutes=10)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 120), **kw)


def today_et():
    return datetime.now(ET).date()


def plan_path(d):
    return os.path.join(PLAN_DIR, d.isoformat() + ".json")


def load_plan(d):
    p = plan_path(d)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def plan_first_commit(d):
    """ISO-8601 commit time of the commit that added the plan file, or None."""
    rel = os.path.relpath(plan_path(d), REPO)
    r = run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%cI", "-1", "--", rel])
    out = r.stdout.strip().splitlines()
    if not out or not out[0]:
        return None
    return datetime.fromisoformat(out[0])


def plan_sha256(d):
    return file_sha256(plan_path(d))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def verify_all():
    """Re-verify every filed plan against its snapshot. Any post-filing
    change (including to plans already checked on earlier days) is
    reverted and logged in the public changelog. Returns event list."""
    state = load_state()
    events = []

    def revert(diso, detail):
        st = state[diso]
        with open(os.path.join(PLAN_DIR, diso + ".json"), "w") as f:
            json.dump(st["content"], f, indent=2)
        log_event(diso, "Schedule tampering detected and reverted.",
                  detail + ".")
        events.append({"date": diso, "detail": detail})

    for fname in sorted(os.listdir(PLAN_DIR)):
        if not fname.endswith(".json") or fname.startswith("_"):
            continue
        diso = fname[:-5]
        st = state.get(diso)
        if not st or not st.get("content") or not st.get("sha256"):
            continue
        if st["sha256"] == file_sha256(os.path.join(PLAN_DIR, fname)):
            continue
        with open(os.path.join(PLAN_DIR, fname)) as f:
            old = json.load(f)
        detail = ("blocks changed from %s to %s"
                  % (fmt_block_list(old.get("blocks", [])),
                     fmt_block_list(st["content"].get("blocks", []))))
        revert(diso, detail)
    for diso, st in state.items():
        if not st.get("content"):
            continue
        if os.path.exists(os.path.join(PLAN_DIR, diso + ".json")):
            continue
        revert(diso, "plan file deleted after filing")
    return events


def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH) as f:
        return json.load(f)


def ytdlp_cmd():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def fetch_streams():
    """Return [(video_id, start_et, end_et)] for the newest 60 streams.

    Uses release_timestamp (actual broadcast start) rather than timestamp
    (when the VOD became public, often hours later for this channel).
    Falls back to timestamp if release_timestamp is missing.
    """
    cmd = ytdlp_cmd() + ["-i", "--playlist-end", "60",
                         "--print", "%(id)s %(release_timestamp)s %(timestamp)s %(duration)s",
                         "--skip-download",
                         "https://www.youtube.com/@constantinestudies/streams"]
    r = run(cmd, timeout=1200)
    streams = []
    for line in r.stdout.splitlines():
        parts = line.strip().split()
        if len(parts) < 4:
            continue
        vid, rts, ts, dur = parts[0], parts[1], parts[2], parts[3]
        start = None
        for cand in (rts, ts):
            try:
                start = datetime.fromtimestamp(int(cand), tz=ET)
                break
            except (ValueError, OSError):
                continue
        if start is None:
            continue
        try:
            end = start + timedelta(seconds=float(dur))
        except (ValueError, OSError):
            continue
        streams.append((vid, start, end))
    return streams


def streams_on(streams, d):
    return [(v, s, e) for (v, s, e) in streams if s.date() == d]


def parse_hm(s):
    h, m = s.split(":")
    return int(h), int(m)


def hm12(s):
    """'16:30' -> '4:30 PM'. Display only; plans stay in HH:MM."""
    h, m = parse_hm(s)
    ap = "AM" if h < 12 else "PM"
    return "%d:%02d %s" % (h % 12 or 12, m, ap)


def compute_windows(d, blocks, filed):
    """Absolute block windows. Blocks are placed on the plan date, rolling
    forward past midnight as needed: a block whose start would otherwise
    precede the filing time (e.g. "12:00am-1:00am" filed in the afternoon)
    belongs to the following night. end <= start also crosses midnight."""
    windows = []
    offset = 0
    prev_start = None
    for b in blocks:
        sh, sm = parse_hm(b[0])
        eh, em = parse_hm(b[1])
        while True:
            bs = datetime(d.year, d.month, d.day, sh, sm, tzinfo=ET) + timedelta(days=offset)
            be = datetime(d.year, d.month, d.day, eh, em, tzinfo=ET) + timedelta(days=offset)
            if be <= bs:
                be += timedelta(days=1)
            if filed and bs < filed:
                offset += 1
                continue
            if prev_start and bs < prev_start:
                offset += 1
                continue
            break
        windows.append((bs, be))
        prev_start = bs
    return windows


def check_day(d, streams):
    plan = load_plan(d)
    state = load_state().get(d.isoformat())
    rec = {"date": d.isoformat(), "blocks": [], "streams": [],
           "hits": 0, "verdict": "", "note": ""}
    tamper_detail = None

    # Tamper handling: the morning snapshot is canonical. Any post-filing
    # change (modified or deleted plan) is logged publicly, the original
    # is restored, and the day is judged against the original schedule.
    if plan is None and state and state.get("content"):
        plan = state["content"]
        tamper_detail = "plan file deleted after filing"
    elif (plan is not None and state and state.get("sha256")
            and state["sha256"] != plan_sha256(d) and state.get("content")):
        tamper_detail = ("blocks changed from %s to %s"
                         % (fmt_block_list(state["content"].get("blocks", [])),
                            fmt_block_list(plan.get("blocks", []))))
        plan = state["content"]

    if plan is None:
        rec["verdict"] = "no_plan"
        rec["note"] = "No plan filed."
        return rec

    if tamper_detail:
        with open(plan_path(d), "w") as f:
            json.dump(plan, f, indent=2)
        log_event(d.isoformat(),
                  "Schedule tampering detected and reverted.",
                  tamper_detail + ".")
        rec["note"] = ("Plan changed after filing; original restored. "
                       + tamper_detail + ". Judged against original schedule. ")

    blocks = plan.get("blocks", [])
    rec["blocks"] = ["%s-%s" % (hm12(b[0]), hm12(b[1])) for b in blocks]

    filed = plan_first_commit(d)
    windows = compute_windows(d, blocks, filed)

    if not windows:
        rec["verdict"] = "no_plan"
        rec["note"] = "Plan filed with no blocks."
        return rec

    # Tamper check 2: the plan must be filed before its earliest block
    # starts. Streams from earlier in the day don't matter; only the
    # plan-then-execute order for the planned blocks.
    first_block = min(bs for (bs, _) in windows)
    if filed and filed >= first_block:
        rec["verdict"] = "late_plan"
        rec["note"] = ("Plan filed at %s, after the first block started at %s: "
                       "unverifiable." % (filed.strftime("%m-%d ") + hm12(filed.strftime("%H:%M")),
                                           first_block.strftime("%m-%d ") + hm12(first_block.strftime("%H:%M"))))
        return rec

    # Validity check: the plan must total at least 6 hours. Short plans
    # are a violation, flagged the same as tampering.
    plan_hours = sum((be - bs).total_seconds() / 3600 for (bs, be) in windows)
    rec["plan_hours"] = round(plan_hours, 1)
    if plan_hours < 6 - 1e-9:
        rec["verdict"] = "short_plan"
        rec["note"] = "Plan totaled %.1fh; 6h required." % plan_hours
        return rec

    span_start = min(bs for (bs, _) in windows)
    span_end = max(be for (_, be) in windows)
    in_span = sorted(((v, s, e) for (v, s, e) in streams if s < span_end and e > span_start),
                     key=lambda t: t[1])
    rec["streams"] = [{"id": v,
                       "start": s.strftime("%m-%d ") + hm12(s.strftime("%H:%M")),
                       "end": e.strftime("%m-%d ") + hm12(e.strftime("%H:%M"))} for (v, s, e) in in_span]

    # Blocks still in the future: no verdict yet, final check runs ~1:30am.
    if span_end > datetime.now(ET):
        rec["verdict"] = "pending"
        rec["note"] = "Blocks still in progress; final check runs ~1:30am ET."
        return rec

    # Hours: total streamed time overlapping the day's span, regardless of
    # when within it the hours happened. Under 6h is marked.
    day_hours = sum((e - s).total_seconds() / 3600
                    for (_, s, e) in streams if s < span_end and e > span_start)
    rec["hours"] = round(day_hours, 1)
    rec["hours_met"] = day_hours >= 6 - 1e-9

    # Adherence: block is HIT if a stream started no later than 10 minutes
    # after block start, was live 10 minutes into the block, and was still
    # live 10 minutes before block end (no bailing early).
    hits = 0
    results = []
    for (b, (bs, be)) in zip(blocks, windows):
        probe = bs + GRACE
        tail = be - GRACE
        hit = any(s <= bs + GRACE and e >= probe and e >= tail
                  for (_, s, e) in streams)
        results.append({"block": "%s-%s" % (hm12(b[0]), hm12(b[1])), "hit": hit})
        hits += 1 if hit else 0
    rec["block_results"] = results
    rec["hits"] = hits

    n = len(blocks)
    if hits == n:
        rec["verdict"] = "adhered"
    elif hits == 0:
        rec["verdict"] = "missed"
    else:
        rec["verdict"] = "partial"
    return rec


def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        return json.load(f)


def save_log(log):
    os.makedirs(PLAN_DIR, exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=1)


def load_changelog():
    if not os.path.exists(CHANGELOG_PATH):
        return []
    with open(CHANGELOG_PATH) as f:
        return json.load(f)


def log_event(date_iso, event, detail):
    cl = load_changelog()
    cl.append({"date": date_iso, "event": event, "detail": detail})
    os.makedirs(PLAN_DIR, exist_ok=True)
    with open(CHANGELOG_PATH, "w") as f:
        json.dump(cl, f, indent=1)


def fmt_block_list(blocks):
    return ", ".join("%s-%s" % (hm12(b[0]), hm12(b[1])) for b in blocks) or "(none)"


def upcoming_section():
    """'I will be live at the following times' — the nearest plan's blocks
    that have not ended yet, published so anyone can check. Prefers today's
    plan; falls back to the next filed future plan (plans may be filed the
    prior day or earlier — they lock at filing either way)."""
    now = datetime.now(ET)
    d = now.date()
    windows = []
    plan = load_plan(d)
    if plan:
        windows = [(bs, be) for (bs, be) in
                   compute_windows(d, plan.get("blocks", []),
                                   plan_first_commit(d))
                   if be > now]
    if not windows:
        for offset in range(1, 8):
            fd = d + timedelta(days=offset)
            fplan = load_plan(fd)
            if fplan and fplan.get("blocks"):
                windows = compute_windows(fd, fplan["blocks"],
                                          plan_first_commit(fd))
                break
    if not windows:
        return ""
    lines = ["## I will be live on "
             "[@constantinestudies](https://www.youtube.com/@constantinestudies) "
             "at the following times",
             "",
             "All times ET.",
             ""]
    for (bs, be) in windows:
        lines.append("- %s, %s – %s"
                     % (bs.strftime("%a %-m/%-d"),
                        bs.strftime("%-I:%M %p"), be.strftime("%-I:%M %p")))
    return "\n".join(lines)


def build_page(log):
    planned = [r for r in log if r["verdict"] not in ("no_plan", "pending")]
    full = [r for r in planned if r["verdict"] == "adhered"]
    met = [r for r in planned if r.get("hours_met")]
    blocks_hit = sum(r["hits"] for r in planned)
    blocks_total = sum(len(r["blocks"]) for r in planned)
    adh = (100.0 * len(full) / len(planned)) if planned else 0.0

    lines = []
    lines.append("---")
    lines.append('title: "Schedule Adherence"')
    lines.append("---")
    lines.append("")
    try:
        with open(os.path.join(REPO, "static", "data", "schedules",
                               "_summary.md")) as f:
            summary = f.read().strip()
        if summary:
            lines.append(summary)
            lines.append("")
    except OSError:
        pass
    up = upcoming_section()
    if up:
        lines.append(up)
        lines.append("")
    lines.append("I file a study schedule — time blocks only, always "
                 "totaling at least 6 hours — sometimes the morning of, "
                 "sometimes the night before or earlier. The plan locks at "
                 "filing: it can't be changed after, no matter when it was "
                 "filed. After the day is done the public streams "
                 "are checked against it: a block counts as hit if a stream started no "
                 "later than ten minutes after the block began and was still live "
                 "ten minutes before the block ended — showing up isn't enough, "
                 "you have to stay. Blocks past midnight count toward the day they were "
                 "planned on.")
    lines.append("")
    lines.append("Plans are timestamped by their git commit and must predate the "
                 "plan's first block. A missing plan, or a plan under 6 hours, is "
                 "marked. If a plan is changed after filing, the change is logged "
                 "below, the original is restored, and the day is judged against "
                 "the original schedule — the same way the CPTS countdown date is "
                 "guarded. The exact machinery is documented on the "
                 "[Schedule Rules & Guard](/schedule-guard/). Days with fewer than "
                 "6 streamed hours are marked, "
                 "regardless of when the hours happened.")
    lines.append("")
    lines.append("Cumulative and weekly hours, running average, streak, and "
                 "hour totals against the 6h/day target are tracked on the "
                 "[Study Log](/study/) page. This page answers one question: "
                 "did I study when I said I would?")
    lines.append("")
    lines.append("**%d of %d planned days fully adhered (%.0f%%). %d of %d blocks hit. "
                 "%d of %d days reached 6h.**"
                 % (len(full), len(planned), adh, blocks_hit, blocks_total,
                    len(met), len(planned)))
    lines.append("")
    lines.append("| Date | Plan | Streams (ET) | Blocks hit | Hours | Verdict | Note |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in sorted(log, key=lambda r: r["date"], reverse=True):
        plan = ", ".join(r["blocks"]) if r["blocks"] else "—"
        streams = ", ".join("%s–%s" % (s["start"], s["end"]) for s in r["streams"]) or "—"
        if r.get("block_results"):
            bh = "%d/%d" % (r["hits"], len(r["blocks"]))
        else:
            bh = "—"
        if "hours" in r:
            h = "%.1fh" % r["hours"]
            if not r.get("hours_met"):
                h = "**%s**" % h
        else:
            h = "—"
        note = r.get("note", "")
        lines.append("| %s | %s | %s | %s | %s | %s | %s |"
                     % (r["date"], plan, streams, bh, h, r["verdict"], note))
    cl = load_changelog()
    if cl:
        lines.append("")
        lines.append("## Changelog")
        lines.append("")
        for e in cl:
            lines.append("- %s — %s %s" % (e["date"], e["event"], e.get("detail", "")))
    lines.append("")
    with open(PAGE_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("--check", "--verify-all", "--rebuild-page"):
        print("usage: schedcheck.py --check [YYYY-MM-DD] | --verify-all | --rebuild-page",
              file=sys.stderr)
        sys.exit(2)
    if args[0] == "--rebuild-page":
        build_page(load_log())
        print("rebuilt")
        return
    if args[0] == "--verify-all":
        events = verify_all()
        build_page(load_log())
        print(json.dumps({"reverted": len(events), "events": events}, indent=1))
        return
    d = date.fromisoformat(args[1]) if len(args) > 1 else today_et()

    streams = fetch_streams()
    rec = check_day(d, streams)

    log = [r for r in load_log() if r["date"] != rec["date"]]
    log.append(rec)
    save_log(log)
    build_page(log)

    print(json.dumps({"date": rec["date"], "verdict": rec["verdict"],
                      "hits": rec["hits"], "blocks": len(rec["blocks"]),
                      "note": rec["note"]}, indent=1))


if __name__ == "__main__":
    main()
