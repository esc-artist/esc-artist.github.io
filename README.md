# esc-artist.github.io

Personal site. Jekyll on GitHub Pages.

## Structure

```
_posts/          # Box notes — one .md file per box
_layouts/        # default.html, post.html
assets/css/      # main.css
box-notes/       # index page for writeups
tamagotchi/      # embeds Constantine-Tamagotchi repo
livestream/      # coming soon placeholder
```

## Adding a box note

```bash
vim _posts/YYYY-MM-DD-boxname.md
```

Front matter:

```yaml
---
layout: post
title: "Box Name"
date: YYYY-MM-DD
os: Windows       # or Linux
difficulty: Medium # Easy / Medium / Hard / Insane
tags: [tag1, tag2]
---
```

Then:

```bash
git add . && git commit -m "boxname writeup" && git push
```

GitHub Actions builds and deploys automatically.
