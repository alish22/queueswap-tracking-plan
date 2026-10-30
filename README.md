# QueueSwap Match: Tracking Plan, KPIs and SQL

A product analytics plan for [QueueSwap Match](https://github.com/alish22/QueueSwap-match), a prototype web app for swapping places in a simulated service queue. It defines what to track, how to measure success, and the SQL to measure it.

> **Status:** a proposal. QueueSwap Match is a prototype with a simulated queue and no real users. The sample data in this repository is **synthetic** (made up) and only exists to test the SQL. No number from it is a finding.

## What is in this repository

| Path | Content |
|---|---|
| [`docs/tracking-plan.md`](docs/tracking-plan.md) | The user journey, 15 events with properties, a property dictionary, tracking rules and daily data quality checks |
| [`docs/kpi-definitions.md`](docs/kpi-definitions.md) | The main measure, funnel measures, quality measures and one guardrail |
| [`docs/experiment-ideas.md`](docs/experiment-ideas.md) | Two A/B test ideas and the sample sizes they would need |
| [`sql/kpi_queries.sql`](sql/kpi_queries.sql) | Seven SQL queries (funnel, split by priority, reasons for no suggestion, integrity check, daily trend, help chat, device split) |
| [`scripts/make_sample_events.py`](scripts/make_sample_events.py) | Makes the synthetic sample events |
| [`scripts/run_queries.py`](scripts/run_queries.py) | Loads the sample into SQLite and runs all queries |
| `data/sample_events.csv` | 6,470 synthetic events in about 1,500 sessions |

## The main ideas

- **Funnel:** page viewed, search submitted, suggestions shown, swap requested, swap confirmed, swap completed.
- **Guardrail:** the assistant can suggest a swap, but only the user can request it and the other side must confirm. So "swap completed without a request and a confirmation" must always be zero. Query 4 checks this. I planted three such errors in the sample data, and the query finds all three.
- **Privacy by design:** no free text is tracked. The note is stored only as "has a note", and help questions only as a category.
- **Portable SQL:** the queries use standard SQL and run in PostgreSQL and SQLite.

## How to run the queries

```bash
pip install pandas
python scripts/run_queries.py
```

The script prints the result of each query. To use the queries on a real events table, load your data into a table called `events` with the columns in `docs/tracking-plan.md` and run the queries from `sql/kpi_queries.sql`.

## Related projects

- [ab-test-cookie-cats](https://github.com/alish22/ab-test-cookie-cats): the A/B test method that these experiment ideas would use.
