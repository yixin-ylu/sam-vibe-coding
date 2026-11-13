# Demo 5: comment sentiment + crisis early warning

```bash
python demos/05_sentiment/sentiment.py
```

- Scores every comment with **VADER** (`pip install vaderSentiment`) or, if that isn't installed, a transparent built-in word list.
- Tracks weekly **net sentiment** (share positive minus share negative) and flags sharp drops. The synthetic data has a "service crisis" in the week of Oct 26.
- Lists the most common complaints.

**Discussion:** a word list is cheap, fast and explainable, but misses sarcasm and context. Demo 6b
asks an LLM to do the same job. Compare them in Exercise 6.2.
