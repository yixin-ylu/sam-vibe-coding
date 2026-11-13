"""Demo 7 (advanced): a campaign-strategy agent built on the Claude API.

Unlike the one-prompt-one-answer calls in Demo 6, Claude here gets nine TOOLS (plain
Python functions over the Athenova campaign data). It decides which to call, in what
order, reads the results, and keeps going until it can write an evidence-based memo
to the CMO: channel economics, the week-7 privacy incident, the A/B test verdict, and
a budget reallocation. Every tool call is printed so students can audit the agent.

Get a key at https://platform.claude.com and store it as ANTHROPIC_API_KEY
(in Colab: Secrets panel → ANTHROPIC_API_KEY). A run costs roughly $0.15–$0.60 on the
default model; the exact token cost is printed at the end.

Usage:
    python demos/07_claude_agent/strategist_agent.py
    python demos/07_claude_agent/strategist_agent.py --goal "Should we cut LinkedIn?"
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "05_sentiment"))
from keys import require_key  # noqa: E402
from sentiment import label as sent_label, score as sent_score, topic as kw_topic  # noqa: E402

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
PRICE_PER_MTOK = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00),
                  "claude-haiku-5-5": (0.10, 0.50)}  # (input, output) USD per 1M tokens

# ── Data (synthetic; fictional company) ───────────────────────────────────────
POSTS = pd.read_csv(ROOT / "data" / "campaign_posts.csv", parse_dates=["posted_at"])
PLAN = pd.read_csv(ROOT / "data" / "budget_plan.csv")
AB = pd.read_csv(ROOT / "data" / "ab_test.csv")
COMMENTS = pd.read_csv(ROOT / "data" / "campaign_comments.csv").merge(POSTS[["post_id", "week"]], on="post_id")
COMMENTS["label"] = COMMENTS.text.map(lambda t: sent_label(sent_score(t)))
COMMENTS["topic"] = COMMENTS.text.map(kw_topic)
POSTS["engagement_rate"] = (POSTS[["likes", "comments", "shares"]].sum(axis=1)
                            / POSTS.impressions.where(POSTS.impressions > 0)).fillna(0)


def _filter(df: pd.DataFrame, platform: str = "all", segment: str = "all") -> pd.DataFrame:
    if platform.lower() != "all":
        df = df[df.platform.str.lower() == platform.lower()]
    if segment.lower() != "all":
        df = df[df.segment.str.lower() == segment.lower()]
    return df


def _econ(g: pd.DataFrame) -> pd.Series:
    s = g[["spend_usd", "impressions", "clicks", "trials", "paid_conversions", "demo_requests",
           "revenue_usd", "pipeline_usd"]].sum()
    d = lambda a, b: round(a / b, 4) if b else None  # noqa: E731
    return pd.Series({"spend": round(s.spend_usd), "CPM": d(s.spend_usd * 1000, s.impressions),
                      "CTR": d(s.clicks, s.impressions), "trials": int(s.trials), "CPA": d(s.spend_usd, s.trials),
                      "customers": int(s.paid_conversions), "CAC": d(s.spend_usd, s.paid_conversions),
                      "ROAS_first_year": d(s.revenue_usd, s.spend_usd), "demo_requests": int(s.demo_requests),
                      "pipeline_per_dollar": d(s.pipeline_usd, s.spend_usd)})


def _json(df: pd.DataFrame) -> str:
    return df.reset_index().to_json(orient="records")


# ── Tools: ordinary Python functions; the docstring is what the model reads ──
from anthropic import beta_tool  # noqa: E402


@beta_tool
def campaign_overview() -> str:
    """Campaign facts and totals: dates, plan, spend to date, trials, customers, demo requests,
    and the business assumptions behind revenue and pipeline."""
    return json.dumps({
        "company": "Athenova (fictional AI-tutoring startup)", "campaign": "Learn Smarter, back-to-school launch of Athenova Pro",
        "weeks": int(POSTS.week.max()), "start": "2026-08-03", "planned_budget": int(PLAN.planned_spend_usd.sum()),
        "actual_spend": round(POSTS.spend_usd.sum()), "trials": int(POSTS.trials.sum()),
        "paying_customers": int(POSTS.paid_conversions.sum()), "school_demo_requests": int(POSTS.demo_requests.sum()),
        "assumptions": {"revenue_per_customer_first_year_usd": 96, "pipeline_value_per_demo_request_usd": 1500,
                        "note": "revenue_usd is first-year only; lifetime value is higher if customers renew"},
        "audiences": {"Students": "users, mostly on TikTok/Instagram/YouTube", "Parents": "payers",
                      "Educators": "B2B school licenses via LinkedIn"},
    })


@beta_tool
def channel_economics(segment: str = "all") -> str:
    """Paid-media unit economics per platform: spend, CPM, CTR, trials, CPA (cost per trial),
    customers, CAC (cost per paying customer), first-year ROAS, demo requests, pipeline per dollar.

    Args:
        segment: Students, Parents, Educators, or "all".
    """
    d = _filter(POSTS[POSTS.paid == 1], segment=segment)
    return _json(d.groupby("platform").apply(_econ, include_groups=False))


@beta_tool
def budget_pacing() -> str:
    """Actual vs planned paid spend by week and platform (pacing = actual / plan - 1)."""
    a = POSTS.groupby(["week", "platform"]).spend_usd.sum().rename("actual").reset_index()
    m = a.merge(PLAN, on=["week", "platform"])
    m["pacing"] = (m.actual / m.planned_spend_usd - 1).round(3)
    m["actual"] = m.actual.round(0)
    return m.to_json(orient="records")


@beta_tool
def weekly_trend(metric: str, platform: str = "all", segment: str = "all") -> str:
    """A metric by campaign week.

    Args:
        metric: one of spend, trials, customers, CPA, CAC, trials_per_1k_clicks, engagement_rate.
        platform: TikTok, Instagram, YouTube, LinkedIn, or "all".
        segment: Students, Parents, Educators, or "all".
    """
    d = _filter(POSTS, platform, segment)
    g = d.groupby("week").agg(spend=("spend_usd", "sum"), trials=("trials", "sum"),
                              customers=("paid_conversions", "sum"), clicks=("clicks", "sum"),
                              engagement_rate=("engagement_rate", "mean"))
    g["CPA"] = g.spend / g.trials.where(g.trials > 0)
    g["CAC"] = g.spend / g.customers.where(g.customers > 0)
    g["trials_per_1k_clicks"] = g.trials / g.clicks * 1000
    if metric not in g.columns:
        return json.dumps({"error": f"unknown metric {metric!r}"})
    return _json(g[[metric]].round(3))


@beta_tool
def performance_by(dimension: str, platform: str = "all", segment: str = "all") -> str:
    """Performance grouped by a dimension: posts, mean engagement rate, CTR, trials, customers,
    demo requests, and CPA for paid posts.

    Args:
        dimension: one of pillar, format, segment, paid.
        platform: TikTok, Instagram, YouTube, LinkedIn, or "all".
        segment: Students, Parents, Educators, or "all".
    """
    if dimension not in {"pillar", "format", "segment", "paid"}:
        return json.dumps({"error": f"unknown dimension {dimension!r}"})
    d = _filter(POSTS, platform, segment)
    g = d.groupby(dimension).agg(posts=("post_id", "count"), engagement_rate=("engagement_rate", "mean"),
                                 impressions=("impressions", "sum"), clicks=("clicks", "sum"),
                                 trials=("trials", "sum"), customers=("paid_conversions", "sum"),
                                 demo_requests=("demo_requests", "sum"))
    g["CTR"] = g.clicks / g.impressions
    paid = d[d.paid == 1].groupby(dimension)[["spend_usd", "trials"]].sum()
    g["paid_CPA"] = paid.spend_usd / paid.trials.where(paid.trials > 0)
    return _json(g.drop(columns=["impressions", "clicks"]).round(4))


@beta_tool
def spend_response(platform: str) -> str:
    """Weekly paid spend vs CPM, CTR and CPA for one platform, to check for diminishing returns.

    Args:
        platform: TikTok, Instagram, YouTube, or LinkedIn.
    """
    d = _filter(POSTS[POSTS.paid == 1], platform)
    return _json(d.groupby("week").apply(_econ, include_groups=False)[["spend", "CPM", "CTR", "CPA", "CAC"]])


@beta_tool
def ab_test_results() -> str:
    """Results of the TikTok ad-hook A/B test (14 days) with two-proportion z-tests for
    click-through rate, trials per click, and trials per impression."""
    t = AB.groupby(["variant", "hook"])[["impressions", "clicks", "trials"]].sum().reset_index()
    a, b = t.iloc[0], t.iloc[1]

    def z_test(x1, n1, x2, n2):
        p1, p2, p = x1 / n1, x2 / n2, (x1 + x2) / (n1 + n2)
        z = (p2 - p1) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
        return {"A": round(p1, 5), "B": round(p2, 5), "lift_B_vs_A": round(p2 / p1 - 1, 3),
                "z": round(z, 2), "p_value": round(math.erfc(abs(z) / math.sqrt(2)), 4)}

    return json.dumps({
        "variants": t.to_dict(orient="records"),
        "ctr": z_test(a.clicks, a.impressions, b.clicks, b.impressions),
        "trials_per_click": z_test(a.trials, a.clicks, b.trials, b.clicks),
        "trials_per_impression": z_test(a.trials, a.impressions, b.trials, b.impressions),
    })


@beta_tool
def comment_topics_by_week(segment: str = "all") -> str:
    """Comment counts per week by issue topic (keyword rules: privacy, pricing, cheating, bugs,
    efficacy, other) plus the share of negative comments.

    Args:
        segment: Students, Parents, Educators, or "all".
    """
    c = _filter(COMMENTS, segment=segment)
    t = c.pivot_table(index="week", columns="topic", values="comment_id", aggfunc="count", fill_value=0)
    t["negative_share"] = c.groupby("week").label.apply(lambda s: round((s == "negative").mean(), 3))
    return _json(t)


@beta_tool
def sample_comments(week: int, segment: str = "all", n: int = 10) -> str:
    """Raw customer comments from one campaign week, to read what people actually said.

    Args:
        week: campaign week 1-12.
        segment: Students, Parents, Educators, or "all".
        n: number of comments (max 20).
    """
    c = _filter(COMMENTS[COMMENTS.week == week], segment=segment)
    return json.dumps(c[["segment", "platform", "text"]].head(min(n, 20)).to_dict(orient="records"))


TOOLS = [campaign_overview, channel_economics, budget_pacing, weekly_trend, performance_by,
         spend_response, ab_test_results, comment_topics_by_week, sample_comments]

SYSTEM = """You are a senior growth-marketing analyst advising the CMO of Athenova, an AI-tutoring
startup, on its 12-week back-to-school campaign. Your tools query the campaign's data
(synthetic, for a graduate business course).

Work like a rigorous analyst: investigate with the tools before concluding, distinguish
cost per trial (CPA) from cost per paying customer (CAC) and from B2B pipeline, check
statistical significance before declaring a test winner, and quote the numbers behind
every claim. Never invent figures; if something cannot be known from the data, say so
and propose how to measure it.

Write the final memo in Markdown for the CMO with these sections:
1. Executive summary (3-4 bullets)
2. Channel economics: what each channel is really buying
3. The week-7 privacy incident: impact, recovery, lessons
4. A/B test verdict, including any compliance concern
5. Budget recommendation: a table allocating the amount in the user's request across
   platform × audience × content, with the expected outcome and rationale for each line
6. Risks, assumptions and measurement plan
Keep it under 900 words."""

DEFAULT_GOAL = ("The board approved a 4-week extension with $400,000 of paid media. How should we "
                "allocate it across platforms, audiences and content, and what did we learn from "
                "the privacy incident and the A/B test?")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", default=DEFAULT_GOAL)
    args = ap.parse_args()

    import anthropic

    client = anthropic.Anthropic(api_key=require_key("ANTHROPIC_API_KEY", "https://platform.claude.com"))
    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        tools=TOOLS,
        output_config={"effort": "medium"},
        # If the model ever declines a request, the API retries it on a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        max_iterations=20,
        messages=[{"role": "user", "content": args.goal}],
    )

    tokens_in = tokens_out = 0
    final = None
    print(f"Agent running on {MODEL}...\n")
    for message in runner:  # one iteration per model turn
        tokens_in += message.usage.input_tokens
        tokens_out += message.usage.output_tokens
        for block in message.content:
            if block.type == "tool_use":
                print(f"  🔧 {block.name}({json.dumps(block.input)})")
        final = message

    if final is None or final.stop_reason == "refusal":
        raise SystemExit("The model declined this request. Try rephrasing the goal.")
    memo = "\n".join(b.text for b in final.content if b.type == "text")
    print("\n" + memo)

    out = ROOT / "reports" / "strategy_memo.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(memo, encoding="utf-8")
    p_in, p_out = PRICE_PER_MTOK.get(MODEL, (4.00, 20.00))
    print("\nsaved -> reports/strategy_memo.md")
    print(f"tokens: {tokens_in:,} in / {tokens_out:,} out  ≈ ${tokens_in / 1e6 * p_in + tokens_out / 1e6 * p_out:.3f}")


if __name__ == "__main__":
    main()
