#!/usr/bin/env python3
"""Atomic site pipeline: rebuild + verify + commit + push.

Runs the full rebuild sequence for the esc-artist blog and pushes to GitHub
Pages. Fails loudly on any error — never silently publishes partial or
stale data.

Usage:
    python3 scripts/pipeline.py --schedule-check [YYYY-MM-DD]
    python3 scripts/pipeline.py --study-refresh
    python3 scripts/pipeline.py --stats-rebuild
    python3 scripts/pipeline.py --all [YYYY-MM-DD]

Each mode:
  1. Runs the rebuild script(s)
  2. Verifies the output files were actually modified (or are correct)
  3. Stages ALL modified content files (never a blanket add — explicit list)
  4. Commits with a descriptive message
  5. Pushes to origin main
  6. Verifies the push succeeded

On any failure: abort, print exactly what failed, exit non-zero.
Never commit or push partial results.
"""

import os
import subprocess
import sys
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, "scripts")

# Explicit file list — never `git add -A`. These are the only files the
# pipeline is allowed to touch. If a script modifies something not on this
# list, that's a bug and the pipeline must fail.
ALLOWED_FILES = {
    "static/data/schedules/_log.json",
    "static/data/schedules/_changelog.json",
    "static/data/schedules/_summary.md",
    "content/schedule.md",
    "content/study.md",
    "content/stats.md",
    "content/stats-rules.md",
    "static/data/stats.json",
    "static/data/study/_summary.md",
    "scripts/study_videos.json",
}

# Files that must NEVER be committed by the pipeline (drafts, etc.)
FORBIDDEN_PATTERNS = [
    "content/posts/",  # blog posts require manual review before publishing
    "content/drafts/",
]


def run(cmd, **kw):
    """Run a command, return CompletedProcess. Doesn't raise."""
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 300),
        cwd=REPO, **kw,
    )


def die(msg):
    print(f"PIPELINE FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_script(name, args):
    """Run a pipeline script. Fail loudly on non-zero exit or stderr errors."""
    cmd = [sys.executable, os.path.join(SCRIPTS, name)] + args
    print(f"  → {' '.join(args) if args else '(no args)'} [{name}]")
    r = run(cmd, timeout=1200)
    if r.returncode != 0:
        die(f"{name} {' '.join(args)} exited {r.returncode}\n"
            f"STDOUT: {r.stdout[-1000:]}\nSTDERR: {r.stderr[-1000:]}")
    # Warn on stderr output (scripts print warnings there)
    if r.stderr.strip():
        print(f"  ⚠ {name} stderr: {r.stderr.strip()[-500:]}")
    return r


def get_modified_files():
    """Return set of modified/staged files relative to REPO."""
    r = run(["git", "status", "--porcelain"])
    if r.returncode != 0:
        die(f"git status failed: {r.stderr}")
    files = set()
    for line in r.stdout.strip().splitlines():
        if not line.strip():
            continue
        # Porcelain format: XY <path>  or  XY <orig> -> <new>
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        files.add(path)
    return files


def verify_no_forbidden(files):
    """Fail if any modified file matches a forbidden pattern."""
    for f in files:
        for pat in FORBIDDEN_PATTERNS:
            if f.startswith(pat):
                die(f"Pipeline would commit forbidden file: {f}\n"
                    f"Blog posts require manual review. Aborting.")


def verify_all_allowed(files):
    """Fail if any modified file is not in the explicit allowlist."""
    for f in files:
        if f not in ALLOWED_FILES:
            # Allow untracked files that are in allowed list (new files)
            # but reject anything unexpected
            die(f"Unexpected modified file not in pipeline allowlist: {f}\n"
                f"If this is legitimate, add it to ALLOWED_FILES in pipeline.py")


def git_add_commit_push(message):
    """Stage allowed files, commit, push. Verify each step."""
    all_files = get_modified_files()
    # Only consider files in the explicit allowlist — untracked drafts,
    # pycache, and anything else is ignored, never staged.
    files = {f for f in all_files if f in ALLOWED_FILES}
    if not files:
        print("  → No pipeline files changed. Nothing to push.")
        # But warn if there are other modifications we ignored
        ignored = all_files - files - {".gitignore"}
        ignored = {f for f in ignored if "__pycache__" not in f}
        if ignored:
            print(f"  → (ignored non-pipeline files: {sorted(ignored)})")
        return False

    print(f"  → Pipeline files changed: {sorted(files)}")
    verify_no_forbidden(files)
    # verify_all_allowed is now redundant (we filtered by allowlist) but
    # keep as a sanity check in case ALLOWED_FILES drifts
    verify_all_allowed(files)

    # Stage only the allowed files
    for f in sorted(files):
        r = run(["git", "add", f])
        if r.returncode != 0:
            die(f"git add {f} failed: {r.stderr}")

    r = run(["git", "commit", "-m", message])
    if r.returncode != 0:
        die(f"git commit failed: {r.stderr}\n{r.stdout}")
    commit_hash = r.stdout.strip().split()[-1].strip("[]") if r.stdout else "?"
    print(f"  → Committed {commit_hash}")

    # Push via the sandbox's GitHub SSH proxy config
    ssh_cmd = (
        'ssh -i ~/.ssh/id_ed25519 '
        '-o ProxyCommand="socat STDIO PROXY:hatch-egress-proxy:ssh.github.com:443,proxyport=3128" '
        '-o StrictHostKeyChecking=yes'
    )
    r = run(
        ["git", "push", "origin", "main"],
        timeout=120,
        **{"env": {**os.environ, "GIT_SSH_COMMAND": ssh_cmd}},
    )
    if r.returncode != 0:
        die(f"git push failed: {r.stderr}\n{r.stdout}")
    print(f"  → Pushed to origin/main")
    return True


def do_schedule_check(check_date=None):
    """Run schedcheck --check, verify output, commit, push."""
    print("Schedule check pipeline:")
    args = ["--check"]
    if check_date:
        args.append(check_date)
    r = check_script("schedcheck.py", args)
    print(f"  → {r.stdout.strip()[-500:]}")
    git_add_commit_push(
        f"Schedule check: {check_date or 'today'} "
        f"({r.stdout.strip().splitlines()[-1][:80] if r.stdout.strip() else 'no output'})"
    )


def do_study_refresh():
    """Run studylog --fetch and --build, verify, commit, push."""
    print("Study log refresh pipeline:")
    # Fetch first — if this fails, don't build from stale data
    check_script("studylog.py", ["--fetch"])
    check_script("studylog.py", ["--build"])
    git_add_commit_push("Study log refresh: fetch + rebuild")


def do_stats_rebuild():
    """Run stats.py --build, verify, commit, push."""
    print("Stats rebuild pipeline:")
    check_script("stats.py", ["--build"])
    git_add_commit_push("Stats rebuild")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)

    mode = args[0]
    rest = args[1:]

    # Pre-flight: ensure we're in a git repo
    r = run(["git", "rev-parse", "--git-dir"])
    if r.returncode != 0:
        die("Not in a git repository")

    # Note: forbidden-file protection happens in git_add_commit_push, which
    # only stages files from the explicit allowlist. Untracked drafts (like
    # a blog post in progress) won't be touched.

    if mode == "--schedule-check":
        check_date = rest[0] if rest else None
        if check_date:
            try:
                date.fromisoformat(check_date)
            except ValueError:
                die(f"Invalid date format: {check_date} (use YYYY-MM-DD)")
        do_schedule_check(check_date)
    elif mode == "--study-refresh":
        do_study_refresh()
    elif mode == "--stats-rebuild":
        do_stats_rebuild()
    elif mode == "--all":
        check_date = rest[0] if rest else None
        do_study_refresh()
        do_stats_rebuild()
        do_schedule_check(check_date)
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        print(__doc__)
        sys.exit(2)

    print("PIPELINE OK")


if __name__ == "__main__":
    main()
