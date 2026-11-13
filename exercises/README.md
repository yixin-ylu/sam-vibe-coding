# SAM exercises (14 weeks)

Each exercise has **a prompt starter**, **acceptance criteria** (how you know you're done), and a
**verify and reflect** step that goes into your Prompt Engineering Journal (`templates/prompt_journal.md`).
Everything runs in Google Colab. Open the matching notebook in `notebooks/` first.

> **House rule:** you may use any AI assistant (Gemini in Colab, Cursor, Claude Code…), but you must be able to
> explain every line you submit. Blind copy-paste loses points.

---

## Weeks 1–2 · Orientation: prompting your first program

**Exercise 1.1: Good prompt vs. weak prompt**
Ask an AI assistant for "a script that analyzes my social media data" (weak), then use the prompt in
`demos/01_prompt_to_code/PROMPT.md` (strong). Compare the two outputs.
- ✅ Journal entry lists 3 things the AI had to *guess* in the weak version.

**Exercise 1.2: Your own KPI**
> *Prompt starter:* "Using `data/sample_posts.csv`, compute the average engagement rate by `post_type`
> for TikTok only and draw a bar chart with plotly. Engagement rate = (likes+comments+shares)/impressions."
- ✅ The chart renders. ✅ You checked **one** bar by hand in Sheets/Excel and it matches.

**Exercise 1.3: Git basics**
Fork the course repo, commit your notebook, open a pull request to your own fork.
- ✅ A PR with a meaningful commit message.

---

## Weeks 3–4 · API basics

**Exercise 2.1: Compare two brands** (`notebooks/02_collect_data.ipynb`)
Fetch two public organisation accounts on Bluesky and compare average engagement per post.
- ✅ A table with both accounts. ✅ One sentence of business interpretation.

**Exercise 2.2: Read the docs, not just the AI**
Find the `getAuthorFeed` endpoint in the Bluesky API docs. Which parameter limits page size, and what is the maximum?
- ✅ Answer with a link to the docs page. Did the AI's first answer match the docs?

**Exercise 2.3: OAuth walkthrough (paper exercise)**
Draw the OAuth 2.0 authorization-code flow for the Instagram Graph API: user, app, Meta, token.
- ✅ Diagram plus a note on where the token is stored safely (`.env` / Colab Secrets, never in Git).

---

## Weeks 5–6 · Data collection & storage

**Exercise 3.1: Clean the data**
> *Prompt starter:* "Write a function `clean_posts(df)` that removes duplicate `post_id`s, drops rows with
> negative metrics, parses `posted_at` as datetime, and returns a report of how many rows were removed and why."
- ✅ Add 3 deliberately bad rows to a copy of the CSV. Your function catches all 3.

**Exercise 3.2: Append-only history**
Make the Bluesky fetcher **append** new posts to the CSV without duplicating old ones.
- ✅ Run it twice in a row. Row count does not double.

**Exercise 3.3: Robust upload**
Upload a CSV with a missing column to the dashboard. Prompt the AI to make the app show a friendly error instead of crashing.
- ✅ A screenshot of the friendly error.

---

## Weeks 7–8 · Visualization

**Exercise 4.1: One new chart, one business question**
Add a chart to `demos/03_dashboard/charts.py` that answers a question a manager would ask
(e.g. *"Do promo posts actually perform better than story posts?"*).
- ✅ The chart title is the question. ✅ A 2-sentence answer under the chart.

**Exercise 4.2: Chart critique**
Ask an AI to critique your dashboard against data-visualization best practice. Accept 2 suggestions and reject 1, with reasons.
- ✅ Journal entry with all three decisions.

**Exercise 4.3: Deploy**
Run the Streamlit app with the Colab tunnel cell, then deploy it to Streamlit Community Cloud.
- ✅ A public URL in your README.

---

## Weeks 9–10 · Automation & AI features

**Exercise 5.1: Your own alert rule**
Add a rule to `weekly_report.py`, e.g. *"alert if a platform posted fewer than 2 times this week"*.
- ✅ A unit test that triggers your alert with fake data.

**Exercise 6.1: Caption A/B test** (Gemini, free)
Generate captions for the same product on all four platforms. Score them yourself with a 1–5 rubric
(on-brand, follows platform rules, no invented facts).
- ✅ A table of scores. ✅ One prompt change that improved the lowest score.

**Exercise 6.2: LLM vs. word list** (`classify_comments.py`)
For every comment where the LLM and the word list disagree, decide who was right.
- ✅ Accuracy of each method on those comments. ✅ When would you pay for the LLM?

**Exercise 6.3: Topic dashboard**
Add a "complaints by topic" chart to the dashboard using the LLM labels.
- ✅ The chart shows which topic got worse in the crisis week.

---

## Weeks 11–12 · Iteration, testing, peer review

**Exercise 7.1: Audit the agent** (Claude, `strategist_agent.py`)
Run the strategist agent with your own business question. Pick **two numbers** from its memo and verify them against the dashboard.
- ✅ Both checked. If either was wrong, explain why the agent got it wrong.

**Exercise 7.2: Give the agent a new tool**
Add a `@beta_tool` function, e.g. `competitor_benchmark()` or `cost_per_post()`. Re-run and see whether the agent uses it.
- ✅ The tool appears in the printed tool calls. ✅ The memo cites its output.

**Exercise 7.3: Peer code review**
Review a teammate's module with `templates/peer_review_rubric.md`.
- ✅ At least one bug or edge case found, filed as a GitHub issue.

---

## Weeks 13–14 · Demo Day & portfolio

**Exercise 8.1: 5-minute demo**
Problem, who it's for, live demo, one thing the AI got wrong and how you caught it.

**Exercise 8.2: Portfolio README**
Use `templates/portfolio_readme.md`: screenshot, live link, tech stack, *your* role versus the AI's role.

**Exercise 8.3: Ethics checklist**
Complete the Responsible-AI checklist in `templates/user_story_template.md` for your final product.
