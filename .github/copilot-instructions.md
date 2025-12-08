## Purpose

This file gives short, actionable guidance to an AI coding agent working in this repository so it can be productive immediately. It focuses on concrete, discoverable patterns from the codebase (examples and file references), developer workflows, and integration points.

## Quick facts

- Project type: small collection of single-purpose Python scripts that generate and insert large volumes of demo banking data into a local MySQL database.
- Main files to inspect: `bank_swapnil_demo.py`, `LoadMassiveDataWith10Tabel.py`, `LoadMassiveDemoData.py` (all at repository root).
- Primary integration: a local MySQL server (scripts use `mysql.connector`).

## How to run (developer workflow)

Prereqs: Python 3.x, running MySQL server, Windows PowerShell (this repository was developed on Windows).

Install Python deps:

```powershell
pip install faker mysql-connector-python tqdm
```

Run a script (example):

```powershell
# run small/demo
python .\LoadMassiveDemoData.py
# run large/benchmark (ensure DB config and capacity)
python .\LoadMassiveDataWith10Tabel.py
```

Notes: scripts either create databases/tables (`bank_swapnil_demo.py`) or expect a DB to exist (`LoadMassiveDemoData.py` has `database="bank_demo"` with comment "Make sure this DB exists"). Update connection parameters before running.

## Concrete patterns & expectations (use these when changing code)

- Direct SQL execution: all DB interactions use `mysql.connector` and raw `cursor.execute(sql, params)`. No ORM.
  - Example: `DB_CONFIG` in `LoadMassiveDataWith10Tabel.py` holds credentials and database name — prefer editing that dict when updating credentials.
- Table lifecycle:
  - Many scripts drop or CREATE tables for clean reruns (e.g., `cur.execute("DROP TABLE IF EXISTS {tbl}")` in `LoadMassiveDataWith10Tabel.py`). Be careful not to run these against production data.
- Large-batch insertion patterns:
  - Scripts insert hundreds of thousands to millions of rows and use manual commit batching. For example, `LoadMassiveDataWith10Tabel.py` commits every 1000–2000 iterations to avoid large transactions.
  - Use the same batching approach when adding new bulk loads. Mirror existing commit thresholds to keep memory and lock behavior consistent.
- Faker usage:
  - `Faker('en_IN')` is used to generate India-centric data in `bank_swapnil_demo.py` and `LoadMassiveDataWith10Tabel.py`. Preserve locale where realistic regional data is needed.

## Safety and editing rules for AI agents

- Never change DB credentials automatically. If you need to modify connection config, place edits behind a clear TODO and flag for developer review.
- Avoid changing `DROP TABLE` or `CREATE DATABASE` lines unless the user explicitly requests it. These scripts are destructive by design for local demo use.
- When proposing performance changes (batch sizing, multi-row inserts, LOAD DATA INFILE), include a short experiment plan and a small, testable change that preserves current behavior by default.

## Key files to reference for patterns and examples

- `bank_swapnil_demo.py` — creates `bank_of_swapnil` and demonstrates schema design for customers/accounts/transactions and use of `Faker('en_IN')`.
- `LoadMassiveDataWith10Tabel.py` — canonical large-run script: `DB_CONFIG` dict, table definitions for 10 tables, heavy loops (500k+ inserts), `tqdm` progress bars, periodic commits (see commit calls inside loops).
- `LoadMassiveDemoData.py` — smaller demo flow; uses `CREATE TABLE IF NOT EXISTS` and explicit `database="bank_demo"` in connection.

## Integration points & external dependencies

- Local MySQL server required (default host `localhost`, user `root`, password set in scripts). No external APIs.
- Python packages: `faker`, `mysql-connector-python`, `tqdm`.

## Useful examples for code edits

- To change DB settings, edit `DB_CONFIG` in `LoadMassiveDataWith10Tabel.py` rather than sprinkling connection literals across files.
- To add a new table, follow the pattern in `LoadMassiveDataWith10Tabel.py`: create DDL string, `cur.execute(DDL)`, then add matching insertion loop with periodic `conn.commit()`.

## What to ask the maintainer before risky changes

1. Which local databases are safe to drop/overwrite? (e.g., `bank_of_swapnil` vs `bank_demo` vs `bankdb`.)
2. Preferred commit/batch sizes for production-like loads.
3. If switching to faster bulk-loading (e.g., `LOAD DATA INFILE`), confirm MySQL server permissions.

---

If anything here is unclear or you want more examples (like a sample batched bulk-insert function or a small test harness), tell me what to add and I'll iterate.
