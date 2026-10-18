-- ============================================================================
-- SkillNexis Internship - Week 2: SQL Mastery & Sales Database Analysis
-- ============================================================================
-- Topics Covered:
--   1. Basic queries: SELECT, WHERE, ORDER BY, LIMIT
--   2. Aggregations: SUM, AVG, COUNT, MIN, MAX
--   3. Grouping & Filtering: GROUP BY, HAVING
--   4. Relational Joins: INNER JOIN, LEFT JOIN, Multi-Table Joins
--   5. Subqueries: Scalar, WHERE IN, and Derived Table Subqueries
--   6. CASE Statements: Categorization and Conditional Aggregation
--   7. Assignments:
--      - Find Top Customers by Total Spending & Volume
--      - Calculate Average Order Values (Overall, Category, Region)
-- ============================================================================


-- ============================================================================
-- PART 1: BASIC QUERIES (SELECT, WHERE, ORDER BY, LIMIT)
-- ============================================================================

-- Query 1.1: Retrieve the first 10 sales records to inspect data structure
SELECT 
    order_id, 
    customer_name, 
    order_date, 
    category, 
    product_name, 
    quantity, 
    unit_price, 
    total_price, 
    region
FROM sales
LIMIT 10;


-- Query 1.2: Filter sales records for a specific region (West)
SELECT 
    order_id, 
    customer_name, 
    product_name, 
    total_price, 
    region
FROM sales
WHERE region = 'West';


-- Query 1.3: Filter sales records with multiple conditions (Electronics with Quantity >= 5)
SELECT 
    order_id, 
    customer_name, 
    category, 
    product_name, 
    quantity, 
    total_price
FROM sales
WHERE category = 'Electronics' 
  AND quantity >= 5;


-- Query 1.4: Sort sales orders from highest total price to lowest
SELECT 
    order_id, 
    customer_name, 
    category, 
    total_price
FROM sales
ORDER BY total_price DESC;


-- ============================================================================
-- PART 2: AGGREGATE FUNCTIONS (SUM, AVG, COUNT, MIN, MAX)
-- ============================================================================

-- Query 2.1: Key summary metrics across all sales orders
SELECT 
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS average_order_value,
    MIN(total_price) AS minimum_order_value,
    MAX(total_price) AS maximum_order_value
FROM sales;


-- Query 2.2: Total volume of units sold and distinct customer count
SELECT 
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT customer_name) AS unique_customers,
    COUNT(DISTINCT category) AS unique_categories
FROM sales;


-- ============================================================================
-- PART 3: GROUPING & FILTERING (GROUP BY, HAVING)
-- ============================================================================

-- Query 3.1: Revenue and order volume summarized by product category
SELECT 
    category,
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_units_sold,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS avg_order_value
FROM sales
GROUP BY category
ORDER BY total_revenue DESC;


-- Query 3.2: Sales distribution by geographic region
SELECT 
    region,
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS average_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;


-- Query 3.3: Filter aggregated groups using HAVING (Categories with revenue > 500,000)
SELECT 
    category,
    COUNT(*) AS order_count,
    SUM(total_price) AS total_revenue
FROM sales
GROUP BY category
HAVING SUM(total_price) > 500000
ORDER BY total_revenue DESC;


-- ============================================================================
-- PART 4: RELATIONAL JOINS (INNER JOIN, LEFT JOIN, MULTI-TABLE JOINS)
-- ============================================================================

-- Query 4.1: INNER JOIN between Orders and Customers
-- Demonstrates linking transactions to customer demographic details
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


-- Query 4.2: Multi-Table INNER JOIN (Orders + Customers + Products)
-- Combines transactional, customer, and product catalog data into a complete invoice view
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


-- Query 4.3: LEFT JOIN between Regional Targets and Actual Sales
-- Compares benchmark corporate revenue targets against actual achieved revenue per region
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


-- ============================================================================
-- PART 5: SUBQUERIES (SCALAR, WHERE IN, AND DERIVED TABLES)
-- ============================================================================

-- Query 5.1: Scalar Subquery - Find orders with total price higher than overall average
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
ORDER BY total_price DESC;


-- Query 5.2: Multi-Row Subquery with IN
-- Find all orders placed in regions where the average order value exceeds 12,000
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


-- Query 5.3: Derived Table Subquery (Subquery in FROM clause)
-- Calculate how much each order deviates from its specific category's average order value
SELECT 
    s.order_id,
    s.customer_name,
    s.category,
    s.total_price,
    ROUND(cat_stats.category_avg, 2) AS category_avg_price,
    ROUND(s.total_price - cat_stats.category_avg, 2) AS difference_from_category_avg
FROM sales s
INNER JOIN (
    SELECT 
        category,
        AVG(total_price) AS category_avg
    FROM sales
    GROUP BY category
) cat_stats 
    ON s.category = cat_stats.category
ORDER BY difference_from_category_avg DESC
LIMIT 10;


-- ============================================================================
-- PART 6: CASE STATEMENTS (CONDITIONAL LOGIC & SEGMENTATION)
-- ============================================================================

-- Query 6.1: Order Value Segmentation using CASE
-- Classify each transaction into High Value, Medium Value, or Low Value tier
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
LIMIT 15;


-- Query 6.2: Purchase Size Segmentation based on Item Quantity
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
LIMIT 15;


-- Query 6.3: Conditional Aggregation (Pivot-style breakdown of category revenue per region)
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


-- ============================================================================
-- PART 7: ASSIGNMENTS (TOP CUSTOMERS & AVERAGE ORDER VALUES)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Assignment 1: Top Customers Analysis
-- ----------------------------------------------------------------------------

-- Query 7.1: Top 10 Customers ranked by total spending
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


-- Query 7.2: Top Customer per Geographic Region
-- Uses a correlated subquery to identify the highest spending customer in each region
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


-- ----------------------------------------------------------------------------
-- Assignment 2: Average Order Value (AOV) Analysis
-- ----------------------------------------------------------------------------

-- Query 7.3: Overall Store Average Order Value (AOV)
SELECT 
    COUNT(*) AS total_orders,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS overall_average_order_value
FROM sales;


-- Query 7.4: Average Order Value (AOV) by Product Category
SELECT 
    category,
    COUNT(*) AS orders_count,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS average_order_value
FROM sales
GROUP BY category
ORDER BY average_order_value DESC;


-- Query 7.5: Average Order Value (AOV) by Geographic Region
SELECT 
    region,
    COUNT(*) AS orders_count,
    SUM(total_price) AS total_revenue,
    ROUND(AVG(total_price), 2) AS average_order_value
FROM sales
GROUP BY region
ORDER BY average_order_value DESC;


-- Query 7.6: Orders Exceeding Average Order Value with Percentage Difference
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