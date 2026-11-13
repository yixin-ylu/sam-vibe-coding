"""Demo 4: automated weekly performance report + alerts.

Compares the most recent week with the week before. Writes a Markdown report
and an HTML report to reports/, and posts a short alert to Slack if the
SLACK_WEBHOOK_URL environment variable is set. The webhook is optional.

Usage:
    python demos/04_automation/weekly_report.py
    python demos/04_automation/weekly_report.py --week 2026-10-26   # report a specific week

Schedule it with cron, Windows Task Scheduler, or GitHub Actions (see README.md).
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "sample_posts.csv"
OUT = ROOT / "reports"
DROP_ALERT = -0.20     # alert if engagement falls by more than 20% week over week
SPIKE_ALERT = 0.50     # celebrate if impressions rise by more than 50%


def weekly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["week"] = pd.to_datetime(df["posted_at"]).dt.to_period("W").dt.start_time
    df["interactions"] = df[["likes", "comments", "shares"]].sum(axis=1)
    g = df.groupby(["week", "platform"]).agg(
        posts=("post_id", "count"),
        impressions=("impressions", "sum"),
        interactions=("interactions", "sum"),
        followers=("followers", "max"),
    )
    g["engagement_rate"] = g["interactions"] / g["impressions"]
    return g.reset_index()


def build_report(kpi: pd.DataFrame, week: pd.Timestamp | None = None) -> tuple[str, list[str]]:
    weeks = sorted(kpi["week"].unique())
    cur = pd.Timestamp(week) if week is not None else weeks[-1]
    prev_candidates = [w for w in weeks if w < cur]
    if not prev_candidates:
        raise SystemExit("Need at least two weeks of data.")
    prev = prev_candidates[-1]

    a = kpi[kpi.week == cur].set_index("platform")
    b = kpi[kpi.week == prev].set_index("platform")
    table = a[["posts", "impressions", "engagement_rate", "followers"]].join(
        b[["impressions", "engagement_rate"]], rsuffix="_prev")
    table["impr_change"] = table["impressions"] / table["impressions_prev"] - 1
    table["eng_change"] = table["engagement_rate"] / table["engagement_rate_prev"] - 1

    alerts = []
    for platform, r in table.iterrows():
        if r.eng_change < DROP_ALERT:
            alerts.append(f"⚠️ {platform}: engagement rate down {abs(r.eng_change):.0%} "
                          f"({r.engagement_rate_prev:.2%} → {r.engagement_rate:.2%})")
        if r.impr_change > SPIKE_ALERT:
            alerts.append(f"🚀 {platform}: impressions up {r.impr_change:.0%}")

    lines = [
        f"# SAM weekly report: week of {cur:%b %d, %Y}",
        f"_Compared with the week of {prev:%b %d, %Y}. Generated {date.today():%Y-%m-%d}._",
        "",
        "| Platform | Posts | Impressions | Δ | Eng. rate | Δ | Followers |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for platform, r in table.sort_values("impressions", ascending=False).iterrows():
        lines.append(f"| {platform} | {r.posts:.0f} | {r.impressions:,.0f} | {r.impr_change:+.0%} "
                     f"| {r.engagement_rate:.2%} | {r.eng_change:+.0%} | {r.followers:,.0f} |")
    lines += ["", "## Alerts", *(f"- {x}" for x in alerts or ["✅ No alerts this week."])]
    return "\n".join(lines), alerts


def to_html(md: str) -> str:
    """Tiny Markdown-table to HTML converter, so the demo needs no extra packages."""
    body, in_table = [], False
    for line in md.splitlines():
        if line.startswith("|---"):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "th" if not in_table else "td"
            if not in_table:
                body.append("<table>")
                in_table = True
            body.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            body.append("</table>")
            in_table = False
        if line.startswith("# "):
            body.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "):
            body.append(f"<p>{line[2:]}</p>")
        elif line.strip():
            body.append(f"<p><em>{line.strip('_')}</em></p>")
    css = ("body{font-family:Segoe UI,Arial,sans-serif;max-width:820px;margin:2rem auto;color:#222}"
           "h1,h2{color:#005581}table{border-collapse:collapse;width:100%}"
           "th{background:#005581;color:#fff}td,th{padding:6px 10px;border-bottom:1px solid #ddd;"
           "text-align:right}td:first-child,th:first-child{text-align:left}")
    return f"<!doctype html><meta charset='utf-8'><title>SAM weekly report</title><style>{css}</style>" \
           + "\n".join(body)


def notify_slack(alerts: list[str]) -> None:
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url or not alerts:
        return
    data = json.dumps({"text": "SAM weekly alerts:\n" + "\n".join(alerts)}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)
    print("alert sent to Slack")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", help="Monday of the week to report (YYYY-MM-DD); default = latest")
    ap.add_argument("--data", default=str(DATA))
    args = ap.parse_args()

    kpi = weekly_kpis(pd.read_csv(args.data))
    md, alerts = build_report(kpi, args.week)
    OUT.mkdir(exist_ok=True)
    stem = OUT / f"weekly_report_{date.today():%Y-%m-%d}"
    stem.with_suffix(".md").write_text(md, encoding="utf-8")
    stem.with_suffix(".html").write_text(to_html(md), encoding="utf-8")
    print(md)
    print(f"\nreports written to {stem}.md / .html")
    notify_slack(alerts)


if __name__ == "__main__":
    main()
