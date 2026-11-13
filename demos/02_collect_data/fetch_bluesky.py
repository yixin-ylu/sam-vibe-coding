"""Demo 2: collect real social-media data from a public REST API.

Bluesky exposes a public, read-only API that needs NO key and NO OAuth, which
makes it ideal for a first API lesson. Later weeks swap in platforms that need
OAuth 2.0 (Meta, LinkedIn, TikTok) using the same fetch -> parse -> save pattern.

Usage:
    python demos/02_collect_data/fetch_bluesky.py                 # default account
    python demos/02_collect_data/fetch_bluesky.py --actor nasa.gov --pages 3
    python demos/02_collect_data/fetch_bluesky.py --offline       # no internet? use sample file

Concepts shown: REST endpoint + query params, JSON parsing, pagination with a
cursor, polite rate limiting, error handling, saving to CSV.
Only public, organisational accounts should be used in class (Responsible AI rules).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


API = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parents[1] / "data"
FIELDS = ["uri", "created_at", "text", "likes", "reposts", "replies", "quotes"]


def fetch_page(actor: str, cursor: str | None = None, limit: int = 50) -> dict:
    """Call the API once and return the decoded JSON."""
    params = {"actor": actor, "limit": limit, "filter": "posts_no_replies"}
    if cursor:
        params["cursor"] = cursor
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "sam-course-demo/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)


def parse_feed(payload: dict) -> list[dict]:
    """Flatten the nested JSON into simple rows (the 'T' in ETL)."""
    rows = []
    for item in payload.get("feed", []):
        if item.get("reason"):  # a repost of someone else's post -> skip
            continue
        post = item.get("post", {})
        record = post.get("record", {})
        rows.append({
            "uri": post.get("uri", ""),
            "created_at": record.get("createdAt", ""),
            "text": " ".join(record.get("text", "").split())[:280],
            "likes": post.get("likeCount", 0),
            "reposts": post.get("repostCount", 0),
            "replies": post.get("replyCount", 0),
            "quotes": post.get("quoteCount", 0),
        })
    return rows


def collect(actor: str, pages: int) -> list[dict]:
    rows, cursor = [], None
    for page in range(1, pages + 1):
        payload = fetch_page(actor, cursor)
        new = parse_feed(payload)
        rows.extend(new)
        print(f"page {page}: {len(new)} posts")
        cursor = payload.get("cursor")
        if not cursor:
            break
        time.sleep(1)  # be polite: never hammer an API
    return rows


def save(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"saved {len(rows)} rows -> {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--actor", default="bsky.app", help="public Bluesky handle")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--offline", action="store_true", help="parse the bundled sample response")
    args = ap.parse_args()

    out = DATA_DIR / f"bluesky_{args.actor.replace('.', '_')}.csv"
    if args.offline:
        payload = json.loads((HERE / "sample_response.json").read_text(encoding="utf-8"))
        save(parse_feed(payload), out)
        return
    try:
        save(collect(args.actor, args.pages), out)
    except urllib.error.HTTPError as e:
        print(f"API returned HTTP {e.code}: check the handle, or try --offline")
    except urllib.error.URLError as e:
        print(f"Network problem ({e.reason}); re-run with --offline")


if __name__ == "__main__":
    main()
