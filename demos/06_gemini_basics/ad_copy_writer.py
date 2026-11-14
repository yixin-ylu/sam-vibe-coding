"""Demo 6a: audience-specific ad copy with brand and compliance guardrails (Gemini, free tier).

Smiley sells to three audiences with different motivations: students (save time,
less stress), parents (results, safety, value) and educators (pedagogy, privacy,
classroom fit). The prompt template encodes the brief: audience insight, platform
rules, and compliance rules (no unsubstantiated efficacy claims, which the FTC
treats as deceptive advertising; no targeting of children under 13). A second
call asks the model to audit its own drafts against those rules.

Get a free key at https://aistudio.google.com/apikey and store it as GEMINI_API_KEY
(in Colab: Secrets panel → GEMINI_API_KEY).

Usage:
    python demos/06_gemini_basics/ad_copy_writer.py
    python demos/06_gemini_basics/ad_copy_writer.py --segment Educators --platform LinkedIn
    python demos/06_gemini_basics/ad_copy_writer.py --segment Parents --platform Instagram --offer "30% off annual plan"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from keys import require_key  # noqa: E402

# "-latest" alias = Google's current Flash model, so the demo survives model updates.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

AUDIENCE = {
    "Students": "high-school and college students; want to save time, feel less stressed, and actually "
                "understand material; skeptical of anything that feels like an ad",
    "Parents": "parents of 13-18 year olds; care about results, value for money, and their child's data "
               "privacy (a privacy rumour circulated in week 7 of the campaign)",
    "Educators": "teachers and school administrators; care about pedagogy (explain, don't just answer), "
                 "academic integrity, student data privacy (FERPA/COPPA), and easy classroom rollout",
}
PLATFORM_RULES = {
    "TikTok": "a hook in the first 5 words, casual, max 150 characters, 2-3 hashtags",
    "Instagram": "2 short sentences, at most 2 emojis, 3-5 hashtags at the end",
    "YouTube": "a 15-second pre-roll script: hook (0-3s), problem, solution, call to action",
    "LinkedIn": "professional, 3-4 sentences, no emojis, end with a question or invitation, 1-2 hashtags",
}
COMPLIANCE = """- Do NOT promise specific grade or score improvements ("raise your grade", "guaranteed A").
- Do NOT invent statistics, testimonials, prices, or dates that are not given in the brief.
- Do NOT address children under 13.
- Privacy claims must be limited to this approved fact: "Smiley does not use student work to train its AI models."
- Smiley explains concepts step by step; never present it as a way to get homework answers."""


def brief(segment: str, platform: str, offer: str | None) -> str:
    return (
        "You are a senior copywriter for Smiley, an AI-tutoring app (Smiley Pro launch, back-to-school campaign).\n"
        f"Audience: {AUDIENCE[segment]}.\n"
        f"Platform: {platform}. Format rules: {PLATFORM_RULES[platform]}.\n"
        f"Offer: {offer or 'free 14-day Pro trial'}.\n"
        f"Compliance rules:\n{COMPLIANCE}\n\n"
        "Write 3 distinct ad variants, each built on a different message angle. "
        "Label each with its angle in brackets, e.g. [Time saved]."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--segment", default="Parents", choices=list(AUDIENCE))
    ap.add_argument("--platform", default="Instagram", choices=list(PLATFORM_RULES))
    ap.add_argument("--offer", default=None)
    args = ap.parse_args()

    from google import genai  # pip install google-genai

    client = genai.Client(api_key=require_key("GEMINI_API_KEY", "https://aistudio.google.com/apikey"))
    prompt = brief(args.segment, args.platform, args.offer)
    print(f"--- brief sent to {MODEL} ---\n{prompt}\n")
    drafts = client.models.generate_content(model=MODEL, contents=prompt).text
    print(f"--- {args.segment} × {args.platform} drafts ---\n{drafts}\n")

    audit = client.models.generate_content(
        model=MODEL,
        contents=("Act as a marketing compliance reviewer. For each ad below, list any violation of these "
                  f"rules, or write 'OK'. Be strict.\nRules:\n{COMPLIANCE}\n\nAds:\n{drafts}"),
    ).text
    print(f"--- compliance self-check (still needs a human!) ---\n{audit}")


if __name__ == "__main__":
    main()
