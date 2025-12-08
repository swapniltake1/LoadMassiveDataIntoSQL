import mysql.connector
from faker import Faker
import random
from tqdm import tqdm
from datetime import datetime, timedelta

# CONFIG
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",    # change if needed
    "database": "BankOf420"
}
TOTAL = 50_000
BATCH = 1000

fake = Faker("en_IN")
random.seed(42)

# Helper
def chunks(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i+n]

# Connect
conn = mysql.connector.connect(**DB_CONFIG)
conn.autocommit = False
cur = conn.cursor()

# Ensure DB exists / switch (comment out if DB already created)
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
cur.execute(f"USE {DB_CONFIG['database']}")

# Drop tables if exist (clean run)
tables = [
    "card_transactions", "cards", "loan_payments", "loans", "transactions",
    "accounts", "customers", "employees", "atm_locations", "branches"
]
for tbl in tables:
    cur.execute(f"DROP TABLE IF EXISTS {tbl}")

# Create schema (FKs aligned for TOTAL rows)
cur.execute("""
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100),
    branch_code VARCHAR(20),
    city VARCHAR(50),
    ifsc_code VARCHAR(20)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_name VARCHAR(100),
    designation VARCHAR(50),
    branch_id INT,
    salary DECIMAL(10,2),
    doj DATE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    dob DATE,
    gender VARCHAR(10),
    city VARCHAR(50),
    contact_no VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    branch_id INT,
    account_type VARCHAR(20),
    balance DECIMAL(12,2),
    opening_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE transactions (
    txn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    txn_type VARCHAR(20),
    amount DECIMAL(12,2),
    txn_date DATETIME,
    description VARCHAR(200),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
) ENGINE=InnoDB
""")

cur.execute("""
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
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE loan_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    payment_date DATE,
    payment_amount DECIMAL(12,2),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    card_type VARCHAR(20),
    card_number VARCHAR(30),
    expiry_date DATE,
    cvv VARCHAR(4),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE card_transactions (
    card_txn_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    card_id INT,
    amount DECIMAL(12,2),
    txn_date DATETIME,
    merchant_name VARCHAR(100),
    city VARCHAR(50),
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
) ENGINE=InnoDB
""")

cur.execute("""
CREATE TABLE atm_locations (
    atm_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    location VARCHAR(200),
    city VARCHAR(50),
    status VARCHAR(20),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
) ENGINE=InnoDB
""")

conn.commit()
print("✅ Schema created.")

# Speed-up: disable FK checks during bulk load
cur.execute("SET FOREIGN_KEY_CHECKS=0")

# 1) Branches
branch_rows = [
    (f"{fake.city()} Branch {i+1}", f"BR{i+1:05d}", fake.city(), f"IFSC{i+1:05d}")
    for i in range(TOTAL)
]
for batch in chunks(branch_rows, BATCH):
    cur.executemany("INSERT INTO branches (branch_name, branch_code, city, ifsc_code) VALUES (%s,%s,%s,%s)", batch)
    conn.commit()
print(f"🏦 Inserted {TOTAL} branches.")

# 2) Employees
designations = ["Manager", "Clerk", "Cashier", "Officer"]
emp_rows = [
    (fake.name(), random.choice(designations), random.randint(1, TOTAL),
     round(random.uniform(25000, 150000),2), fake.date_between(start_date="-8y", end_date="today"))
    for _ in range(TOTAL)
]
for batch in chunks(emp_rows, BATCH):
    cur.executemany("INSERT INTO employees (emp_name, designation, branch_id, salary, doj) VALUES (%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"👨‍💼 Inserted {TOTAL} employees.")

# 3) Customers
cities = ["Pune","Mumbai","Nagpur","Nashik","Aurangabad","Kolhapur","Solapur","Thane","Ahmednagar","Satara"]
cust_rows = [
    (fake.name(), fake.date_of_birth(minimum_age=18, maximum_age=75), random.choice(["Male","Female"]),
     random.choice(cities), fake.phone_number(), fake.safe_email())
    for _ in range(TOTAL)
]
for batch in chunks(cust_rows, BATCH):
    cur.executemany("INSERT INTO customers (full_name, dob, gender, city, contact_no, email) VALUES (%s,%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"👥 Inserted {TOTAL} customers.")

# 4) Accounts (1:1 mapping with customers here)
account_rows = [
    (cust_id, random.randint(1, TOTAL), random.choice(["Saving","Current"]),
     round(random.uniform(1000, 200000),2), fake.date_between(start_date="-8y", end_date="today"))
    for cust_id in range(1, TOTAL+1)
]
for batch in chunks(account_rows, BATCH):
    cur.executemany("INSERT INTO accounts (customer_id, branch_id, account_type, balance, opening_date) VALUES (%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"💰 Inserted {TOTAL} accounts.")

# 5) Transactions
txn_rows = []
for _ in range(TOTAL):
    txn_rows.append((
        random.randint(1, TOTAL),
        random.choice(["Credit","Debit"]),
        round(random.uniform(50, 100000),2),
        fake.date_time_between(start_date="-2y", end_date="now"),
        fake.sentence(nb_words=6)
    ))
for batch in chunks(txn_rows, BATCH):
    cur.executemany("INSERT INTO transactions (account_id, txn_type, amount, txn_date, description) VALUES (%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"💳 Inserted {TOTAL} transactions.")

# 6) Loans
loan_types = ["Home Loan","Personal Loan","Car Loan","Education Loan"]
loan_rows = [
    (random.randint(1, TOTAL), random.randint(1, TOTAL), random.choice(loan_types),
     round(random.uniform(50000, 5000000),2), round(random.uniform(6.5,12.5),2),
     fake.date_between(start_date="-8y", end_date="today"))
    for _ in range(TOTAL)
]
for batch in chunks(loan_rows, BATCH):
    cur.executemany("INSERT INTO loans (customer_id, branch_id, loan_type, loan_amount, interest_rate, start_date) VALUES (%s,%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"🏠 Inserted {TOTAL} loans.")

# 7) Loan Payments
loan_payment_rows = [
    (random.randint(1, TOTAL), fake.date_between(start_date="-5y", end_date="today"), round(random.uniform(500, 100000),2))
    for _ in range(TOTAL)
]
for batch in chunks(loan_payment_rows, BATCH):
    cur.executemany("INSERT INTO loan_payments (loan_id, payment_date, payment_amount) VALUES (%s,%s,%s)", batch)
    conn.commit()
print(f"💵 Inserted {TOTAL} loan payments.")

# 8) Cards
card_rows = [
    (random.randint(1, TOTAL), random.choice(["Debit","Credit"]),
     fake.credit_card_number(card_type=None), fake.date_between(start_date="today", end_date="+5y"), f"{random.randint(100,999)}")
    for _ in range(TOTAL)
]
for batch in chunks(card_rows, BATCH):
    cur.executemany("INSERT INTO cards (customer_id, card_type, card_number, expiry_date, cvv) VALUES (%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"💳 Inserted {TOTAL} cards.")

# 9) Card Transactions
card_txn_rows = [
    (random.randint(1, TOTAL), round(random.uniform(20, 20000),2), fake.date_time_between(start_date="-2y", end_date="now"), fake.company(), random.choice(cities))
    for _ in range(TOTAL)
]
for batch in chunks(card_txn_rows, BATCH):
    cur.executemany("INSERT INTO card_transactions (card_id, amount, txn_date, merchant_name, city) VALUES (%s,%s,%s,%s,%s)", batch)
    conn.commit()
print(f"🛒 Inserted {TOTAL} card transactions.")

# 10) ATM Locations
atm_rows = [
    (random.randint(1, TOTAL), fake.street_address(), random.choice(cities), random.choice(["Active","Inactive"]))
    for _ in range(TOTAL)
]
for batch in chunks(atm_rows, BATCH):
    cur.executemany("INSERT INTO atm_locations (branch_id, location, city, status) VALUES (%s,%s,%s,%s)", batch)
    conn.commit()
print(f"🏧 Inserted {TOTAL} ATM locations.")

# Re-enable FK checks
cur.execute("SET FOREIGN_KEY_CHECKS=1")
conn.commit()

cur.close()
conn.close()
print("\n✅ All tables populated with 50,000 rows each.")
