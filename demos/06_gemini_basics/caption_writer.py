"""Demo 6a: your first LLM API call, writing platform-specific captions with Gemini.

Uses the free tier of the Google Gemini API, so students need no credit card.
Get a key at https://aistudio.google.com/apikey and store it as GEMINI_API_KEY
(in Colab: Secrets panel → GEMINI_API_KEY).

Usage:
    python demos/06_gemini_basics/caption_writer.py
    python demos/06_gemini_basics/caption_writer.py --product "pumpkin spice cold brew" --platform TikTok
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from keys import require_key  # noqa: E402

# "-latest" alias = Google's current Flash model, so the demo keeps working when
# model versions change. Override with:  export GEMINI_MODEL=<model id>
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

PLATFORM_RULES = {
    "Instagram": "max 2 short sentences, 1-2 emojis, 3-5 hashtags at the end",
    "TikTok": "very casual, a hook in the first 5 words, 2-3 trending-style hashtags",
    "LinkedIn": "professional tone, no emojis, mention community or sustainability, 1-2 hashtags",
    "X": "under 200 characters, witty, at most 1 hashtag",
}


def build_prompt(brand: str, product: str, platform: str, audience: str) -> str:
    return (
        f"You are the social media manager for {brand}, a coffee shop near a university campus.\n"
        f"Write 3 different {platform} captions announcing: {product}.\n"
        f"Audience: {audience}.\n"
        f"Platform rules: {PLATFORM_RULES[platform]}.\n"
        "Number the captions 1-3. Do not invent prices, dates or discounts that were not given."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="Foggy Bottom Coffee Co.")
    ap.add_argument("--product", default="our new oat-milk maple latte")
    ap.add_argument("--platform", default="Instagram", choices=list(PLATFORM_RULES))
    ap.add_argument("--audience", default="undergraduate students during midterms")
    args = ap.parse_args()

    from google import genai  # pip install google-genai

    client = genai.Client(api_key=require_key("GEMINI_API_KEY", "https://aistudio.google.com/apikey"))
    prompt = build_prompt(args.brand, args.product, args.platform, args.audience)
    print(f"--- prompt sent to {MODEL} ---\n{prompt}\n")

    response = client.models.generate_content(model=MODEL, contents=prompt)
    print(f"--- {args.platform} captions ---\n{response.text}")


if __name__ == "__main__":
    main()
