# From business goal to user stories to prompts

## 1. Business goal
_Example: "Help Smiley's CMO decide how to allocate a $20k campaign extension across channels and audiences."_

## 2. User stories
`As a <role>, I want <capability>, so that <business value>.`

| # | User story | Acceptance criteria (testable) | Priority |
|---|---|---|---|
| 1 | As the **CMO**, I want CAC and pipeline per dollar by channel, so that I can reallocate budget to what creates customers, not just clicks. | Table of CPA, CAC, pipeline per $ for paid posts; matches a hand check on one channel | Must |
| 2 | As the **paid-media manager**, I want weekly spend vs. plan per channel, so that I catch overspend before month-end. | Pacing chart + alert when a channel is >10% over plan | Must |
| 3 | As the **head of communications**, I want an alert when privacy complaints spike, so that we respond within 24 hours. | Alert fires when parent/educator conversion or sentiment drops sharply; tested with fake data | Must |

## 3. Prompt plan (one small prompt per story)
1. Story 1 → "…"
2. Story 2 → "…"

## 4. Responsible-AI checklist
- [ ] Only public or synthetic data; no personal data stored without consent (GDPR/CCPA)
- [ ] Platform API terms of service read; rate limits respected
- [ ] API keys in Colab Secrets / `.env`, never in code or Git
- [ ] AI-generated code is marked and was reviewed by a human
- [ ] Sentiment/LLM labels spot-checked for bias (slang, non-native English, dialects)
- [ ] The AI's numbers were verified against the data before going in a report
