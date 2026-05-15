---
layout: default
---

<div class="page-label">// <span>index</span></div>

<div class="intro">
  <h1>penetration tester.<br>student of systems.</h1>
  <p>OSCP. Working toward CPTS. Box notes, behavioral experiments, and a livestream when the hardware arrives.</p>
</div>

<div class="sections">
  <a href="{{ '/box-notes/' | relative_url }}" class="section-card">
    <div class="card-label">01 / notes</div>
    <h2>Box Notes</h2>
    <p>HTB writeups. Attack chains, rabbit holes, and what actually worked.</p>
  </a>

  <a href="{{ '/tamagotchi/' | relative_url }}" class="section-card">
    <div class="card-label">02 / project</div>
    <h2>Tamagotchi</h2>
    <p>Public behavioral accountability system. Token economy. Wheel of punishment.</p>
  </a>

  <div class="section-card coming-soon">
    <span class="soon-tag">coming soon</span>
    <div class="card-label">03 / live</div>
    <h2>Livestream</h2>
    <p>Live camera feed. Pending hardware.</p>
  </div>

  <a href="https://github.com/esc-artist" target="_blank" class="section-card">
    <div class="card-label">04 / code</div>
    <h2>GitHub</h2>
    <p>Repos, tools, and whatever else ends up public.</p>
  </a>
</div>

{% assign recent_posts = site.posts | limit: 3 %}
{% if recent_posts.size > 0 %}
<div class="page-label">// <span>recent box notes</span></div>
<ul class="posts-list">
  {% for post in recent_posts %}
  <li>
    <a href="{{ post.url | relative_url }}">
      <span class="post-title-link">{{ post.title }}</span>
      <span class="post-meta-inline">{{ post.date | date: "%Y-%m-%d" }}{% if post.difficulty %} · {{ post.difficulty }}{% endif %}</span>
    </a>
  </li>
  {% endfor %}
</ul>
{% endif %}
