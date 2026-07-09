-- Retail Sales Analytics Dashboard
-- Reusable SQL queries for the generated SQLite database.

-- 1. Monthly revenue and profit trend
SELECT
  month,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(profit), 2) AS profit,
  COUNT(DISTINCT order_id) AS orders
FROM clean_orders
GROUP BY month
ORDER BY month;

-- 2. Category performance
SELECT
  category,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(profit), 2) AS profit,
  SUM(units) AS units_sold
FROM clean_orders
GROUP BY category
ORDER BY revenue DESC;

-- 3. Region performance
SELECT
  region,
  ROUND(SUM(revenue), 2) AS revenue,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM clean_orders
GROUP BY region
ORDER BY revenue DESC;

-- 4. Channel mix
SELECT
  channel,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM clean_orders), 2) AS revenue_share_pct
FROM clean_orders
GROUP BY channel
ORDER BY revenue DESC;

-- 5. Top products
SELECT
  product,
  category,
  SUM(units) AS units_sold,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(profit), 2) AS profit
FROM clean_orders
GROUP BY product, category
ORDER BY revenue DESC
LIMIT 10;
