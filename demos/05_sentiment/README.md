# Demo 5: comment sentiment + issue early warning

```bash
python demos/05_sentiment/sentiment.py
```

- Scores all 1,496 campaign comments with **VADER** (or, if VADER isn't installed, a transparent word list).
- Tracks weekly **net sentiment** (share positive minus share negative), overall and by segment, and flags sharp drops.
- Tags issue topics with **keyword rules** (privacy, pricing, cheating, bugs, efficacy).
- Week 7: parent and educator sentiment turns negative, and "privacy" dominates the complaints. That is the viral
  rumour that Smiley trains its AI on student homework.

**Discussion:** rules and lexicons are cheap, fast and explainable, but they miss context. VADER, for instance,
scores *"Deleting the app until you explain what you do with student data"* as neutral. Demo 6b gives the same job
to an LLM. Compare them in Exercise 6.2.
