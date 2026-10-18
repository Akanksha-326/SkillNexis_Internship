# SkillNexis Internship - Week 2: SQL Sales Analysis

Welcome to the **Week 2: SQL Mastery & Sales Database Analysis** project. This project implements SQL solutions covering fundamental to advanced SQL queries, multi-table joins, subqueries, conditional logic, and required business assignments.

---

## 📁 Folder Structure

```text
Week2_SQL/
├── SQL_Sales_Dataset_200_Rows.csv   # Raw dataset with 200 order transactions
├── sales.db                         # SQLite database with all tables populated
├── import_dataset.py                # Python setup script to import data into SQLite
├── analysis.sql                     # Complete SQL script containing all 24 queries
├── run_analysis.py                  # Python query execution runner for VS Code terminal
├── week2.ipynb                      # Interactive Jupyter Notebook with outputs
└── README.md                        # Documentation and assignment results
```

---

## 🎯 Syllabus & Topics Covered

| Category | Topics / Clauses | File Reference |
| :--- | :--- | :--- |
| **Basic Queries** | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT` | Part 1 (`analysis.sql` / `run_analysis.py`) |
| **Aggregations** | `SUM()`, `AVG()`, `COUNT()`, `MIN()`, `MAX()`, `DISTINCT` | Part 2 (`analysis.sql` / `run_analysis.py`) |
| **Grouping & Filtering** | `GROUP BY`, `HAVING` | Part 3 (`analysis.sql` / `run_analysis.py`) |
| **Relational Joins** | `INNER JOIN`, `LEFT JOIN`, Multi-Table Joins | Part 4 (`analysis.sql` / `run_analysis.py`) |
| **Subqueries** | Scalar Subquery, `WHERE IN`, Derived Table Subquery | Part 5 (`analysis.sql` / `run_analysis.py`) |
| **CASE Statements** | Value Tiering, Quantity Sizing, Conditional Aggregation | Part 6 (`analysis.sql` / `run_analysis.py`) |
| **Assignments** | Top Customers by Total Spending & Volume | Part 7.1 (`analysis.sql` / `run_analysis.py`) |
| **Assignments** | Average Order Value (AOV) (Overall, Category, Region) | Part 7.2 (`analysis.sql` / `run_analysis.py`) |

---

## 📊 Database Schema (`sales.db`)

1. **`sales`** (Raw 200 rows):
   - `order_id`, `customer_name`, `order_date`, `category`, `sub_category`, `product_name`, `quantity`, `unit_price`, `total_price`, `region`
2. **`customers`** (Normalized customer entity):
   - `customer_id` (PK), `customer_name`, `region`
3. **`products`** (Normalized product catalog):
   - `product_id` (PK), `product_name`, `category`, `sub_category`, `unit_price`
4. **`orders`** (Relational transaction table):
   - `order_id` (PK), `customer_id` (FK), `product_id` (FK), `order_date`, `quantity`, `total_price`
5. **`regional_targets`** (Benchmark lookup table for Joins & KPI reporting):
   - `region` (PK), `target_revenue`, `regional_manager`

---

## 🏆 Key Assignment Results

### 1. Top Customers by Total Spending (Top 5)

| Rank | Customer Name | Region | Orders | Units Bought | Total Spending (₹) | Average Order Value (₹) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | **Lynn Garrison** | East | 1 | 10 | 47,940 | 47,940.00 |
| 2 | **Debbie Turner** | West | 1 | 10 | 44,990 | 44,990.00 |
| 3 | **Megan Charles** | West | 1 | 10 | 44,620 | 44,620.00 |
| 4 | **Michelle Beltran** | East | 1 | 9 | 42,471 | 42,471.00 |
| 5 | **Rick Sanford** | South | 1 | 9 | 41,211 | 41,211.00 |

### 2. Average Order Value (AOV) Summary

- **Overall Store AOV**: **₹12,100.53** (200 Orders, Total Revenue: ₹2,420,107)

#### AOV by Product Category:
1. **Grocery**: ₹13,717.29 (49 orders, Total Revenue: ₹672,147)
2. **Furniture**: ₹12,108.46 (59 orders, Total Revenue: ₹714,399)
3. **Clothing**: ₹12,106.48 (40 orders, Total Revenue: ₹484,259)
4. **Electronics**: ₹10,563.50 (52 orders, Total Revenue: ₹549,302)

#### AOV by Geographic Region:
1. **West**: ₹13,938.77 (43 orders, Total Revenue: ₹599,367)
2. **South**: ₹12,252.29 (66 orders, Total Revenue: ₹808,651)
3. **East**: ₹12,142.16 (51 orders, Total Revenue: ₹619,250)
4. **North**: ₹9,820.98 (40 orders, Total Revenue: ₹392,839)

---

## 🚀 How to Run in VS Code

### Method 1: Run via Python Runner (Terminal)
Open VS Code terminal in the workspace and execute:
```bash
python Week2_SQL/run_analysis.py
```
Or right-click `run_analysis.py` in VS Code and select **"Run Python File in Terminal"**.
This executes all 24 queries sequentially and displays formatted tables directly in the terminal.

### Method 2: Open and Run Jupyter Notebook (`week2.ipynb`)
1. Open `Week2_SQL/week2.ipynb` in VS Code.
2. Select your Python 3 kernel in the top-right corner.
3. Click **"Run All"** to execute all queries cell-by-cell interactively.

### Method 3: Re-import / Reset Database
To rebuild `sales.db` from scratch:
```bash
python Week2_SQL/import_dataset.py
```

### Method 4: Execute SQL directly with SQLite Extension
Install the **SQLite Viewer** or **SQLTools** extension in VS Code:
1. Open `Week2_SQL/sales.db` in VS Code.
2. Open `Week2_SQL/analysis.sql` and run queries against the active database.
