"""Make SYNTHETIC sample events for QueueSwap Match.

This is made-up data. QueueSwap Match is a prototype with a simulated queue and no real users.
The file only exists so that the SQL queries in sql/kpi_queries.sql can be run and tested.
The step-to-step chances below are invented. Do not read any result from this data as a finding.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
N_SESSIONS = 1500
PRIORITIES = ["deadline_lowest_cost", "most_time_saved", "lowest_price"]
SCENARIOS = ["scenario_a", "scenario_b", "scenario_c"]
REASONS = ["time_limit", "locked_ticket", "priority_ticket", "budget_too_low"]
CATEGORIES = ["how_it_works", "credits", "rules", "other"]

COLUMNS = ["event_id", "event_time", "user_id", "session_id", "device_type", "event_name", "scenario_id",
           "minutes_left", "max_credits", "priority", "has_note", "source", "suggestions_count",
           "top_time_saved_min", "top_credits_asked", "explanation_mode", "reason", "rank", "swap_id",
           "credits_offered", "time_saved_min", "credits_paid", "credits_asked", "question_category", "answered"]

rows = []
swap_counter = 0
start = pd.Timestamp("2026-09-01 08:00")


def add(t, user, session, device, name, **props):
    rows.append({"event_time": t, "user_id": user, "session_id": session, "device_type": device,
                 "event_name": name, **props})


for s in range(N_SESSIONS):
    user = f"u{rng.integers(1, 900):04d}"
    session = f"s{s:05d}"
    device = rng.choice(["desktop", "phone"], p=[0.45, 0.55])
    t = start + pd.Timedelta(minutes=int(rng.integers(0, 60 * 24 * 14)))
    add(t, user, session, device, "page_viewed")

    if rng.random() < 0.20:                               # some visitors use the help chat first
        t += pd.Timedelta(seconds=20)
        add(t, user, session, device, "help_chat_opened")
        t += pd.Timedelta(seconds=15)
        add(t, user, session, device, "help_chat_question_asked",
            question_category=rng.choice(CATEGORIES), answered=bool(rng.random() < 0.85))

    if rng.random() > 0.70:                               # no search in this session
        continue

    source = "scenario" if rng.random() < 0.6 else "manual"
    if source == "scenario":
        t += pd.Timedelta(seconds=10)
        add(t, user, session, device, "scenario_selected", scenario_id=rng.choice(SCENARIOS))
    t += pd.Timedelta(seconds=30)
    add(t, user, session, device, "swap_search_submitted", minutes_left=int(rng.integers(5, 90)),
        max_credits=int(rng.integers(5, 60)), priority=rng.choice(PRIORITIES), has_note=bool(rng.random() < 0.15),
        source=source)

    t += pd.Timedelta(seconds=2)
    if rng.random() < 0.80:
        n = int(rng.integers(1, 6))
        add(t, user, session, device, "suggestions_shown", suggestions_count=n,
            top_time_saved_min=int(rng.integers(3, 40)), top_credits_asked=int(rng.integers(3, 50)),
            explanation_mode="rule_based")
    else:
        add(t, user, session, device, "no_suggestions_shown", reason=rng.choice(REASONS, p=[0.35, 0.25, 0.15, 0.25]))
        continue

    if rng.random() < 0.55:
        t += pd.Timedelta(seconds=15)
        add(t, user, session, device, "suggestion_opened", rank=int(rng.integers(1, 4)))
    if rng.random() < 0.20:
        t += pd.Timedelta(seconds=10)
        add(t, user, session, device, "explanation_viewed")
    if rng.random() > 0.45:                               # no request sent
        continue

    swap_counter += 1
    swap = f"w{swap_counter:05d}"
    t += pd.Timedelta(seconds=20)
    add(t, user, session, device, "swap_requested", swap_id=swap, rank=int(rng.integers(1, 4)),
        credits_offered=int(rng.integers(3, 50)))
    t += pd.Timedelta(seconds=5)
    if rng.random() < 0.75:
        add(t, user, session, device, "swap_confirmed", swap_id=swap)
        t += pd.Timedelta(seconds=2)
        add(t, user, session, device, "swap_completed", swap_id=swap, time_saved_min=int(rng.integers(3, 40)),
            credits_paid=int(rng.integers(3, 50)))
        if rng.random() < 0.3:
            t += pd.Timedelta(seconds=8)
            add(t, user, session, device, "audit_log_viewed")
    else:
        add(t, user, session, device, "swap_declined", swap_id=swap)

    if rng.random() < 0.08:
        t += pd.Timedelta(seconds=40)
        add(t, user, session, device, "listing_created", credits_asked=int(rng.integers(3, 40)))

df = pd.DataFrame(rows)

# Three planted errors, so the integrity check in the SQL file has something to find:
# a swap that is "completed" with no confirmation.
for i in range(3):
    swap_counter += 1
    t = start + pd.Timedelta(days=int(rng.integers(1, 13)), hours=int(rng.integers(9, 18)))
    bad = pd.DataFrame([{"event_time": t, "user_id": f"u9{i:03d}", "session_id": f"bad{i:02d}", "device_type": "desktop",
                         "event_name": "swap_completed", "swap_id": f"w9{i:04d}", "time_saved_min": 10, "credits_paid": 10}])
    df = pd.concat([df, bad], ignore_index=True)

df = df.sort_values("event_time").reset_index(drop=True)
df.insert(0, "event_id", np.arange(1, len(df) + 1))
for c in COLUMNS:
    if c not in df.columns:
        df[c] = np.nan
df = df[COLUMNS]
df["event_time"] = df["event_time"].dt.strftime("%Y-%m-%d %H:%M:%S")

out = Path(__file__).resolve().parent.parent / "data" / "sample_events.csv"
df.to_csv(out, index=False)
print(f"Wrote {len(df):,} synthetic events in {df['session_id'].nunique():,} sessions to {out}")
