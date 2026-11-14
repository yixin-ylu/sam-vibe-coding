# Plug-in modules for existing courses

The full SAM course is 14 weeks, but each piece also works on its own. Below are drop-in modules
that other GWSB courses can adopt **without** turning into a programming course.
Every module runs in Google Colab with no installation and uses the same case, Smiley's $1.2M EdTech launch campaign (`data/README.md`), so instructors can mix modules freely.

| Module | Length | Fits courses like… | Notebooks | Students leave with |
|---|---|---|---|---|
| **A. Vibe-coding taster** | 1 session (75 min) | Intro programming (ISTM 3119), any MBA core | 01 | A tested KPI script built from a prompt |
| **B. Crisis & social listening lab** | 2 sessions | Marketing Analytics, Digital Marketing, Crisis Communication | 02, 05, 06 | Incident brief on the week-7 privacy rumour |
| **C. Campaign dashboard sprint** | 2 weeks | Business Analytics, Data Visualization, Information Systems | 01, 03 | A deployed dashboard + unit-economics analysis |
| **D. Automate the boring report** | 1 week | Operations, Business Process Management | 04 | A scheduled pacing report with alerts |
| **E. AI agent for strategy** | 1–2 sessions | Marketing Strategy, MBA capstone, AI electives | 07 | An audited AI-written budget memo |
| **F. Experimentation & marketing statistics** | 1 session | Marketing Research, Business Statistics | 07 + `ab_test.csv` | A/B verdict with z-tests, power analysis, compliance risk |
| **G. Build-a-startup MVP** | 3–4 weeks | Entrepreneurship, New Venture Creation | 01–07 | MVP + pricing / go-to-market slide |

## Beyond social media: the same recipe, other domains

The SAM recipe is **domain + public data/API + dashboard + automation + AI layer**. Swap the domain:

| Course area | Project idea | Data / API (free) | AI layer |
|---|---|---|---|
| Finance | Personal portfolio tracker with risk alerts | Yahoo Finance (`yfinance`), FRED | LLM summary of earnings news |
| HR / People Analytics | Job-posting skills radar | USAJobs API, public job boards | Extract skills from postings into JSON |
| Supply chain | Port and shipping delay monitor | NOAA weather, public port data | Agent drafts supplier risk memo |
| Real estate | Neighborhood price explorer | Census ACS, Zillow research data | Natural-language Q&A over the data |
| Public policy / nonprofit | Grant opportunity finder | Grants.gov API | Classify fit with the org's mission |
| Accounting | Expense anomaly detector | Synthetic ledger (generated) | Explain flagged anomalies in plain English |

## Suggested sequencing for a department

1. **Semester 1:** Module A in ISTM 3119, Module B in one marketing section (pilot).
2. **Semester 2:** Full SAM course as an elective (undergraduate) + Module E in the MBA strategy capstone.
3. **Semester 3:** Graduate track. Faculty from other departments adapt the "beyond social media" recipes.
