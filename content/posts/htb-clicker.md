---
title: "HTB: Clicker"
date: 2026-11-22
draft: false
tags: ["htb", "linux", "mass-assignment", "php-filter-bypass", "suid", "arbitrary-file-read", "setenv", "perl-env-hijacking", "xxe", "ld-preload"]
cover:
  image: /images/htb-clicker-cover.jpg
  alt: "A retro clicker-game leaderboard with its top score being rewritten by a rogue script, phosphor green on black"
  relative: false
---

Clicker. Linux, medium, retired. The chain in one line: PHP filter bypass / mass assignment web app admin escalation → webshell via upload manipulation → arbitrary file read in SUID binary → sudo SETENV abuse.

## Initial Access

HTTP, SSH, and NFS are open. The NFS share contains the source code for the website. There is functionality that lets you write profile attributes to the database, via mass assignment, with some filtering to prevent writing the "role" attribute. If role is Admin, you get access to an admin panel. The filtering just does a string comparison to the GET parameters, and if the key is "role", it throws an error. It then passes the GET parameters to a SQL statement. Playing around with the filtering, it is bypassed using %0d%0a, as in role%0d%0a = Admin.

The admin panel of the site allows you to "export" a file of top players and their scores, which just writes it to a subdir of the website. There is a front-end selector for the file extension (txt, json, html), which you can change (via Burp) to php. Using the same functionality that let you change the role attribute, you can change your own profile's score so you appear in top players, and also change the "nickname" attribute, which shows in top players, to be a php webshell. Upon exporting top players with a php extension and navigating to the exported file, you get a webshell. Shell as www-data.

There is a binary, execute_query, running as SUID as user "jack". I decompiled it with Ghidra, and from that and "strings" output it appears that it is, based on the number 0-4 passed as an argument, running a specific .sql file from the /home/jack/queries directory. But, the default case of the switch/case statement for the arguments is to run any .sql file passed as a second argument. It runs the mysql command by concatenating the command with the file and using system(). It then prints the contents of the file. With path traversal, this is an arbitrary file read. Reading /home/jack/.ssh/id_rsa gives me an ssh key. Shell as "jack" user.

## Root

User "jack" has sudo with NOPASS and SETENV on a script, /opt/monitor.sh. Within monitor.sh, the PATH env variable is set, and PERLLIB and PERL5LIB env variables are "unset", preventing their use. The script parses some data that it curls to /usr/bin/xml_pp, a perl script. A little research shows that the environment variable PERL5OPT (and optionally PERL5DB), which is not set or unset in the script, can be used to achieve code execution. Setting the env variable "PERL5OPT = -Mbase; print("/tmp/shell")" should run the shell at that location. monitor.sh didn't work, but it worked when I used sudo --preserve-env=PERL5OPT instead of -E. Shell as root.

## Alternate root #1

The intended path was actually XXE injection to read root's id_rsa key. The sudo script curls an endpoint that returns xml that then gets sent to xml_pp. So, by setting the "http_proxy" environment variable, you can intercept and modify the response to include an XXE payload:

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
<!ELEMENT foo ANY>
<!ENTITY xxe SYSTEM "/root/.ssh/id_rsa">]>
<foo>&xxe;</foo>
```

## Alternate root #2

Yet another alternate path is to use the LD_PRELOAD env variable. Set it to a malicious .so and run sudo keeping LD_PRELOAD.

## New Information

• PHP Filtering
When trying to beat filtering in php, try %0d%0a. SQL statements ignore line breaks.

• ELF decompiling
Ghidra is a useful tool for decompiling elf files to C-like code. "Export" as C.

• SETENV
If SETENV is in sudo -l, you can keep environment variables by running sudo --preserve-env=<var>, <var>

• Perl env hijacking
Environment variables PERLLIB, PERL5LIB, and PERL5OPT can be used to get code execution when Perl scripts are executed.
PERL5OPT:
export 'PERL5OPT=-Mbase; print("/tmp/shell")'
You may only be able to use commands with no spaces.

## LD_PRELOAD

If you have sudo SETENV, don't forget about LD_PRELOAD.
Compile the following C program as an .so:

```c
#include <unistd.h>
#include <stdlib.h>
__attribute__((constructor)) void privesc() {
unsetenv("LD_PRELOAD");
setgid(0);
setuid(0);
system("/bin/bash")
}
```

And then set LD_PRELOAD=/tmp/mal.so

## http_proxy

If you have sudo SETENV, you may be able to be a MitM for web requests in the script, by setting http_proxy to your ip. Don't forget to add the interface to Burp proxies, and intercept responses.
