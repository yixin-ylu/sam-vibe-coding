"""Build the Colab notebooks in notebooks/ from the cell lists below.

    python tools/build_notebooks.py

Keeping notebooks generated from one script keeps the setup cell identical everywhere.
"""
from pathlib import Path

import nbformat as nbf

REPO = "yixin-ylu/sam-vibe-coding"
OUT = Path(__file__).resolve().parents[1] / "notebooks"


def badge(name: str) -> str:
    return (f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"(https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{name})")


SETUP = f"""# ▶ Run this cell first: it copies the course files into this Colab session
import os
if not os.path.exists("data/campaign_posts.csv"):
    if not os.path.exists("sam-vibe-coding"):
        !git clone -q https://github.com/{REPO}.git
    %cd sam-vibe-coding
!pip -q install -r requirements.txt
print("Ready ✔  working folder:", os.getcwd())"""

CASE = ("> **Case: Smiley** (fictional) is an AI-tutoring startup running *Learn Smarter*, a 12-week, "
        "$60,000 back-to-school campaign on TikTok, Instagram, YouTube and LinkedIn, aimed at **students** "
        "(users), **parents** (payers) and **educators** (B2B school licenses). All data is synthetic.")

KEY_HELP = """**API keys: never paste them into code.** In Colab, click the 🔑 **Secrets** icon in the left
sidebar, add a secret named `{name}`, and switch on *Notebook access*. Get a key here: {url}"""

NOTEBOOKS = {
    "01_prompt_to_code.ipynb": [
        ("md", "# Demo 1: from a prompt to working code\n{badge}\n\n" + CASE + "\n\nThe CMO asks *“which channel "
               "is actually paying off?”*. The student writes the **specification**, including KPI definitions, "
               "the AI writes the code, and the student **verifies** it with tests."),
        ("code", SETUP),
        ("code", "from IPython.display import Markdown\nMarkdown(open('demos/01_prompt_to_code/PROMPT.md', encoding='utf-8').read())"),
        ("md", "## Run the code the AI produced"),
        ("code", "!python demos/01_prompt_to_code/campaign_kpis.py"),
        ("md", "**Discuss:** rank the channels by CPA, then by CAC, then by pipeline per dollar. "
               "Why do the rankings disagree? Which one should drive the budget?"),
        ("md", "## Verify it: never trust code you have not tested"),
        ("code", "!python -m pytest -q demos/01_prompt_to_code"),
        ("md", "## Your turn (Exercise 1.2)\nClick **✨ Generate** in an empty code cell (Gemini in Colab, free) and ask for "
               "*CAC by audience segment for paid posts, as a bar chart*. Then verify one bar by hand."),
        ("code", "import pandas as pd\ndf = pd.read_csv('data/campaign_posts.csv')\ndf.head()"),
    ],
    "02_collect_data.ipynb": [
        ("md", "# Demo 2: collecting data from a real social-media API\n{badge}\n\n"
               "Before a campaign, marketers benchmark competitors' public channels. Bluesky's public API needs no key, "
               "so we can learn **endpoint → JSON → table → CSV** right away."),
        ("code", SETUP),
        ("code", "!python demos/02_collect_data/fetch_bluesky.py --actor bsky.app --pages 2"),
        ("md", "No internet, or the API is down? Run with `--offline` to use a saved real response instead."),
        ("code", "import glob, pandas as pd\npath = sorted(glob.glob('data/bluesky_*.csv'))[-1]\n"
                 "posts = pd.read_csv(path)\nposts['engagement'] = posts[['likes','reposts','replies','quotes']].sum(axis=1)\n"
                 "posts.sort_values('engagement', ascending=False).head(10)"),
        ("md", "## Your turn (Exercise 2.1)\nFind two **public organisation** accounts in education or EdTech on Bluesky "
               "(search on bsky.app), fetch both, and compare posting cadence and engagement per post."),
    ],
    "03_dashboard.ipynb": [
        ("md", "# Demo 3: the campaign dashboard\n{badge}\n\n" + CASE + "\n\nThe same charts as the Streamlit app, "
               "shown inline. At the end you can launch the full interactive app with a temporary public link."),
        ("code", SETUP),
        ("code", "import sys; sys.path.insert(0, 'demos/03_dashboard')\nimport charts\n"
                 "df, plan = charts.load(), charts.load_plan()\ncharts.kpis(df, plan)"),
        ("code", "charts.weekly_spend_vs_plan(df, plan).show()"),
        ("code", "charts.channel_efficiency(df).show()"),
        ("code", "charts.spend_response(df).show()"),
        ("code", "charts.funnel_by_segment(df).show()"),
        ("code", "charts.segment_week_rate(df).show()"),
        ("code", "charts.pillar_heatmap(df).show()"),
        ("md", "## Optional: run the full Streamlit app from Colab\nThis starts the app and opens a free, "
               "temporary Cloudflare tunnel. Click the printed `trycloudflare.com` link. Stop the cell to shut it down."),
        ("code", "!wget -q -nc https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared && chmod +x cloudflared\n"
                 "import subprocess, re\n"
                 "subprocess.Popen(['streamlit', 'run', 'demos/03_dashboard/app.py', '--server.port', '8501', '--server.headless', 'true'])\n"
                 "tunnel = subprocess.Popen(['./cloudflared', 'tunnel', '--url', 'http://localhost:8501'], stderr=subprocess.PIPE, text=True)\n"
                 "for line in tunnel.stderr:\n"
                 "    m = re.search(r'https://[-a-z0-9]+\\.trycloudflare\\.com', line)\n"
                 "    if m:\n"
                 "        print('👉 Open your dashboard:', m.group(0))\n"
                 "        break"),
    ],
    "04_automation.ipynb": [
        ("md", "# Demo 4: automated weekly campaign report\n{badge}\n\nBudget pacing, week-over-week CPA/CAC, "
               "and alert rules, generated every Monday without anyone opening a spreadsheet."),
        ("code", SETUP),
        ("code", "!python demos/04_automation/weekly_report.py --week 7"),
        ("md", "Week 7 is the privacy-incident week. Now week 10, after the team scaled TikTok spend:"),
        ("code", "!python demos/04_automation/weekly_report.py --week 10"),
        ("code", "from IPython.display import HTML\nHTML(open('reports/weekly_report_wk10.html', encoding='utf-8').read())"),
        ("md", "To run it **every Monday automatically**, see `demos/04_automation/README.md` "
               "(cron, Windows Task Scheduler, or GitHub Actions)."),
    ],
    "05_sentiment.ipynb": [
        ("md", "# Demo 5: comment sentiment + issue early warning\n{badge}\n\n"
               "VADER plus keyword topic rules. Can we see the week-7 privacy incident in the comments? "
               "Demo 6 repeats the job with an LLM."),
        ("code", SETUP),
        ("code", "!python demos/05_sentiment/sentiment.py"),
        ("code", "import pandas as pd, plotly.express as px\nw = pd.read_csv('reports/weekly_sentiment.csv', index_col=0)\n"
                 "px.line(w[['Students','Parents','Educators']], markers=True, title='Net sentiment by segment',\n"
                 "        labels={'value': 'net sentiment', 'index': 'week'}).show()"),
    ],
    "06_gemini_basics.ipynb": [
        ("md", "# Demo 6: AI features with Google Gemini (free tier)\n{badge}\n\n" + CASE + "\n\n"
               "Two simple uses of an LLM API: **generating** compliant ad copy for each audience, and "
               "**classifying** comments into structured data for the community team."),
        ("md", KEY_HELP.format(name="GEMINI_API_KEY", url="https://aistudio.google.com/apikey")),
        ("code", SETUP),
        ("md", "## 6a: audience-specific ad copy + compliance self-check"),
        ("code", "!python demos/06_gemini_basics/ad_copy_writer.py --segment Parents --platform Instagram"),
        ("code", "!python demos/06_gemini_basics/ad_copy_writer.py --segment Educators --platform LinkedIn"),
        ("md", "## 6b: classify comments → JSON → pandas (crisis week)"),
        ("code", "!python demos/06_gemini_basics/classify_comments.py --week 7"),
        ("md", "## Try your own prompt\nDraft a 3-sentence holding statement the brand could post in week 7. "
               "Then critique it: is every claim approved?"),
        ("code", "import sys, os; sys.path.insert(0, 'demos')\nfrom keys import require_key\nfrom google import genai\n"
                 "client = genai.Client(api_key=require_key('GEMINI_API_KEY', 'https://aistudio.google.com/apikey'))\n"
                 "prompt = ('Draft a 3-sentence public statement for Smiley, an AI-tutoring app, responding to a viral rumour '\n"
                 "          'that it trains its AI on student homework. Approved fact: Smiley does not use student work to train its AI. '\n"
                 "          'Tone: calm, transparent, no defensiveness. Offer a live Q&A with the Chief Privacy Officer.')\n"
                 "print(client.models.generate_content(model=os.environ.get('GEMINI_MODEL', 'gemini-flash-latest'), contents=prompt).text)"),
    ],
    "07_claude_agent.ipynb": [
        ("md", "# Demo 7: a campaign-strategy agent with the Claude API\n{badge}\n\n" + CASE + "\n\n"
               "Claude is given **nine tools** (Python functions over the campaign data). It decides which to call, "
               "then writes a memo to the CMO: channel economics, the privacy incident, the A/B test verdict, and a "
               "$20k budget reallocation. Every tool call is printed so you can audit it. A run costs roughly "
               "$0.15–$0.60; the exact cost is printed at the end."),
        ("md", KEY_HELP.format(name="ANTHROPIC_API_KEY", url="https://platform.claude.com")),
        ("code", SETUP),
        ("code", "!python demos/07_claude_agent/strategist_agent.py"),
        ("code", "from IPython.display import Markdown\nMarkdown(open('reports/strategy_memo.md', encoding='utf-8').read())"),
        ("md", "## Your turn (Exercise 7.1)\nVerify **three numbers** in the memo against the dashboard (Demo 3) or "
               "the KPI script (Demo 1). Did the agent treat CPA, CAC and pipeline correctly? Did it check significance "
               "before calling the A/B test?"),
        ("code", "!python demos/07_claude_agent/strategist_agent.py --goal \"Should we cut LinkedIn and move that budget to Instagram parents?\""),
    ],
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        nb = nbf.v4.new_notebook()
        nb.metadata = {"colab": {"provenance": []},
                       "kernelspec": {"name": "python3", "display_name": "Python 3"},
                       "language_info": {"name": "python"}}
        for kind, src in cells:
            src = src.replace("{badge}", badge(name))
            nb.cells.append(nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src))
        nbf.write(nb, OUT / name)
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()
