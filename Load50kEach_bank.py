"""Load 50k rows (default) into each table of a 10-table banking schema."""

from __future__ import annotations

import argparse

from LoadMassiveDataWith10Tabel import main as run_massive_loader


# Kept as a separate entrypoint for backwards compatibility.
# This script delegates to the configurable loader with defaults tuned to 50k.

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=50_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--database", default="BankOf420")
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def build_argv(args: argparse.Namespace) -> list[str]:
    rows = str(args.rows)
    return [
        "--host",
        args.host,
        "--user",
        args.user,
        "--password",
        args.password,
        "--database",
        args.database,
        "--seed",
        str(args.seed),
        "--batch-size",
        str(args.batch_size),
        "--branches",
        rows,
        "--employees",
        rows,
        "--customers",
        rows,
        "--accounts",
        rows,
        "--transactions",
        rows,
        "--loans",
        rows,
        "--loan-payments",
        rows,
        "--cards",
        rows,
        "--card-transactions",
        rows,
        "--atms",
        rows,
    ]


if __name__ == "__main__":
    import sys

    cli_args = parse_args()
    sys.argv = [sys.argv[0], *build_argv(cli_args)]
    run_massive_loader()
