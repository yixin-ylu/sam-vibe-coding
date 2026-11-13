# From business goal to user stories to prompts

## 1. Business goal
_Example: "Help the coffee shop owner decide where to spend 5 hours a week of social media effort."_

## 2. User stories
`As a <role>, I want <capability>, so that <business value>.`

| # | User story | Acceptance criteria (testable) | Priority |
|---|---|---|---|
| 1 | As the **owner**, I want to see engagement by platform, so that I can drop the weakest channel. | Dashboard shows mean engagement rate per platform; numbers match a hand check | Must |
| 2 | As the **marketing intern**, I want the best time to post, so that I schedule posts when people are online. | Heatmap of weekday × hour; top 3 slots listed | Should |
| 3 | As the **owner**, I want an alert when complaints spike, so that I can fix service issues fast. | Alert fires when weekly negative share > 30%; tested with fake data | Must |

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
