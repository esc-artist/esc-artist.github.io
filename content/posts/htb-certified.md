---
title: "HTB: Certified"
date: 2026-11-06
draft: false
tags: ["htb", "windows", "active-directory", "acl-abuse", "esc9", "shadow-credentials"]
cover:
  image: /images/htb-certified-cover.jpg
  alt: "A chain of access-control links leading to a certificate, phosphor green on black"
  relative: false
---

Certified. Windows, medium, retired. The chain in one line: ACL abuse chain → shadow credentials → ESC9.

But the box isn't really about the chain. It's about how one small permission — WriteOwner on a group — is the whole box, if you follow where it leads.

## Initial access

Pre-given credentials for user `judith.mader`. Running BloodHound shows a clear ACL abuse escalation chain: the user has WriteOwner on a group, which has GenericWrite over account `management_svc`, which in turn has GenericAll over account `ca-operator`. So, the steps for getting from `judith.mader` to `ca-operator` are:

- Use user `judith.mader`, with WriteOwner over group Management, to write `judith.mader` as owner of Management
- Use user `judith.mader`, owner of group Management, to grant full control over group Management to `judith.mader`
- Use user `judith.mader`, with full control over group Management, to add user `judith.mader` to group Management
- Use user `judith.mader`, member of group Management with GenericWrite over user `management_svc`, to perform a shadow credential attack on user `management_svc`
- Use user `management_svc`, with GenericAll over `ca-operator`, to perform a shadow credential attack on user `ca-operator`

The shadow credential attacks are most easily automated with certipy. Impacket and rpc handle the earlier steps, as shown in the New Information section below.

## Root: ESC9

Running certipy with `ca-operator` shows that a template in which `ca-operator` can enroll is vulnerable to ESC9. ESC9 takes advantage of `SZOID_NTDS_CA_SECURITY_EXT` being disabled for a particular template. This means the UPN of a user who can enroll in that certificate (`ca-operator`) can be changed to a target user (administrator), that user registered for a certificate, and the resulting certificate will allow authentication as the target user (administrator).

The steps for exploiting ESC9 are identical to those for exploiting ESC16, as shown in the box Fluffy. See notes on that box for detailed exploitation steps.

---

## Takeaways

WriteOwner looks harmless. It's one permission on one group, and it doesn't even grant you membership — but ownership lets you grant yourself full control, full control lets you add yourself to the group, and the group is the key to the next account. The whole escalation is just that one permission, walked to its conclusion, twice over.

The other thing worth keeping: ESC9 and ESC16 are the same trick wearing different clothes. Both come down to the CA trusting a UPN you were allowed to change. Learn the ESC16 steps once and you have ESC9 for free.

---

## Reference

A few things worth keeping from this box's notes:

**WriteOwner → group member.** Three steps, in order:

```bash
# 1) Set owner
impacket-owneredit -action write -new-owner '<target-user>' -target-dn 'CN=<group>, CN=Users, DC=<domain>, DC=<local>' <domain.local>/<user>:<pass> -dc-ip <ip>

# 2) Grant full control over group
impacket-dacledit -action 'write' -rights 'WriteMembers' -principal '<target-user>' -target-dn 'CN=<group>, CN=Users, DC=<domain>, DC=<local>' <domain.local>/<user>:<pass> -dc-ip <ip>

# 3) Add user to group
net rpc group addmem "<group>" "<target-user>" -U <domain>/<user>%<pass> -S <ip>
```

**ESC9.** Follow the ESC16 exploitation steps, as described in the Fluffy box — change the UPN to administrator, enroll for a certificate, change the UPN back, authenticate with the certificate.
