"""Load data/sample_events.csv into an in-memory SQLite database and run every query in sql/kpi_queries.sql.

Usage:  python scripts/run_queries.py
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

root = Path(__file__).resolve().parent.parent
events = pd.read_csv(root / "data" / "sample_events.csv")
for col in ["answered", "has_note"]:          # True/False to 1/0, so the same SQL runs in SQLite and PostgreSQL
    events[col] = events[col].map({True: 1.0, False: 0.0})

con = sqlite3.connect(":memory:")
events.to_sql("events", con, index=False)

sql_text = (root / "sql" / "kpi_queries.sql").read_text(encoding="utf-8")
blocks = re.split(r"^-- name: (\S+)\s*$", sql_text, flags=re.MULTILINE)

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)
for name, body in zip(blocks[1::2], blocks[2::2]):
    print(f"\n=== {name} ===")
    print(pd.read_sql_query(body, con).to_string(index=False))
