---
title: "HTB: Arkham"
date: 2026-09-30
draft: false
tags: ["htb", "windows", "jsf-deserialization", "luks", "credential-hunting"]
cover:
  image: /images/htb-arkham-cover.jpg
  alt: "Gothic asylum on a hill at night, bats crossing a sickly green moon"
  relative: false
---

Arkham. Windows, medium, retired. The chain in one line: LUKS-encrypted disk image off a null-auth SMB share → Tomcat secrets sitting in plaintext → JSF ViewState deserialization → shell as Alfred → backup.zip → an Outlook .ost → creds for Batman, an Administrator.

The box is really about refusing to do the expensive thing when the cheap thing works.

// ──

## Initial access

A null-auth SMB share held a file called `backup.img` — a LUKS-encrypted image of a Linux server. Two paths forward: crack the encryption, or read around it. The walkthrough cracked it with hashcat. I tried that. It was taking ages.

So instead: `strings`, `awk`, and `grep` straight against the image. The Tomcat configuration files were sitting in there in plaintext. No cracking required.

Port 8080 ran JavaServer Faces (`.faces`). JSF is sometimes vulnerable to ViewState deserialization, and with the secrets pulled from the Tomcat XML configs, ysoserial, and some custom Python, you can build a serialized Java object that executes whatever command you want.

I tested with a pingback first. It worked. Getting an actual shell took more tries — something kept eating it, probably Defender. Transferring `nc.exe` to the machine and using `-e` got through. Shell as user Alfred.

// ──

## Root

My initial checks missed a file sitting in Alfred's Downloads directory: `backup.zip`. Found it manually, later. Getting it off the box was its own fight — it kept corrupting in transfer with the usual methods, and PowerShell execution policy blocked the others. In the end I used `cmd /c curl -T` to PUT the file to a custom server running on my own box.

Unzipped: a `.ost` file — Outlook messages. I moved it to my Windows VM and opened it with Kernel OST Viewer. In the Drafts folder were credentials for the Batman user. An Administrator.

(The walkthrough did a UAC bypass after the credential hunting. It wasn't needed for the flag, so it's not covered here.)

// ──

## Reference: cracking LUKS

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">luks-notes.txt</span></div>
<div class="terminal-body"><pre>$ # LUKS v1 (this box)
$ hashcat -m 14600 &lt;hash&gt;
$ # alternatives
$ luks2hashcat        # convert it to a crackable format
$ bruteforce-luks     # Kali tool, does the whole thing</pre></div>
</div>

LUKS is Linux full-disk encryption, v1 and v2, and you approach them differently. This box was v1: crackable directly with hashcat (`-m 14600`), or extract the header and crack just that.

But the actual lesson of this box: check for the plaintext first. The fastest crack is the one you never run.
