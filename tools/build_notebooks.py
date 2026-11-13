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
if not os.path.exists("data/sample_posts.csv"):
    if not os.path.exists("sam-vibe-coding"):
        !git clone -q https://github.com/{REPO}.git
    %cd sam-vibe-coding
!pip -q install -r requirements.txt
print("Ready ✔  working folder:", os.getcwd())"""

KEY_HELP = """**API keys: never paste them into code.** In Colab, click the 🔑 **Secrets** icon in the left
sidebar, add a secret named `{name}`, and switch on *Notebook access*. Get a key here: {url}"""

NOTEBOOKS = {
    "01_prompt_to_code.ipynb": [
        ("md", "# Demo 1: from a prompt to working code\n{badge}\n\nA business student writes the "
               "*specification* in plain English, an AI assistant writes the code, and the student "
               "*verifies* it with tests. Below is the exact prompt we used."),
        ("code", SETUP),
        ("code", "from IPython.display import Markdown\nMarkdown(open('demos/01_prompt_to_code/PROMPT.md', encoding='utf-8').read())"),
        ("md", "## Run the code the AI produced"),
        ("code", "!python demos/01_prompt_to_code/engagement.py"),
        ("md", "## Verify it: never trust code you have not tested"),
        ("code", "!python -m pytest -q demos/01_prompt_to_code"),
        ("md", "## Your turn (Exercise 1.2)\nIn Colab, click **✨ Generate** in an empty code cell "
               "(Gemini in Colab, free) and paste a prompt asking for: *the average engagement rate by "
               "`post_type` for TikTok only, as a bar chart*. Then check one number by hand."),
        ("code", "import pandas as pd\ndf = pd.read_csv('data/sample_posts.csv')\ndf.head()"),
    ],
    "02_collect_data.ipynb": [
        ("md", "# Demo 2: collecting data from a real social-media API\n{badge}\n\n"
               "Bluesky's public API needs no key, so we can learn **endpoint → JSON → table → CSV** right away."),
        ("code", SETUP),
        ("code", "!python demos/02_collect_data/fetch_bluesky.py --actor bsky.app --pages 2"),
        ("md", "No internet or the API is down? Run `--offline` to use a saved real response instead."),
        ("code", "import glob, pandas as pd\npath = sorted(glob.glob('data/bluesky_*.csv'))[-1]\n"
                 "posts = pd.read_csv(path)\nposts['engagement'] = posts[['likes','reposts','replies','quotes']].sum(axis=1)\n"
                 "posts.sort_values('engagement', ascending=False).head(10)"),
        ("md", "## Your turn (Exercise 2.1)\nChange `--actor` to another **public organisation** account "
               "(e.g. `nasa.gov`, `nytimes.com`) and compare their average engagement per post."),
    ],
    "03_dashboard.ipynb": [
        ("md", "# Demo 3: the SAM dashboard\n{badge}\n\nThe same charts as the Streamlit app, "
               "shown inline. At the end you can launch the full interactive app with a temporary public link."),
        ("code", SETUP),
        ("code", "import sys; sys.path.insert(0, 'demos/03_dashboard')\nimport charts\n"
                 "df = charts.load()\ncharts.kpis(df)"),
        ("code", "charts.weekly_trend(df).show()"),
        ("code", "charts.by_post_type(df).show()"),
        ("code", "charts.best_time_heatmap(df).show()"),
        ("code", "charts.top_posts(df)"),
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
        ("md", "# Demo 4: automated weekly report + alerts\n{badge}"),
        ("code", SETUP),
        ("code", "!python demos/04_automation/weekly_report.py"),
        ("md", "The week of Oct 26 had a (simulated) service problem. Report on that week:"),
        ("code", "!python demos/04_automation/weekly_report.py --week 2026-10-26"),
        ("code", "import glob\nfrom IPython.display import HTML\nHTML(open(sorted(glob.glob('reports/weekly_report_*.html'))[-1], encoding='utf-8').read())"),
        ("md", "To run it **every Monday automatically**, see `demos/04_automation/README.md` "
               "(cron, Windows Task Scheduler, or GitHub Actions)."),
    ],
    "05_sentiment.ipynb": [
        ("md", "# Demo 5: comment sentiment + crisis early warning\n{badge}\n\n"
               "A transparent word-list (or VADER) scorer. Demo 6 compares it with an LLM."),
        ("code", SETUP),
        ("code", "!python demos/05_sentiment/sentiment.py"),
        ("code", "import pandas as pd, plotly.express as px\nw = pd.read_csv('reports/weekly_sentiment.csv')\n"
                 "px.bar(w, x='week', y='net_sentiment', color_discrete_sequence=['#005581'], title='Weekly net sentiment').show()"),
    ],
    "06_gemini_basics.ipynb": [
        ("md", "# Demo 6: LLM APIs with Google Gemini (free tier)\n{badge}\n\n"
               "Two simple uses of an LLM API: **generating** marketing copy and **classifying** customer comments into structured data."),
        ("md", KEY_HELP.format(name="GEMINI_API_KEY", url="https://aistudio.google.com/apikey")),
        ("code", SETUP),
        ("md", "## 6a: platform-specific captions"),
        ("code", "!python demos/06_gemini_basics/caption_writer.py --platform Instagram\n"
                 "!python demos/06_gemini_basics/caption_writer.py --platform LinkedIn"),
        ("md", "## 6b: classify comments → JSON → pandas"),
        ("code", "!python demos/06_gemini_basics/classify_comments.py --limit 30"),
        ("md", "## Try your own prompt\nEdit the prompt and re-run. What happens if you remove the platform rules?"),
        ("code", "import sys, os; sys.path.insert(0, 'demos')\nfrom keys import require_key\nfrom google import genai\n"
                 "client = genai.Client(api_key=require_key('GEMINI_API_KEY', 'https://aistudio.google.com/apikey'))\n"
                 "prompt = 'Suggest 5 post ideas for a campus coffee shop during finals week, one line each.'\n"
                 "print(client.models.generate_content(model=os.environ.get('GEMINI_MODEL', 'gemini-flash-latest'), contents=prompt).text)"),
    ],
    "07_claude_agent.ipynb": [
        ("md", "# Demo 7: an AI strategist agent with the Claude API\n{badge}\n\n"
               "Claude is given **tools** (Python functions over our data), decides which to call, "
               "and writes an evidence-based strategy memo. Every tool call is printed so you can audit it. "
               "A run costs roughly $0.10–$0.40; the exact cost is printed at the end."),
        ("md", KEY_HELP.format(name="ANTHROPIC_API_KEY", url="https://platform.claude.com")),
        ("code", SETUP),
        ("code", "!python demos/07_claude_agent/strategist_agent.py"),
        ("code", "from IPython.display import Markdown\nMarkdown(open('reports/strategy_memo.md', encoding='utf-8').read())"),
        ("md", "## Your turn (Exercise 7.1)\nAsk a different business question, then **check two of the agent's "
               "numbers** against the dashboard. Did it make anything up?"),
        ("code", "!python demos/07_claude_agent/strategist_agent.py --goal \"Should we stop posting on X and move that effort to TikTok?\""),
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
