"""Demo 5 (graduate track): comment sentiment + crisis early warning.

Scores every comment in data/sample_comments.csv, then tracks weekly *net
sentiment* (share positive minus share negative) per platform, and flags
weeks where it falls sharply.

Engine: VADER (pip install vaderSentiment) if available, otherwise a small
built-in word list, so the demo always runs. Comparing the two engines is
Exercise 5.2. Extension (Exercise 5.3): replace the scorer with an LLM API call
and compare cost, speed and accuracy.

Usage:
    python demos/05_sentiment/sentiment.py
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
COMMENTS = ROOT / "data" / "sample_comments.csv"
OUT = ROOT / "reports" / "weekly_sentiment.csv"

POS = {"love", "best", "good", "great", "amazing", "fantastic", "friendly", "obsessed", "deal"}
NEG = {"waited", "expensive", "loud", "wrong", "disappointed", "closed", "terrible", "bad", "slow"}

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    ENGINE = "VADER"
except ImportError:  # fall back to the tiny lexicon
    _vader = None
    ENGINE = "word list"


def score(text: str) -> float:
    """Return a sentiment score in [-1, 1]."""
    if _vader:
        return _vader.polarity_scores(text)["compound"]
    words = re.findall(r"[a-z']+", text.lower())
    p, n = sum(w in POS for w in words), sum(w in NEG for w in words)
    return 0.0 if p == n else (p - n) / (p + n)


def label(s: float) -> str:
    return "positive" if s >= 0.05 else "negative" if s <= -0.05 else "neutral"


def main() -> None:
    df = pd.read_csv(COMMENTS, parse_dates=["commented_at"])
    df["score"] = df["text"].map(score)
    df["label"] = df["score"].map(label)
    df["week"] = df["commented_at"].dt.to_period("W").dt.start_time

    print(f"Sentiment engine: {ENGINE}\n")
    print(df["label"].value_counts(normalize=True).mul(100).round(1).to_string(), "\n")

    weekly = (df.groupby(["week", "label"]).size().unstack(fill_value=0))
    weekly["net_sentiment"] = (weekly.get("positive", 0) - weekly.get("negative", 0)) / weekly.sum(axis=1)
    weekly["change"] = weekly["net_sentiment"].diff()

    print("Weekly net sentiment (all platforms)")
    for wk, r in weekly.iterrows():
        bar = "█" * max(0, int(r.net_sentiment * 40))
        flag = "  ⚠️  ALERT: sharp drop" if r.change < -0.25 else ""
        print(f"{wk:%b %d}  {r.net_sentiment:+.2f}  {bar}{flag}")

    print("\nMost common complaints:")
    print(df[df.label == "negative"]["text"].value_counts().head(5).to_string())

    OUT.parent.mkdir(exist_ok=True)
    weekly.to_csv(OUT)
    print(f"\nsaved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
