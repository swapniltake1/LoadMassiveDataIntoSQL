import mysql.connector
from faker import Faker
import random
from tqdm import tqdm

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # Replace with your MySQL root password
    "database": "BankOf420"
}

# Initialize Faker for Indian data
fake = Faker("en_IN")

# Connect to MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

# Drop tables if they exist (for clean reruns)
tables = [
    "card_transactions", "cards", "loan_payments", "loans", "transactions",
    "accounts", "customers", "employees", "atm_locations", "branches"
]
for tbl in tables:
    cur.execute(f"DROP TABLE IF EXISTS {tbl}")

# === TABLE CREATION ===
cur.execute("""
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100),
    branch_code VARCHAR(20),
    city VARCHAR(50),
    ifsc_code VARCHAR(20)
)
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
)
""")

cur.execute("""
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100),
    dob DATE,
    gender VARCHAR(10),
    city VARCHAR(50),
    contact_no VARCHAR(15),
    email VARCHAR(100)
)
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
)
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
)
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
)
""")

cur.execute("""
CREATE TABLE loan_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    payment_date DATE,
    payment_amount DECIMAL(12,2),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
)
""")

cur.execute("""
CREATE TABLE cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    card_type VARCHAR(20),
    card_number VARCHAR(20),
    expiry_date DATE,
    cvv VARCHAR(4),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
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
)
""")

cur.execute("""
CREATE TABLE atm_locations (
    atm_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT,
    location VARCHAR(100),
    city VARCHAR(50),
    status VARCHAR(20),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
)
""")

print("✅ Tables created successfully.")

# === INSERT SAMPLE DATA ===
cities = [
    "Pune", "Mumbai", "Nagpur", "Nashik", "Aurangabad",
    "Kolhapur", "Solapur", "Thane", "Ahmednagar", "Satara"
]

# Branches
for i in range(100):
    city = random.choice(cities)
    cur.execute(
        "INSERT INTO branches (branch_name, branch_code, city, ifsc_code) VALUES (%s,%s,%s,%s)",
        (f"{city} Branch {i+1}", f"BR{i+1:03d}", city, f"MAHB000{i+1:03d}")
    )
conn.commit()
print("🏦 Inserted 50 branches.")

# Employees
for i in range(500):
    cur.execute(
        "INSERT INTO employees (emp_name, designation, branch_id, salary, doj) VALUES (%s,%s,%s,%s,%s)",
        (fake.name(), random.choice(["Manager", "Clerk", "Cashier", "Officer"]),
         random.randint(1, 50), random.randint(30000, 90000), fake.date_between(start_date="-5y", end_date="today"))
    )
conn.commit()
print("👨‍💼 Inserted 500 employees.")

# Customers
for i in tqdm(range(500000), desc="Inserting customers"):
    cur.execute(
        "INSERT INTO customers (full_name, dob, gender, city, contact_no, email) VALUES (%s,%s,%s,%s,%s,%s)",
        (
            fake.name(),
            fake.date_of_birth(minimum_age=18, maximum_age=75),
            random.choice(["Male", "Female"]),
            random.choice(cities),
            fake.phone_number(),
            fake.email()
        )
    )
    if i % 1000 == 0:
        conn.commit()
conn.commit()
print("👥 Inserted 50,0000 customers.")

# Accounts
for i in tqdm(range(500000), desc="Creating accounts"):
    cur.execute(
        "INSERT INTO accounts (customer_id, branch_id, account_type, balance, opening_date) VALUES (%s,%s,%s,%s,%s)",
        (
            i + 1,
            random.randint(1, 50),
            random.choice(["Saving", "Current"]),
            random.randint(1000, 100000),
            fake.date_between(start_date="-5y", end_date="today")
        )
    )
    if i % 1000 == 0:
        conn.commit()
conn.commit()
print("💰 Inserted 50,0000 accounts.")

# Transactions
for i in tqdm(range(1000000), desc="Creating transactions"):
    cur.execute(
        "INSERT INTO transactions (account_id, txn_type, amount, txn_date, description) VALUES (%s,%s,%s,%s,%s)",
        (
            random.randint(1, 500000),
            random.choice(["Credit", "Debit"]),
            random.randint(100, 50000),
            fake.date_time_between(start_date="-2y", end_date="now"),
            fake.sentence(nb_words=6)
        )
    )
    if i % 2000 == 0:
        conn.commit()
conn.commit()
print("💳 Inserted 100,0000 transactions.")

# Loans
for i in tqdm(range(5000), desc="Creating loans"):
    cur.execute(
        "INSERT INTO loans (customer_id, branch_id, loan_type, loan_amount, interest_rate, start_date) VALUES (%s,%s,%s,%s,%s,%s)",
        (
            random.randint(1, 50000),
            random.randint(1, 50),
            random.choice(["Home Loan", "Personal Loan", "Car Loan", "Education Loan"]),
            random.randint(100000, 2000000),
            random.uniform(6.5, 12.5),
            fake.date_between(start_date="-5y", end_date="today")
        )
    )
conn.commit()
print("🏠 Inserted 5,000 loans.")

# Loan Payments
for i in tqdm(range(20000), desc="Creating loan payments"):
    cur.execute(
        "INSERT INTO loan_payments (loan_id, payment_date, payment_amount) VALUES (%s,%s,%s)",
        (
            random.randint(1, 5000),
            fake.date_between(start_date="-3y", end_date="today"),
            random.randint(2000, 50000)
        )
    )
conn.commit()

# Cards
for i in tqdm(range(100000), desc="Creating cards"):
    cur.execute(
        "INSERT INTO cards (customer_id, card_type, card_number, expiry_date, cvv) VALUES (%s,%s,%s,%s,%s)",
        (
            random.randint(1, 500000),
            random.choice(["Debit", "Credit"]),
            fake.credit_card_number(card_type=None),
            fake.date_between(start_date="today", end_date="+5y"),
            str(random.randint(100, 999))
        )
    )
conn.commit()

# Card Transactions
for i in tqdm(range(50000), desc="Creating card transactions"):
    cur.execute(
        "INSERT INTO card_transactions (card_id, amount, txn_date, merchant_name, city) VALUES (%s,%s,%s,%s,%s)",
        (
            random.randint(1, 10000),
            random.randint(100, 10000),
            fake.date_time_between(start_date="-2y", end_date="now"),
            fake.company(),
            random.choice(cities)
        )
    )
    if i % 2000 == 0:
        conn.commit()
conn.commit()

# ATM Locations
for i in range(100):
    cur.execute(
        "INSERT INTO atm_locations (branch_id, location, city, status) VALUES (%s,%s,%s,%s)",
        (
            random.randint(1, 50),
            fake.street_address(),
            random.choice(cities),
            random.choice(["Active", "Inactive"])
        )
    )
conn.commit()
print("🏧 Inserted 100 ATM locations.")

print("\n✅ All tables populated successfully with realistic Maharashtra-based banking data!")

cur.close()
conn.close()
