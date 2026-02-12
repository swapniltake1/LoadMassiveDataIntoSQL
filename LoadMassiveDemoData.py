"""Generate a small 3-table banking demo dataset in MySQL."""

from __future__ import annotations

import argparse
import random
from typing import Iterable

import mysql.connector
from faker import Faker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--database", default="bank_demo")
    parser.add_argument("--customers", type=int, default=10_000)
    parser.add_argument("--batch-size", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def chunks(rows: list[tuple], batch_size: int) -> Iterable[list[tuple]]:
    for i in range(0, len(rows), batch_size):
        yield rows[i : i + batch_size]


def create_schema(cursor: mysql.connector.cursor.MySQLCursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            created_at DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            account_type ENUM('SAVINGS', 'CHECKING'),
            balance DECIMAL(10,2),
            opened_at DATETIME,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT,
            amount DECIMAL(10,2),
            transaction_type ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER'),
            transaction_date DATETIME,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    conn = mysql.connector.connect(
        host=args.host,
        user=args.user,
        password=args.password,
    )
    cursor = conn.cursor()

    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {args.database}")
        cursor.execute(f"USE {args.database}")
        create_schema(cursor)
        conn.commit()

        print("Inserting customers...")
        customer_rows = [
            (
                fake.name(),
                fake.email(),
                fake.date_time_between(start_date="-5y", end_date="now"),
            )
            for _ in range(args.customers)
        ]
        for batch in chunks(customer_rows, args.batch_size):
            cursor.executemany(
                "INSERT INTO customers (name, email, created_at) VALUES (%s, %s, %s)",
                batch,
            )
            conn.commit()

        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]

        print("Inserting accounts...")
        account_rows: list[tuple] = []
        for cust_id in customer_ids:
            for _ in range(random.randint(1, 2)):
                account_rows.append(
                    (
                        cust_id,
                        random.choice(["SAVINGS", "CHECKING"]),
                        round(random.uniform(100, 10_000), 2),
                        fake.date_time_between(start_date="-5y", end_date="now"),
                    )
                )
        for batch in chunks(account_rows, args.batch_size):
            cursor.executemany(
                """
                INSERT INTO accounts (customer_id, account_type, balance, opened_at)
                VALUES (%s, %s, %s, %s)
                """,
                batch,
            )
            conn.commit()

        cursor.execute("SELECT id FROM accounts")
        account_ids = [row[0] for row in cursor.fetchall()]

        print("Inserting transactions...")
        txn_rows: list[tuple] = []
        for acc_id in account_ids:
            for _ in range(random.randint(5, 20)):
                txn_rows.append(
                    (
                        acc_id,
                        round(random.uniform(10, 5000), 2),
                        random.choice(["DEPOSIT", "WITHDRAWAL", "TRANSFER"]),
                        fake.date_time_between(start_date="-3y", end_date="now"),
                    )
                )
        for batch in chunks(txn_rows, args.batch_size):
            cursor.executemany(
                """
                INSERT INTO transactions (account_id, amount, transaction_type, transaction_date)
                VALUES (%s, %s, %s, %s)
                """,
                batch,
            )
            conn.commit()

        print("✅ All done! Check your MySQL database.")
    except mysql.connector.Error as exc:
        conn.rollback()
        raise SystemExit(f"Database error: {exc}") from exc
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
