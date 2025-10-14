from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  # 🔁 Replace with your password
    database="bank_demo"       # 🔁 Make sure this DB exists
)

cursor = conn.cursor()

# ---------- STEP 1: Create Tables ----------
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

conn.commit()


# ---------- STEP 2: Insert Customers ----------
def insert_customers(n=10000):
    customer_ids = []
    for _ in range(n):
        name = fake.name()
        email = fake.email()
        created_at = fake.date_time_between(start_date='-5y', end_date='now')
        cursor.execute("INSERT INTO customers (name, email, created_at) VALUES (%s, %s, %s)",
                       (name, email, created_at))
        customer_ids.append(cursor.lastrowid)
    conn.commit()
    return customer_ids


# ---------- STEP 3: Insert Accounts ----------
def insert_accounts(customer_ids):
    account_ids = []
    for cust_id in customer_ids:
        num_accounts = random.randint(1, 2)
        for _ in range(num_accounts):
            account_type = random.choice(['SAVINGS', 'CHECKING'])
            balance = round(random.uniform(100, 10000), 2)
            opened_at = fake.date_time_between(start_date='-5y', end_date='now')
            cursor.execute("INSERT INTO accounts (customer_id, account_type, balance, opened_at) VALUES (%s, %s, %s, %s)",
                           (cust_id, account_type, balance, opened_at))
            account_ids.append(cursor.lastrowid)
    conn.commit()
    return account_ids


# ---------- STEP 4: Insert Transactions ----------
def insert_transactions(account_ids):
    for acc_id in account_ids:
        for _ in range(random.randint(5, 20)):
            amount = round(random.uniform(10, 5000), 2)
            txn_type = random.choice(['DEPOSIT', 'WITHDRAWAL', 'TRANSFER'])
            txn_date = fake.date_time_between(start_date='-3y', end_date='now')
            cursor.execute("INSERT INTO transactions (account_id, amount, transaction_type, transaction_date) VALUES (%s, %s, %s, %s)",
                           (acc_id, amount, txn_type, txn_date))
    conn.commit()


# ---------- RUN ----------
print("Inserting customers...")
customer_ids = insert_customers(10000)  # 💡 You can increase this to 5000 or 10000

print("Inserting accounts...")
account_ids = insert_accounts(customer_ids)

print("Inserting transactions...")
insert_transactions(account_ids)

print("✅ All done! Check your MySQL database.")

# Clean up
cursor.close()
conn.close()
