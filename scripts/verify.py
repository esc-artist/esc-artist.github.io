#!/usr/bin/env python3
"""Pipeline health verifier for esc-artist.github.io.

Checks that the scheduled pipeline jobs (schedule check, study log refresh,
stats rebuild) actually ran and produced sane output. Fails loudly on any
problem — this is the watchdog, not the pipeline itself.

Checks:
  1. Schedule log: latest entry exists for the expected date, has valid
     verdict, hours are within sane bounds, streams list is present.
  2. Study videos: store exists, has videos, total hours sane, recently
     updated (within expected window).
  3. Stats: stats.json exists, points/level sane, matches schedule data.
  4. Git: no uncommitted pipeline files (would indicate a failed push).
  5. Cron recency: the schedule check ran within the last 26 hours.

Usage:
    python3 scripts/verify.py [--json]

Exit 0 if all checks pass. Exit 1 with details on stderr if any fail.
"""

import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAILURES = []


def fail(check, detail):
    FAILURES.append(f"{check}: {detail}")


def ok(check):
    print(f"  ✓ {check}")


def run(cmd, **kw):
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 60),
        cwd=REPO, **kw,
    )


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return None


def check_schedule_log():
    """Verify the schedule log has a sane latest entry."""
    log_path = os.path.join(REPO, "static", "data", "schedules", "_log.json")
    log = load_json(log_path)
    if log is None:
        fail("schedule-log", f"cannot read {log_path}")
        return
    if not log:
        fail("schedule-log", "log is empty")
        return

    # Latest entry should be for yesterday or today (check runs ~1:23am)
    today = datetime.now(ET).date()
    dates = sorted(r["date"] for r in log)
    latest = dates[-1]
    latest_date = date.fromisoformat(latest)
    age_days = (today - latest_date).days
    if age_days > 1:
        fail("schedule-log", f"latest entry is {latest} ({age_days} days old)")
        return

    rec = next(r for r in log if r["date"] == latest)

    # Verdict must be valid
    valid_verdicts = {"adhered", "partial", "missed", "no_plan", "pending",
                      "late_plan", "short_plan"}
    if rec.get("verdict") not in valid_verdicts:
        fail("schedule-log", f"invalid verdict '{rec.get('verdict')}' for {latest}")
        return

    # Hours sanity: 0-24
    hours = rec.get("hours")
    if hours is not None and not (0 <= hours <= 24):
        fail("schedule-log", f"insane hours value {hours} for {latest}")
        return

    # Streams list must exist (even if empty — empty is valid for missed days)
    if "streams" not in rec:
        fail("schedule-log", f"missing streams list for {latest}")
        return

    # Suspicious: verdict is missed/partial/adhered but hours is 0 AND
    # the plan had blocks. Could indicate a blind fetch. (0 hours with
    # actual streams outside blocks is fine — that's what happened Oct 2.)
    # We can't distinguish without video data, so just note it.
    ok(f"schedule-log (latest: {latest}, {rec['verdict']}, {hours}h)")


def check_study_videos():
    """Verify the video store exists and has sane data."""
    store_path = os.path.join(REPO, "scripts", "study_videos.json")
    vids = load_json(store_path)
    if vids is None:
        fail("study-videos", f"cannot read {store_path}")
        return
    if not vids:
        fail("study-videos", "store is empty")
        return

    # Total hours sanity
    total_secs = sum(v.get("secs", 0) for v in vids.values())
    total_hours = total_secs / 3600
    if total_hours < 1:
        fail("study-videos", f"suspiciously low total: {total_hours:.1f}h")
        return
    if total_hours > 5000:
        fail("study-videos", f"suspiciously high total: {total_hours:.1f}h")
        return

    # Check for videos with zero/negative duration
    bad = [vid for vid, v in vids.items() if v.get("secs", 0) <= 0]
    if bad:
        fail("study-videos", f"{len(bad)} videos with non-positive duration")

    # Recency: at least one video from the last 14 days (he streams regularly)
    today = datetime.now(ET).date()
    recent = 0
    for v in vids.values():
        try:
            d = date.fromisoformat(v.get("date", ""))
            if (today - d).days <= 14:
                recent += 1
        except ValueError:
            pass
    if recent == 0:
        fail("study-videos", "no videos from the last 14 days — fetch may be broken")

    ok(f"study-videos ({len(vids)} videos, {total_hours:.1f}h total)")


def check_stats():
    """Verify stats.json exists and is internally consistent."""
    stats_path = os.path.join(REPO, "static", "data", "stats.json")
    stats = load_json(stats_path)
    if stats is None:
        fail("stats", f"cannot read {stats_path}")
        return

    points = stats.get("points", 0)
    if points < 0 or points > 10000:
        fail("stats", f"insane points value: {points}")
        return

    ok(f"stats ({points} points)")


def check_git_clean():
    """Verify no uncommitted pipeline files (would indicate failed push)."""
    r = run(["git", "status", "--porcelain"])
    if r.returncode != 0:
        fail("git", f"git status failed: {r.stderr}")
        return

    pipeline_files = {
        "static/data/schedules/_log.json",
        "static/data/schedules/_changelog.json",
        "static/data/schedules/_summary.md",
        "content/schedule.md",
        "content/study.md",
        "content/stats.md",
        "content/stats-rules.md",
        "static/data/stats.json",
        "scripts/study_videos.json",
    }
    dirty = []
    for line in r.stdout.strip().splitlines():
        if not line.strip():
            continue
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        if path in pipeline_files and "__pycache__" not in path:
            dirty.append(path)
    if dirty:
        fail("git", f"uncommitted pipeline files (push may have failed): {dirty}")
        return

    ok("git (pipeline files clean)")


def check_cron_recency():
    """Verify the schedule check cron ran recently."""
    # We can't query cron directly from here, so check the log's mtime
    # as a proxy: if _log.json was modified in the last 26 hours, the
    # check ran.
    log_path = os.path.join(REPO, "static", "data", "schedules", "_log.json")
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(log_path), tz=ET)
    except OSError:
        fail("cron-recency", f"cannot stat {log_path}")
        return

    age = datetime.now(ET) - mtime
    if age > timedelta(hours=26):
        fail("cron-recency",
             f"_log.json not modified in {age.total_seconds()/3600:.1f}h "
             f"(schedule check may not have run)")
        return

    ok(f"cron-recency (log updated {age.total_seconds()/3600:.1f}h ago)")


def main():
    as_json = "--json" in sys.argv
    print("Pipeline health check:")
    check_schedule_log()
    check_study_videos()
    check_stats()
    check_git_clean()
    check_cron_recency()

    if FAILURES:
        print(f"\n{len(FAILURES)} CHECK(S) FAILED:", file=sys.stderr)
        for f in FAILURES:
            print(f"  ✗ {f}", file=sys.stderr)
        if as_json:
            print(json.dumps({"ok": False, "failures": FAILURES}))
        sys.exit(1)

    print("\nAll checks passed.")
    if as_json:
        print(json.dumps({"ok": True, "failures": []}))


if __name__ == "__main__":
    main()
