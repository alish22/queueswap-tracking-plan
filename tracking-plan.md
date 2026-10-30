# QueueSwap Match: tracking plan

**Status: proposal.** QueueSwap Match is a prototype with a simulated queue and no real users. This plan describes what I would track, and why, if the app had real users. The events and rules are written so that they can be set up in a product analytics tool (for example Amplitude or GA4) or stored in a database table.

## 1. Goal and the journey to measure

The app helps a person who must leave a queue soon to swap places with a person who can wait. The main journey is:

1. The person opens the page.
2. The person tells the app their situation (ticket, minutes left, maximum price, what matters most), by hand or with a ready-made scenario.
3. The app shows ranked swap suggestions, or says why there is none.
4. The person sends a swap request (only the person can do this, never the assistant).
5. The other side confirms.
6. The swap is completed and written to the audit log.

Other parts of the page: the open listings (and a form to add a listing), the explanation of what the assistant did, the audit log, and the help chat.

## 2. Rules for tracking

- **One event for one user action.** No event is sent for something that happens in the background without the person's action, except the results the app shows (`suggestions_shown`, `no_suggestions_shown`).
- **Names:** `snake_case`, object first, then the past-tense action (`swap_requested`).
- **No personal data.** The user ID is a random ID from the device. Free text is never sent: the optional note is not stored, only whether one was written (`has_note`). Help questions are stored as a category, not as text.
- **Every event has the same base properties:** `event_time`, `user_id`, `session_id`, `device_type`.
- **Properties have fixed values** (lists below), so that charts do not break when a new value appears.

## 3. Events

| Event | When it fires | Extra properties |
|---|---|---|
| `page_viewed` | The page loads | none |
| `scenario_selected` | The person chooses a ready-made scenario | `scenario_id` |
| `swap_search_submitted` | The person presses the button to find swaps | `minutes_left`, `max_credits`, `priority`, `has_note`, `source` |
| `suggestions_shown` | The app shows one or more suggestions | `suggestions_count`, `top_time_saved_min`, `top_credits_asked`, `explanation_mode` |
| `no_suggestions_shown` | The rules return no suggestion | `reason` |
| `suggestion_opened` | The person opens the details of a suggestion | `rank` |
| `explanation_viewed` | The person opens the "what the assistant did" panel | none |
| `swap_requested` | The person sends a swap request | `swap_id`, `rank`, `credits_offered` |
| `swap_confirmed` | The other side confirms the request | `swap_id` |
| `swap_declined` | The other side declines the request | `swap_id` |
| `swap_completed` | The swap is completed | `swap_id`, `time_saved_min`, `credits_paid` |
| `listing_created` | The person adds a listing to the open listings | `credits_asked` |
| `audit_log_viewed` | The person opens the audit log | none |
| `help_chat_opened` | The person opens the help chat | none |
| `help_chat_question_asked` | The person asks the help chat a question | `question_category`, `answered` |

## 4. Property dictionary

| Property | Type | Values or unit |
|---|---|---|
| `event_time` | timestamp | UTC |
| `user_id` | text | Random ID from the device |
| `session_id` | text | New for each visit |
| `device_type` | text | `desktop`, `phone` |
| `scenario_id` | text | ID of the ready-made scenario |
| `minutes_left` | integer | Minutes until the person must leave |
| `max_credits` | integer | The most the person will pay, in credits |
| `priority` | text | `deadline_lowest_cost`, `most_time_saved`, `lowest_price` |
| `has_note` | boolean | True if the person wrote a note (the text is never sent) |
| `source` | text | `scenario` or `manual` |
| `suggestions_count` | integer | Number of suggestions shown |
| `top_time_saved_min` | integer | Minutes saved by the first suggestion |
| `top_credits_asked` | integer | Credits asked in the first suggestion |
| `explanation_mode` | text | `rule_based` or `ai` |
| `reason` | text | `time_limit`, `locked_ticket`, `priority_ticket`, `budget_too_low` |
| `rank` | integer | Position of the suggestion in the list (1 is the top) |
| `swap_id` | text | One ID for the whole life of a swap, used in every swap event |
| `credits_offered`, `credits_paid`, `credits_asked` | integer | Credits |
| `time_saved_min` | integer | Minutes saved |
| `question_category` | text | `how_it_works`, `credits`, `rules`, `other` |
| `answered` | boolean | True if the help chat had an answer |

## 5. Data quality checks

Run these every day. Any failure means a tracking error or a bug.

| Check | Rule |
|---|---|
| No swap without a request and a confirmation | Every `swap_completed` has a `swap_requested` and a `swap_confirmed` with the same `swap_id`. This protects the main design rule of the app. (Query 4 in `sql/kpi_queries.sql`.) |
| Funnel order | A session cannot have `swap_requested` without an earlier `suggestions_shown`. |
| No duplicate events | `event_id` is unique. |
| Allowed values only | `priority`, `reason`, `device_type`, `question_category` and `explanation_mode` only have the values in the dictionary. |
| No text leaks | No property holds free text from the person. |

## 6. Open questions

- How should a returning person be recognised, if there is no sign-in?
- Should the simulated "other side" be tracked in the same way as a real person?
