# SAM: Vibe Coding in the Business Classroom

**S**ocial Medi**a** **M**anagement Toolkit: demo programs, Colab notebooks, exercises and templates for a
project-based course in which business students build a real social-media analytics product by guiding AI
coding assistants in plain English.

🌐 **Course site:** <https://yixin-ylu.github.io/sam-vibe-coding/>

![SAM dashboard](assets/dashboard.png)

## Run everything in Google Colab (no installation)

| # | Demo | Skills | AI API | Open |
|---|---|---|---|---|
| 1 | Prompt → tested code | prompting, pandas, pytest | none | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/01_prompt_to_code.ipynb) |
| 2 | Collect data from a real API | REST, JSON, pagination | none | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/02_collect_data.ipynb) |
| 3 | KPI dashboard | Plotly, Streamlit, deployment | none | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/03_dashboard.ipynb) |
| 4 | Weekly report + alerts | automation, scheduling | none | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/04_automation.ipynb) |
| 5 | Sentiment & crisis warning | NLP basics | none | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/05_sentiment.ipynb) |
| 6 | Captions & comment classification | LLM API, structured output | **Gemini (free)** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/06_gemini_basics.ipynb) |
| 7 | AI strategist agent | tool use, agents, auditing AI | **Claude** | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/yixin-ylu/sam-vibe-coding/blob/main/notebooks/07_claude_agent.ipynb) |

Demos 1–5 need no account and no key. Demo 6 needs a free Gemini key; Demo 7 needs a Claude key
(about $0.10–$0.40 per run). Keys go in Colab's 🔑 **Secrets** panel, never in code.

## Or run locally

```bash
git clone https://github.com/yixin-ylu/sam-vibe-coding.git
cd sam-vibe-coding
pip install -r requirements.txt          # Python 3.10+
python demos/01_prompt_to_code/engagement.py
streamlit run demos/03_dashboard/app.py
```

## What's inside

```
data/              synthetic data for a fictional campus brand (+ generator script)
demos/01..07/      the demo programs, each with a README and the prompts used to build it
notebooks/         one Colab notebook per demo
exercises/         14-week exercise sequence with acceptance criteria
course-modules/    plug-in modules for other courses + "same recipe, other domains"
templates/         prompt journal, peer-review rubric, user stories, portfolio README
.github/workflows/ GitHub Actions example that runs the weekly report in the cloud
```

## Data & responsible use
All data in `data/sample_*.csv` is **synthetic** (fictional "Foggy Bottom Coffee Co."). Demo 2 reads public
posts from organisational accounts via Bluesky's public API. Do not collect personal data, and read each
platform's developer terms of service before using its API.

## License
Code: MIT. Teaching materials: CC BY 4.0. Please adapt them for your own courses.
