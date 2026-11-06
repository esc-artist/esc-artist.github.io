---
title: "HTB: Epsilon"
date: 2026-09-30
draft: false
tags: ["htb", "linux", "aws-lambda", "ssti", "git"]
cover:
  image: /images/htb-epsilon-cover.jpg
  alt: "Storm cloud shaped like a lambda symbol looming over a tiny server, deep orange on black"
  relative: false
---

Epsilon. Linux, medium, retired. The chain in one line: leaked `.git` directory → AWS Lambda enumeration → JWT forgery → Jinja2 SSTI → symlink race on a backup script → root.

But the box isn't really about the chain. It's about git history doing the attacker's recon for them. One careless commit handed over cloud keys, and everything after that was just following the thread.

## Initial access

Three open TCP ports: 22, 80, 5000. Port 80 gave a 403 Forbidden at the web root, but it had a `.git` directory sitting exposed. Dumped it with git-dumper. Inside: a `server.py`, and another `.py` that looked AWS lambda-related — containing an AWS endpoint (`http://cloud.epsilon.htb`), an access key, and a key ID.

Enumerating lambda, there was just one function, and its source code contained some API key.

Port 5000 was a Flask website. The `server.py` from the git dump suggested it used a JWT for authorization. Forging a JWT with the key from the lambda function worked — `server.py` basically laid out the forging and usage steps.

The now-accessible page used `render_template()` on user input. So: SSTI. Testing confirmed it, and a revshell via Jinja2 SSTI followed. Shell as user "tom".

---

## Root

Two backup directories told the story: `/opt/backups` was writable, `/var/backups/web_backups` was readable, and files were being added to and removed from the latter on a schedule. Running pspy showed a `.sh` script running from `/bin` — readable — that was, among other things, tar'ing some files into `web_backups`, including one file from the writable `/opt/backups` directory. That file only stayed in the writable directory briefly.

So: replace it with a symlink, and the root-run tar follows it — root-privileged file read. I wrote a small script to win the race, then read `/root/.ssh/id_rsa`. Shell as root.

---

## Reference: AWS Lambda enumeration

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">aws-notes.txt</span></div>
<div class="terminal-body"><pre>$ sudo apt install awscli
$ aws configure

$ aws --endpoint-url &lt;url&gt; lambda list-functions
$ aws --endpoint-url &lt;url&gt; lambda get-function --function-name &lt;name&gt;
# look for "Code:" in the json, then go to the "Location:" url</pre></div>
</div>

---

## Reference: Jinja2 SSTI

First, make sure it is Jinja2. This decision tree from PortSwigger is the quick way to identify the engine:

<figure class="diagram">
<img src="/images/ssti-flowchart.png" alt="SSTI template engine identification flowchart">
<figcaption>Diagram: <a href="https://portswigger.net/web-security/server-side-template-injection">PortSwigger</a></figcaption>
</figure>

Once confirmed, the shape of the attack is: enumerate the template config object to pull environment info, then walk the template object's class hierarchy to reach the builtins and get file read, then enumerate the subclasses to find a process-spawning class and get RCE.

For the exact payload strings, the SSTI page on HackTricks and PayloadsAllTheThings have the canonical ones.
