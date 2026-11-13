"""Data prep + Plotly charts shared by the Streamlit app (app.py) and the Colab notebook.

Keeping the charts here means students can view them inline in Colab or Jupyter
without running a web server.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px

DATA = Path(__file__).resolve().parents[2] / "data" / "sample_posts.csv"
GW_BLUE = "#005581"
PALETTE = ["#005581", "#A75523", "#0D9488", "#7C3AED"]  # blue, buff-brown, teal, violet
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load(file=DATA) -> pd.DataFrame:
    df = pd.read_csv(file, parse_dates=["posted_at"])
    df["interactions"] = df[["likes", "comments", "shares"]].sum(axis=1)
    df["engagement_rate"] = (df["interactions"] / df["impressions"].where(df["impressions"] > 0)).fillna(0.0)
    df["week"] = df["posted_at"].dt.to_period("W").dt.start_time
    df["hour"] = df["posted_at"].dt.hour
    df["weekday"] = df["posted_at"].dt.day_name()
    return df


def kpis(df: pd.DataFrame) -> dict:
    g = df.sort_values("posted_at").groupby("platform")["followers"].agg(["first", "last"])
    return {
        "Posts": f"{len(df):,}",
        "Impressions": f"{df.impressions.sum():,}",
        "Avg engagement rate": f"{df.engagement_rate.mean():.2%}",
        "Follower growth": f"{(g['last'].sum() / g['first'].sum() - 1) * 100:+.1f}%",
    }


def weekly_trend(df: pd.DataFrame):
    w = df.groupby(["week", "platform"], as_index=False)["engagement_rate"].mean()
    return px.line(w, x="week", y="engagement_rate", color="platform", markers=True,
                   color_discrete_sequence=PALETTE,
                   title="Weekly engagement rate by platform").update_yaxes(tickformat=".0%")


def by_post_type(df: pd.DataFrame):
    t = df.groupby("post_type", as_index=False)["engagement_rate"].mean().sort_values("engagement_rate")
    return px.bar(t, x="engagement_rate", y="post_type", orientation="h",
                  color_discrete_sequence=[GW_BLUE],
                  title="Which content format works best?").update_xaxes(tickformat=".1%")


def best_time_heatmap(df: pd.DataFrame):
    heat = df.pivot_table(index="weekday", columns="hour", values="engagement_rate",
                          aggfunc="mean").reindex(WEEKDAYS)
    return px.imshow(heat, color_continuous_scale="Blues", aspect="auto",
                     labels=dict(color="Eng. rate"),
                     title="Best time to post (avg engagement rate)")


def top_posts(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.nlargest(n, "engagement_rate")[
        ["posted_at", "platform", "post_type", "caption", "impressions", "engagement_rate"]]
