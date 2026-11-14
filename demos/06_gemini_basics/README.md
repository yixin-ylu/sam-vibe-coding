# Demo 6: AI features with Google Gemini (free tier)

Two **simple** AI features built on the Smiley case:

| Script | What it shows |
|---|---|
| `ad_copy_writer.py` | A **creative brief as a prompt template**: audience insight × platform rules × compliance rules → 3 ad variants, then a second call in which the model audits its own drafts. Discussion: why does a human still sign off? |
| `classify_comments.py` | **Structured output**: the model returns JSON matching a schema (sentiment, issue topic, needs_reply) that goes straight into pandas, then is compared with Demo 5's VADER/keyword rules |

## Setup (free, no credit card)
1. Create a key at <https://aistudio.google.com/apikey>.
2. **Colab:** 🔑 Secrets → add `GEMINI_API_KEY` → turn on *Notebook access*.
   **Laptop:** `export GEMINI_API_KEY=...` (PowerShell: `$env:GEMINI_API_KEY="..."`).
3. Open `notebooks/06_gemini_basics.ipynb`, or run:
```bash
python demos/06_gemini_basics/ad_copy_writer.py --segment Educators --platform LinkedIn
python demos/06_gemini_basics/classify_comments.py --week 7
```

The scripts use the `gemini-flash-latest` alias, so they keep working as Google releases new Flash
models. To pin a model: `export GEMINI_MODEL=<model id>`. Free-tier rate limits are low, so
`classify_comments.py` sends all *unique* comments in **one** request. Batching and deduplicating
cut both cost and rate-limit pain, which is a point worth making to students.

## Graduate discussion points
- **Compliance:** the FTC treats unsubstantiated efficacy claims ("raise your grade") as deceptive. Ad B in
  the A/B test (`data/ab_test.csv`) makes exactly such a claim. Does its higher CTR justify the risk?
- **Model self-review:** the audit catches some problems, not all. Who is accountable?
- **Data:** free-tier prompts may be used by Google to improve its products. Use synthetic or public data only.
