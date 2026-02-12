"""Create and populate an Indian banking demo database."""

from __future__ import annotations

import argparse
import random
from typing import Iterable

import mysql.connector
from faker import Faker


fake = Faker("en_IN")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--database", default="bank_of_swapnil")
    parser.add_argument("--customers", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def chunks(rows: list[tuple], batch_size: int) -> Iterable[list[tuple]]:
    for i in range(0, len(rows), batch_size):
        yield rows[i : i + batch_size]


def create_schema(cursor: mysql.connector.cursor.MySQLCursor) -> None:
    cursor.execute(
        """
        CREATE TABLE customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            address TEXT,
            phone_number VARCHAR(20),
            id_number VARCHAR(20),
            created_at DATETIME
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            account_number VARCHAR(20) UNIQUE,
            account_type ENUM('SAVINGS', 'CHECKING'),
            balance DECIMAL(12,2),
            opened_at DATETIME,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT,
            amount DECIMAL(10,2),
            transaction_type ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER'),
            transaction_date DATETIME,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
        """
    )


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    Faker.seed(args.seed)

    conn = mysql.connector.connect(host=args.host, user=args.user, password=args.password)
    cursor = conn.cursor()

    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {args.database}")
        cursor.execute(f"CREATE DATABASE {args.database}")
        cursor.execute(f"USE {args.database}")
        create_schema(cursor)
        conn.commit()

        print("📥 Inserting customers...")
        customer_rows = [
            (
                fake.first_name(),
                fake.last_name(),
                fake.address().replace("\n", ", "),
                fake.phone_number(),
                str(fake.random_int(min=100000000000, max=999999999999)),
                fake.date_time_between(start_date="-5y", end_date="now"),
            )
            for _ in range(args.customers)
        ]
        for batch in chunks(customer_rows, args.batch_size):
            cursor.executemany(
                """
                INSERT INTO customers
                (first_name, last_name, address, phone_number, id_number, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                batch,
            )
            conn.commit()

        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]

        print("🏦 Inserting accounts...")
        account_rows: list[tuple] = []
        used_account_numbers: set[str] = set()
        for cid in customer_ids:
            for _ in range(random.randint(1, 2)):
                while True:
                    account_number = str(fake.random_number(digits=12, fix_len=True))
                    if account_number not in used_account_numbers:
                        used_account_numbers.add(account_number)
                        break
                account_rows.append(
                    (
                        cid,
                        account_number,
                        random.choice(["SAVINGS", "CHECKING"]),
                        round(random.uniform(1000.0, 100000.0), 2),
                        fake.date_time_between(start_date="-5y", end_date="now"),
                    )
                )
        for batch in chunks(account_rows, args.batch_size):
            cursor.executemany(
                """
                INSERT INTO accounts (customer_id, account_number, account_type, balance, opened_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                batch,
            )
            conn.commit()

        cursor.execute("SELECT id FROM accounts")
        account_ids = [row[0] for row in cursor.fetchall()]

        print("💸 Inserting transactions...")
        transaction_rows: list[tuple] = []
        for acc_id in account_ids:
            for _ in range(random.randint(5, 15)):
                transaction_rows.append(
                    (
                        acc_id,
                        round(random.uniform(100.0, 50000.0), 2),
                        random.choice(["DEPOSIT", "WITHDRAWAL", "TRANSFER"]),
                        fake.date_time_between(start_date="-3y", end_date="now"),
                    )
                )

        for batch in chunks(transaction_rows, args.batch_size):
            cursor.executemany(
                """
                INSERT INTO transactions (account_id, amount, transaction_type, transaction_date)
                VALUES (%s, %s, %s, %s)
                """,
                batch,
            )
            conn.commit()

        print(f"✅ Demo DB '{args.database}' created with mock data!")
    except mysql.connector.Error as exc:
        conn.rollback()
        raise SystemExit(f"Database error: {exc}") from exc
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
