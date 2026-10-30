# QueueSwap Match: KPI definitions

The goal of the product is that a person who must leave soon gets a **successful, fair swap**. The main measure follows the journey in `tracking-plan.md`. I do not set targets here. A target needs a first measurement as a baseline.

## Main measure

**Swap completion rate:** sessions with a completed swap, divided by sessions with a search.
Why: it shows if the whole journey works, from the search to a finished swap. (Query 1.)

## Funnel measures (where do people drop out?)

| KPI | Definition | Why it matters |
|---|---|---|
| Search rate | Sessions with a search / all sessions | Do visitors try the main feature? |
| Suggestion rate | Searches that show at least one suggestion / all searches | Do the rules find something? A low rate may mean the rules are too strict, or too few listings. |
| Request rate | Sessions that send a request / sessions with suggestions | Are the suggestions good enough to act on? |
| Confirmation rate | Requests that are confirmed / all requests | Do the other people accept? |
| Completion rate | Confirmed swaps that complete / confirmed swaps | Should be close to 100%. A gap means something breaks at the end. |

## Quality and trust measures

| KPI | Definition | Why it matters |
|---|---|---|
| Reasons for no suggestion | Share of `no_suggestions_shown` by `reason` | Shows which rule blocks people most. (Query 3.) |
| Help chat answer rate | Questions with an answer / all questions, by category | Shows what the help guide is missing. (Query 6.) |
| Explanation views | Sessions that open the explanation / sessions with suggestions | Do people want to know why the app suggests something? |
| Audit log views | Sessions that open the audit log / sessions with a completed swap | A sign of trust in the process. |

## Guardrail (must always hold)

**Swaps completed without a request and a confirmation = 0.** The assistant can suggest a swap, but cannot request, confirm or complete one. Query 4 must always return zero rows.

## How to cut the numbers

By `priority`, by `source` (scenario or manual), by `device_type`, and by day. (Queries 2, 5 and 7.)

## Reading the numbers

- Count **sessions**, not events. One person can search many times in one visit.
- With small numbers, give a confidence interval, not only a percentage. The method is in the A/B test project (`ab-test-cookie-cats`).
- Look at the funnel from the end back to the start: the biggest drop in absolute people is where to work first.
