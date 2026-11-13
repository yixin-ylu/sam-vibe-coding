# Demo 6: LLM APIs with Google Gemini (free tier)

Two **simple** AI features any business student can build in a class session:

| Script | What it shows |
|---|---|
| `caption_writer.py` | Your first LLM call: a prompt template with platform rules → 3 captions |
| `classify_comments.py` | **Structured output**: the model returns JSON matching a schema (sentiment + topic) that goes straight into pandas, then is compared with Demo 5's word list |

## Setup (free, no credit card)
1. Create a key at <https://aistudio.google.com/apikey>.
2. **Colab:** 🔑 Secrets → add `GEMINI_API_KEY` → turn on *Notebook access*.
   **Laptop:** `export GEMINI_API_KEY=...` (PowerShell: `$env:GEMINI_API_KEY="..."`).
3. Open `notebooks/06_gemini_basics.ipynb` or run:
```bash
python demos/06_gemini_basics/caption_writer.py --platform TikTok --product "pumpkin cold brew"
python demos/06_gemini_basics/classify_comments.py --limit 30
```

The scripts use the `gemini-flash-latest` alias, so they keep working as Google releases new
Flash models. To pin a specific model: `export GEMINI_MODEL=<model id>`.
Free-tier rate limits apply (a few requests per minute), so `classify_comments.py` sends all
comments in **one** request on purpose. Point that out to students: batching cuts both cost and rate-limit pain.

> Free-tier prompts may be used by Google to improve its products. Use synthetic or public data only.
