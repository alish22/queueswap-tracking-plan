# QueueSwap Match: experiment ideas

These are ideas for A/B tests, for the time when the app has real traffic. The sample sizes use the usual formula for comparing two proportions (95% confidence, 80% power). The baseline rates are **assumptions for illustration**, not measurements. Replace them with the real rates after launch.

## Idea 1: explain why there is no suggestion

- **Problem:** when the rules return nothing, the person may just leave.
- **Change:** show the reason in plain words (for example "your time limit is too short for any open ticket") and what to change.
- **Primary metric:** share of `no_suggestions_shown` sessions that run a second search.
- **Guardrail:** the number of swaps completed without confirmation stays at 0.

## Idea 2: show the top suggestion first, or the top three

- **Change:** show only the best suggestion, against a ranked list.
- **Primary metric:** request rate (sessions that send a request / sessions with suggestions).
- **Secondary:** time from `suggestions_shown` to `swap_requested`; confirmation rate.

## How many sessions are needed?

Sessions per group for 95% confidence and 80% power:

| Assumed baseline | Change to detect | Sessions needed per group |
|---|---|---|
| 30% | +3 percentage points | 3,763 |
| 30% | +5 percentage points | 1,377 |
| 30% | +10 percentage points | 356 |
| 50% | +3 percentage points | 4,356 |
| 50% | +5 percentage points | 1,565 |
| 50% | +10 percentage points | 388 |

A prototype without real traffic cannot run these tests. The table shows how much traffic would be needed first.
