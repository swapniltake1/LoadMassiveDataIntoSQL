"""Populate a 10-table banking schema with configurable row counts."""

from __future__ import annotations

import argparse
import random
from typing import Iterable

import mysql.connector
from faker import Faker
from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--user", default="root")
    parser.add_argument("--password", default="root")
    parser.add_argument("--database", default="BankOf420")
    parser.add_argument("--branches", type=int, default=100)
    parser.add_argument("--employees", type=int, default=500)
    parser.add_argument("--customers", type=int, default=500_000)
    parser.add_argument("--accounts", type=int, default=500_000)
    parser.add_argument("--transactions", type=int, default=1_000_000)
    parser.add_argument("--loans", type=int, default=5_000)
    parser.add_argument("--loan-payments", type=int, default=20_000)
    parser.add_argument("--cards", type=int, default=100_000)
    parser.add_argument("--card-transactions", type=int, default=50_000)
    parser.add_argument("--atms", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def chunks(rows: list[tuple], batch_size: int) -> Iterable[list[tuple]]:
    for i in range(0, len(rows), batch_size):
        yield rows[i : i + batch_size]


def create_schema(cur: mysql.connector.cursor.MySQLCursor) -> None:
    tables = [
        "card_transactions",
        "cards",
        "loan_payments",
        "loans",
        "transactions",
        "accounts",
        "customers",
        "employees",
        "atm_locations",
        "branches",
    ]
    for tbl in tables:
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    cur.execute(
        """
        CREATE TABLE branches (
            branch_id INT AUTO_INCREMENT PRIMARY KEY,
            branch_name VARCHAR(100),
            branch_code VARCHAR(20),
            city VARCHAR(50),
            ifsc_code VARCHAR(20)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE employees (
            emp_id INT AUTO_INCREMENT PRIMARY KEY,
            emp_name VARCHAR(100),
            designation VARCHAR(50),
            branch_id INT,
            salary DECIMAL(10,2),
            doj DATE,
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100),
            dob DATE,
            gender VARCHAR(10),
            city VARCHAR(50),
            contact_no VARCHAR(15),
            email VARCHAR(100)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE accounts (
            account_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            branch_id INT,
            account_type VARCHAR(20),
            balance DECIMAL(12,2),
            opening_date DATE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE transactions (
            txn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            account_id INT,
            txn_type VARCHAR(20),
            amount DECIMAL(12,2),
            txn_date DATETIME,
            description VARCHAR(200),
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE loans (
            loan_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            branch_id INT,
            loan_type VARCHAR(50),
            loan_amount DECIMAL(12,2),
            interest_rate FLOAT,
            start_date DATE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE loan_payments (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            loan_id INT,
            payment_date DATE,
            payment_amount DECIMAL(12,2),
            FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE cards (
            card_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT,
            card_type VARCHAR(20),
            card_number VARCHAR(20),
            expiry_date DATE,
            cvv VARCHAR(4),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE card_transactions (
            card_txn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            card_id INT,
            amount DECIMAL(12,2),
            txn_date DATETIME,
            merchant_name VARCHAR(100),
            city VARCHAR(50),
            FOREIGN KEY (card_id) REFERENCES cards(card_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE atm_locations (
            atm_id INT AUTO_INCREMENT PRIMARY KEY,
            branch_id INT,
            location VARCHAR(100),
            city VARCHAR(50),
            status VARCHAR(20),
            FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
        )
        """
    )


def insert_batched(
    conn: mysql.connector.MySQLConnection,
    cur: mysql.connector.cursor.MySQLCursor,
    sql: str,
    rows: list[tuple],
    batch_size: int,
    desc: str,
) -> None:
    total_batches = (len(rows) + batch_size - 1) // batch_size
    for batch in tqdm(chunks(rows, batch_size), total=total_batches, desc=desc):
        cur.executemany(sql, batch)
        conn.commit()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    Faker.seed(args.seed)
    fake = Faker("en_IN")

    conn = mysql.connector.connect(host=args.host, user=args.user, password=args.password)
    cur = conn.cursor()

    cities = [
        "Pune",
        "Mumbai",
        "Nagpur",
        "Nashik",
        "Aurangabad",
        "Kolhapur",
        "Solapur",
        "Thane",
        "Ahmednagar",
        "Satara",
    ]

    try:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {args.database}")
        cur.execute(f"USE {args.database}")
        create_schema(cur)
        conn.commit()

        branch_rows = [
            (
                f"{random.choice(cities)} Branch {i + 1}",
                f"BR{i + 1:03d}",
                random.choice(cities),
                f"MAHB{i + 1:07d}",
            )
            for i in range(args.branches)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO branches (branch_name, branch_code, city, ifsc_code) VALUES (%s,%s,%s,%s)",
            branch_rows,
            args.batch_size,
            "branches",
        )

        employee_rows = [
            (
                fake.name(),
                random.choice(["Manager", "Clerk", "Cashier", "Officer"]),
                random.randint(1, args.branches),
                random.randint(30000, 90000),
                fake.date_between(start_date="-5y", end_date="today"),
            )
            for _ in range(args.employees)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO employees (emp_name, designation, branch_id, salary, doj) VALUES (%s,%s,%s,%s,%s)",
            employee_rows,
            args.batch_size,
            "employees",
        )

        customer_rows = [
            (
                fake.name(),
                fake.date_of_birth(minimum_age=18, maximum_age=75),
                random.choice(["Male", "Female"]),
                random.choice(cities),
                fake.phone_number(),
                fake.email(),
            )
            for _ in range(args.customers)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO customers (full_name, dob, gender, city, contact_no, email) VALUES (%s,%s,%s,%s,%s,%s)",
            customer_rows,
            args.batch_size,
            "customers",
        )

        account_rows = [
            (
                random.randint(1, args.customers),
                random.randint(1, args.branches),
                random.choice(["Saving", "Current"]),
                random.randint(1000, 100000),
                fake.date_between(start_date="-5y", end_date="today"),
            )
            for _ in range(args.accounts)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO accounts (customer_id, branch_id, account_type, balance, opening_date) VALUES (%s,%s,%s,%s,%s)",
            account_rows,
            args.batch_size,
            "accounts",
        )

        transaction_rows = [
            (
                random.randint(1, args.accounts),
                random.choice(["Credit", "Debit"]),
                random.randint(100, 50000),
                fake.date_time_between(start_date="-2y", end_date="now"),
                fake.sentence(nb_words=6),
            )
            for _ in range(args.transactions)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO transactions (account_id, txn_type, amount, txn_date, description) VALUES (%s,%s,%s,%s,%s)",
            transaction_rows,
            args.batch_size,
            "transactions",
        )

        loan_rows = [
            (
                random.randint(1, args.customers),
                random.randint(1, args.branches),
                random.choice(["Home Loan", "Personal Loan", "Car Loan", "Education Loan"]),
                random.randint(100000, 2000000),
                random.uniform(6.5, 12.5),
                fake.date_between(start_date="-5y", end_date="today"),
            )
            for _ in range(args.loans)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO loans (customer_id, branch_id, loan_type, loan_amount, interest_rate, start_date) VALUES (%s,%s,%s,%s,%s,%s)",
            loan_rows,
            args.batch_size,
            "loans",
        )

        loan_payment_rows = [
            (
                random.randint(1, args.loans),
                fake.date_between(start_date="-3y", end_date="today"),
                random.randint(2000, 50000),
            )
            for _ in range(args.loan_payments)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO loan_payments (loan_id, payment_date, payment_amount) VALUES (%s,%s,%s)",
            loan_payment_rows,
            args.batch_size,
            "loan_payments",
        )

        card_rows = [
            (
                random.randint(1, args.customers),
                random.choice(["Debit", "Credit"]),
                fake.credit_card_number(card_type=None),
                fake.date_between(start_date="today", end_date="+5y"),
                str(random.randint(100, 999)),
            )
            for _ in range(args.cards)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO cards (customer_id, card_type, card_number, expiry_date, cvv) VALUES (%s,%s,%s,%s,%s)",
            card_rows,
            args.batch_size,
            "cards",
        )

        card_txn_rows = [
            (
                random.randint(1, args.cards),
                random.randint(100, 10000),
                fake.date_time_between(start_date="-2y", end_date="now"),
                fake.company(),
                random.choice(cities),
            )
            for _ in range(args.card_transactions)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO card_transactions (card_id, amount, txn_date, merchant_name, city) VALUES (%s,%s,%s,%s,%s)",
            card_txn_rows,
            args.batch_size,
            "card_transactions",
        )

        atm_rows = [
            (
                random.randint(1, args.branches),
                fake.street_address(),
                random.choice(cities),
                random.choice(["Active", "Inactive"]),
            )
            for _ in range(args.atms)
        ]
        insert_batched(
            conn,
            cur,
            "INSERT INTO atm_locations (branch_id, location, city, status) VALUES (%s,%s,%s,%s)",
            atm_rows,
            args.batch_size,
            "atm_locations",
        )

        print("\n✅ All tables populated successfully with realistic banking data!")
    except mysql.connector.Error as exc:
        conn.rollback()
        raise SystemExit(f"Database error: {exc}") from exc
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
