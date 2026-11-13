import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engagement import add_engagement, engagement_rate  # noqa: E402


def test_basic_rate():
    assert engagement_rate(80, 10, 10, 1000) == pytest.approx(0.10)


def test_zero_impressions_is_zero_not_crash():
    assert engagement_rate(5, 1, 0, 0) == 0.0


def test_add_engagement_does_not_mutate_input():
    df = pd.DataFrame({"likes": [1], "comments": [1], "shares": [0], "impressions": [4]})
    out = add_engagement(df)
    assert "engagement_rate" not in df.columns
    assert out.loc[0, "engagement_rate"] == pytest.approx(0.5)
