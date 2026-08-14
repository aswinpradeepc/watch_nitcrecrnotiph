# Setup

Takes about five minutes. You need a [Resend](https://resend.com) account with a
verified sending domain.

## 1. Fork or copy the repo

Keep these at the repo root:

- `watch.py`
- `.github/workflows/watch.yml`

## 2. Add repository secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `RESEND_API_KEY` | Your Resend API key (`re_...`) |
| `SENDER` | Sender address on your **verified** domain |
| `RECEIVER` | Where alerts should land |

Paste addresses bare — no surrounding quotes, no trailing spaces.

## 3. Enable Actions

Push, then open the **Actions** tab and enable workflows if prompted.

The workflow needs `contents: write` to commit the state file back; if your repo
or org restricts this, set **Settings → Actions → General → Workflow
permissions** to *Read and write permissions*.

## 4. Verify

**A. Test the email pipe.**
Actions → **NITC recruitment watch** → **Run workflow** → toggle
**Send a test email** on → Run. Check your inbox for "NITC watch: test email".
This isolates "are Resend and the secrets correct" from "is the diff logic correct".

**B. Establish the baseline.**
Run the workflow again with the test toggle **off**. The log should print
`first run - recorded baseline, no email sent`, and a `state:` commit should
appear. No email is expected here.

**C. Confirm the diff fires.**
Either wait for a real new posting, or simulate one: delete a couple of lines
from `nitc_seen.txt` and commit. The next run treats them as new and emails you,
then re-records the full set.

## Running locally

Put the three values in a `.env` at the repo root (it is gitignored):

```
RESEND_API_KEY=re_xxx
SENDER=alerts@yourdomain.com
RECEIVER=you@example.com
```

Then:

```bash
set -a; source .env; set +a

TEST_MODE=1 python3 watch.py     # send a test email only
python3 watch.py                 # real run (creates/updates nitc_seen.txt)
```

Python 3.9+ (uses only the standard library).

## Tuning

**Frequency.** Edit the cron in `.github/workflows/watch.yml`. It is in **UTC**
— the default `30 11 * * *` is 5:00 PM IST. Scheduled runs are best-effort and
may drift or occasionally skip a tick.

**Empty results.** If `nitc_seen.txt` comes back empty after a run, the site
markup changed. Adjust the regex in `fetch_links()` in `watch.py`.
