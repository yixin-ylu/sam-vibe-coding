# SAM exercises (14 weeks): the Smiley case

All exercises use the **Smiley "Learn Smarter" campaign** (see [`data/README.md`](../data/README.md)).
Each one has **a prompt starter**, **acceptance criteria** (how you know you're done), and a
**verify and reflect** step for your Prompt Engineering Journal (`templates/prompt_journal.md`).
Everything runs in Google Colab. Open the matching notebook in `notebooks/` first.

> **House rule:** use any AI assistant you like (Gemini in Colab, Cursor, Claude Code…), but you must be able to
> explain every line you submit and every number you report. Blind copy-paste loses points.
>
> **Grad track** items are marked 🎓. Undergraduate sections may skip or simplify them.

---

## Weeks 1–2 · Orientation: from business question to tested code

**Exercise 1.1: Weak vs. strong prompt**
Ask an assistant: *"Analyze my campaign data and tell me which channel is best."* Then use the prompt in
`demos/01_prompt_to_code/PROMPT.md`. Compare the outputs.
- ✅ Journal entry: list 4 different definitions of "best" and which channel wins under each.

**Exercise 1.2: CAC by audience**
> *Prompt starter:* "Using `data/campaign_posts.csv`, paid posts only, compute CAC = spend / paid_conversions by
> `segment` and plot it as a bar chart with plotly. Return NaN where there are no conversions."
- ✅ Chart renders. ✅ You verified one bar by hand in Sheets/Excel. ✅ Two sentences: why is Parents' CAC so much lower than Students'?

**Exercise 1.3: 🎓 LTV:CAC**
Revenue in the data is *first-year only*. Assume monthly churn of 6% after year one. Prompt the AI to compute a
3-year LTV per subscriber and the LTV:CAC ratio by channel.
- ✅ State every assumption in a markdown cell. ✅ Which channel clears the common 3:1 benchmark?

---

## Weeks 3–4 · API basics

**Exercise 2.1: Competitor benchmark** (`notebooks/02_collect_data.ipynb`)
Find two public **education or EdTech organisation** accounts on Bluesky and compare posting cadence and engagement per post.
- ✅ Table for both accounts. ✅ One recommendation for Smiley's organic strategy.

**Exercise 2.2: Read the docs, not just the AI**
Find `getAuthorFeed` in the Bluesky API docs. Which parameter limits page size, and what is its maximum?
- ✅ Answer with a link. Did the AI's first answer match the docs?

**Exercise 2.3: OAuth and data governance**
Diagram the OAuth 2.0 flow for the LinkedIn Marketing API. Where does the token live? Who in the company should own it?
- ✅ Diagram + a 5-line data-governance note (token storage, rotation, least privilege).

---

## Weeks 5–6 · Data collection & storage

**Exercise 3.1: Data-quality gate**
> *Prompt starter:* "Write `validate_posts(df)` that checks: unique `post_id`; no negative metrics;
> `clicks ≤ impressions`; `trials ≤ clicks`; `paid_conversions ≤ trials`; `spend_usd == 0` for organic posts.
> Return a table of violations."
- ✅ Inject 4 bad rows into a copy of the data. Your function catches all 4.

**Exercise 3.2: Joining sources**
Join `campaign_posts.csv` with `budget_plan.csv` to compute weekly pacing by platform.
- ✅ Your weekly totals match the dashboard's spend-vs-plan chart.

**Exercise 3.3: 🎓 Attribution assumptions**
The data credits each trial to the post that was clicked last. List three ways this could overstate or understate a channel (e.g. YouTube view-through, cross-device journeys).
- ✅ One paragraph. ✅ A proposal for a geo-holdout or conversion-lift test.

---

## Weeks 7–8 · Visualization

**Exercise 4.1: One chart, one decision**
Add a chart to `demos/03_dashboard/charts.py` that answers a question the CMO would ask, for example
*"Which content pillar should we fund for parents?"*
- ✅ The chart title is the question. ✅ A two-sentence answer under the chart.

**Exercise 4.2: Chart critique**
Ask an AI to critique the dashboard. Accept two suggestions and reject one, with reasons. Hint: is the funnel chart misleading in any way?
- ✅ Journal entry with all three decisions.

**Exercise 4.3: Deploy**
Run the app through the Colab tunnel cell, then deploy it to Streamlit Community Cloud.
- ✅ A public URL in your README.

---

## Weeks 9–10 · Automation & AI features

**Exercise 5.1: A new alert rule**
Add a rule to `weekly_report.py`: *"alert when a channel's CPM rises more than 20% while its spend is above plan"* (a saturation signal).
- ✅ The rule fires for TikTok in week 9 or 10. ✅ A unit test with fake data.

**Exercise 6.1: Copy test** (Gemini, free)
Generate copy for all 3 audiences × 2 platforms with `ad_copy_writer.py`. Score each ad yourself (1–5) on
fit with the audience, platform rules, and compliance.
- ✅ Score table. ✅ Did the model's self-check miss a violation you caught?

**Exercise 6.2: LLM vs. rules** (`classify_comments.py --week 7`)
For every comment where the LLM and VADER/keyword rules disagree, decide who was right.
- ✅ Accuracy of each method on those comments. ✅ At what volume would you pay for the LLM?

**Exercise 6.3: 🎓 Crisis response plan**
Using Demo 5/6 output, write a one-page incident brief for week 7: timeline, affected segments, conversion impact
(in $), the response that worked, and a playbook for next time.
- ✅ Every number traceable to code. ✅ A draft public statement that uses only approved claims.

---

## Weeks 11–12 · Iteration, testing, agents

**Exercise 7.1: Audit the agent** (Claude, `strategist_agent.py`)
Run the agent with the default goal. Verify **three numbers** in its memo against Demo 1 or Demo 3.
- ✅ All three checked. ✅ Did it separate CPA, CAC and pipeline? Did it test significance before calling the A/B test?

**Exercise 7.2: Give the agent a new tool**
Add a `@beta_tool`, e.g. `ltv_cac(churn: float)` or `budget_simulator(platform, extra_spend)`. Re-run and check that the memo uses it.
- ✅ The tool appears in the printed tool calls. ✅ The memo cites its output.

**Exercise 7.3: 🎓 A/B test, properly**
Re-do the analysis in `ab_test.csv` yourself: a two-proportion z-test on CTR, trials per click, and trials per impression; a 95% CI for each; and the sample size you would need to detect a 5% lift in trials per impression.
- ✅ Matches the agent's p-values. ✅ A recommendation that weighs the statistics against the compliance risk of hook B.

**Exercise 7.4: Peer code review**
Review a teammate's module with `templates/peer_review_rubric.md`.
- ✅ At least one bug or edge case, filed as a GitHub issue.

---

## Weeks 13–14 · Demo Day & portfolio

**Exercise 8.1: Board presentation (7 minutes)**
Recommend how to allocate the $400k extension. Show the live dashboard, one thing the AI got wrong and how you caught it, and the measurement plan.

**Exercise 8.2: Portfolio README**
Use `templates/portfolio_readme.md`: screenshot, live link, tech stack, *your* role versus the AI's role.

**Exercise 8.3: Responsible-AI checklist**
Complete the checklist in `templates/user_story_template.md` for your final product, including the student-data
privacy questions (FERPA/COPPA) that the Smiley case raises.
