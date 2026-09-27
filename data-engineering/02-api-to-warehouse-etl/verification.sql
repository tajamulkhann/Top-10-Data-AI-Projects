-- SQLite query over the generated artifact.
SELECT customer_id, COUNT(*) AS orders, SUM(amount_cents) AS amount_cents FROM orders GROUP BY customer_id;
