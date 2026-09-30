---
title: "HTB: Backend"
date: 2026-09-30
draft: false
tags: ["htb", "linux", "api-fuzzing", "jwt"]
cover:
  image: /images/htb-backend-cover.jpg
  alt: "Glowing API endpoint paths and JSON braces drifting in a dark blue-black void"
  relative: false
---

Backend. Linux, medium, retired. The chain in one line: API fuzzing → JWT manipulation → credential hunting → root via someone else's typo in auth.log.

But the box isn't really about the chain. It's about a fuzzing footgun and a JSON document that hands you the whole game.

## Initial access

This whole box was built around API fuzzing. 22 and 80 open, and 80 is a JSON API running on uvicorn and FastAPI. Dirbusting turned up a `/docs` endpoint (Forbidden) and an `/api` endpoint. GETing `/api` returned JSON pointing at another endpoint, `/api/v1`. GETing `/api/v1` returned more JSON with two more endpoints: `/api/v1/user` and `/api/v1/admin`. Fuzzing `/api/v1/admin` showed POST only and asked for a Bearer token. The latter showed details for an admin user.

And then I was stuck.

From previous experience fuzzing APIs I tried multiple methods (POST, PUT). But it turns out ffuf doesn't return all responses in the 400s unless you use `-mc all` in addition to `-fc` for the codes you want to filter. Without it, ffuf quietly drops 4xx responses and you sit there thinking there's nothing to find.

The facts:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">fuzz.sh</span></div>
<div class="terminal-body"><pre>$ ffuf -u http://&lt;ip&gt;/api/v1/user/FUZZ -w wordlist -X POST -mc all -fc 404
/signup    # user creation via JSON POST
/login     # login via x-www-form-urlencoded

$ curl -X POST http://&lt;ip&gt;/api/v1/user/signup \
    -H "Content-Type: application/json" \
    -d '{"username":"x","password":"x"}'

$ curl -X POST http://&lt;ip&gt;/api/v1/user/login \
    -d "username=x&amp;password=x"</pre></div>
</div>

Fuzzing with POST revealed `/api/v1/user/signup` and `/api/v1/user/login`. The former allowed user creation via JSON POST; the latter handled login via x-www-form-urlencoded (`param1=value1&param2=value2`). In my experience, `-H "Content-Type: application/json"` is usually required when sending JSON, while no content-type header is needed for x-www-form-urlencoded — and that turned out to be true here as well.

Signing in hands you an API (Bearer) token. With the token (`Authorization: Bearer <token>`), the previously forbidden `/docs` and `/openapi.json` open up, and `/openapi.json` gives you the comprehensive view: every endpoint and its params, including an endpoint for getting the user flag. There's also a change-password endpoint, and you can change the admin user's password. As an admin API user, the `admin/file` endpoint lets you read files on the machine.

Looking up typical FastAPI configuration, I read `app/core/config.py` — which revealed the secret used for generating the tokens (JWTs). `/openapi.json` also revealed an `admin/exec/<cmd>` endpoint. Trying it, the API complained the `debug` key was missing from the JWT, so I took the secret to an online tool and minted a token with `debug: true` added (first site didn't work; ended up using www.jwt.io). That unlocked the exec endpoint. Playing with it showed spaces had to be encoded as `%20`, and I ended up piping a base64-encoded `/dev/tcp/<ip>/<port>` reverse shell through `base64 -d` into bash. Shell as user.

---

## Root

The directory I landed in had a file called `auth.log` — normal auth attempts, and then one that looked like someone typed their password instead of their username. `su -` with that password worked. Shell as root.

Nothing clever. Somebody's typo did the privesc.

---

## Reference

The general notes from this box, worth keeping around:

Typical FastAPI config paths:

<div class="terminal">
<div class="terminal-head"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="fname">fastapi-layout.txt</span></div>
<div class="terminal-body"><pre>&lt;project-name&gt;/
  .env
  pyproject.toml
  logging.ini
  app/
    main.py
    core/
      config.py    &lt;-- this one held JWT_SECRET</pre></div>
</div>

API fuzzing with ffuf: when you want to match all codes except some specific ones, use `-mc all` alongside `-fc <codes-to-filter>`. Otherwise ffuf ignores some codes, like the ones in the 400s range — which is exactly where the interesting API responses live. And with APIs, always fuzz with different methods; feroxbuster supports multiple methods too.

Many APIs ship `/docs` and `/openapi.json`, which document the whole API. Read them before you brute-force anything; the endpoint list is sitting right there.

Don't forget the `Content-Type: application/json` header when POSTing JSON.

Manipulating JWTs: if you have the `JWT_SECRET`, you can mint your own tokens and add whatever keys and values you want (I used www.jwt.io). The `debug: true` claim is what this box's exec endpoint was gating on — the kind of thing you only find by reading the API docs the box gives you.
