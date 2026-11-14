"""Demo 5: comment sentiment + issue early warning for the Smiley campaign.

Scores every comment in data/campaign_comments.csv, tracks weekly *net sentiment*
(share positive minus share negative) per audience segment, tags simple issue topics
with keyword rules, and flags weeks where sentiment drops sharply. In this dataset,
that is week 7, when a viral post alleged Smiley trained its AI on student data.

Engine: VADER (pip install vaderSentiment) if installed, otherwise a transparent
word list, so the demo always runs. Demo 6b repeats the job with an LLM; comparing
the two approaches is Exercise 6.2.

Usage:
    python demos/05_sentiment/sentiment.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


ROOT = Path(__file__).resolve().parents[2]
COMMENTS = ROOT / "data" / "campaign_comments.csv"
POSTS = ROOT / "data" / "campaign_posts.csv"
OUT = ROOT / "reports" / "weekly_sentiment.csv"

POS = {"amazing", "love", "best", "worth", "great", "loves", "helped", "pass", "good", "thanks", "helps", "improved"}
NEG = {"expensive", "not", "deleting", "crashing", "broken", "buggy", "slow", "cheating", "hate", "copy",
       "didn't", "did", "too"}  # 'did not', 'too long', 'too expensive': crude on purpose, see Exercise 6.2
TOPIC_RULES = {   # keyword rules a student might write first
    "privacy": r"data|privacy|training|train",
    "pricing": r"expensive|price|plan|discount|\$",
    "cheating": r"cheat|copy",
    "bugs": r"crash|broken|bug|login|slow",
    "efficacy": r"score|evidence|grades|pass|help",
}

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    ENGINE = "VADER"
except ImportError:
    _vader = None
    ENGINE = "word list"


def score(text: str) -> float:
    """Sentiment score in [-1, 1]."""
    if _vader:
        return _vader.polarity_scores(text)["compound"]
    words = re.findall(r"[a-z']+", text.lower())
    p, n = sum(w in POS for w in words), sum(w in NEG for w in words)
    return 0.0 if p == n else (p - n) / (p + n)


def label(s: float) -> str:
    return "positive" if s >= 0.05 else "negative" if s <= -0.05 else "neutral"


def topic(text: str) -> str:
    for name, pattern in TOPIC_RULES.items():
        if re.search(pattern, text, flags=re.I):
            return name
    return "other"


def main() -> None:
    c = pd.read_csv(COMMENTS)
    weeks = pd.read_csv(POSTS, usecols=["post_id", "week"])
    c = c.merge(weeks, on="post_id")
    c["score"] = c["text"].map(score)
    c["label"] = c["score"].map(label)
    c["topic"] = c["text"].map(topic)

    print(f"Sentiment engine: {ENGINE}   ·   {len(c):,} comments\n")
    shares = c.groupby(["week", "label"]).size().unstack(fill_value=0)
    weekly = ((shares.get("positive", 0) - shares.get("negative", 0)) / shares.sum(axis=1)).rename("net_sentiment")
    by_seg = (c.assign(v=c.label.map({"positive": 1, "neutral": 0, "negative": -1}))
                .pivot_table(index="week", columns="segment", values="v", aggfunc="mean"))

    print("Weekly net sentiment (all segments)          by segment: Students / Parents / Educators")
    for wk, v in weekly.items():
        bar = "█" * max(0, int(v * 40))
        flag = "  ⚠️ ALERT: sharp drop" if wk > 1 and v - weekly.get(wk - 1, v) < -0.25 else ""
        segs = " / ".join(f"{by_seg.loc[wk, s]:+.2f}" for s in ["Students", "Parents", "Educators"])
        print(f"week {wk:>2}  {v:+.2f}  {bar:<24} {segs}{flag}")

    worst = int(weekly.idxmin())
    print(f"\nWorst week: {worst}. Negative comments by topic (keyword rules):")
    print(c[(c.week == worst) & (c.label == "negative")].topic.value_counts().to_string())
    print("\nMost common negative comments that week:")
    print(c[(c.week == worst) & (c.label == "negative")].text.value_counts().head(5).to_string())

    OUT.parent.mkdir(exist_ok=True)
    pd.concat([weekly, by_seg], axis=1).to_csv(OUT)
    print(f"\nsaved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
