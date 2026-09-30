---
title: "HTB: Interface"
date: 2026-09-30
draft: false
tags: ["htb", "linux", "dompdf", "api-fuzzing", "privesc"]
cover:
  image: /images/htb-interface-cover.jpg
  alt: "A PDF document dissolving into glowing bash arithmetic symbols, purple on black"
  relative: false
---

Interface. Linux, medium, retired. The chain in one line: API endpoint discovery → dompdf html-to-pdf exploit → shell as www-data → a root script doing bash arithmetic comparison on attacker-controlled file metadata → shell as root.

But the box isn't really about the chain. It's about a root script that trusted `$(( ))` with your input.

## Initial access

Two ports open: 80 and 22. Port 80 was a Node.js instance. Poking around in Burp, the Content-Security-Policy had a connect-src pointing at a domain: `prd.m.rendering-api.interface.htb`. That's an API endpoint.

Fuzzing eventually turned up two endpoints: `/api/html2pdf` and `/vendor`. The former takes HTML in an "html" param, JSON, and returns a PDF. The returned PDF's metadata said it was produced with dompdf 1.2.0 — vulnerable to CVE-2022-28368, essentially a file upload vulnerability.

I found the required `/vendor/dompdf/dompdf` endpoint on the site, slightly modified a PoC, and it worked. Shell as www-data.

---

## Root: a `-eq` that runs your code

Then a whole lot of nothing. Normal enumeration turned up nothing useful, so I ran pspy and found two scripts running repeatedly on the machine. One was `/root/clean.sh`, which cleaned a directory used for the exploit and restored its file log. The other was `/usr/local/sbin/cleancache.sh`, and it was readable.

cleancache.sh used exiftool to extract the "Producer" from the metadata of any file in /tmp, compared it to the string 'dompdf' — using `-eq` inside `[[ ]]`, which evaluates the strings as integers instead of comparing them. Genuine bug: non-numeric strings both reduce to 0, so every Producer "matched" — and removed it.

The facts:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">pspy.txt</span></div>
<div class="terminal-body"><pre>$ pspy64
/root/clean.sh ............ on schedule, cleans exploit dir, restores file log
/usr/local/sbin/cleancache . readable
  exiftool -"Producer" of every file in /tmp
  [[ "$producer" -eq "dompdf" ]] &amp;&amp; rm   # [[ -eq evaluates arithmetic: a bug, not a comparison</pre></div>
</div>

Arithmetic comparison on attacker-controlled input. If the Producer value is something bash arithmetic expansion will evaluate — like `a[$(id)]` — it executes. It doesn't like spaces, so the payload has to avoid them:

```bash
exiftool -Producer="a[$(/tmp/shell)]" /tmp/whatever.pdf
```

where /tmp is any writable directory and shell is a revshell elf. When the script ran on schedule as root, the `-eq` comparison expanded the string and the shell executed as root. Shell as root.

---

## Reference

API endpoint fuzzing, learned on this box:

- Include 404s and filter by size instead. Filtering on status code alone hides things.
- Test with POST and other methods, not just GET. The interesting endpoints here only answered to the right method.

Bash arithmetic comparison:

- It can happen explicitly in `(( ))`, or implicitly with arithmetic comparison operators (`-eq`, `-gt`, ...) inside `[[ ]]`. (Single-bracket `[ ]` just errors on non-integers — no evaluation happens.) If either side of the comparison is attacker-controlled, it's code execution.
