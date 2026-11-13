# Demo 7: a campaign-strategy agent (Claude API, tool use)

The step up from Demo 6: instead of one prompt and one answer, Claude gets **nine tools**
(ordinary Python functions over the Athenova data) and decides on its own which to call, in what order,
until it can write a memo to the CMO.

```
"How should we spend the $400k extension?"
   └─► Claude ─► campaign_overview()            ─► facts & assumptions
              ─► channel_economics()            ─► CPA vs CAC vs pipeline
              ─► spend_response("TikTok")       ─► diminishing returns after week 9
              ─► weekly_trend("trials_per_1k_clicks", segment="Parents") ─► week-7 drop
              ─► comment_topics_by_week() / sample_comments(7) ─► privacy rumour
              ─► ab_test_results()              ─► z-tests: B wins CTR, A wins trials/click
              ─► memo + budget table  (reports/strategy_memo.md)
```

Every tool call is printed. **The teaching point is auditing:** students verify the agent's numbers (Exercise 7.1),
extend it with their own tool (7.2), and redo the A/B analysis by hand (7.3).

## Setup
1. Create a key at <https://platform.claude.com> and add a small prepaid credit (e.g. $5).
2. **Colab:** 🔑 Secrets → add `ANTHROPIC_API_KEY` → turn on *Notebook access*.
3. Run `notebooks/07_claude_agent.ipynb`, or:
```bash
python demos/07_claude_agent/strategist_agent.py
python demos/07_claude_agent/strategist_agent.py --goal "Should we cut LinkedIn?"
```

## Cost control
- Default model: `claude-opus-5-5` with `effort: "medium"`. A run is about $0.15–$0.60; the script prints the exact token cost.
- For large classes set `CLAUDE_MODEL=claude-haiku-5-5` (much cheaper) or `claude-sonnet-5-5`. Comparing memo quality across models makes a good extra exercise.
- Capped at 20 model turns (`max_iterations`). If the model declines a request, the API retries it on a fallback model (`fallbacks="default"`).

## How it works
- `@beta_tool` turns a Python function + docstring into a tool definition. The docstring **is** the tool description the model reads.
- `client.beta.messages.tool_runner(...)` runs the loop: call the model → run the requested tools → send results back → repeat.
- The system prompt sets the role, demands evidence and significance testing, and fixes the memo structure.
