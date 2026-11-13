"""Data prep + Plotly charts for the Lumora campaign dashboard.

Shared by the Streamlit app (app.py) and the Colab notebook, so students can
see the charts inline in Colab/Jupyter without running a web server.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA = DATA_DIR / "campaign_posts.csv"
PLAN = DATA_DIR / "budget_plan.csv"
GW_BLUE = "#005581"
PALETTE = {"TikTok": "#005581", "Instagram": "#A75523", "YouTube": "#0D9488", "LinkedIn": "#7C3AED"}
SEG_COLORS = {"Students": "#005581", "Parents": "#A75523", "Educators": "#7C3AED"}
B2C = ["TikTok", "Instagram", "YouTube"]


def load(file=DATA) -> pd.DataFrame:
    df = pd.read_csv(file, parse_dates=["posted_at"])
    df["interactions"] = df[["likes", "comments", "shares"]].sum(axis=1)
    df["engagement_rate"] = (df["interactions"] / df["impressions"].where(df["impressions"] > 0)).fillna(0.0)
    return df


def load_plan(file=PLAN) -> pd.DataFrame:
    return pd.read_csv(file)


def _div(a, b):
    return a / b if b else float("nan")


def kpis(df: pd.DataFrame, plan: pd.DataFrame | None = None) -> dict:
    spend = df.spend_usd.sum()
    out = {"Paid spend": f"${spend / 1e6:.2f}M" if spend >= 1e6 else f"${spend / 1e3:,.0f}k"}
    if plan is not None:
        planned = plan[plan.week.isin(df.week.unique()) & plan.platform.isin(df.platform.unique())].planned_spend_usd.sum()
        out["Spend vs. plan"] = f"{_div(spend, planned) - 1:+.1%}"
    out.update({
        "Free trials": f"{df.trials.sum():,}",
        "Paying customers": f"{df.paid_conversions.sum():,}",
        "Blended CAC": f"${_div(spend, df.paid_conversions.sum()):,.0f}",
        "First-year ROAS": f"{_div(df.revenue_usd.sum(), spend):.2f}",
        "School demo requests": f"{df.demo_requests.sum():,}",
    })
    return out


def weekly_spend_vs_plan(df: pd.DataFrame, plan: pd.DataFrame):
    s = df.groupby(["week", "platform"], as_index=False).spend_usd.sum()
    fig = px.bar(s, x="week", y="spend_usd", color="platform", color_discrete_map=PALETTE,
                 title="Weekly paid spend vs. plan", labels={"spend_usd": "spend (USD)"})
    p = plan[plan.platform.isin(df.platform.unique())].groupby("week", as_index=False).planned_spend_usd.sum()
    fig.add_trace(go.Scatter(x=p.week, y=p.planned_spend_usd, mode="lines", name="plan",
                             line=dict(color="black", dash="dash")))
    return fig.update_yaxes(tickprefix="$")


def funnel_by_segment(df: pd.DataFrame):
    rows = []
    for seg, g in df.groupby("segment"):
        for stage, col in (("Clicks", "clicks"), ("Free trials", "trials"), ("Paying customers", "paid_conversions")):
            rows.append({"segment": seg, "stage": stage, "count": g[col].sum()})
    return px.funnel(pd.DataFrame(rows), x="count", y="stage", color="segment",
                     color_discrete_map=SEG_COLORS, title="Funnel by audience segment")


def channel_efficiency(df: pd.DataFrame):
    """CPA vs CAC for the B2C channels: the cheapest trials are not the cheapest customers."""
    g = df[(df.paid == 1) & df.platform.isin(B2C)].groupby("platform")[
        ["spend_usd", "trials", "paid_conversions"]].sum()
    g["Cost per trial (CPA)"] = g.spend_usd / g.trials
    g["Cost per customer (CAC)"] = g.spend_usd / g.paid_conversions
    long = g.reset_index().melt(id_vars="platform", value_vars=["Cost per trial (CPA)", "Cost per customer (CAC)"],
                                var_name="metric", value_name="usd")
    return px.bar(long, x="platform", y="usd", color="metric", barmode="group",
                  color_discrete_sequence=[GW_BLUE, "#A75523"], text_auto="$.0f",
                  title="Cheapest trials ≠ cheapest customers (paid, B2C)").update_yaxes(tickprefix="$")


def pillar_heatmap(df: pd.DataFrame):
    h = df.pivot_table(index="pillar", columns="platform", values="engagement_rate", aggfunc="mean")
    return px.imshow(h, color_continuous_scale="Blues", text_auto=".1%", aspect="auto",
                     labels=dict(color="Eng. rate"), title="Engagement rate by content pillar × platform")


def spend_response(df: pd.DataFrame):
    """Weekly spend vs. CPA per channel: rising CPA at higher spend = diminishing returns."""
    w = df[(df.paid == 1) & df.platform.isin(B2C)].groupby(["platform", "week"], as_index=False)[
        ["spend_usd", "trials"]].sum()
    w["CPA"] = w.spend_usd / w.trials
    return px.scatter(w, x="spend_usd", y="CPA", color="platform", hover_data=["week"],
                      color_discrete_map=PALETTE, trendline=None,
                      title="Spend vs. cost per trial, by week (diminishing returns?)",
                      labels={"spend_usd": "weekly spend (USD)"}).update_xaxes(tickprefix="$").update_yaxes(tickprefix="$")


def segment_week_rate(df: pd.DataFrame):
    """Trials per 1,000 clicks by segment and week: the privacy crisis shows up here."""
    w = df.groupby(["segment", "week"], as_index=False)[["clicks", "trials"]].sum()
    w["trials_per_1k_clicks"] = w.trials / w.clicks * 1000
    return px.line(w, x="week", y="trials_per_1k_clicks", color="segment", markers=True,
                   color_discrete_map=SEG_COLORS, title="Conversion rate by segment (trials per 1,000 clicks)")


def top_posts(df: pd.DataFrame, n: int = 10, by: str = "trials") -> pd.DataFrame:
    return df.nlargest(n, by)[["posted_at", "platform", "segment", "pillar", "paid", "caption",
                               "spend_usd", "trials", "paid_conversions", "demo_requests"]]
