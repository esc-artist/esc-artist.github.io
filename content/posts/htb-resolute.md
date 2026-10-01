---
title: "HTB: Resolute"
date: 2026-10-01
draft: false
tags: ["htb", "windows", "active-directory", "ldap", "password-spraying", "dnsadmins"]
cover:
  image: /images/htb-resolute-cover.jpg
  alt: "Glowing DNS zone tree with a poisoned node, phosphor green on black"
  relative: false
---

Resolute. Windows, medium, retired. The chain in one line: null-auth LDAP → a password sitting in a description field → spraying it across the domain → a hidden PowerShell transcript → DnsAdmins DLL injection on the DC.

But the box isn't really about the chain. It's about reading everything the domain tells you for free, and then reading the things nobody bothered to hide properly.

## Initial access

LDAP was accessible with null authentication. That's the whole foothold handed over without a fight: enumerate the domain, no creds required.

In the `description` attribute of one of the users, it said their password was set to 'Welcome123!'. It didn't work for that user — passwords get changed, descriptions don't. But a password in a description field is worth spraying across every other account, because people reuse. One quick spray and it landed: user "melanie", a member of Remote Management Users. Shell as melanie.

The lesson is a small one, but it keeps paying: when you find a credential that doesn't work where you found it, spray it everywhere else before you throw it away.

## Root: PSTranscripts

There didn't appear to be much on the machine, so I started looking for hidden files. In `C:\` there was a hidden directory, "PSTranscripts", which contained a log of PowerShell commands — and in that log, credentials for user "ryan".

Ryan was a member of both Remote Management Users and DnsAdmins. Quick research suggested that members of the DnsAdmins group could get the DNS server to run arbitrary DLLs — and on a domain controller, the DNS server *is* the domain controller. The sequence, from my notes:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">dnsadmins.txt</span></div>
<div class="terminal-body"><pre>dnscmd.exe &lt;dc_fqdn&gt; /config /serverlevelplugindll &lt;c:\path\to\mal.dll&gt;
sc.exe stop dns
sc.exe start dns</pre></div>
<div class="vim-status"><span>"dnsadmins.txt" [readonly] 3L</span><span>1,1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;All</span></div>
</div>

DNS restarts, loads your DLL, and your DLL runs as SYSTEM. Simple one. Shell as SYSTEM.

---

## Takeaways

This box rewards two habits. First, read the LDAP attributes nobody bothers to clean up — description fields, comments, notes. They're free with null auth and they're full of passwords people forgot they wrote down. Second, when a machine feels empty, look for hidden files before you look for exploits. The transcript log wasn't hidden by anything cleverer than a directory attribute.

And the DnsAdmins trick is worth keeping in the back pocket permanently: any time you own a user in that group and the DNS server runs on the DC, it's game over via a malicious DLL.

---

## Reference

A few things worth keeping from this box's notes:

**Null-auth BloodHound.** If you can access LDAP without credentials, you may be able to run rusthound/sharphound without credentials too. Free graph, no account needed.

**DnsAdmins group.** If you own a user who is a member of the DnsAdmins group, you may be able to get the DNS server to run an arbitrary DLL, as follows:

```text
dnscmd.exe <dc_fqdn> /config /serverlevelplugindll <c:\path\to\mal.dll>
sc.exe stop dns
sc.exe start dns
```

The DNS service restarts and loads the DLL as SYSTEM.
