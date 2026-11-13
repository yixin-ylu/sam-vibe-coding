# Demo 7: an AI strategist agent (Claude API, tool use)

The step up from Demo 6: instead of one prompt and one answer, Claude gets **six tools**
(ordinary Python functions over the SAM data) and decides on its own which to call, in what order,
until it can write an evidence-based strategy memo with a two-week content calendar.

```
goal ─► Claude ─► calls platform_summary()        ─► reads JSON
                ─► calls performance_by("hour")    ─► reads JSON
                ─► calls comment_sentiment_by_week ─► spots the Oct 26 crisis
                ─► calls sample_comments("2026-10-26")
                ─► writes memo (reports/strategy_memo.md)
```

Every tool call is printed. **The teaching point is auditing:** students verify the agent's numbers (Exercise 7.1)
and extend it with their own tool (Exercise 7.2).

## Setup
1. Create a key at <https://platform.claude.com> (add a small prepaid credit, e.g. $5; a class
   section's worth of runs typically costs a few dollars).
2. **Colab:** 🔑 Secrets → add `ANTHROPIC_API_KEY` → turn on *Notebook access*.
3. Run `notebooks/07_claude_agent.ipynb`, or:
```bash
python demos/07_claude_agent/strategist_agent.py
python demos/07_claude_agent/strategist_agent.py --goal "Is LinkedIn worth our time?"
```

## Cost control
- Default model: `claude-opus-5-5` with `effort: "medium"`. One run is about $0.10–$0.40, and the script prints the exact token cost.
- For large classes, set `CLAUDE_MODEL=claude-haiku-5-5` (much cheaper) or `claude-sonnet-5-5`.
  Comparing memo quality across models is a good extra exercise.
- The run is capped at 15 model turns (`max_iterations`).
- If the model declines a request, the API retries it on a fallback model (`fallbacks="default"`).

## How it works (≈ 40 lines that matter)
- `@beta_tool` turns a Python function + docstring into a tool definition (the docstring *is* the tool description the model reads).
- `client.beta.messages.tool_runner(...)` runs the loop: call model → run requested tools → send results back → repeat.
- The system prompt sets the role, demands evidence ("quote the numbers"), and fixes the memo structure.
