# Demo 1 — From a prompt to working code

**Goal:** show that a business student can turn a plain-English requirement into a
tested Python module, and that the *student* still owns the specification and the checks.

## The prompt we gave the AI assistant (Cursor / Claude Code)

> I have a CSV file `data/sample_posts.csv` with columns
> `post_id, platform, posted_at, post_type, category, caption, impressions, likes, comments, shares, followers`.
>
> Write a Python script `engagement.py` that:
> 1. Loads the CSV with pandas.
> 2. Adds a column `engagement_rate = (likes + comments + shares) / impressions`.
> 3. Prints a table of the **average engagement rate per platform**, sorted high to low, as percentages with 2 decimals.
> 4. Prints the **top 5 posts** by engagement rate (platform, caption, rate).
> 5. Guards against division by zero (impressions = 0 → rate = 0).
>
> Keep it under 60 lines, add docstrings, and include a `if __name__ == "__main__":` block.
> Also write 3 small `pytest` tests for the engagement-rate function, including the zero-impressions case.

## What makes this a *good* prompt (rubric: Clarity of Intent)

| Element | In the prompt |
|---|---|
| Input specified | file path and exact column names |
| Output specified | two printed tables, format of numbers |
| Business definition | the KPI formula is written out by the student |
| Constraints | length, docstrings, entry point |
| Verification | tests requested, incl. an edge case |

## A weak version of the same prompt (for comparison in class)

> "Make me a script that analyzes my social media data."

Ask students: *what would the AI have to guess?* (which file, which KPI, which formula,
what output, how to handle bad data …)

## Files

- `engagement.py` — the code the assistant produced (lightly reviewed by the instructor)
- `test_engagement.py` — the tests

```bash
python demos/01_prompt_to_code/engagement.py
pytest demos/01_prompt_to_code
```
