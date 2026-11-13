import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from campaign_kpis import channel_kpis, safe_div  # noqa: E402


def test_safe_div_normal():
    assert safe_div(10, 4) == 2.5


def test_safe_div_by_zero_is_nan_not_zero():
    assert math.isnan(safe_div(500, 0))


def test_cac_by_hand():
    # Two paid TikTok posts: $300 + $100 spend, 3 + 1 customers -> CAC = 400 / 4 = $100.
    # One organic post must be ignored.
    df = pd.DataFrame({
        "platform": ["TikTok", "TikTok", "TikTok"], "paid": [1, 1, 0],
        "spend_usd": [300, 100, 0], "impressions": [30000, 10000, 5000], "clicks": [300, 100, 50],
        "trials": [30, 10, 5], "paid_conversions": [3, 1, 1], "demo_requests": [0, 0, 0],
        "revenue_usd": [288, 96, 96], "pipeline_usd": [0, 0, 0],
    })
    k = channel_kpis(df).loc["TikTok"]
    assert k.CAC == pytest.approx(100)
    assert k.CPA == pytest.approx(10)
    assert math.isnan(k.cost_per_demo)
