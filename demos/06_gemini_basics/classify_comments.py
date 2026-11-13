"""Demo 6b: classifying customer comments with an LLM and getting structured (JSON) output.

Gemini (free tier) labels each unique comment with a sentiment AND a business topic,
returning JSON that matches a schema, so the result goes straight into pandas.
Then we compare the LLM's labels with the simple word-list scorer from Demo 5.

Usage:
    python demos/06_gemini_basics/classify_comments.py            # 40 unique comments
    python demos/06_gemini_basics/classify_comments.py --limit 15
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

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "05_sentiment"))
from keys import require_key  # noqa: E402
from sentiment import label as wordlist_label, score as wordlist_score  # noqa: E402

MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
COMMENTS = HERE.parents[2] / "data" / "sample_comments.csv"
OUT = HERE.parents[2] / "reports" / "comment_labels.csv"


class Sentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class Topic(str, Enum):
    service = "service"
    price = "price"
    product = "product"
    ambience = "ambience"
    question = "question"
    other = "other"


class Label(BaseModel):
    id: int
    sentiment: Sentiment
    topic: Topic


def classify(client, texts: list[str]) -> list[Label]:
    numbered = "\n".join(f"{i}. {t}" for i, t in enumerate(texts))
    prompt = ("Classify each customer comment about a coffee shop. "
              "Return one item per comment, using the comment's number as id.\n\n" + numbered)
    from google.genai import types
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[Label],
        ),
    )
    return [Label(**d) for d in json.loads(response.text)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40, help="max unique comments to send")
    args = ap.parse_args()

    from google import genai

    client = genai.Client(api_key=require_key("GEMINI_API_KEY", "https://aistudio.google.com/apikey"))
    texts = pd.read_csv(COMMENTS)["text"].drop_duplicates().head(args.limit).tolist()
    print(f"Sending {len(texts)} unique comments to {MODEL} in ONE request...")

    labels = {l.id: l for l in classify(client, texts)}
    rows = []
    for i, t in enumerate(texts):
        l = labels.get(i)
        rows.append({"text": t,
                     "llm_sentiment": l.sentiment.value if l else None,
                     "llm_topic": l.topic.value if l else None,
                     "wordlist_sentiment": wordlist_label(wordlist_score(t))})
    df = pd.DataFrame(rows)

    pd.set_option("display.width", 140, "display.max_colwidth", 50)
    print(df.to_string(index=False), "\n")
    agree = (df.llm_sentiment == df.wordlist_sentiment).mean()
    print(f"LLM vs word-list agreement on sentiment: {agree:.0%}")
    print("Where they disagree, who is right? (That is Exercise 6.2.)\n")
    print("Complaints by topic (LLM):")
    print(df[df.llm_sentiment == "negative"].llm_topic.value_counts().to_string())

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nsaved -> {OUT.relative_to(HERE.parents[2])}")


if __name__ == "__main__":
    main()
