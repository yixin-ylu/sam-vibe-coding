# Demo 3: building the campaign dashboard in 6 prompts

The prompts below are the sequence used to build `app.py` + `charts.py`. Each prompt is **one small,
testable step**, which is the habit the course grades under *AI Workflow Design* (A2).

| # | Prompt (abridged) | What the student checks before the next prompt |
|---|---|---|
| 1 | "Create a Streamlit app that loads `data/campaign_posts.csv` and `data/budget_plan.csv` and shows KPI tiles: paid spend (and % vs plan), free trials, paying customers, blended CAC, first-year ROAS, school demo requests." | Do spend and CAC match the Demo 1 script? |
| 2 | "Add sidebar filters: platform, audience segment, paid/organic, and a week-range slider. Every tile and chart must respect them." | Filter to TikTok + paid. Does spend match a pandas one-liner? |
| 3 | "Add a stacked bar of weekly spend by platform with the plan as a dashed line, and a grouped bar comparing CPA and CAC for TikTok, Instagram and YouTube." | Which weeks overspend? Why is TikTok's CPA bar short but its CAC bar tall? |
| 4 | "Add a funnel (clicks → trials → paying customers) by segment, and a line chart of trials per 1,000 clicks by segment and week." | Do you see week 7? What happened? (→ Demo 5) |
| 5 | "Add a heatmap of engagement rate by content pillar × platform, and a scatter of weekly spend vs. CPA per platform." | Is there evidence of diminishing returns on TikTok? |
| 6 | "Put the charts in tabs, add a top-10 posts table by trials and a CSV download button." | Is anything misleading? (Exercise 4.2: chart critique) |

## Run it

```bash
pip install -r requirements.txt
streamlit run demos/03_dashboard/app.py
```

## Deploy it

Push to GitHub, then go to <https://share.streamlit.io>, pick the repo, and set the main file to `demos/03_dashboard/app.py`.
