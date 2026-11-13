"""Demo 3: SAM social-media KPI dashboard (Streamlit).

Run locally:
    streamlit run demos/03_dashboard/app.py
In Colab: open notebooks/03_dashboard.ipynb (inline charts + optional public link).

Uses data/sample_posts.csv by default. Upload your own CSV with the same columns
in the sidebar. Built in roughly five prompts; see PROMPTS.md.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402

st.set_page_config(page_title="SAM Dashboard", page_icon="📊", layout="wide")
load = st.cache_data(charts.load)

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.title("SAM · Filters")
upload = st.sidebar.file_uploader("Upload a posts CSV (optional)", type="csv")
df = load(upload or charts.DATA)

platforms = st.sidebar.multiselect("Platform", sorted(df.platform.unique()),
                                   default=sorted(df.platform.unique()))
types = st.sidebar.multiselect("Post type", sorted(df.post_type.unique()),
                               default=sorted(df.post_type.unique()))
d0, d1 = df.posted_at.min().date(), df.posted_at.max().date()
dates = st.sidebar.date_input("Date range", (d0, d1), min_value=d0, max_value=d1)

mask = df.platform.isin(platforms) & df.post_type.isin(types)
if isinstance(dates, tuple) and len(dates) == 2:
    mask &= df.posted_at.dt.date.between(*dates)
f = df[mask]

st.title("📊 Social Media Management Toolkit")
st.caption("Foggy Bottom Coffee Co. · synthetic demo data · built with AI-assisted 'vibe coding'")

if f.empty:
    st.warning("No posts match the current filters.")
    st.stop()

# ── KPI tiles ────────────────────────────────────────────
for col, (name, value) in zip(st.columns(4), charts.kpis(f).items()):
    col.metric(name, value)

# ── Charts ───────────────────────────────────────────────
left, right = st.columns(2)
left.plotly_chart(charts.weekly_trend(f), use_container_width=True)
right.plotly_chart(charts.by_post_type(f), use_container_width=True)
st.plotly_chart(charts.best_time_heatmap(f), use_container_width=True)

st.subheader("Top posts")
st.dataframe(charts.top_posts(f).style.format({"engagement_rate": "{:.2%}", "impressions": "{:,}"}),
             use_container_width=True, hide_index=True)

st.download_button("Download filtered data (CSV)", f.to_csv(index=False),
                   "sam_filtered.csv", "text/csv")
