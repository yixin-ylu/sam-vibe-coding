"""Demo 3: campaign performance dashboard for Athenova's "Learn Smarter" launch (Streamlit).

Run locally:
    streamlit run demos/03_dashboard/app.py
In Colab: open notebooks/03_dashboard.ipynb (inline charts + optional public link).

Uses data/campaign_posts.csv and data/budget_plan.csv (synthetic, fictional company).
Built in about six prompts; see PROMPTS.md.
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import charts  # noqa: E402

st.set_page_config(page_title="SAM · Campaign Dashboard", page_icon="📊", layout="wide")
df = st.cache_data(charts.load)()
plan = st.cache_data(charts.load_plan)()

# ── Sidebar filters ──────────────────────────────────────
st.sidebar.title("SAM · Filters")
platforms = st.sidebar.multiselect("Platform", list(charts.PALETTE), default=list(charts.PALETTE))
segments = st.sidebar.multiselect("Audience segment", list(charts.SEG_COLORS), default=list(charts.SEG_COLORS))
media = st.sidebar.radio("Media", ["Paid + organic", "Paid only", "Organic only"])
w0, w1 = st.sidebar.slider("Campaign weeks", 1, int(df.week.max()), (1, int(df.week.max())))

mask = df.platform.isin(platforms) & df.segment.isin(segments) & df.week.between(w0, w1)
if media == "Paid only":
    mask &= df.paid == 1
elif media == "Organic only":
    mask &= df.paid == 0
f = df[mask]

st.title("📊 Athenova · Learn Smarter campaign")
st.caption("Fictional AI-tutoring startup · 12 weeks · $1.2M plan · synthetic data · built with AI-assisted 'vibe coding'")

if f.empty:
    st.warning("No posts match the current filters.")
    st.stop()

# ── KPI tiles ────────────────────────────────────────────
tiles = charts.kpis(f, plan[plan.week.between(w0, w1)])
for col, (name, value) in zip(st.columns(len(tiles)), tiles.items()):
    col.metric(name, value)

# ── Charts ───────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Budget & efficiency", "Audience & content", "Posts"])
with tab1:
    a, b = st.columns(2)
    a.plotly_chart(charts.weekly_spend_vs_plan(f, plan), use_container_width=True)
    b.plotly_chart(charts.channel_efficiency(f), use_container_width=True)
    st.plotly_chart(charts.spend_response(f), use_container_width=True)
with tab2:
    a, b = st.columns(2)
    a.plotly_chart(charts.funnel_by_segment(f), use_container_width=True)
    b.plotly_chart(charts.segment_week_rate(f), use_container_width=True)
    st.plotly_chart(charts.pillar_heatmap(f), use_container_width=True)
with tab3:
    st.dataframe(charts.top_posts(f).style.format({"spend_usd": "${:,.0f}"}),
                 use_container_width=True, hide_index=True)
    st.download_button("Download filtered data (CSV)", f.to_csv(index=False), "athenova_filtered.csv", "text/csv")
