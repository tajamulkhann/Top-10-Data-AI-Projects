-- SQLite query over the generated artifact.
SELECT order_date, COUNT(*) AS orders, SUM(amount_cents) AS amount_cents FROM silver_orders GROUP BY order_date;
