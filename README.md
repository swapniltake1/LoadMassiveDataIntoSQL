# Load Massive Data Into SQL

Utilities for generating realistic demo banking datasets in MySQL using `Faker`.

## What this repository provides

- Fast data loaders for one small 3-table banking schema and one larger 10-table schema.
- Batch inserts (`executemany`) for better performance.
- CLI options to control row counts, batch size, and DB connection settings.
- Reproducible datasets via configurable random seeds.

## Requirements

- Python 3.9+
- MySQL server (8+ recommended)
- Python packages:
  - `mysql-connector-python`
  - `faker`
  - `tqdm`

Install dependencies:

```bash
pip install mysql-connector-python faker tqdm
```

## Quick start

### 1) Generate 50k rows for each table (10-table schema)

```bash
python Load50kEach_bank.py --rows 50000 --batch-size 1000 --database BankOf420
```

### 2) Generate a larger custom 10-table dataset

```bash
python LoadMassiveDataWith10Tabel.py --customers 200000 --transactions 400000 --cards 120000
```

### 3) Generate a small 3-table demo dataset

```bash
python LoadMassiveDemoData.py --customers 10000 --database bank_demo
```

### 4) Generate swapnil demo database

```bash
python bank_swapnil_demo.py --customers 500 --database bank_of_swapnil
```

## Common CLI options

All scripts support these connection overrides:

- `--host` (default: `localhost`)
- `--user` (default: `root`)
- `--password` (default: `root`)
- `--database` (script-specific default)

Some scripts also support:

- `--batch-size`
- `--seed`
- per-table row-count options

## Safety notes

- Most scripts **drop and recreate tables**, and some recreate databases.
- Use a non-production MySQL instance for testing.

## Troubleshooting

- If connection fails, verify MySQL credentials and that MySQL is running.
- If inserts are slow, increase `--batch-size` carefully (watch memory).
- If locale-specific faker data causes formatting issues, switch locale in script.

## Files

- `LoadMassiveDemoData.py`: small 3-table demo dataset (`customers`, `accounts`, `transactions`).
- `bank_swapnil_demo.py`: small Indian-locale demo with account numbers.
- `LoadMassiveDataWith10Tabel.py`: configurable 10-table “massive” loader.
- `Load50kEach_bank.py`: optimized loader targeting equal row counts per table.

