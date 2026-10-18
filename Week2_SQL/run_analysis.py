"""
SkillNexis Internship - Week 2: SQL Query Execution Runner
This script connects to sales.db, executes all SQL queries, and prints formatted outputs.
Can be run directly in VS Code by clicking 'Run Python File' or running `python run_analysis.py`.
"""

from pathlib import Path
import sqlite3
import pandas as pd

# Set display options for clean terminal output
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)
pd.set_option("display.colheader_justify", "left")

# Locate sales.db in current script directory
current_dir = Path(__file__).resolve().parent
db_path = current_dir / "sales.db"

if not db_path.exists():
    print(f"Error: Database not found at {db_path}.")
    print("Please run `python import_dataset.py` first to initialize the database.")
    exit(1)

conn = sqlite3.connect(db_path)

# Query suite matching analysis.sql
queries = [
    # -------------------------------------------------------------
    # PART 1: BASIC QUERIES
    # -------------------------------------------------------------
    (
        "Query 1.1: First 10 Sales Records (SELECT, LIMIT)",
        """
        SELECT order_id, customer_name, order_date, category, product_name, quantity, unit_price, total_price, region
        FROM sales
        LIMIT 10;
        """
    ),
    (
        "Query 1.2: Filter Sales in West Region (WHERE)",
        """
        SELECT order_id, customer_name, product_name, total_price, region
        FROM sales
        WHERE region = 'West'
        LIMIT 10;
        """
    ),
    (
        "Query 1.3: Filter Multiple Conditions (Electronics with Quantity >= 5)",
        """
        SELECT order_id, customer_name, category, product_name, quantity, total_price
        FROM sales
        WHERE category = 'Electronics' AND quantity >= 5;
        """
    ),
    (
        "Query 1.4: Sales Ordered by Total Price (ORDER BY DESC)",
        """
        SELECT order_id, customer_name, category, total_price
        FROM sales
        ORDER BY total_price DESC
        LIMIT 10;
        """
    ),

    # -------------------------------------------------------------
    # PART 2: AGGREGATE FUNCTIONS
    # -------------------------------------------------------------
    (
        "Query 2.1: Key Sales Metrics (COUNT, SUM, AVG, MIN, MAX)",
        """
        SELECT 
            COUNT(*) AS total_orders,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS average_order_value,
            MIN(total_price) AS minimum_order_value,
            MAX(total_price) AS maximum_order_value
        FROM sales;
        """
    ),
    (
        "Query 2.2: Total Units Sold and Unique Counts",
        """
        SELECT 
            SUM(quantity) AS total_units_sold,
            COUNT(DISTINCT customer_name) AS unique_customers,
            COUNT(DISTINCT category) AS unique_categories
        FROM sales;
        """
    ),

    # -------------------------------------------------------------
    # PART 3: GROUPING & FILTERING
    # -------------------------------------------------------------
    (
        "Query 3.1: Revenue and Volume by Product Category (GROUP BY)",
        """
        SELECT 
            category,
            COUNT(*) AS total_orders,
            SUM(quantity) AS total_units_sold,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS avg_order_value
        FROM sales
        GROUP BY category
        ORDER BY total_revenue DESC;
        """
    ),
    (
        "Query 3.2: Sales Distribution by Geographic Region (GROUP BY)",
        """
        SELECT 
            region,
            COUNT(*) AS total_orders,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS average_order_value
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC;
        """
    ),
    (
        "Query 3.3: High Revenue Categories with HAVING (Revenue > 500k)",
        """
        SELECT 
            category,
            COUNT(*) AS order_count,
            SUM(total_price) AS total_revenue
        FROM sales
        GROUP BY category
        HAVING SUM(total_price) > 500000
        ORDER BY total_revenue DESC;
        """
    ),

    # -------------------------------------------------------------
    # PART 4: RELATIONAL JOINS
    # -------------------------------------------------------------
    (
        "Query 4.1: INNER JOIN between Orders and Customers",
        """
        SELECT 
            o.order_id,
            c.customer_name,
            c.region,
            o.order_date,
            o.total_price
        FROM orders o
        INNER JOIN customers c 
            ON o.customer_id = c.customer_id
        ORDER BY o.total_price DESC
        LIMIT 10;
        """
    ),
    (
        "Query 4.2: Multi-Table INNER JOIN (Orders + Customers + Products)",
        """
        SELECT 
            o.order_id,
            c.customer_name,
            c.region,
            p.category,
            p.product_name,
            o.quantity,
            p.unit_price,
            o.total_price
        FROM orders o
        INNER JOIN customers c 
            ON o.customer_id = c.customer_id
        INNER JOIN products p 
            ON o.product_id = p.product_id
        ORDER BY o.order_id ASC
        LIMIT 10;
        """
    ),
    (
        "Query 4.3: LEFT JOIN Regional Targets vs Actual Revenue & Variance",
        """
        SELECT 
            t.region,
            t.regional_manager,
            t.target_revenue,
            COALESCE(SUM(s.total_price), 0) AS actual_revenue,
            ROUND(COALESCE(SUM(s.total_price), 0) - t.target_revenue, 2) AS revenue_variance,
            CASE 
                WHEN COALESCE(SUM(s.total_price), 0) >= t.target_revenue THEN 'Target Achieved'
                ELSE 'Target Not Achieved'
            END AS performance_status
        FROM regional_targets t
        LEFT JOIN sales s 
            ON t.region = s.region
        GROUP BY t.region, t.regional_manager, t.target_revenue
        ORDER BY actual_revenue DESC;
        """
    ),

    # -------------------------------------------------------------
    # PART 5: SUBQUERIES
    # -------------------------------------------------------------
    (
        "Query 5.1: Scalar Subquery - Orders Above Overall Average",
        """
        SELECT 
            order_id,
            customer_name,
            category,
            total_price
        FROM sales
        WHERE total_price > (
            SELECT AVG(total_price) 
            FROM sales
        )
        ORDER BY total_price DESC
        LIMIT 10;
        """
    ),
    (
        "Query 5.2: Multi-Row Subquery with IN (Regions with AOV > 12,000)",
        """
        SELECT 
            order_id,
            customer_name,
            region,
            total_price
        FROM sales
        WHERE region IN (
            SELECT region
            FROM sales
            GROUP BY region
            HAVING AVG(total_price) > 12000
        )
        ORDER BY total_price DESC
        LIMIT 10;
        """
    ),
    (
        "Query 5.3: Derived Table Subquery (Difference from Category Average)",
        """
        SELECT 
            s.order_id,
            s.customer_name,
            s.category,
            s.total_price,
            ROUND(cat_stats.category_avg, 2) AS category_avg_price,
            ROUND(s.total_price - cat_stats.category_avg, 2) AS diff_from_category_avg
        FROM sales s
        INNER JOIN (
            SELECT 
                category,
                AVG(total_price) AS category_avg
            FROM sales
            GROUP BY category
        ) cat_stats 
            ON s.category = cat_stats.category
        ORDER BY diff_from_category_avg DESC
        LIMIT 10;
        """
    ),

    # -------------------------------------------------------------
    # PART 6: CASE STATEMENTS
    # -------------------------------------------------------------
    (
        "Query 6.1: Order Value Segmentation with CASE",
        """
        SELECT 
            order_id,
            customer_name,
            category,
            total_price,
            CASE 
                WHEN total_price >= 20000 THEN 'High Value (>= 20k)'
                WHEN total_price >= 10000 THEN 'Medium Value (10k-20k)'
                ELSE 'Low Value (< 10k)'
            END AS order_value_tier
        FROM sales
        ORDER BY total_price DESC
        LIMIT 10;
        """
    ),
    (
        "Query 6.2: Purchase Size Segmentation by Quantity",
        """
        SELECT 
            order_id,
            customer_name,
            product_name,
            quantity,
            CASE 
                WHEN quantity >= 8 THEN 'Bulk Purchase'
                WHEN quantity >= 4 THEN 'Standard Purchase'
                ELSE 'Small Purchase'
            END AS purchase_size
        FROM sales
        ORDER BY quantity DESC
        LIMIT 10;
        """
    ),
    (
        "Query 6.3: Conditional Aggregation (Category Breakdown by Region)",
        """
        SELECT 
            region,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN category = 'Electronics' THEN total_price ELSE 0 END) AS electronics_revenue,
            SUM(CASE WHEN category = 'Furniture' THEN total_price ELSE 0 END) AS furniture_revenue,
            SUM(CASE WHEN category = 'Grocery' THEN total_price ELSE 0 END) AS grocery_revenue,
            SUM(CASE WHEN category = 'Clothing' THEN total_price ELSE 0 END) AS clothing_revenue,
            SUM(total_price) AS total_regional_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_regional_revenue DESC;
        """
    ),

    # -------------------------------------------------------------
    # PART 7: ASSIGNMENTS
    # -------------------------------------------------------------
    (
        "Assignment 1.1: Top 10 Customers by Total Spending",
        """
        SELECT 
            customer_name,
            region,
            COUNT(*) AS number_of_orders,
            SUM(quantity) AS total_units_purchased,
            SUM(total_price) AS total_spending,
            ROUND(AVG(total_price), 2) AS average_order_value
        FROM sales
        GROUP BY customer_name, region
        ORDER BY total_spending DESC
        LIMIT 10;
        """
    ),
    (
        "Assignment 1.2: Top Customer per Geographic Region",
        """
        SELECT 
            s1.region,
            s1.customer_name,
            s1.total_price AS highest_single_order_value
        FROM sales s1
        WHERE s1.total_price = (
            SELECT MAX(s2.total_price)
            FROM sales s2
            WHERE s2.region = s1.region
        )
        ORDER BY s1.total_price DESC;
        """
    ),
    (
        "Assignment 2.1: Overall Store Average Order Value (AOV)",
        """
        SELECT 
            COUNT(*) AS total_orders,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS overall_average_order_value
        FROM sales;
        """
    ),
    (
        "Assignment 2.2: Average Order Value (AOV) by Product Category",
        """
        SELECT 
            category,
            COUNT(*) AS orders_count,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS average_order_value
        FROM sales
        GROUP BY category
        ORDER BY average_order_value DESC;
        """
    ),
    (
        "Assignment 2.3: Average Order Value (AOV) by Geographic Region",
        """
        SELECT 
            region,
            COUNT(*) AS orders_count,
            SUM(total_price) AS total_revenue,
            ROUND(AVG(total_price), 2) AS average_order_value
        FROM sales
        GROUP BY region
        ORDER BY average_order_value DESC;
        """
    ),
    (
        "Assignment 2.4: Orders Exceeding Average Order Value with Comparison",
        """
        SELECT 
            order_id,
            customer_name,
            category,
            total_price,
            ROUND((SELECT AVG(total_price) FROM sales), 2) AS overall_avg,
            ROUND(total_price - (SELECT AVG(total_price) FROM sales), 2) AS amount_above_avg,
            ROUND(((total_price - (SELECT AVG(total_price) FROM sales)) / (SELECT AVG(total_price) FROM sales)) * 100, 2) AS pct_above_avg
        FROM sales
        WHERE total_price > (SELECT AVG(total_price) FROM sales)
        ORDER BY total_price DESC
        LIMIT 10;
        """
    )
]

print("\n" + "=" * 80)
print(" SKILLNEXIS INTERNSHIP - WEEK 2 SQL QUERY EXECUTION")
print("=" * 80)

success_count = 0
failed_count = 0

for title, sql in queries:
    print("\n" + "-" * 80)
    print(f">> {title}")
    print("-" * 80)
    try:
        df_result = pd.read_sql_query(sql, conn)
        print(df_result.to_string(index=False))
        success_count += 1
    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        failed_count += 1

conn.close()

print("\n" + "=" * 80)
print(f" EXECUTION SUMMARY: {success_count} Passed | {failed_count} Failed")
print("=" * 80 + "\n")
