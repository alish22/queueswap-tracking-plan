-- KPI queries for QueueSwap Match
-- Table: events (one row per tracked event). See docs/tracking-plan.md for the columns.
-- The queries use standard SQL, so they run in PostgreSQL and in SQLite.
-- Each query starts with a "-- name:" line. scripts/run_queries.py runs them one by one.


-- name: 1_session_funnel
-- Sessions that reach each step of the swap journey, and the conversion from the step before.
-- A session counts at a step only if it also reached all earlier steps.
WITH session_flags AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_name = 'page_viewed'           THEN 1 ELSE 0 END) AS viewed,
        MAX(CASE WHEN event_name = 'swap_search_submitted' THEN 1 ELSE 0 END) AS searched,
        MAX(CASE WHEN event_name = 'suggestions_shown'     THEN 1 ELSE 0 END) AS got_suggestions,
        MAX(CASE WHEN event_name = 'swap_requested'        THEN 1 ELSE 0 END) AS requested,
        MAX(CASE WHEN event_name = 'swap_confirmed'        THEN 1 ELSE 0 END) AS confirmed,
        MAX(CASE WHEN event_name = 'swap_completed'        THEN 1 ELSE 0 END) AS completed
    FROM events
    GROUP BY session_id
),
steps AS (
    SELECT 1 AS step_no, 'Page viewed' AS step, SUM(viewed) AS sessions FROM session_flags
    UNION ALL SELECT 2, 'Search submitted',  SUM(viewed * searched) FROM session_flags
    UNION ALL SELECT 3, 'Suggestions shown', SUM(viewed * searched * got_suggestions) FROM session_flags
    UNION ALL SELECT 4, 'Swap requested',    SUM(viewed * searched * got_suggestions * requested) FROM session_flags
    UNION ALL SELECT 5, 'Swap confirmed',    SUM(viewed * searched * got_suggestions * requested * confirmed) FROM session_flags
    UNION ALL SELECT 6, 'Swap completed',    SUM(viewed * searched * got_suggestions * requested * confirmed * completed) FROM session_flags
)
SELECT
    s.step_no,
    s.step,
    s.sessions,
    ROUND(100.0 * s.sessions / NULLIF(p.sessions, 0), 1) AS pct_of_previous_step,
    ROUND(100.0 * s.sessions / NULLIF(f.sessions, 0), 1) AS pct_of_all_sessions
FROM steps s
LEFT JOIN steps p ON p.step_no = s.step_no - 1
CROSS JOIN (SELECT sessions FROM steps WHERE step_no = 1) f
ORDER BY s.step_no;


-- name: 2_funnel_by_priority
-- Does the priority the user chooses change the result?
-- A session with searches under two different priorities counts once under each.
WITH searches AS (
    SELECT DISTINCT session_id, priority
    FROM events
    WHERE event_name = 'swap_search_submitted'
),
outcomes AS (
    SELECT
        session_id,
        MAX(CASE WHEN event_name = 'suggestions_shown' THEN 1 ELSE 0 END) AS got_suggestions,
        MAX(CASE WHEN event_name = 'swap_requested'    THEN 1 ELSE 0 END) AS requested,
        MAX(CASE WHEN event_name = 'swap_completed'    THEN 1 ELSE 0 END) AS completed
    FROM events
    GROUP BY session_id
)
SELECT
    s.priority,
    COUNT(*)                                              AS searches,
    ROUND(100.0 * SUM(o.got_suggestions) / COUNT(*), 1)   AS pct_with_suggestions,
    ROUND(100.0 * SUM(o.requested) / COUNT(*), 1)         AS pct_requested,
    ROUND(100.0 * SUM(o.completed) / COUNT(*), 1)         AS pct_completed
FROM searches s
JOIN outcomes o ON o.session_id = s.session_id
GROUP BY s.priority
ORDER BY searches DESC;


-- name: 3_why_no_suggestions
-- Why did the rules return no suggestion? Shows which rule blocks users most.
SELECT
    reason,
    COUNT(*) AS times_shown,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_all
FROM events
WHERE event_name = 'no_suggestions_shown'
GROUP BY reason
ORDER BY times_shown DESC;


-- name: 4_integrity_swap_completed_without_confirmation
-- GUARDRAIL. Design rule of the app: only the user can request a swap, and the other person
-- must confirm it. A swap must never be completed without a request and a confirmation.
-- This query must return zero rows. Any row is a bug or a tracking error.
SELECT c.swap_id, c.session_id, c.event_time
FROM events c
WHERE c.event_name = 'swap_completed'
  AND (
        NOT EXISTS (SELECT 1 FROM events r WHERE r.event_name = 'swap_requested' AND r.swap_id = c.swap_id)
     OR NOT EXISTS (SELECT 1 FROM events f WHERE f.event_name = 'swap_confirmed' AND f.swap_id = c.swap_id)
  )
ORDER BY c.event_time;


-- name: 5_daily_trend
-- Daily sessions, searches and completed swaps.
SELECT
    DATE(event_time) AS day,
    COUNT(DISTINCT session_id) AS sessions,
    COUNT(DISTINCT CASE WHEN event_name = 'swap_search_submitted' THEN session_id END) AS sessions_with_search,
    COUNT(CASE WHEN event_name = 'swap_completed' THEN 1 END) AS swaps_completed
FROM events
GROUP BY DATE(event_time)
ORDER BY day;


-- name: 6_help_chat
-- Is the help chat answering questions? Unanswered questions show what the guide is missing.
SELECT
    question_category,
    COUNT(*) AS questions,
    ROUND(100.0 * SUM(CAST(answered AS INTEGER)) / COUNT(*), 1) AS pct_answered
FROM events
WHERE event_name = 'help_chat_question_asked'
GROUP BY question_category
ORDER BY questions DESC;


-- name: 7_device_split
-- Do phone and desktop sessions behave differently? (share of sessions that complete a swap)
WITH session_flags AS (
    SELECT
        session_id,
        MAX(device_type) AS device_type,
        MAX(CASE WHEN event_name = 'swap_search_submitted' THEN 1 ELSE 0 END) AS searched,
        MAX(CASE WHEN event_name = 'swap_completed'        THEN 1 ELSE 0 END) AS completed
    FROM events
    GROUP BY session_id
)
SELECT
    device_type,
    COUNT(*) AS sessions,
    SUM(searched) AS searches,
    ROUND(100.0 * SUM(completed) / NULLIF(SUM(searched), 0), 1) AS pct_of_searching_sessions_completed
FROM session_flags
GROUP BY device_type
ORDER BY sessions DESC;
