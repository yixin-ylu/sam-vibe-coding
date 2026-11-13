# Demo 3: building the dashboard in 5 prompts

The prompts below are the actual sequence used to build `app.py`, in order. Each prompt is
**one small, testable step**, which is the habit the course grades under *AI Workflow Design* (A2).

| # | Prompt (abridged) | What the student checks before the next prompt |
|---|---|---|
| 1 | "Create a Streamlit app that loads `data/sample_posts.csv`, computes `engagement_rate = (likes+comments+shares)/impressions`, and shows four KPI tiles: posts, impressions, average engagement rate, follower growth." | Do the KPI numbers match a hand calculation in Excel for 3 rows? |
| 2 | "Add sidebar filters for platform, post type and date range. All tiles and charts must respect the filters. Show a warning if nothing matches." | Filter to one platform. Does the post count match `df[df.platform=="X"]`? |
| 3 | "Add a Plotly line chart of weekly average engagement rate per platform, and a horizontal bar chart of engagement by post type. Use #005581 as the primary color." | Are the y-axes in % format? Is the week grouping correct? |
| 4 | "Add a weekday × hour heatmap of average engagement rate so a marketing manager can see the best time to post." | Does the heatmap agree with the pattern in the data (lunch and evening peaks)? |
| 5 | "Add a top-10 posts table and a button to download the filtered data. Let the user upload their own CSV with the same columns." | Upload a CSV with a missing column. What happens? (→ Exercise 3.3) |

## Run it

```bash
pip install -r requirements.txt
streamlit run demos/03_dashboard/app.py
```

## Deploy it (week 13)

Push the repo to GitHub, then go to <https://share.streamlit.io>, pick the repo and set the main file
to `demos/03_dashboard/app.py`. The free tier gives you a public URL to put on a résumé.
