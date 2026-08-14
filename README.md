# nitc-watch

Email notification to my personal inbox when new notifications pop up in the
recruitment pages, since I had completed all levels in the employment test.

Watches <https://nitc.ac.in/non-faculty-recruitments> and emails when a new
notice link appears. Runs on GitHub Actions — no server, no cost.

## How it works

Each run fetches the page, extracts the set of non-faculty recruitment links,
and diffs against `nitc_seen.txt`. New links → email via [Resend](https://resend.com).

The state file is committed back to the repo, so it survives between ephemeral
runner VMs, and the commits keep the scheduled workflow from being auto-disabled
for inactivity.

The first run only records a baseline and sends nothing.

## Schedule

Daily at 5:00 PM IST (`30 11 * * *` UTC), plus a manual **Run workflow** button.
Scheduled runs on GitHub Actions are best-effort and can drift by a few minutes.

## Files

| File | Purpose |
|------|---------|
| `watch.py` | Fetch, diff, send |
| `.github/workflows/watch.yml` | Schedule + state commit |
| `nitc_seen.txt` | Links already seen (created on first run) |

## Setup

See [SETUP.md](SETUP.md).

## License

GNU AGPL v3 — see [LICENSE](LICENSE).

Copyright (C) 2026 Aswin Pradeep C
