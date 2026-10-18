from pathlib import Path
import pandas as pd
import sqlite3

# Find the folder containing this Python file
folder = Path(__file__).resolve().parent

# CSV dataset path
file_name = folder / "SQL_Sales_Dataset_200_Rows.csv"

print("=" * 60)
print("Week 2 SQL: Database Setup & Dataset Import")
print("=" * 60)
print("Looking for dataset at:", file_name)
print("File exists:", file_name.exists())

if file_name.exists():
    # Read the CSV dataset
    df = pd.read_csv(file_name)

    print("\nDataset loaded successfully!")
    print(f"Total Rows: {len(df)}")
    print(f"Columns ({len(df.columns)}): {df.columns.tolist()}")

    # Display sample rows
    print("\nSample Preview (First 3 rows):")
    print(df.head(3).to_string())

    # Create / Connect to SQLite database
    db_path = folder / "sales.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    # -------------------------------------------------------------
    # 1. Main table: sales (all raw records)
    # -------------------------------------------------------------
    df.to_sql("sales", conn, if_exists="replace", index=False)
    print("\n[OK] Table 'sales' created with 200 records.")

    # -------------------------------------------------------------
    # 2. Normalized Relational Schema for JOIN Demonstrations
    # -------------------------------------------------------------
    # Assign unique IDs for normalization
    df["customer_id"] = range(1, len(df) + 1)
    df["product_id"] = range(1, len(df) + 1)

    # Customers table
    customers_df = df[["customer_id", "customer_name", "region"]].copy()
    customers_df.to_sql("customers", conn, if_exists="replace", index=False)
    print("[OK] Table 'customers' created with 200 records.")

    # Products table
    products_df = df[["product_id", "product_name", "category", "sub_category", "unit_price"]].copy()
    products_df.to_sql("products", conn, if_exists="replace", index=False)
    print("[OK] Table 'products' created with 200 records.")

    # Orders table
    orders_df = df[["order_id", "customer_id", "product_id", "order_date", "quantity", "total_price"]].copy()
    orders_df.to_sql("orders", conn, if_exists="replace", index=False)
    print("[OK] Table 'orders' created with 200 records.")

    # -------------------------------------------------------------
    # 3. Lookup / Business Targets Table (for JOIN & KPI Analysis)
    # -------------------------------------------------------------
    regional_targets = [
        ("South", 750000.0, "David Miller"),
        ("East", 600000.0, "Sarah Johnson"),
        ("West", 550000.0, "Michael Brown"),
        ("North", 450000.0, "Emily Wilson")
    ]
    cursor.execute("DROP TABLE IF EXISTS regional_targets;")
    cursor.execute("""
        CREATE TABLE regional_targets (
            region TEXT PRIMARY KEY,
            target_revenue REAL NOT NULL,
            regional_manager TEXT NOT NULL
        );
    """)
    cursor.executemany("""
        INSERT INTO regional_targets (region, target_revenue, regional_manager)
        VALUES (?, ?, ?);
    """, regional_targets)
    conn.commit()
    print("[OK] Table 'regional_targets' created with 4 regional benchmarks.")

    # -------------------------------------------------------------
    # Summary of Tables in sales.db
    # -------------------------------------------------------------
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    print("\nDatabase Schema Summary ('sales.db'):")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t[0]};")
        count = cursor.fetchone()[0]
        print(f"  - Table '{t[0]}': {count} rows")

    conn.close()
    print("\nDatabase setup complete! 'sales.db' is ready for all SQL queries.")
    print("=" * 60)

else:
    print("\nError: CSV file not found. Ensure 'SQL_Sales_Dataset_200_Rows.csv' is in Week2_SQL folder.")