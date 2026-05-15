---
layout: default
title: Box Notes
permalink: /box-notes/
---

<div class="page-label">// <span>box notes</span></div>

{% if site.posts.size > 0 %}
<ul class="posts-list">
  {% for post in site.posts %}
  <li>
    <a href="{{ post.url | relative_url }}">
      <span>
        <div class="post-title-link">{{ post.title }}</div>
        {% if post.tags %}
        <div class="post-tags">
          {% for tag in post.tags %}<span class="tag">{{ tag }}</span>{% endfor %}
        </div>
        {% endif %}
      </span>
      <span class="post-meta-inline">
        {{ post.date | date: "%Y-%m-%d" }}<br>
        {% if post.os %}{{ post.os }}{% endif %}{% if post.difficulty %} · {{ post.difficulty }}{% endif %}
      </span>
    </a>
  </li>
  {% endfor %}
</ul>
{% else %}
<p style="color: var(--text-dimmer); margin-top: 2rem;">No notes yet.</p>
{% endif %}
