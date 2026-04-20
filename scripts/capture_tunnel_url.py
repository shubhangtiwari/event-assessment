"""Read cloudflared stdout/stderr from stdin, extract the first
trycloudflare.com URL, and write it to the settings table so /banner
picks it up without manual admin configuration.
"""

from __future__ import annotations

import re
import sys
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import database as db

URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def main() -> None:
    captured = False
    for line in sys.stdin:
        if captured:
            continue
        match = URL_RE.search(line)
        if not match:
            continue
        url = match.group(0).rstrip("/") + "/"
        db.set_setting("proxy_url", url)
        print(f"[capture] proxy_url set to {url}", file=sys.stderr, flush=True)
        admin_url = url + "admin/login"
        try:
            time.sleep(3)
            webbrowser.open(admin_url)
            print(f"[capture] opened {admin_url}", file=sys.stderr, flush=True)
        except Exception as exc:
            print(
                f"[capture] failed to open browser: {exc}", file=sys.stderr, flush=True
            )
        captured = True


if __name__ == "__main__":
    main()
