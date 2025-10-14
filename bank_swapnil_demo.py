from faker import Faker
import mysql.connector
import random
from datetime import datetime

fake = Faker('en_IN')  # Indian locale

# --- Database connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  
)
cursor = conn.cursor()

# --- Step 1: Create Database ---
cursor.execute("DROP DATABASE IF EXISTS bank_of_swapnil")
cursor.execute("CREATE DATABASE bank_of_swapnil")
cursor.execute("USE bank_of_swapnil")

# --- Step 2: Create Tables ---
cursor.execute("""
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    address TEXT,
    phone_number VARCHAR(20),
    id_number VARCHAR(20),
    created_at DATETIME
)
""")

cursor.execute("""
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_number VARCHAR(20) UNIQUE,
    account_type ENUM('SAVINGS', 'CHECKING'),
    balance DECIMAL(12,2),
    opened_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

cursor.execute("""
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
    amount DECIMAL(10,2),
    transaction_type ENUM('DEPOSIT', 'WITHDRAWAL', 'TRANSFER'),
    transaction_date DATETIME,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
)
""")

conn.commit()

# --- Step 3: Insert Data ---
def generate_customers(n):
    customer_ids = []
    for _ in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        address = fake.address().replace("\n", ", ")
        phone = fake.phone_number()
        id_number = fake.random_int(min=100000000000, max=999999999999)
        created_at = fake.date_time_between(start_date='-5y', end_date='now')

        cursor.execute("""
        INSERT INTO customers (first_name, last_name, address, phone_number, id_number, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, address, phone, str(id_number), created_at))
        customer_ids.append(cursor.lastrowid)
    conn.commit()
    return customer_ids


def generate_accounts(customer_ids):
    account_ids = []
    for cid in customer_ids:
        num_accounts = random.randint(1, 2)
        for _ in range(num_accounts):
            account_number = str(fake.random_number(digits=12, fix_len=True))
            account_type = random.choice(['SAVINGS', 'CHECKING'])
            balance = round(random.uniform(1000.00, 100000.00), 2)
            opened_at = fake.date_time_between(start_date='-5y', end_date='now')

            cursor.execute("""
            INSERT INTO accounts (customer_id, account_number, account_type, balance, opened_at)
            VALUES (%s, %s, %s, %s, %s)
            """, (cid, account_number, account_type, balance, opened_at))
            account_ids.append(cursor.lastrowid)
    conn.commit()
    return account_ids


def generate_transactions(account_ids):
    for acc_id in account_ids:
        num_txns = random.randint(5, 15)
        for _ in range(num_txns):
            amount = round(random.uniform(100.00, 50000.00), 2)
            txn_type = random.choice(['DEPOSIT', 'WITHDRAWAL', 'TRANSFER'])
            txn_date = fake.date_time_between(start_date='-3y', end_date='now')

            cursor.execute("""
            INSERT INTO transactions (account_id, amount, transaction_type, transaction_date)
            VALUES (%s, %s, %s, %s)
            """, (acc_id, amount, txn_type, txn_date))
    conn.commit()


# --- Step 4: Run All ---
print("📥 Inserting customers...")
customer_ids = generate_customers(500)

print("🏦 Inserting accounts...")
account_ids = generate_accounts(customer_ids)

print("💸 Inserting transactions...")
generate_transactions(account_ids)

# --- Done ---
cursor.close()
conn.close()
print("✅ Demo DB 'bank_of_swapnil' created with mock data!")
