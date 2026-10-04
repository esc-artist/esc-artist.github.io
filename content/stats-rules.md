---
title: "Stats Rules"
summary: "how points, levels, and ranks work"
robotsNoIndex: true
---

The rulebook for the [stats](/stats/) page. Everything is computed from public data — stream durations — starting 2026-08-30.

## Points

| Action | Points |
|---|---|
| 1 hour studied (streamed) | 1 |
| 6+ hour day | +3 |
| Each day of a 3+ day run of 6h days | +2 |

Points never expire and are never taken away. Each point also buys 16.67 minutes of
unblocked screen time, usable the day after it's earned — see Screen time below.

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

| Badge | How |
|---|---|
| First Stream | First tracked study stream |
| First Blood | First 6-hour day |
| Warming Up | 10 total hours |
| Committed | 25 total hours |
| Half Century | 50 total hours |
| Centurion | 100 total hours |
| Centurion II | 250 total hours |
| Centurion III | 500 total hours |
| Centurion IV | 1000 total hours |
| Overtime | 8+ hours in a day |
| Marathon | 10+ hours in a day |
| Ultra | 12+ hours in a day |
| Grinder | 5 six-hour days |
| Grinder II | 10 six-hour days |
| Grinder III | 25 six-hour days |
| Grinder IV | 50 six-hour days |
| Hat Trick | 3 straight 6-hour days |
| Week Clear | 7 straight 6-hour days |
| Week Straight | 7 days straight studying |
| Fortnight | 14 days straight studying |
| Month Straight | 30 days straight studying |
| Halfway There | 50% of current exam's estimated hours |
| Three-Quarter | 75% of current exam's estimated hours |
| Exam Ready | 100% of current exam's estimated hours |
| Comeback | 6-hour day right after a zero day |
| Weekend Warrior | Studied Saturday and Sunday |
| No Zero Week | 7 days straight, none zero |

## Screen time

Points are spent on entertainment. Each point buys 16.67 minutes of unblocked
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
