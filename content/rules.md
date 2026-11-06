---
title: "Rules"
date: 2026-11-06
draft: false
---

The rulebook for this site: how the CPTS exam date is handled, and how study hours turn into points, levels, and ranks. Everything is computed from public data — stream durations — starting 2026-08-30.

## CPTS exam date

The exam target date lives on the [CPTS page](/cpts/) and in `static/data/cpts-target.json`, with a public history of every change.

- **Date changes are logged, not reverted.** If the target date moves, the old date, the new date, and the date of the change are added to the history on the CPTS page. Nothing is silently changed and nothing is rolled back.
- **Accountability is the changelog.** The history is the record, and it stays public.
- The date is changed by editing `static/data/cpts-target.json` (target + a history entry), not by editing the CPTS page directly.

## Points

| Action | Points |
|---|---|
| 1 hour studied (streamed) | 1 |
| 6+ hour day | +3 |
| Each day of a 3+ day run of 6h days | +2 |

Points never expire and are never taken away. Each point also buys 16.67 minutes of unblocked screen time, usable the day after it's earned — see Screen time below.

## Levels

1 level = 20 points. Thresholds are absolute: level 5 always means 250 points of work, no matter the rank.

1. Slacker, 2. Drifter, 3. Dabbler, 4. Restless, 5. Hungry, 6. Driven, 7. Grinder, 8. Disciplined, 9. Academic, 10. Scholar, 11. Relentless, 12. Obsessive, 13. Elite, 14. Apex

## Ranks

Ranks are earned only by passing certifications — never by points. The current rank is set by hand when an exam is passed.

| Span | Est. hours | Levels |
|---|---|---|
| OSCP → CPTS | ~320h | 10 |
| CPTS → CAPE | ~200h | 6 |
| CAPE → OSEP | ~350h | 10 |
| OSEP → OSWE | ~350h | 10 |
| OSWE → OSED | ~450h | 13 |

When a rank is earned, the level resets to 1 in the new rank. The peak level from the old rank is kept as a Veteran badge — retired, not lost.

## Badges

Badges are earned for hours totals, single-day feats, streaks of 6-hour days, streaks of studying at all, and progress toward the current exam's estimated hours. The full list — First Stream, First Blood, Centurion, Grinder, Hat Trick, Week Clear, Comeback, Weekend Warrior, No Zero Week, and the rest — is on the [Stats Rules](/stats-rules/) page.

## Screen time

Points are spent on entertainment. Each point buys 16.67 minutes of unblocked screen time, usable the day after it's earned — yesterday's points are today's budget. One session per day; unused minutes don't roll over.

Blocked by default, at the DNS level: a Pi-hole on the home network sinkholes Instagram, TikTok, Netflix, Hulu, HBO Max, Apple TV+, and Reddit (domains, subdomains, and CDN hosts). YouTube is deliberately excluded — it's a study tool.

To spend the budget: open the TV control page (linked from the TV Budget card on [stats](/stats/) — the URL is stored in your browser, never in the repo), enter the Pi-hole admin password, and tap Start. Blocking lifts for exactly the earned minutes, then Pi-hole's built-in timer re-enables it automatically. If anything crashes, it fails closed — blocking stays on.
