"""
Generate a synthetic social-media dataset for the SAM course demos.

Everything here is FAKE: a fictional campus brand, "Foggy Bottom Coffee Co.",
posting on four platforms for 12 weeks. Using synthetic data means every demo
runs offline, with no API keys and no personal data (see the course's
Responsible-AI rules).

Run:
    python data/generate_sample_data.py
Outputs:
    data/sample_posts.csv     one row per post (metrics)
    data/sample_comments.csv  one row per comment (for sentiment demos)
"""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 2026
OUT_DIR = Path(__file__).resolve().parent

PLATFORMS = {
    # platform: (start followers, weekly growth, base reach multiplier)
    "Instagram": (4200, 0.025, 1.00),
    "TikTok":    (1800, 0.060, 1.80),
    "LinkedIn":  (950,  0.015, 0.45),
    "X":         (2600, 0.008, 0.60),
}
POST_TYPES = {
    # post type: engagement multiplier
    "photo": 1.00, "video": 1.45, "carousel": 1.20, "text": 0.70, "poll": 1.10,
}
TOPICS = [
    ("New seasonal latte is here", "product"),
    ("Study-break discount for students this week", "promo"),
    ("Meet our barista of the month", "people"),
    ("Behind the scenes: how we roast our beans", "story"),
    ("Finals week hours extended until 2am", "info"),
    ("Latte-art challenge: vote for your favorite", "engagement"),
    ("We now offer oat milk at no extra charge", "product"),
    ("Sustainability update: compostable cups", "story"),
    ("Live music Friday night at the shop", "event"),
    ("Hiring part-time baristas", "info"),
]
POSITIVE = ["Love this place!", "Best latte near campus", "So good, going back tomorrow",
            "Great service and friendly staff", "Amazing deal for students",
            "The new drink is fantastic", "Obsessed with the oat milk option"]
NEUTRAL = ["What time do you open on Sunday?", "Is there wifi?", "Do you take Apple Pay?",
           "Where is the new location?", "Is the discount valid on weekends?"]
NEGATIVE = ["Waited 25 minutes for one coffee", "Too expensive for a small cup",
            "The music was way too loud", "My order was wrong again",
            "Disappointed, the shop was closed early", "Terrible wifi today"]


def best_hour_bonus(hour: int) -> float:
    """Posts around lunch and evening do better -- a pattern students can discover."""
    if 11 <= hour <= 13:
        return 1.25
    if 18 <= hour <= 21:
        return 1.35
    if hour < 8:
        return 0.70
    return 1.0


def main() -> None:
    rng = random.Random(SEED)
    start = datetime(2026, 8, 31, 0, 0)  # first week of fall semester
    posts, comments = [], []
    post_id = 1000
    comment_id = 50000

    for platform, (followers0, growth, reach_mult) in PLATFORMS.items():
        for week in range(12):
            followers = int(followers0 * (1 + growth) ** week)
            for _ in range(rng.randint(2, 4)):
                post_id += 1
                day = rng.randint(0, 6)
                hour = rng.choice([7, 9, 11, 12, 13, 15, 17, 19, 20, 21])
                posted_at = start + timedelta(weeks=week, days=day, hours=hour,
                                              minutes=rng.randint(0, 59))
                ptype = rng.choice(list(POST_TYPES))
                if platform == "TikTok":
                    ptype = "video"
                topic, category = rng.choice(TOPICS)

                impressions = int(followers * reach_mult * rng.uniform(0.6, 1.6)
                                  * best_hour_bonus(hour))
                eng_rate = 0.045 * POST_TYPES[ptype] * best_hour_bonus(hour) * rng.uniform(0.6, 1.4)
                if category in ("promo", "engagement"):
                    eng_rate *= 1.3
                interactions = max(1, int(impressions * eng_rate))
                likes = int(interactions * rng.uniform(0.70, 0.85))
                n_comments = int(interactions * rng.uniform(0.05, 0.15))
                shares = max(0, interactions - likes - n_comments)

                # week 9 = a small "service crisis": more negative comments
                crisis = week == 8
                posts.append({
                    "post_id": post_id, "platform": platform,
                    "posted_at": posted_at.isoformat(timespec="minutes"),
                    "post_type": ptype, "category": category, "caption": topic,
                    "impressions": impressions, "likes": likes,
                    "comments": n_comments, "shares": shares, "followers": followers,
                })
                for _ in range(min(n_comments, 6)):
                    comment_id += 1
                    r = rng.random()
                    neg_p = 0.45 if crisis else 0.15
                    if r < neg_p:
                        text = rng.choice(NEGATIVE)
                    elif r < neg_p + 0.25:
                        text = rng.choice(NEUTRAL)
                    else:
                        text = rng.choice(POSITIVE)
                    comments.append({
                        "comment_id": comment_id, "post_id": post_id,
                        "platform": platform,
                        "commented_at": (posted_at + timedelta(minutes=rng.randint(5, 600)))
                        .isoformat(timespec="minutes"),
                        "text": text,
                    })

    posts.sort(key=lambda p: p["posted_at"])
    for name, rows in (("sample_posts.csv", posts), ("sample_comments.csv", comments)):
        with open(OUT_DIR / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows):>5} rows -> data/{name}")


if __name__ == "__main__":
    main()
