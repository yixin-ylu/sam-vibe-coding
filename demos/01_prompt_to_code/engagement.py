"""Demo 1: engagement-rate report generated from a single natural-language prompt.

Usage:
    python demos/01_prompt_to_code/engagement.py [path/to/posts.csv]
"""
import sys
from pathlib import Path

import pandas as pd

DEFAULT_CSV = Path(__file__).resolve().parents[2] / "data" / "sample_posts.csv"


def engagement_rate(likes: float, comments: float, shares: float, impressions: float) -> float:
    """Return (likes + comments + shares) / impressions, or 0.0 when impressions is 0."""
    if not impressions:
        return 0.0
    return (likes + comments + shares) / impressions


def add_engagement(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with an `engagement_rate` column."""
    out = df.copy()
    out["engagement_rate"] = [
        engagement_rate(r.likes, r.comments, r.shares, r.impressions)
        for r in out.itertuples()
    ]
    return out


def main(csv_path: Path = DEFAULT_CSV) -> None:
    df = add_engagement(pd.read_csv(csv_path))

    by_platform = (df.groupby("platform")["engagement_rate"].mean()
                     .sort_values(ascending=False) * 100).round(2)
    print("Average engagement rate by platform (%)")
    print(by_platform.to_string(), "\n")

    top5 = df.nlargest(5, "engagement_rate")[["platform", "caption", "engagement_rate"]]
    top5["engagement_rate"] = (top5["engagement_rate"] * 100).round(2).astype(str) + "%"
    print("Top 5 posts by engagement rate")
    print(top5.to_string(index=False))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV)
