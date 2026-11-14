"""Demo 6b: classifying campaign comments with an LLM into structured (JSON) data.

Gemini (free tier) labels each unique comment with sentiment, an issue topic, and
whether it needs a reply from the brand, returning JSON that matches a schema, so
results go straight into pandas. We then compare the LLM's sentiment with the
VADER / word-list scorer from Demo 5 and the keyword topic rules.

Usage:
    python demos/06_gemini_basics/classify_comments.py
    python demos/06_gemini_basics/classify_comments.py --week 7      # only the crisis week
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from enum import Enum
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "05_sentiment"))
from keys import require_key  # noqa: E402
from sentiment import ENGINE, label as rule_label, score as rule_score, topic as rule_topic  # noqa: E402

MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
OUT = ROOT / "reports" / "comment_labels.csv"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Topic(str, Enum):
    privacy = "privacy"
    pricing = "pricing"
    efficacy = "efficacy"
    cheating = "cheating"
    bugs = "bugs"
    praise = "praise"
    question = "question"
    other = "other"


class Label(BaseModel):
    id: int
    sentiment: Sentiment
    topic: Topic
    needs_reply: bool


def classify(client, texts: list[str]) -> list[Label]:
    from google.genai import types
    numbered = "\n".join(f"{i}. {t}" for i, t in enumerate(texts))
    prompt = ("These are social-media comments on ads for Smiley, an AI-tutoring app. For each comment give "
              "sentiment, the main topic, and needs_reply=true if the brand's community team should respond "
              "(questions, complaints, or misinformation). Use the comment number as id.\n\n" + numbered)
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=list[Label]),
    )
    return [Label(**d) for d in json.loads(response.text)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, help="only comments on posts from this campaign week")
    args = ap.parse_args()

    from google import genai

    c = pd.read_csv(ROOT / "data" / "campaign_comments.csv").merge(
        pd.read_csv(ROOT / "data" / "campaign_posts.csv", usecols=["post_id", "week"]), on="post_id")
    if args.week:
        c = c[c.week == args.week]
    counts = c.text.value_counts()
    texts = counts.index.tolist()  # unique comments: one request, fewer tokens
    client = genai.Client(api_key=require_key("GEMINI_API_KEY", "https://aistudio.google.com/apikey"))
    print(f"Sending {len(texts)} unique comments ({len(c)} total) to {MODEL} in ONE request...")

    labels = {l.id: l for l in classify(client, texts)}
    rows = []
    for i, t in enumerate(texts):
        l = labels.get(i)
        rows.append({"text": t, "count": counts[t],
                     "llm_sentiment": l.sentiment.value if l else None,
                     "llm_topic": l.topic.value if l else None,
                     "needs_reply": l.needs_reply if l else None,
                     "rule_sentiment": rule_label(rule_score(t)), "rule_topic": rule_topic(t)})
    df = pd.DataFrame(rows)

    pd.set_option("display.width", 160, "display.max_colwidth", 55)
    print(df.to_string(index=False), "\n")
    w = df["count"]
    print(f"Sentiment agreement, LLM vs {ENGINE} (weighted by volume): "
          f"{((df.llm_sentiment == df.rule_sentiment) * w).sum() / w.sum():.0%}")
    print(f"Topic agreement, LLM vs keyword rules: {((df.llm_topic == df.rule_topic) * w).sum() / w.sum():.0%}")
    print(f"Comments needing a reply: {int(w[df.needs_reply == True].sum()):,} of {int(w.sum()):,}\n")  # noqa: E712
    print("Negative volume by topic (LLM):")
    print(df[df.llm_sentiment == "negative"].groupby("llm_topic")["count"].sum().sort_values(ascending=False).to_string())

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nsaved -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
