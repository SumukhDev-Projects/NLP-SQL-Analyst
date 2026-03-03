"""
Seed the local SQLite database with realistic sample data.
Schema: customers, products, orders, order_items, sales_reps

Run: python scripts/seed_db.py
"""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "backend" / "data" / "analyst.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CATEGORIES = {
    "Electronics":   ["Laptop", "Monitor", "Keyboard", "Mouse", "Webcam", "Headphones", "Tablet", "SSD"],
    "Software":      ["CRM License", "Analytics Suite", "Security Package", "Collaboration Tool", "ERP Module"],
    "Office":        ["Desk Chair", "Standing Desk", "Whiteboard", "Filing Cabinet", "Printer"],
    "Services":      ["Onboarding", "Training", "Consulting", "Support Contract", "Integration"],
}

SEGMENTS = ["Enterprise", "Mid-Market", "SMB", "Startup"]
CITIES = [
    ("New York", "NY", "USA"), ("Los Angeles", "CA", "USA"), ("Chicago", "IL", "USA"),
    ("Houston", "TX", "USA"), ("Phoenix", "AZ", "USA"), ("Philadelphia", "PA", "USA"),
    ("San Antonio", "TX", "USA"), ("San Diego", "CA", "USA"), ("Dallas", "TX", "USA"),
    ("San Jose", "CA", "USA"), ("Austin", "TX", "USA"), ("Seattle", "WA", "USA"),
    ("Denver", "CO", "USA"), ("Boston", "MA", "USA"), ("Nashville", "TN", "USA"),
    ("Toronto", "ON", "Canada"), ("London", None, "UK"), ("Berlin", None, "Germany"),
    ("Paris", None, "France"), ("Sydney", None, "Australia"),
]

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "International"]
STATUSES = ["completed", "completed", "completed", "completed", "pending", "refunded", "cancelled"]

FIRST_NAMES = ["James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","William",
               "Barbara","David","Elizabeth","Richard","Susan","Joseph","Jessica","Thomas","Sarah",
               "Charles","Karen","Christopher","Lisa","Daniel","Nancy","Matthew","Betty","Anthony",
               "Margaret","Mark","Sandra","Donald","Ashley","Steven","Dorothy","Paul","Kimberly",
               "Andrew","Emily","Kenneth","Donna","Joshua","Michelle","Kevin","Carol","Brian","Amanda"]

LAST_NAMES = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez",
              "Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor",
              "Moore","Jackson","Martin","Lee","Perez","Thompson","White","Harris","Sanchez",
              "Clark","Ramirez","Lewis","Robinson","Walker","Young","Allen","King","Wright","Scott",
              "Torres","Nguyen","Hill","Flores","Green","Adams","Nelson","Baker","Hall","Rivera"]

COMPANY_PREFIXES = ["Acme","Global","Tech","Digital","Cloud","Smart","Apex","Prime","Core","Next",
                    "Alpha","Beta","Sigma","Delta","Omega","Vertex","Nexus","Pinnacle","Summit","Elite"]
COMPANY_SUFFIXES = ["Corp","Inc","LLC","Group","Solutions","Systems","Technologies","Ventures",
                    "Partners","Consulting","Dynamics","Analytics","Labs","Works","Innovations"]

random.seed(42)

def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def rand_company():
    return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"

def rand_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Drop and recreate ────────────────────────────────────────────────────
    cur.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS sales_reps;
    """)

    # ── Tables ───────────────────────────────────────────────────────────────
    cur.executescript("""
        CREATE TABLE customers (
            customer_id   INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            company       TEXT,
            email         TEXT UNIQUE NOT NULL,
            city          TEXT,
            state         TEXT,
            country       TEXT DEFAULT 'USA',
            segment       TEXT,
            signup_date   TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id    INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            category      TEXT NOT NULL,
            subcategory   TEXT,
            unit_price    REAL NOT NULL,
            unit_cost     REAL NOT NULL
        );

        CREATE TABLE sales_reps (
            rep_id        INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            region        TEXT NOT NULL,
            annual_quota  REAL NOT NULL,
            hire_date     TEXT NOT NULL
        );

        CREATE TABLE orders (
            order_id      INTEGER PRIMARY KEY,
            customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
            rep_id        INTEGER REFERENCES sales_reps(rep_id),
            order_date    TEXT NOT NULL,
            status        TEXT NOT NULL DEFAULT 'completed',
            shipping_city TEXT,
            total_amount  REAL NOT NULL
        );

        CREATE TABLE order_items (
            item_id       INTEGER PRIMARY KEY,
            order_id      INTEGER NOT NULL REFERENCES orders(order_id),
            product_id    INTEGER NOT NULL REFERENCES products(product_id),
            quantity      INTEGER NOT NULL DEFAULT 1,
            unit_price    REAL NOT NULL,
            discount_pct  REAL NOT NULL DEFAULT 0.0,
            line_total    REAL NOT NULL
        );

        CREATE INDEX idx_orders_date    ON orders(order_date);
        CREATE INDEX idx_orders_cust    ON orders(customer_id);
        CREATE INDEX idx_items_order    ON order_items(order_id);
        CREATE INDEX idx_items_product  ON order_items(product_id);
    """)

    # ── Customers (500) ──────────────────────────────────────────────────────
    customers = []
    used_emails = set()
    for i in range(1, 501):
        name = rand_name()
        company = rand_company()
        email_base = f"{name.lower().replace(' ', '.')}.{i}@{company.lower().split()[0]}.com"
        email = email_base
        while email in used_emails:
            email = f"{email_base.split('@')[0]}{random.randint(1,99)}@{email_base.split('@')[1]}"
        used_emails.add(email)
        city, state, country = random.choice(CITIES)
        customers.append((
            i, name, company, email,
            city, state, country,
            random.choice(SEGMENTS),
            rand_date(2020, 2022).strftime("%Y-%m-%d"),
        ))
    cur.executemany(
        "INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?)", customers
    )

    # ── Products (60) ────────────────────────────────────────────────────────
    products = []
    pid = 1
    for category, items in CATEGORIES.items():
        for item in items:
            base_price = random.uniform(50, 3000)
            if category == "Services":
                base_price = random.uniform(500, 8000)
            unit_cost = round(base_price * random.uniform(0.35, 0.65), 2)
            unit_price = round(base_price, 2)
            products.append((pid, item, category, None, unit_price, unit_cost))
            pid += 1
    cur.executemany(
        "INSERT INTO products VALUES (?,?,?,?,?,?)", products
    )

    # ── Sales reps (20) ──────────────────────────────────────────────────────
    reps = []
    for i in range(1, 21):
        reps.append((
            i,
            rand_name(),
            random.choice(REGIONS),
            round(random.uniform(500_000, 2_000_000), 0),
            rand_date(2018, 2022).strftime("%Y-%m-%d"),
        ))
    cur.executemany(
        "INSERT INTO sales_reps VALUES (?,?,?,?,?)", reps
    )

    # ── Orders + items (3500) ────────────────────────────────────────────────
    order_id = 1
    item_id = 1

    for _ in range(3500):
        cust_id = random.randint(1, 500)
        rep_id = random.randint(1, 20)
        order_date = rand_date(2022, 2024)
        status = random.choice(STATUSES)
        city, _, _ = random.choice(CITIES)

        # Pick 1-4 items
        n_items = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
        selected = random.sample(products, n_items)

        total = 0.0
        items_to_insert = []
        for prod in selected:
            qty = random.choices([1, 2, 3, 5, 10], weights=[50, 25, 12, 8, 5])[0]
            discount = random.choices([0, 5, 10, 15, 20], weights=[55, 20, 12, 8, 5])[0] / 100
            unit_price = prod[4]
            line_total = round(qty * unit_price * (1 - discount), 2)
            total += line_total
            items_to_insert.append((item_id, order_id, prod[0], qty, unit_price, discount * 100, line_total))
            item_id += 1

        cur.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?,?,?)",
            (order_id, cust_id, rep_id, order_date.strftime("%Y-%m-%d"), status, city, round(total, 2))
        )
        cur.executemany(
            "INSERT INTO order_items VALUES (?,?,?,?,?,?,?)", items_to_insert
        )
        order_id += 1

    conn.commit()
    conn.close()

    # Verify
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    print("Database seeded successfully:")
    for table in ["customers", "products", "sales_reps", "orders", "order_items"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"  {table}: {cur.fetchone()[0]} rows")
    conn.close()
    print(f"\nDB location: {DB_PATH}")


if __name__ == "__main__":
    seed()
