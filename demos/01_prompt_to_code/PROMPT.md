# Demo 1: from a prompt to working code

**Case:** Smiley, a fictional AI-tutoring startup, is halfway through a $60,000 back-to-school campaign.
The CMO asks: *"Which channel is actually paying off?"* A graduate student turns that question into a
precise specification. The AI writes the code. The student checks it.

## The prompt we gave the AI assistant (Cursor / Claude Code / Gemini in Colab)

> I have `data/campaign_posts.csv`, one row per social post, with columns including
> `platform, segment, paid, spend_usd, impressions, clicks, trials, paid_conversions, demo_requests, revenue_usd, pipeline_usd`.
>
> Write a Python module `campaign_kpis.py` that:
> 1. Loads the CSV with pandas and keeps **paid** posts only (`paid == 1`).
> 2. Aggregates by `platform` and computes:
>    - CPM = spend / impressions × 1000
>    - CTR = clicks / impressions
>    - CPA = spend / trials (cost per free trial)
>    - CAC = spend / paid_conversions (cost per paying customer)
>    - ROAS = revenue_usd / spend (first-year revenue)
>    - Cost per demo request = spend / demo_requests (B2B, LinkedIn)
> 3. Prints a table sorted by CAC, with money to 2 decimals and CTR as a %.
> 4. Uses a helper `safe_div(a, b)` that returns `NaN` (not an error, not 0) when `b` is 0.
>
> Keep it under 70 lines, with docstrings and an `if __name__ == "__main__":` block.
> Also write `pytest` tests for `safe_div` (including b = 0) and one test that checks CAC on a 2-row DataFrame I can verify by hand.

## Why this prompt works (rubric: Clarity of Intent)

| Element | In the prompt |
|---|---|
| Input specified | file path and exact columns |
| **Business definitions** | the student defines every KPI. *CPA ≠ CAC* is a business decision, not a coding one |
| Scope decision | paid posts only (organic posts have zero spend) |
| Edge cases | division by zero returns `NaN` on purpose, because `0` would make a channel look free |
| Verification | tests requested, including a case small enough to check by hand |

## The weak version (for class discussion)

> "Analyze my campaign data and tell me which channel is best."

What would the AI have to guess? *Best by what?* Engagement, cheapest trials, cheapest customers, or B2B pipeline?
In this dataset those four answers **pick different channels**. That is the lesson.

## Files

- `campaign_kpis.py`: the code the assistant produced (reviewed by the instructor)
- `test_campaign_kpis.py`: the tests

```bash
python demos/01_prompt_to_code/campaign_kpis.py
pytest demos/01_prompt_to_code
```
