---
title: "HTB: Inception"
date: 2026-09-30
draft: false
tags: ["htb", "linux", "container-escape", "privesc"]
cover:
  image: /images/htb-inception-cover.jpg
  alt: "Nested wireframe containers receding into darkness, green on black"
  relative: false
---

Inception. Linux, medium, retired. The chain in one line: dompdf arbitrary file read → credential hunting → WebDAV webshell → arbitrary file write via a TFTP misconfig → `/etc/ld.so.preload` abuse.

But the box isn't really about the chain. It's about a container that lies to you about where things are.

## Initial access

Two ports open: 80 (http) and 3128 (Squid proxy). Port 80 was a template site. The only interesting thing in it was an HTML comment buried far down in the source: "Todo: test dompdf on php 7.x".

I scanned loopback through the proxy with nmap and spose.py — a tool for port-scanning through a proxy, useful thing to have around — and found 22 reachable through the proxy. Then I got stuck for a while. Eventually I just checked `/dompdf` directly — directory listing. dompdf 0.6.0, vulnerable to arbitrary file read via CVE-2014-2383.

From there I eventually read `/etc/apache2/000-default.conf`, which revealed a WebDAV endpoint and a credential file holding a crackable (md5) hash. Using cadaver with those creds, I uploaded a webshell.

Then came the long stupid part. I spent a long time trying to get a bind or reverse shell, and nothing worked. The shell was in a container and just wasn't reachable via the squid proxy. The revshell failing bothered me more than it should have — it didn't make sense, and there were a number of other strange details floating around. The box was deliberately misleading me. It wanted the attacker to think the squid proxy led to loopback on the target host. In reality, both the proxy and the website were inside the container.

---

## The container misdirection

This is the part worth writing about, so here's how I actually worked it out. My notes from the time start with: "Let's think this through. Let me first assemble the facts."

The facts:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">field-notes.txt</span></div>
<div class="terminal-body"><pre>facts:
  me (vpn):  10.10.14.239
  target:    10.129.56.242
  open:      80, 3128

squid:
  curl squid directly:     "Client IP: 192.168.0.1"
  curl loopback via squid: "Client IP: 127.0.0.1"
  proxy -&gt; 10.129.56.242 / 192.168.0.x ... access denied

webshell recon:
  interfaces: loopback, 192.168.0.10/24
  listening (all ifaces): 22, 80, 3128
  loopback via squid: 80, 22 open (22 NOT open publicly)
  port 80 identical direct vs proxied
  ssh to loopback via squid -&gt; 192.168.0.10 (same host as website)</pre></div>
<div class="vim-status"><span>"field-notes.txt" [readonly] 16L</span><span>1,1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;All</span></div>
</div>

The conclusion: 192.168.0.10 is a container on 10.129.56.242, and all three services — 80, 22, *and* 3128 — run inside it. Ports 80 and 3128 are published through the target; 22 is reachable only through the squid proxy. Squid is running on the container, not the target, and squid's internal interface is the container's loopback.

The box was designed to make you believe only port 80 was containerized, squid was on the target, and ssh was on the target's loopback. In reality, 80, 22, and 3128 all run in the container, all published through the target, and squid proxies to the container's loopback.

And suddenly the bind shell made sense. I'd run nc in the container listening on all interfaces, then proxied through squid — but squid could only reach loopback, and I'd aimed at 192.168.0.10. I retried against loopback with a bind shell. It worked. :)

The revshell struggle was never a technical failure. It was a wrong mental model.

---

## Foothold to user

With the network understood, I uploaded a more interactive PHP webshell for convenience and kept digging. There was a wordpress directory with a wp-config file containing a database password. I SSH'd through squid to 127.0.0.1's ssh, thinking I finally had a shell on the target machine. The user had sudo ALL — giving me root — except the root flag turned out to be a riddle. Still in the container.

That sent me back to the network layout. I ran nmap against the host's container interface (not docker, apparently): 192.168.0.1, with ports 53, 22, and 21 open. I SSH'd into the host machine through that interface using the same database creds. Shell as a low-priv user, on the real box this time.

(Useful pattern from this box: `ssh -J <user>@<jump> <user>@<target>` for hopping through.)

---

## Root: /etc/ld.so.preload via TFTP

First I tried the classic container privesc: find mounted directories, drop a SUID bash. Dead — there was a UID mapping that made container root a high-numbered UID on the host.

FTP sitting exposed on the container interface was conspicuous. TFTP was configured too, and running as the root user. Through TFTP I had both read and write: I could read world-readable files and overwrite world-writable ones. The interesting bit: creating a *non-existent* file via TFTP from the container landed root-owned on the host.

First idea: write an authorized_keys file into root's .ssh. Failed — presumably StrictModes was set in sshd_config, requiring 600, while everything I wrote via TFTP came out 666. SUID bits didn't survive either.

Next: `apt update` was being run by cron every 5 minutes. PATH-hijack it? Reasonable thought, except there was no way to make my binary or script executable. Dead end.

Quick research suggested `/etc/ld.so.preload`. It works like the `LD_PRELOAD` environment variable, except no variable needs to be set — the file just has to exist. And luckily, it didn't exist yet on the system.

I got it working. The .so used a constructor that ran whenever any dynamically-linked SUID binary executed: it copied /bin/bash to /tmp/bash, chown'd it 0:0, chmod'd it 04755, and cleaned up the preload file. Then `/tmp/bash -p`. Shell as root.

The privesc.c, as written in my notes:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/stat.h>
__attribute__((constructor)) void privesc() {
    unlink("/etc/ld.so.preload");
    if (system("cp /bin/bash /tmp/bash") != 0) {
        perror("copy failed");
    }
    if (chown("/tmp/bash", 0, 0) != 0) {
        perror("chown failed");
    }
    if (chmod("/tmp/bash", 04755) != 0) {
        perror("chmod failed");
    }
}
```

---

## Takeaways

The box's whole trick was getting the attacker to misrepresent what was containerized and what wasn't. Every weird detail — the revshell failing, the ssh that wasn't where it looked, the proxy that wasn't on the host — was one wrong assumption stacked on another. Assembling the facts on paper is what broke it, not another scan.

On the privesc side: the obvious paths all died (SUID bash via mounts, authorized_keys, PATH hijacking cron). The thing that worked was the weird one — a TFTP quirk creating root-owned files, plus a preload file that only needs to exist. Worth the research detour.
