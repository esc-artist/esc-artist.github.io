---
title: "Schedule Rules & Guard"
date: 2026-09-30
draft: false
---

The complete public rulebook for the [schedule log](/schedule/): what I have to do, how I'm judged, and the machinery that keeps the log honest. Not in the nav; it exists so I can audit it.

## The rules I follow

- **I file time blocks.** Each day's plan is a list of time blocks (e.g. 9:00–13:00, 14:00–18:00). Times only.
- **Every plan must total at least 6 hours.** A plan under 6h is filed anyway and marked `short_plan`. Six hours is aspirational — falling short is expected and accepted, but it's marked.
- **The plan locks at filing.** I can file the morning of, the night before, or earlier — but once filed, it can't be changed, and I'm judged against the original. No exceptions, no "just this once."
- **Filing must predate the first block.** A plan committed after its first block started is `late_plan`: unverifiable, marked.
- **A block is HIT if a stream was live 10 minutes in, having started no later than 10 minutes after the block began.** Ten minutes of grace on both ends — my choice.
- **Blocks past midnight count toward the day they were planned on.** A 00:00–01:00 block on a 9/30 plan is 9/30's, not 10/1's.
- **Days with fewer than 6 streamed hours are marked**, regardless of when during the day those hours happened.
- **No rollover.** Extra minutes don't reduce later blocks. A 12-hour day buys nothing tomorrow. No retroactive catch-up. Each day's plan stands alone. The schedule is a consistency device, not an hours ledger — hours are the [Study Log](/study/)'s job.

## Verdicts

- `adhered` — every block hit.
- `partial` — some blocks hit.
- `missed` — no blocks hit.
- `no_plan` — nothing filed. A valid outcome, marked.
- `short_plan` — plan totaled under 6h.
- `late_plan` — filed after the first block started; unverifiable.
- `pending` — blocks still in progress when checked; the final check runs around 1:30am ET.

## The guard (anti-tampering machinery)

**The snapshot (canonical copy).** When a plan is filed, its full content is saved — before the first block starts — to a snapshot file outside the git repo (`~/workspace/sched-guard/hidden_files/state.json`), together with a sha256 hash of the filed file. The snapshot is canonical: if the plan file in the repo and the snapshot ever disagree, the snapshot wins. Always.

**The nightly sweep.** Every night around 1:30am ET, the checker re-hashes *every* filed plan — not just the day being graded — and compares each hash to its snapshot. Any post-filing change, to any plan, including plans already graded on earlier days:

1. Is logged as a public entry in the changelog on the schedule page.
2. Is reverted: the original plan is restored from the snapshot.
3. Is graded against the original schedule. Deviations from the original count as violations.

The per-day check runs the same revert-and-log step for the day it grades before judging it.

**The changelog.** Every revert becomes a public, permanent entry: the date, what happened, and the before/after blocks. Entries are never edited or deleted.

**Refusal policy.** Migi refuses any request to change a filed plan after filing — the same standing refusal as the CPTS countdown date. No debate.

## Honest limits

I own the repo, so I can technically edit anything in it. This system does not make tampering impossible — it makes it pointless: edits are publicly logged and automatically reverted, usually within a day. The snapshot lives outside the repo, where repo edits can't reach it. Same pattern guards the CPTS countdown date: weekly verify, public history, auto-restore.
