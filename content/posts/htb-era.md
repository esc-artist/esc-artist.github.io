---
title: "HTB: Era"
date: 2026-11-07
draft: false
tags: ["htb", "linux", "username-enumeration", "brute-force", "idor", "access-control", "php", "ssh2", "scheduled-binary", "binary-hijacking"]
cover:
  image: /images/htb-era-cover.jpg
  alt: "A file management website, an FTP server, and a scheduled antivirus monitor, phosphor green on black"
  relative: false
---

Era. Linux, medium, retired. The chain in one line: username enumeration → brute force login → IDOR → web app access control abuse → PHP wrapper abuse → scheduled binary hijacking.

But the box isn't really about the chain. It's about a file manager that trusts the id in the URL, trusts the user in the security-question panel, and trusts a binary just because it looks right — and a root path that only works once you stop trying to race it.

## Initial access

A website and an FTP server are running. FTP doesn't accept anonymous access. The website has a subdomain, revealing a file management site. There is a security questions login page that has username enumeration. Brute forcing usernames with ffuf gives a short list of usernames. Brute forcing the usernames with common passwords on the login page gives a set of credentials, `yuri:mustang`.

Uploaded files are fetched using an `id` parameter in the url. Fuzzing for a range of possible ids reveals two zips, an IDOR vulnerability.

One of these zips has the source code and original database of the site. One of the users is `admin_ef01cab31aa`, unlikely to show up in earlier username enumeration. Within the authenticated site dashboard, there is a panel to change the security question answers. It allows you to do so not just for your current user but for any user. Doing so for the `admin_ef01cab31aa` allows you to sign into their account.

FTP is accessible via `yuri:mustang`. There is one directory with web server configuration files, another with php library files. One of the included libraries is `ssh2.so`.

The site source code shows that there is an admin-only feature that runs php's `fopen()` on a given file, and takes a url parameter that prepends a wrapper to the file to be opened. Using the `ssh2.exec://` wrapper with `yuri:mustang` and `127.0.0.1`, with a `#` character at the end to nullify the appended file path, allows code execution via ssh. Shell as "yuri" user.

## Root: scheduled binary hijacking

Inspection with pspy shows that a custom antivirus executable, "monitor", is being run periodically by a script running as root. Replacing it does not execute the replacement executable, instead generating an error message in the log file stating that the executable is not signed. Pspy output shows that the executable is being checked for some sort of signature, and only then run. I tried to abuse this race condition by creating a script that continually swapped the executable between the legitimate, signed one and my malicious one, but this didn't work. Instead, you can dump the part of the executable that is being checked (as shown by pspy), and add it to your own executable, using objcopy. This allows the malicious executable to run. Swapped it for an executable that is a simple C wrapper for a shell command that creates a SUID bash executable. Running that executable with the `-p` flag gives shell as root.

---

## Takeaways

The initial access is a stack of small trust failures, each one unremarkable on its own: the login page tells you which usernames exist, the file fetcher trusts an id, the security-question panel trusts whoever is logged in to change anyone's answers, and `fopen()` trusts a wrapper. None of them is the box — together they are.

The root is the memorable part, and it's a lesson in not forcing the race. Swapping the binary back and forth against the signature check didn't work. Reading what the check actually looks at, and copying that piece into your own binary with objcopy, did. When a check is beating you, look at the check.

---

## Reference

**New information:**

- When used even in just file-read, rather than file inclusion, php functions, the `ssh2.exec://` wrapper can execute code.
- Try many characters, including `#`, when trying to nullify an appended string to an input field.
