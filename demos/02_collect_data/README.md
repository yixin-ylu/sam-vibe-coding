# Demo 2 — Collecting data from a real API

`fetch_bluesky.py` pulls recent public posts from a Bluesky account and saves them to CSV.
Bluesky's public read API needs **no key and no OAuth**, so week 3 can focus on the core ideas:

```
 REST endpoint ──► JSON response ──► flatten (parse) ──► CSV on disk
        ▲                │
        └── cursor ◄─────┘   (pagination, with a 1-second pause between calls)
```

```bash
python demos/02_collect_data/fetch_bluesky.py                       # bsky.app, 2 pages
python demos/02_collect_data/fetch_bluesky.py --actor nasa.gov --pages 3
python demos/02_collect_data/fetch_bluesky.py --offline             # uses sample_response.json
```

## The prompt that produced the first draft

> Write a Python script with only the standard library that calls
> `https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed` for a given handle,
> follows the `cursor` for N pages with a 1-second pause, skips reposts,
> keeps uri, createdAt, text, likeCount, repostCount, replyCount, quoteCount,
> and writes them to `data/bluesky_<handle>.csv`. Handle HTTP and network errors
> with a friendly message and offer an `--offline` mode that reads a saved JSON file.

## Things the AI got wrong the first time (good classroom discussion)

1. It kept **reposts**, so other accounts' posts were counted as the brand's own (fixed by checking `item["reason"]`).
2. It had no pause between pages. Ask students why that matters for **rate limits** and the platform's terms of service.
3. It printed the full post text, including line breaks, which made the CSV messy (fixed by collapsing whitespace).

## Moving to OAuth platforms (weeks 3–4)

Instagram Graph API, LinkedIn Marketing API and the TikTok Display API all use **OAuth 2.0**.
The fetch → parse → save shape stays the same. What changes:

- tokens live in a `.env` file that is **never committed** (see `.gitignore`)
- you send `Authorization: Bearer <token>`
- you deal with token expiry and app review

Until developer access is approved, run the exercises against the synthetic Lumora case in `data/`.
