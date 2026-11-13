"""Demo 7 (advanced): an AI "social media strategist" agent built on the Claude API.

Unlike the single prompt → single answer calls in Demo 6, Claude here gets a set of
TOOLS (plain Python functions over our data). It decides which tools to call, in what
order, reads the results, and keeps going until it can write an evidence-based
strategy memo. Every tool call is printed, so students can audit the agent's reasoning.

Get a key at https://platform.claude.com and store it as ANTHROPIC_API_KEY
(in Colab: Secrets panel → ANTHROPIC_API_KEY). One run costs roughly $0.10–$0.40 on
the default model and prints the exact token cost at the end.

Usage:
    python demos/07_claude_agent/strategist_agent.py
    python demos/07_claude_agent/strategist_agent.py --goal "Should we keep posting on X?"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1]))
from keys import require_key  # noqa: E402

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")
PRICE_PER_MTOK = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00),
                  "claude-haiku-5-5": (0.10, 0.50)}  # (input, output) USD per 1M tokens

# ── Data the tools work on (synthetic, no personal data) ──────────────────────
POSTS = pd.read_csv(ROOT / "data" / "sample_posts.csv", parse_dates=["posted_at"])
POSTS["engagement_rate"] = (POSTS[["likes", "comments", "shares"]].sum(axis=1)
                            / POSTS["impressions"].where(POSTS["impressions"] > 0)).fillna(0)
POSTS["week"] = POSTS["posted_at"].dt.to_period("W").dt.start_time.dt.strftime("%Y-%m-%d")
COMMENTS = pd.read_csv(ROOT / "data" / "sample_comments.csv", parse_dates=["commented_at"])
COMMENTS["week"] = COMMENTS["commented_at"].dt.to_period("W").dt.start_time.dt.strftime("%Y-%m-%d")


def _subset(platform: str) -> pd.DataFrame:
    return POSTS if platform.lower() == "all" else POSTS[POSTS.platform.str.lower() == platform.lower()]


# ── Tools: ordinary Python functions + a docstring the model reads ───────────
from anthropic import beta_tool  # noqa: E402


@beta_tool
def platform_summary() -> str:
    """Return one row per platform: posts, total impressions, mean engagement rate,
    and follower count at the start and end of the period."""
    g = POSTS.sort_values("posted_at").groupby("platform").agg(
        posts=("post_id", "count"), impressions=("impressions", "sum"),
        avg_engagement_rate=("engagement_rate", "mean"),
        followers_start=("followers", "first"), followers_end=("followers", "last"))
    return g.round(4).reset_index().to_json(orient="records")


@beta_tool
def weekly_trend(platform: str) -> str:
    """Weekly impressions and mean engagement rate.

    Args:
        platform: Instagram, TikTok, LinkedIn, X, or "all".
    """
    d = _subset(platform).groupby("week").agg(
        impressions=("impressions", "sum"), engagement_rate=("engagement_rate", "mean"))
    return d.round(4).reset_index().to_json(orient="records")


@beta_tool
def performance_by(dimension: str, platform: str = "all") -> str:
    """Mean engagement rate and post count grouped by a dimension.

    Args:
        dimension: one of post_type, category, hour, weekday.
        platform: Instagram, TikTok, LinkedIn, X, or "all".
    """
    d = _subset(platform).copy()
    d["hour"] = d.posted_at.dt.hour
    d["weekday"] = d.posted_at.dt.day_name()
    if dimension not in {"post_type", "category", "hour", "weekday"}:
        return json.dumps({"error": f"unknown dimension {dimension!r}"})
    g = d.groupby(dimension).agg(posts=("post_id", "count"),
                                 avg_engagement_rate=("engagement_rate", "mean"))
    return g.round(4).sort_values("avg_engagement_rate", ascending=False).reset_index().to_json(orient="records")


@beta_tool
def top_posts(platform: str = "all", n: int = 5, worst: bool = False) -> str:
    """The best (or worst) posts by engagement rate.

    Args:
        platform: Instagram, TikTok, LinkedIn, X, or "all".
        n: how many posts to return (max 10).
        worst: true to return the lowest-engagement posts instead.
    """
    d = _subset(platform)
    d = d.nsmallest(min(n, 10), "engagement_rate") if worst else d.nlargest(min(n, 10), "engagement_rate")
    cols = ["posted_at", "platform", "post_type", "category", "caption", "impressions", "engagement_rate"]
    return d[cols].assign(posted_at=d.posted_at.astype(str)).round(4).to_json(orient="records")


@beta_tool
def comment_sentiment_by_week() -> str:
    """Share of comments per week that contain common complaint words, plus total
    comment counts. Use it to spot reputation problems."""
    neg = COMMENTS.text.str.contains("wait|expensive|loud|wrong|disappoint|closed|terrible", case=False)
    g = COMMENTS.assign(negative=neg).groupby("week").agg(comments=("text", "count"),
                                                         negative_share=("negative", "mean"))
    return g.round(3).reset_index().to_json(orient="records")


@beta_tool
def sample_comments(week: str, n: int = 8) -> str:
    """Return up to n raw customer comments from a given week, to read what people actually said.

    Args:
        week: week start date as YYYY-MM-DD (as returned by other tools).
        n: number of comments (max 15).
    """
    d = COMMENTS[COMMENTS.week == week]
    return json.dumps(d.text.head(min(n, 15)).tolist())


TOOLS = [platform_summary, weekly_trend, performance_by, top_posts,
         comment_sentiment_by_week, sample_comments]

SYSTEM = """You are a senior social media strategist advising Foggy Bottom Coffee Co., a
coffee shop next to a university campus. You have tools that query 12 weeks of the
shop's social media data (synthetic, for a class).

Work like an analyst: look at the data with the tools before concluding anything,
and quote the numbers that support each claim. Do not invent figures.

When you have enough evidence, write a memo in Markdown for the shop owner, who is
not technical, with these sections:
1. Executive summary (3 bullets)
2. What is working (with numbers)
3. Problems and risks (with numbers, including anything you find in the comments)
4. Recommendations (5 concrete actions, each tied to evidence)
5. Two-week content calendar (a table: day, platform, format, time, post idea)
Keep it under 700 words."""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", default="Review our last 12 weeks and tell us what to do next.")
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
        max_iterations=15,
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
    cost = tokens_in / 1e6 * p_in + tokens_out / 1e6 * p_out
    print(f"\nsaved -> reports/strategy_memo.md")
    print(f"tokens: {tokens_in:,} in / {tokens_out:,} out  ≈ ${cost:.3f}")


if __name__ == "__main__":
    main()
