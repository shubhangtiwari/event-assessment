# Claude Enablement — Pre-Event Assessment App

A self-contained web app for the Claude Enablement Session in Bonn
(April 20–21, 2026). Participants fill in a short 16-question assessment,
the app scores and groups them automatically, and organizers see everything
in a live dashboard.

![flow](https://img.shields.io/badge/flow-survey→score→group→dashboard-E20074)

---

## Features

- **Survey form** with Telekom-inspired design (magenta, clean white, diagonal hero).
- **One submission per user** — enforced by a signed session cookie *and* by email dedup.
- **Automatic scoring + grouping** — the grouper reruns on every submit, so
  group assignments are always current.
- **Live organizer dashboard** — auto-refreshes every 30 seconds,
  tabbed view (Groups / Participants), level-distribution bar, Excel export.
- **SQLite storage** — a single `data/responses.sqlite` file; no DB server.
- **One-command start** — `make start` (Flask + ngrok tunnel) or `make app` (Flask only).
- **ngrok-ready** — listens on `0.0.0.0:2408` by default.

---

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/) and `make`.

```bash
make app           # Flask only, on localhost:2408
make start         # Flask + ngrok tunnel (needs NGROK_DOMAIN in .env)
make start-cf      # Flask + Cloudflare quick tunnel
```

`make install` runs `uv sync`; the `app`/`start` targets invoke it automatically. On first run you'll see:

```
┌────────────────────────────────────────────────────────────────────┐
│  Claude Enablement — pre-event assessment                         │
│  Bonn · April 20–21, 2026                                         │
├────────────────────────────────────────────────────────────────────┤
│  Survey:    http://localhost:2408/                                │
│  Dashboard: http://localhost:2408/admin/login                     │
├────────────────────────────────────────────────────────────────────┤
│  ⚠  Admin password is the default ('admin').                      │
│     Before exposing via ngrok, set: export ADMIN_PASSWORD=...     │
│  Submissions so far: 0                                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## Exposing via ngrok

`make start` runs Flask and ngrok together (using `NGROK_DOMAIN` from `.env`).
If you only want the tunnel against an already-running app, use `make tunnel`.

ngrok will print a public `https://xxxx.ngrok-free.app` URL. Share **only** the
root URL with participants — the `/admin/*` routes are password-protected.

### Before you open the ngrok tunnel

1. **Set a real admin password.** The default is `admin`, which is
   unacceptable once the app is reachable from the public internet.
   Put it in `.env` or export it before running `make start`:

   ```bash
   export ADMIN_PASSWORD="something-long-and-random"
   make start
   ```

2. **Confirm the survey loads** at `https://your-ngrok-url/` — check
   that the header, hero, and form all render.

3. **Share the URL** with invited participants.

4. **Watch the dashboard** at `https://your-ngrok-url/admin/login` —
   sign in with your `ADMIN_PASSWORD`.

---

## Directory layout

```
event_assessment/
├── app.py                   # Flask entry point (routes)
├── core/                    # business logic package
│   ├── __init__.py
│   ├── config.py            # Scoring rubric + runtime config
│   ├── database.py          # SQLite wrapper
│   ├── grouper.py           # Snake-draft group formation
│   ├── questions.py         # Single source of truth for all 16 questions
│   └── scorer.py            # Submission scoring logic
├── pyproject.toml           # uv-managed dependencies
├── uv.lock
├── Makefile                 # `make app` / `make start` / `make start-cf`
├── scripts/
│   └── capture_tunnel_url.py  # stores cloudflared URL for the banner page
├── README.md                # this file
├── templates/               # Jinja templates
│   ├── base.html
│   ├── survey.html
│   ├── thanks.html
│   ├── already_submitted.html
│   ├── admin_login.html
│   ├── dashboard.html
│   └── banner.html
├── static/
│   ├── css/style.css        # Telekom-inspired styles
│   ├── js/dashboard.js      # Dashboard logic (fetch + render)
│   └── img/telekom-logo.svg
└── data/                    # created on first run
    ├── responses.sqlite     # all submissions
    └── secret_key           # persisted Flask SECRET_KEY
```

---

## Configuration

All tunables are environment variables — no config file editing needed.

| Variable | Default | Purpose |
|---|---|---|
| `ADMIN_PASSWORD` | `admin` | Dashboard password. **Must be set before ngrok exposure.** |
| `PORT` | `2408` | Port to listen on. |
| `HOST` | `0.0.0.0` | Bind host. Use `127.0.0.1` to block remote access entirely. |
| `GROUP_SIZE` | `6` | Default group size (can also be changed live in the dashboard). |
| `GROUPING_SEED` | `42` | Random seed for tie-breaking in the snake-draft. |

---

## How the grouper is triggered

There are two places group assignment is (re)computed:

1. **On every form submission** — `/submit` calls `form_balanced_groups()`
   after writing the new row. This guarantees the grouper runs on every submit,
   as you asked.
2. **On every dashboard data fetch** — the JS polls `/admin/api/data` every
   30 seconds, and each response includes a fresh group assignment.

Because the grouper is deterministic (seeded snake-draft), the same input
set always yields the same groups. As new participants join, groups
naturally rebalance — which is the desired behavior until registration closes.

---

## Data & privacy

- All responses are stored in a local SQLite file at
  `data/responses.sqlite`. Delete it after the workshop.
- Session cookies are HTTP-only and signed with a persisted 32-byte key
  at `data/secret_key` — keep this file out of version control.
- The app sets `robots: noindex, nofollow` so it won't be indexed even
  while accessible via ngrok.

---

## Troubleshooting

**Port 2408 already in use.** Edit `PORT` at the top of the `Makefile`
(or override per-invocation: `make app PORT=2409`).

**Someone cleared their cookies and wants to resubmit.** Don't let them —
the app also blocks duplicates by email. If there's a legitimate reason,
manually delete their row from `data/responses.sqlite`:

```bash
sqlite3 data/responses.sqlite "DELETE FROM responses WHERE email='user@telekom.de';"
```

**Dashboard won't load.** The admin cookie lasts 12 hours; sign in again
at `/admin/login`. If you rotated `ADMIN_PASSWORD`, all existing admin
cookies are invalidated automatically.

**Excel export button does nothing.** Make sure you're signed in. The
export route returns 401 to anonymous requests.

---

## For developers

To change scoring weights or thresholds, edit `core/config.py`. To add or
remove a question, edit `core/questions.py` — the form renders from that file
directly, so you don't need to touch templates.

Running the smoke test:

```bash
uv run python -m unittest tests.py    # if you add your own
```
