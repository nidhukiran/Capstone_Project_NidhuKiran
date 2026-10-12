-- =====================================================================
-- reports.sql  |  Mamaearth Growth Analytics: Layer 1 reports
-- Run AFTER schema.sql and seed_data.sql, against the RAW (uncleaned) data.
-- Each query is preceded by its exact output as a comment.
-- Revenue per row = quantity * price * (1 - COALESCE(discount_pct, 0) / 100.0)
-- Note: /100.0 (not /100) forces decimal division; integer division would
-- turn 10/100 into 0 and silently ignore every discount.
-- Report (i) alters the customers table, so it is last; to re-run this file
-- on the same database, rebuild with schema.sql + seed_data.sql first.
-- =====================================================================

-- ---------------------------------------------------------------------
-- (a) Order totals: COUNT(*), total revenue, average order value (NULL discount = 0%)
-- ---------------------------------------------------------------------
-- Output:
--   total_orders | total_revenue | avg_order_value
--   -------------+---------------+----------------
--   180          | 99860.20      | 554.78         
SELECT COUNT(*)                         AS total_orders,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2)            AS total_revenue,
       ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2)            AS avg_order_value
FROM orders o
JOIN products p ON p.product_id = o.product_id;

-- ---------------------------------------------------------------------
-- (b) COUNT(*) vs COUNT(column): COUNT(rating) skips NULLs, COUNT(*) does not
-- ---------------------------------------------------------------------
-- Output:
--   total_rows | rated_rows | unrated_rows
--   -----------+------------+-------------
--   180        | 165        | 15          
SELECT COUNT(*)                  AS total_rows,
       COUNT(rating)             AS rated_rows,
       COUNT(*) - COUNT(rating)  AS unrated_rows
FROM orders;

-- ---------------------------------------------------------------------
-- (c) Customers with zero orders: LEFT JOIN + HAVING, cross-checked with NOT IN
-- ---------------------------------------------------------------------
-- c1: LEFT JOIN ... HAVING COUNT(order_id) = 0
-- Output:
--   customer_id | name  
--   ------------+-------
--   C045        | Vihaan
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- c2: independent NOT IN check (must return the same customer)
-- Output:
--   customer_id | name  
--   ------------+-------
--   C045        | Vihaan
SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- ---------------------------------------------------------------------
-- (d) Return rate by city, keeping only cities above 20%
-- ---------------------------------------------------------------------
-- Output:
--   city      | total_orders | returned_orders | return_rate_pct
--   ----------+--------------+-----------------+----------------
--   Jaipur    | 19           | 8               | 42.1           
--   Lucknow   | 49           | 15              | 30.6           
--   Bangalore | 33           | 8               | 24.2           
SELECT c.city,
       COUNT(*)                                      AS total_orders,
       SUM(o.returned)                               AS returned_orders,
       ROUND(100.0 * SUM(o.returned) / COUNT(*), 1)  AS return_rate_pct
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;

-- ---------------------------------------------------------------------
-- (e) Top customers by spend; top 5, then ranks 3-5 via LIMIT 3 OFFSET 2
-- ---------------------------------------------------------------------
-- e1: top 5 (LIMIT 5)
-- Output:
--   customer_id | name    | total_spend
--   ------------+---------+------------
--   C043        | Reyansh | 12920.00   
--   C026        | Isha    | 8371.60    
--   C008        | Meera   | 4564.60    
--   C011        | Arjun   | 4111.00    
--   C042        | Sanya   | 3785.00    
SELECT c.customer_id, c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products  p ON p.product_id  = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
-- customer_id ASC is the tie-break: if two customers have equal spend, it keeps
-- the order deterministic, so LIMIT/OFFSET pages never skip or repeat a row.
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- e2: ranks 3-5 (LIMIT 3 OFFSET 2)
-- Output:
--   customer_id | name  | total_spend
--   ------------+-------+------------
--   C008        | Meera | 4564.60    
--   C011        | Arjun | 4111.00    
--   C042        | Sanya | 3785.00    
SELECT c.customer_id, c.name,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products  p ON p.product_id  = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
-- customer_id ASC is the tie-break: if two customers have equal spend, it keeps
-- the order deterministic, so LIMIT/OFFSET pages never skip or repeat a row.
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- ---------------------------------------------------------------------
-- (f) Three-table JOIN, revenue by product category (customers joined to confirm Part 3 join compiles)
-- ---------------------------------------------------------------------
-- Output:
--   category     | order_count | category_revenue
--   -------------+-------------+-----------------
--   Haircare     | 54          | 44956.10        
--   Skincare     | 60          | 27346.00        
--   Babycare     | 30          | 16805.00        
--   PersonalCare | 36          | 10753.10        
SELECT p.category,
       COUNT(*)                AS order_count,
       ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2)    AS category_revenue
FROM orders o
JOIN products  p ON p.product_id  = o.product_id
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- ---------------------------------------------------------------------
-- (g) LIKE: customers whose name starts with 'A'
-- ---------------------------------------------------------------------
-- Output:
--   customer_id | name  
--   ------------+-------
--   C001        | Aarav 
--   C003        | Aditi 
--   C004        | Ananya
--   C011        | Arjun 
--   C021        | Aryan 
--   C030        | Anika 
--   C031        | Aditya
--   C036        | Aisha 
--   C041        | Ayaan 
--   C044        | Aria  
SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;

-- ---------------------------------------------------------------------
-- (h) DISTINCT acquisition sources
-- ---------------------------------------------------------------------
-- Output:
--   acquisition_source
--   ------------------
--   Ad                
--   Organic           
--   Referral          
--   Social            
SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;

-- ---------------------------------------------------------------------
-- (i) ALTER TABLE + UPDATE with CASE: add loyalty_tier, set for every row (no WHERE)
-- ---------------------------------------------------------------------
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END;

-- Verification output:
--   loyalty_tier | customers
--   -------------+----------
--   Gold         | 28       
--   Silver       | 17       
SELECT loyalty_tier, COUNT(*) AS customers
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;