---
title: "HTB: Sweep"
date: 2026-11-06
draft: false
tags: ["htb", "windows", "active-directory", "lansweeper", "password-spraying", "acl-abuse", "credential-dumping"]
cover:
  image: /images/htb-sweep-cover.jpg
  alt: "A rogue SSH server sweeping up credentials from a network scanner, phosphor green on black"
  relative: false
---

Sweep. Windows, medium, retired. The chain in one line: RID cycling with Guest → password spraying/guessing (user as pass) → rogue SSH server for creds capture from Lansweeper via scanning → ACL abuse → credential dumping and decryption.

But the box isn't really about the chain. It's about a scanner that will happily hand its own credentials to anyone who asks it to scan them.

## Initial access

There are some SMB shares related to Lansweeper. There is a site on port 81, the Lansweeper UI.

`impacket-lookupsid` works with Guest. I got a userlist.

There is a user "intern". I figured it'd be a simple password, so I tried `intern:intern` and it worked, both for the UI and SMB (nxc).

There appear to be ways to immediately get shell access from the Lansweeper UI, but they're all disabled.

Going through HackTricks, I tried setting up an SSH server and capturing credentials as described:

On attacking machine:

```bash
sudo apt install -y sshesame
```

Write the following to `./sshesame.conf`:

```yaml
server:
  listen_address: <attacker-ip>:<port>
```

```bash
sshesame --config sshesame.conf
```

On target Lansweeper web interface:

- Scanning → Scanning Targets → Add Scanning Target
- Type: IP Range → use your IP for start and end
- Set SSH port to listen_address port
- Scanning → Scanning Credentials → assign credentials to target (you)
- Click "Scan now"

It didn't work at first, but I strongly suspected it, so I reset the box and it worked. Got creds for `svc-inventory-lnx` user.

One other thing HackTricks says is that it's common for there to be a Lansweeper group that may have an ACE over a more privileged group. From bloodhound-python, that appears to be the case here — `svc-inventory-lnx` is a member of "Lansweeper Discovery", which has GenericAll over "Lansweeper Admins", which is a member of Remote Management Users. So if I can compromise `svc-inventory-lnx`, as I just did, I can get WinRM access.

So then I just had to add myself to the Lansweeper Admins group. I used `net rpc` to add intern and `svc-inventory-lnx` to the group. Initial access was evil-winrm.

## Root: SharpLansweeperDecrypt

Post-exploitation is on HackTricks too.

Using SharpLansweeperDecrypt (`LansweeperDecrypt.ps1`), got creds of `svc-inventory-win` user. Basically the tool finds and decrypts database creds, dumps scanning creds, finds the encryption key, and decrypts them. `svc-inventory-win` is an Administrator. Game.

---

## Takeaways

The whole box is Lansweeper trusting whatever you point it at. Point it at your own SSH server and it hands you a service account's credentials. Point it at nothing, and the stored creds are still sitting in its database, encrypted with a key the box also holds — so SharpLansweeperDecrypt just walks in and takes them.

And the entry is worth remembering for how cheap it was: Guest RID cycling for a userlist, then `intern:intern`. The box never asked for anything cleverer than guessing the obvious, once.

---

## Reference

A few things worth keeping from this box's notes:

**Rogue server cred capture.** On Lansweeper and possibly similar services, you can set up a rogue server and scan it to potentially capture creds. For Lansweeper and SSH, you can do it as described in Initial Access above — sshesame on your machine, add your IP as a scanning target, assign credentials, scan now.

**Lansweeper group ACEs.** It is common for there to be a Lansweeper group that may have ACEs over a more privileged group. Here, "Lansweeper Discovery" had GenericAll over "Lansweeper Admins", which was a member of Remote Management Users — so compromising a Discovery member meant WinRM.

**SharpLansweeperDecrypt.** Can be used to decrypt stored scanning creds in Lansweeper. It finds and decrypts the database creds, dumps the scanning creds, finds the encryption key, and decrypts them.
