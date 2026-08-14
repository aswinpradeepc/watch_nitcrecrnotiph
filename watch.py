#!/usr/bin/env python3
#
# nitc-watch — email alerts for new NITC recruitment notices.
# Copyright (C) 2026 Aswin Pradeep C
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Watches the NITC non-faculty recruitment page for new notices and emails
you via Resend when the set of notice links changes.

State ("what we've already seen") is stored in nitc_seen.txt, which the
GitHub Actions workflow commits back to the repo so it survives between
ephemeral runs.

Env vars required:
  RESEND_API_KEY   your Resend API key (re_...)
  SENDER           sender on your VERIFIED domain, e.g. alerts@yourdomain.com
  RECEIVER         recipient address

Optional:
  TEST_MODE=1      send a one-off test email and exit (no diffing)
"""
import os
import re
import json
import pathlib
import urllib.request
import urllib.error

URL   = "https://nitc.ac.in/non-faculty-recruitments"
BASE  = "https://nitc.ac.in"
STATE = pathlib.Path("nitc_seen.txt")   # lives in the repo

# Both hosts sit behind Cloudflare, which 403s the default Python-urllib
# user agent (error 1010). Send a browser-ish one on every request.
UA    = "Mozilla/5.0"


def send_email(subject: str, body: str) -> None:
    payload = json.dumps({
        "from":    os.environ["SENDER"],
        "to":      [os.environ["RECEIVER"]],
        "subject": subject,
        "text":    body,
    }).encode()

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type":  "application/json",
            "User-Agent":    UA,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("resend:", r.status)
    except urllib.error.HTTPError as e:
        # surface the exact validation reason instead of a bare traceback
        print("resend error:", e.code, e.read().decode())
        raise


def fetch_links() -> set[str]:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    return set(re.findall(r'/recruitments/non-faculty-recruitment/[^\s"\'<>]+', html))


def main() -> None:
    # ---- test mode: prove the email pipe works, then bail ----
    if os.environ.get("TEST_MODE") == "1":
        send_email("NITC watch: test email",
                   "If you're reading this, Resend + your secrets are wired correctly.")
        return

    links = fetch_links()
    print(f"found {len(links)} recruitment links")

    seen = set(STATE.read_text().splitlines()) if STATE.exists() else set()
    new  = links - seen

    if new and seen:                       # skip the first-run baseline
        body = "New NITC recruitment notice(s):\n\n" + "\n".join(
            BASE + slug for slug in sorted(new)
        )
        send_email(f"NITC: {len(new)} new recruitment notice(s)", body)
        print(f"notified about {len(new)} new link(s)")
    elif not seen:
        print("first run - recorded baseline, no email sent")
    else:
        print("no change")

    STATE.write_text("\n".join(sorted(links)))


if __name__ == "__main__":
    main()
