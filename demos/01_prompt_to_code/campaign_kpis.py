"""Demo 1: channel unit economics for the Athenova campaign, generated from one prompt.

Usage:
    python demos/01_prompt_to_code/campaign_kpis.py [path/to/campaign_posts.csv]
"""
import math
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # emoji/Δ output on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_CSV = Path(__file__).resolve().parents[2] / "data" / "campaign_posts.csv"
SUM_COLS = ["spend_usd", "impressions", "clicks", "trials", "paid_conversions",
            "demo_requests", "revenue_usd", "pipeline_usd"]


def safe_div(a: float, b: float) -> float:
    """Return a / b, or NaN when b is 0 (so a channel never looks 'free')."""
    return a / b if b else math.nan


def channel_kpis(df: pd.DataFrame, by: str = "platform") -> pd.DataFrame:
    """Aggregate PAID posts by `by` and compute CPM, CTR, CPA, CAC, ROAS, cost per demo."""
    g = df[df["paid"] == 1].groupby(by)[SUM_COLS].sum()
    rows = {}
    for key, r in g.iterrows():
        rows[key] = {
            "spend": r.spend_usd,
            "CPM": safe_div(r.spend_usd, r.impressions) * 1000,
            "CTR": safe_div(r.clicks, r.impressions),
            "CPA": safe_div(r.spend_usd, r.trials),
            "CAC": safe_div(r.spend_usd, r.paid_conversions),
            "ROAS": safe_div(r.revenue_usd, r.spend_usd),
            "cost_per_demo": safe_div(r.spend_usd, r.demo_requests),
            "pipeline_per_$": safe_div(r.pipeline_usd, r.spend_usd),
        }
    return pd.DataFrame.from_dict(rows, orient="index").sort_values("CAC")


def main(csv_path: Path = DEFAULT_CSV) -> None:
    k = channel_kpis(pd.read_csv(csv_path))
    out = k.copy()
    out["CTR"] = (out["CTR"] * 100).map("{:.2f}%".format)
    for col in ["spend", "CPM", "CPA", "CAC", "cost_per_demo"]:
        out[col] = out[col].map(lambda v: "-" if math.isnan(v) else f"${v:,.2f}")
    for col in ["ROAS", "pipeline_per_$"]:
        out[col] = out[col].map("{:.2f}".format)
    print("Paid-media unit economics by platform (sorted by CAC)\n")
    print(out.to_string())


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV)
