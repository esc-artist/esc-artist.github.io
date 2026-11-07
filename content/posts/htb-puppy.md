---
title: "HTB: Puppy"
date: 2026-11-07
draft: false
tags: ["htb", "windows", "active-directory", "bloodyad", "keepass", "dpapi", "impacket", "winpeas", "evil-winrm"]
cover:
  image: /images/htb-puppy-cover.jpg
  alt: "A puppy, an Active Directory domain controller, a KeePass vault, and a DPAPI key, phosphor green on black"
  relative: false
---

Puppy. Windows, medium, retired. The chain in one line: write access over a group → add self → KeePass (kdbx) cracking → write access over a user, change pass → write access over a user, enable disabled account → credential hunting → DPAPI decryption.

But the box isn't really about the chain. It's about write access being the whole box — every step is just finding something you can write to, and then writing to it.

## Initial access

Given credentials for low-priv user `levi.james`. SMB had a share "DEV", not readable or writable. bloodyad showed write access over the "Developers" group. Added my user to the group, read the DEV share (finicky, had to add immediately before reading the share). The share contained a file "recovery.kdbx", a KeePass database. Cracked it (`keepass2john.py` — had to download, the built-in version didn't work — cracked with hashcat), opened it (KeePassXC on Linux). It contained credentials for a bunch of users, only one of which was valid — user `ant.edwards`.

Using bloodyad again, it showed `ant.edwards` had write access over user `adam.silver`. I changed `adam.silver`'s password, but SMB auth was showing `STATUS_ACCOUNT_DISABLED`. Quick research showed I could, with write access, use bloodyad to enable the account (command in New Information). `adam.silver` was a member of Remote Management Users. Had to enable immediately before logging in (evil-winrm). Shell as user.

## Root

In `C:\` was a directory "Backups". It contained a website backup `.zip`, which contained the file "nms-auth-config.xml.bak". This appeared to contain LDAP config info, including creds for user `steph.cooper`. `steph.cooper` was also a member of Remote Management Users. Shell as `steph.cooper`.

My earlier enumeration showed there was another account, `steph.cooper-adm`. The same creds didn't work for this account. Ran WinPEAS, saw that `steph.cooper` had some DPAPI files. After some finagling (see New Information), I got the key and used it to decrypt the credential file. Used impacket-dpapi for both key extraction and credential decryption. It contained creds for `steph.cooper-adm`, an Administrator. Shell as administrator.

---

## Takeaways

Puppy is a box about ACLs, not exploits. Nothing here is a vulnerability in the usual sense — it's all write access, group membership, and a disabled account flag. The KeePass database is the only thing that looks like a classic box step, and even that is just credential hunting.

The DPAPI part is the one to remember: get the masterkey, decrypt the credential file, and don't forget the `-sid` flag — without it, it fails.

---

## Reference

**New information:**

- Get group membership, bloodyad:
  - `bloodyad -d <domain> -i <dc_ip> -u <username> -p <pass> get membership <target_user>`
- Find writable objects, bloodyad:
  - `bloodyad -d <domain> -i <dc_ip> -u <username> -p <pass> get writable`
- Enable a disabled account (with write access), bloodyad:
  - `bloodyad --host <dc> -d <domain> -u <username> -p <pass> remove uac <target_username> -f ACCOUNTDISABLE`
- DPAPI — get masterkey, decrypt credential file(s):
  - Get masterkey, impacket-dpapi:
    - `impacket-dpapi masterkey -file <masterkey_file> -sid <user_sid> -password <user_pass>`
    - *Note: MUST use `-sid` flag, or it fails!*
  - Decrypt credential file, impacket-dpapi:
    - Copy the returned hex key from the above command, including the "0x", and use it in the following:
    - `impacket-dpapi credential -file <cred_file> -key <hex_key>`
