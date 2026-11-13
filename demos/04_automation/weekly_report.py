"""Demo 4: automated weekly campaign report with budget pacing and alerts.

For a chosen campaign week (default: latest) it compares each channel with the
previous week and with the budget plan, then writes reports/weekly_report_wkNN.md
and .html. If SLACK_WEBHOOK_URL is set, it also posts the alerts to Slack.

Alert rules (edit them in RULES):
  • overspend: channel spend > plan by more than 10%
  • CPA / CAC up more than 25% week over week
  • trust signal: Parents or Educators conversion (trials per 1k clicks) down > 30%

Usage:
    python demos/04_automation/weekly_report.py
    python demos/04_automation/weekly_report.py --week 7      # the privacy-crisis week
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "data" / "campaign_posts.csv"
PLAN = ROOT / "data" / "budget_plan.csv"
OUT = ROOT / "reports"
RULES = {"overspend": 0.10, "cost_jump": 0.25, "trust_drop": -0.30}


def _div(a, b):
    return a / b if b else float("nan")


def money(v: float, decimals: int = 0) -> str:
    return "–" if pd.isna(v) else f"${v:,.{decimals}f}"


def pct(v: float) -> str:
    return "–" if pd.isna(v) else f"{v:+.0%}"


def channel_week(df: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["week", "platform"]).agg(
        spend=("spend_usd", "sum"), clicks=("clicks", "sum"), trials=("trials", "sum"),
        customers=("paid_conversions", "sum"), demos=("demo_requests", "sum")).reset_index()
    g = g.merge(plan, on=["week", "platform"], how="left")
    g["pacing"] = g.spend / g.planned_spend_usd - 1
    g["CPA"] = g.spend / g.trials.where(g.trials > 0)
    g["CAC"] = g.spend / g.customers.where(g.customers > 0)
    return g


def segment_week(df: pd.DataFrame) -> pd.DataFrame:
    s = df.groupby(["week", "segment"])[["clicks", "trials"]].sum().reset_index()
    s["trials_per_1k_clicks"] = s.trials / s.clicks * 1000
    return s


def build_report(df: pd.DataFrame, plan: pd.DataFrame, week: int | None) -> tuple[str, list[str]]:
    cw = channel_week(df, plan)
    week = week or int(cw.week.max())
    if week < 2:
        raise SystemExit("Pick week 2 or later (need a previous week to compare).")
    cur = cw[cw.week == week].set_index("platform")
    prev = cw[cw.week == week - 1].set_index("platform")

    alerts = []
    for p, r in cur.iterrows():
        if r.pacing > RULES["overspend"]:
            alerts.append(f"💸 {p}: spend ${r.spend:,.0f} is {r.pacing:+.0%} vs plan (${r.planned_spend_usd:,.0f})")
        for metric in ("CPA", "CAC"):
            change = _div(r[metric], prev.loc[p, metric]) - 1 if p in prev.index else float("nan")
            if change > RULES["cost_jump"] and p != "LinkedIn":
                alerts.append(f"📈 {p}: {metric} up {change:.0%} (${prev.loc[p, metric]:,.0f} → ${r[metric]:,.0f})")
    sw = segment_week(df)
    for seg in ("Parents", "Educators"):
        a = sw[(sw.week == week) & (sw.segment == seg)].trials_per_1k_clicks
        b = sw[(sw.week == week - 1) & (sw.segment == seg)].trials_per_1k_clicks
        if len(a) and len(b):
            ch = a.iloc[0] / b.iloc[0] - 1
            if ch < RULES["trust_drop"]:
                alerts.append(f"⚠️ {seg}: conversion down {abs(ch):.0%} week over week "
                              f"({b.iloc[0]:.0f} → {a.iloc[0]:.0f} trials per 1k clicks). Check comments for a trust issue.")

    to_date = cw[cw.week <= week]
    spent, planned = to_date.spend.sum(), to_date.planned_spend_usd.sum()
    lines = [
        f"# Athenova campaign: weekly report, week {week} of 12",
        f"_Budget to date: ${spent:,.0f} spent vs ${planned:,.0f} planned ({spent / planned - 1:+.1%})._",
        "",
        "| Channel | Spend | vs plan | Trials | CPA | Δ CPA | Customers | CAC | Demo req. |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p, r in cur.sort_values("spend", ascending=False).iterrows():
        dcpa = _div(r.CPA, prev.loc[p, "CPA"]) - 1 if p in prev.index else float("nan")
        lines.append(f"| {p} | {money(r.spend)} | {pct(r.pacing)} | {r.trials:,.0f} | {money(r.CPA, 2)} | {pct(dcpa)} "
                     f"| {r.customers:,.0f} | {money(r.CAC)} | {r.demos:,.0f} |")
    lines += ["", "## Alerts", *(f"- {x}" for x in alerts or ["✅ No alerts this week."])]
    return "\n".join(lines), alerts


def to_html(md: str) -> str:
    """Tiny Markdown-to-HTML converter (tables, headings, bullets), so no extra packages are needed."""
    body, in_table = [], False
    for line in md.splitlines():
        if line.startswith("|---"):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            tag = "td" if in_table else "th"
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
    css = ("body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:2rem auto;color:#222}"
           "h1,h2{color:#005581}table{border-collapse:collapse;width:100%}"
           "th{background:#005581;color:#fff}td,th{padding:6px 10px;border-bottom:1px solid #ddd;"
           "text-align:right}td:first-child,th:first-child{text-align:left}")
    return f"<!doctype html><meta charset='utf-8'><title>Athenova weekly report</title><style>{css}</style>" + "\n".join(body)


def notify_slack(alerts: list[str]) -> None:
    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url or not alerts:
        return
    data = json.dumps({"text": "Athenova campaign alerts:\n" + "\n".join(alerts)}).encode()
    urllib.request.urlopen(urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}),
                           timeout=10)
    print("alerts sent to Slack")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, help="campaign week 2-12 (default: latest)")
    args = ap.parse_args()
    md, alerts = build_report(pd.read_csv(POSTS), pd.read_csv(PLAN), args.week)
    OUT.mkdir(exist_ok=True)
    week = args.week or int(pd.read_csv(POSTS).week.max())
    stem = OUT / f"weekly_report_wk{week:02d}"
    stem.with_suffix(".md").write_text(md, encoding="utf-8")
    stem.with_suffix(".html").write_text(to_html(md), encoding="utf-8")
    print(md)
    print(f"\nreports written to {stem.relative_to(ROOT)}.md / .html")
    notify_slack(alerts)


if __name__ == "__main__":
    main()
